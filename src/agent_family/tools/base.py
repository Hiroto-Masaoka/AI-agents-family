"""ツールの共通定義(Track A / B で共通)。

1 つのツール = 名前 + 説明 + 入力の形(JSON Schema)+ 実際に動く Python 関数。
同じ ToolSpec を、Track B では Messages API の `tools` 定義に、
Track A では Agent SDK のツール(プロセス内 MCP)に変換して登録します。
こうすることで「変えるのは実行方式だけ」という比較の条件を守ります(ADR-0012)。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


class ToolError(Exception):
    """ツールの実行に失敗したとき(引数の誤り、ファイルがない等)。LLM には失敗として返す。"""


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]  # JSON Schema(type: object)
    func: Callable[[dict[str, Any]], str]
    read_only: bool = True

    def to_api_tool(self) -> dict[str, Any]:
        """Track B: Messages API の tools 配列に入れる形式。"""
        return {"name": self.name, "description": self.description, "input_schema": self.input_schema}


class ToolRegistry:
    """使ってよいツールの一覧。Phase 1 では読み取り専用のツールしか登録できない。"""

    def __init__(self, tools: list[ToolSpec] | None = None, *, allow_write: bool = False) -> None:
        self._tools: dict[str, ToolSpec] = {}
        self.allow_write = allow_write
        for t in tools or []:
            self.register(t)

    def register(self, tool: ToolSpec) -> None:
        if not tool.read_only and not self.allow_write:
            # ADR-0009: Phase 1 では書き込み能力をツールとして存在させない
            raise ValueError(f"Phase 1 では書き込み系ツールを登録できません: {tool.name}")
        if tool.name in self._tools:
            raise ValueError(f"同じ名前のツールが既にあります: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolSpec:
        if name not in self._tools:
            raise ToolError(f"存在しないツールです: {name}")
        return self._tools[name]

    def __iter__(self):
        return iter(self._tools.values())

    def __len__(self) -> int:
        return len(self._tools)

    def names(self) -> list[str]:
        return list(self._tools)

    def api_tools(self) -> list[dict[str, Any]]:
        return [t.to_api_tool() for t in self._tools.values()]
