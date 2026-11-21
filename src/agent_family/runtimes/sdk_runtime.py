"""Track A:Claude Agent SDK を Claude Pro アカウントで使う実行方式。

エージェントループ(LLM 呼び出し → ツール実行 → 繰り返し)は SDK(Claude Code と同じ仕組み)が担います。
このファイルが行うのは次の 3 つだけです:

    1. 共通の ToolSpec を SDK のツール(プロセス内 MCP サーバー)に変換して登録する
    2. 読み取り専用にするための設定をする(下記)
    3. SDK から返るメッセージを、Track B と同じトレース形式・RunResult に変換する

読み取り専用の強制(ADR-0009):
- tools=[] で Claude Code の組み込みツール(Read / Write / Edit / Bash / Web 検索など)をすべて無効にする
- allowed_tools には自作の読み取りツールだけを入れ、念のため書き込み系を disallowed_tools にも入れる
- setting_sources=[] で、利用者の設定ファイルや CLAUDE.md を読み込ませない(Track B と条件を揃えるため)

認証:Claude Pro のログイン(事前に `claude` を起動して /login)。
環境変数 ANTHROPIC_API_KEY があると従量課金の API が使われてしまうため、実行中は一時的に取り除きます。
"""

from __future__ import annotations

import asyncio
import contextlib
import os
import time
from pathlib import Path
from typing import Any, Iterator

from ..tools import ToolError, ToolRegistry, ToolSpec
from ..trace import TraceRecorder
from .base import RunConfig, RunResult

TRACK = "A-sdk"
SERVER_NAME = "af"  # ツール名は mcp__af__<name> になる

# 念のため明示的に禁止する組み込みツール(tools=[] で既に無効)
BUILTIN_WRITE_TOOLS = ["Write", "Edit", "MultiEdit", "NotebookEdit", "Bash", "BashOutput", "KillShell",
                       "WebFetch", "WebSearch", "Read", "Glob", "Grep", "Task"]
API_KEY_ENV_VARS = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")


def sdk_tool_name(name: str) -> str:
    return f"mcp__{SERVER_NAME}__{name}"


@contextlib.contextmanager
def subscription_auth_env() -> Iterator[None]:
    """実行中だけ API キーの環境変数を外し、Pro のログインが使われるようにする。"""
    saved = {k: os.environ.pop(k) for k in API_KEY_ENV_VARS if k in os.environ}
    try:
        yield
    finally:
        os.environ.update(saved)


def build_sdk_tools(tools: ToolRegistry, trace: TraceRecorder) -> list[Any]:
    """共通の ToolSpec を SDK のツールに変換する。ツール呼び出しは Track B と同じ形式でトレースに記録する。"""
    from claude_agent_sdk import tool

    def make(spec: ToolSpec):
        @tool(spec.name, spec.description, spec.input_schema)
        async def handler(args: dict[str, Any]) -> dict[str, Any]:
            ts = time.monotonic()
            try:
                out, ok = spec.func(args or {}), True
            except ToolError as e:
                out, ok = f"エラー: {e}", False
            except Exception as e:
                out, ok = f"エラー(予期しない失敗): {type(e).__name__}: {e}", False
            trace.tool_call(name=spec.name, tool_input=args or {}, ok=ok, output=out,
                            duration_s=time.monotonic() - ts)
            return {"content": [{"type": "text", "text": out}], "is_error": not ok}

        return handler

    return [make(s) for s in tools]


def build_options(tools: ToolRegistry, config: RunConfig, trace: TraceRecorder, cwd: Path | None = None) -> Any:
    from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server

    server = create_sdk_mcp_server(SERVER_NAME, tools=build_sdk_tools(tools, trace))
    return ClaudeAgentOptions(
        tools=[],                                            # 組み込みツールをすべて無効化
        mcp_servers={SERVER_NAME: server},
        allowed_tools=[sdk_tool_name(n) for n in tools.names()],
        disallowed_tools=list(BUILTIN_WRITE_TOOLS),
        system_prompt=config.system_prompt,                  # Track B と同じ指示文
        model=config.model,
        max_turns=config.max_steps,
        max_budget_usd=config.max_cost_usd,
        setting_sources=[],                                  # 利用者の設定・CLAUDE.md を読み込まない
        cwd=str(cwd) if cwd else None,
    )


def _usage_int(usage: Any, key: str) -> int:
    if isinstance(usage, dict):
        return int(usage.get(key) or 0)
    return int(getattr(usage, key, 0) or 0)


class SdkRuntime:
    track = TRACK

    def __init__(self, tools: ToolRegistry, config: RunConfig | None = None, *,
                 trace_dir: Path | None = None, cwd: Path | None = None) -> None:
        self.tools = tools
        self.config = config or RunConfig()
        self.trace_dir = trace_dir
        self.cwd = cwd

    def run(self, prompt: str) -> RunResult:
        return asyncio.run(self.arun(prompt))

    async def arun(self, prompt: str) -> RunResult:
        try:
            from claude_agent_sdk import AssistantMessage, ResultMessage, TextBlock, query
        except ImportError as e:
            raise RuntimeError("Track A には claude-agent-sdk が必要です: pip install -e '.[sdk]'") from e

        cfg = self.config
        trace = TraceRecorder(self.track, self.trace_dir)
        trace.run_start(model=cfg.model, prompt=prompt)
        t0 = time.monotonic()
        steps, texts = 0, []
        final: Any = None
        error = None
        try:
            options = build_options(self.tools, cfg, trace, self.cwd)
            with subscription_auth_env():
                async for msg in query(prompt=prompt, options=options):
                    if isinstance(msg, AssistantMessage):
                        steps += 1
                        u = msg.usage or {}
                        trace.llm_call(input_tokens=_usage_int(u, "input_tokens"),
                                       output_tokens=_usage_int(u, "output_tokens"), stop_reason=msg.stop_reason,
                                       cache_read_tokens=_usage_int(u, "cache_read_input_tokens"),
                                       cache_write_tokens=_usage_int(u, "cache_creation_input_tokens"))
                        texts += [b.text for b in msg.content if isinstance(b, TextBlock)]
                    elif isinstance(msg, ResultMessage):
                        final = msg
        except Exception as e:
            error = f"{type(e).__name__}: {e}"

        u = (final.usage if final else None) or {}
        answer = (final.result if final and final.result else (texts[-1] if texts else "")).strip()
        if final is not None and final.is_error and error is None:
            error = f"SDK がエラーを報告: {final.subtype} {final.errors or ''}".strip()
        result = RunResult(
            track=self.track, model=cfg.model, answer=answer, steps=steps,
            tool_calls=len(trace.tool_calls()),
            input_tokens=_usage_int(u, "input_tokens") if final else None,
            output_tokens=_usage_int(u, "output_tokens") if final else None,
            cost_usd=final.total_cost_usd if final else None,
            duration_s=round(time.monotonic() - t0, 3), error=error, run_id=trace.run_id,
            extra={"num_turns": getattr(final, "num_turns", None),
                   "cache_read_tokens": _usage_int(u, "cache_read_input_tokens"),
                   "cache_write_tokens": _usage_int(u, "cache_creation_input_tokens"),
                   "permission_denials": getattr(final, "permission_denials", None),
                   "cost_note": "Pro 枠では total_cost_usd は API 料金換算の参考値(請求ではない)"},
        )
        trace.run_end(**{k: v for k, v in result.to_dict().items() if k not in ("track", "trace")})
        result.trace = trace
        return result
