"""トレース(エージェントの行動記録)の共通形式。Track A / B で同じ形式を使う。

1 行 = 1 イベントの JSON(JSON Lines)。イベントの種類:
- run_start : 実行の開始(track、モデル、質問)
- llm_call  : LLM の 1 回の応答(トークン数、停止理由)
- tool_call : ツール呼び出し(名前、入力、成功/失敗、結果の先頭、所要時間)
- run_end   : 実行の終了(最終回答、合計、エラー)

書き込み先は logs/runtime/(.gitignore 済み)。これはエージェントではなく
ハーネス(このプログラム)が書く唯一の例外です(ADR-0009)。
write_to=None にすると、ファイルに書かずメモリ上に保持するだけになります。
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PREVIEW_CHARS = 500
SCHEMA_VERSION = 1


class TraceRecorder:
    def __init__(self, track: str, write_to: Path | None = None, run_id: str | None = None) -> None:
        self.track = track
        self.run_id = run_id or f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{track}-{uuid.uuid4().hex[:6]}"
        self.events: list[dict[str, Any]] = []
        self._t0 = time.monotonic()
        self.path: Path | None = None
        if write_to is not None:
            write_to.mkdir(parents=True, exist_ok=True)
            self.path = write_to / f"{self.run_id}.jsonl"

    def _emit(self, kind: str, **data: Any) -> dict[str, Any]:
        ev = {
            "schema": SCHEMA_VERSION,
            "run_id": self.run_id,
            "track": self.track,
            "t": round(time.monotonic() - self._t0, 3),
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "event": kind,
            **data,
        }
        self.events.append(ev)
        if self.path is not None:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        return ev

    def run_start(self, *, model: str, prompt: str) -> None:
        self._emit("run_start", model=model, prompt=prompt)

    def llm_call(self, *, input_tokens: int | None, output_tokens: int | None, stop_reason: str | None,
                 cache_read_tokens: int | None = None, cache_write_tokens: int | None = None) -> None:
        self._emit("llm_call", input_tokens=input_tokens, output_tokens=output_tokens, stop_reason=stop_reason,
                   cache_read_tokens=cache_read_tokens, cache_write_tokens=cache_write_tokens)

    def tool_call(self, *, name: str, tool_input: dict[str, Any], ok: bool, output: str, duration_s: float) -> None:
        self._emit("tool_call", name=name, input=tool_input, ok=ok,
                   output_preview=output[:PREVIEW_CHARS], output_chars=len(output), duration_s=round(duration_s, 3))

    def run_end(self, **summary: Any) -> None:
        self._emit("run_end", **summary)

    # --- 集計(評価・比較用) ---
    def tool_calls(self) -> list[dict[str, Any]]:
        return [e for e in self.events if e["event"] == "tool_call"]
