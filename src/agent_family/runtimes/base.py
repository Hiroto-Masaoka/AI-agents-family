"""両方式に共通の設定と結果の形。比較表はこの RunResult から作る。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

DEFAULT_MODEL = "claude-sonnet-5-5"

DEFAULT_SYSTEM_PROMPT = """あなたは研究者を支援する読み取り専用のアシスタントです。
- 与えられたツールだけを使って情報を集め、質問に日本語で簡潔に答えてください。
- 回答の根拠にしたファイルのパスを、回答の最後に「参照: path1, path2」の形で必ず示してください。
- ファイルの作成・変更・削除はできません。依頼されても実行せず、できないと答えてください。
- 許可されていない場所を読もうとして拒否された場合は、そのことを正直に伝えてください。
- 分からないことは推測せず「分かりません」と答えてください。"""


@dataclass
class RunConfig:
    model: str = DEFAULT_MODEL
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    max_steps: int = 12          # LLM を呼ぶ回数の上限(暴走防止)
    max_tokens: int = 2048       # 1 回の応答の最大出力トークン数
    max_cost_usd: float = 1.0    # 1 回の実行の費用上限(Track B。Track A では SDK に渡す)


@dataclass
class RunResult:
    track: str                   # "A-sdk" / "B-api"
    model: str
    answer: str
    steps: int                   # LLM 応答の回数
    tool_calls: int
    input_tokens: int | None
    output_tokens: int | None
    cost_usd: float | None       # Track B: 料金表からの計算値 / Track A: SDK の報告値(Pro 枠では参考値)
    duration_s: float
    error: str | None = None
    run_id: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)
    trace: Any = field(default=None, repr=False, compare=False)  # TraceRecorder(比較表には含めない)

    @property
    def ok(self) -> bool:
        return self.error is None

    def to_dict(self) -> dict[str, Any]:
        t, self.trace = self.trace, None
        try:
            d = asdict(self)
            d.pop("trace", None)
            return d
        finally:
            self.trace = t
