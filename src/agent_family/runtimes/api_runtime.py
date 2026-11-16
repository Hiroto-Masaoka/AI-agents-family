"""Track B:Messages API を直接呼ぶ、自作のエージェントループ。

エージェントの仕組みがすべてここに見えるように書いています。流れ:

    1. 質問と「使えるツールの一覧」を LLM に送る
    2. LLM の応答を見る
       - stop_reason == "tool_use" なら、LLM が「このツールをこの引数で呼んで」と言っている
         → このプログラムがツールを実行し、結果を LLM に返して 1 に戻る
       - それ以外なら、最終回答として終了
    3. 回数(max_steps)と費用(max_cost_usd)の上限で必ず止まる

LLM 自身は何も実行しません。実行するのは常にこのプログラムで、実行できるのは
ToolRegistry に登録された読み取り専用のツールだけです(ADR-0009)。

認証:環境変数 ANTHROPIC_API_KEY(.env から読み込み)。従量課金です(ADR-0012)。
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Protocol

from ..tools import ToolError, ToolRegistry
from ..trace import TraceRecorder
from .base import RunConfig, RunResult
from .pricing import BudgetExceeded, SpendLedger, estimate_cost

TRACK = "B-api"


class MessagesClient(Protocol):
    """anthropic.Anthropic().messages と同じ形の create() を持つもの(試験では偽物に差し替える)。"""

    def create(self, **kwargs: Any) -> Any: ...


def load_dotenv(path: Path = Path(".env")) -> None:
    """依存ライブラリを増やさないための最小の .env 読み込み(既に設定済みの環境変数は上書きしない)。"""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def default_client() -> MessagesClient:
    try:
        import anthropic  # 遅延 import:Track A だけ使う人はインストール不要
    except ImportError as e:
        raise RuntimeError("Track B には anthropic パッケージが必要です: pip install -e '.[api]'") from e
    load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY が設定されていません(.env.example を参照)")
    return anthropic.Anthropic().messages


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """SDK のオブジェクトと dict の両方から値を取り出す。"""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _block_to_dict(block: Any) -> dict[str, Any]:
    if isinstance(block, dict):
        return block
    if hasattr(block, "model_dump"):
        return block.model_dump(exclude_none=True)
    return dict(vars(block))


class ApiRuntime:
    track = TRACK

    def __init__(self, tools: ToolRegistry, config: RunConfig | None = None, *,
                 client: MessagesClient | None = None, trace_dir: Path | None = None,
                 ledger: SpendLedger | None = None) -> None:
        self.tools = tools
        self.config = config or RunConfig()
        self._client = client
        self.trace_dir = trace_dir
        self.ledger = ledger

    @property
    def client(self) -> MessagesClient:
        if self._client is None:
            self._client = default_client()
        return self._client

    def run(self, prompt: str) -> RunResult:
        cfg = self.config
        trace = TraceRecorder(self.track, self.trace_dir)
        trace.run_start(model=cfg.model, prompt=prompt)
        t0 = time.monotonic()
        messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
        tin = tout = cread = cwrite = 0
        steps = ntools = 0
        answer, error = "", None

        try:
            if self.ledger is not None:
                self.ledger.check(cfg.max_cost_usd)
            while True:
                if steps >= cfg.max_steps:
                    error = f"max_steps({cfg.max_steps})に達したため停止"
                    break
                # --- 1. LLM を呼ぶ ---
                resp = self.client.create(
                    model=cfg.model, max_tokens=cfg.max_tokens, system=cfg.system_prompt,
                    tools=self.tools.api_tools(), messages=messages,
                )
                steps += 1
                usage = _get(resp, "usage", {}) or {}
                u_in, u_out = _get(usage, "input_tokens", 0) or 0, _get(usage, "output_tokens", 0) or 0
                u_cr = _get(usage, "cache_read_input_tokens", 0) or 0
                u_cw = _get(usage, "cache_creation_input_tokens", 0) or 0
                tin, tout, cread, cwrite = tin + u_in, tout + u_out, cread + u_cr, cwrite + u_cw
                stop = _get(resp, "stop_reason")
                trace.llm_call(input_tokens=u_in, output_tokens=u_out, stop_reason=stop,
                               cache_read_tokens=u_cr, cache_write_tokens=u_cw)

                content = [_block_to_dict(b) for b in (_get(resp, "content", []) or [])]
                messages.append({"role": "assistant", "content": content})

                cost_so_far = estimate_cost(cfg.model, tin, tout, cread, cwrite) or 0.0
                if cost_so_far > cfg.max_cost_usd:
                    error = f"max_cost_usd(${cfg.max_cost_usd})を超えたため停止"
                    break

                # --- 2. ツール呼び出しがなければ最終回答 ---
                tool_uses = [b for b in content if b.get("type") == "tool_use"]
                if stop != "tool_use" or not tool_uses:
                    answer = "\n".join(b.get("text", "") for b in content if b.get("type") == "text").strip()
                    break

                # --- 3. ツールを実行し、結果を LLM に返す ---
                results = []
                for tu in tool_uses:
                    ntools += 1
                    name, tool_input = tu.get("name", ""), tu.get("input", {}) or {}
                    ts = time.monotonic()
                    try:
                        out, ok = self.tools.get(name).func(tool_input), True
                    except ToolError as e:
                        out, ok = f"エラー: {e}", False
                    except Exception as e:  # 想定外の失敗も LLM に伝えて続行させる
                        out, ok = f"エラー(予期しない失敗): {type(e).__name__}: {e}", False
                    trace.tool_call(name=name, tool_input=tool_input, ok=ok, output=out,
                                    duration_s=time.monotonic() - ts)
                    results.append({"type": "tool_result", "tool_use_id": tu.get("id"),
                                    "content": out, "is_error": not ok})
                messages.append({"role": "user", "content": results})
        except BudgetExceeded as e:
            error = str(e)
        except Exception as e:
            error = f"{type(e).__name__}: {e}"

        cost = estimate_cost(cfg.model, tin, tout, cread, cwrite)
        if self.ledger is not None and cost:
            self.ledger.add(cost, trace.run_id, cfg.model)
        result = RunResult(track=self.track, model=cfg.model, answer=answer, steps=steps, tool_calls=ntools,
                           input_tokens=tin, output_tokens=tout, cost_usd=cost,
                           duration_s=round(time.monotonic() - t0, 3), error=error, run_id=trace.run_id,
                           extra={"cache_read_tokens": cread, "cache_write_tokens": cwrite})
        trace.run_end(**{k: v for k, v in result.to_dict().items() if k not in ("track", "trace")})
        result.trace = trace
        return result
