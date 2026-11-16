"""読み取り専用のファイルツール(P1-0 / P1-1 用)。

- list_dir:ディレクトリの中身を一覧する
- read_file:テキストファイルを読む(行範囲の指定可)

どちらも PathAllowlist を通すので、許可外の場所や機密ファイルは読めません。
書き込み・削除の機能はありません(ADR-0009)。
"""

from __future__ import annotations

from typing import Any

from ..guard import AccessDenied, PathAllowlist
from .base import ToolError, ToolSpec

MAX_ENTRIES = 200
MAX_LINES = 400


def filesystem_tools(allow: PathAllowlist) -> list[ToolSpec]:
    def list_dir(args: dict[str, Any]) -> str:
        path = args.get("path", ".")
        try:
            real = allow.resolve(path)
        except AccessDenied as e:
            raise ToolError(str(e)) from e
        if not real.is_dir():
            raise ToolError(f"ディレクトリではありません: {path}")
        entries = []
        for child in sorted(real.iterdir(), key=lambda c: (not c.is_dir(), c.name)):
            try:
                allow.resolve(child)  # 機密ファイル・外部へのリンクは一覧にも出さない
            except AccessDenied:
                continue
            entries.append(child.name + ("/" if child.is_dir() else ""))
            if len(entries) >= MAX_ENTRIES:
                entries.append(f"...(上限 {MAX_ENTRIES} 件で打ち切り)")
                break
        return f"{allow.display(real)}:\n" + "\n".join(entries) if entries else f"{allow.display(real)}: (空)"

    def read_file(args: dict[str, Any]) -> str:
        path = args.get("path")
        if not path:
            raise ToolError("path を指定してください")
        try:
            real = allow.resolve(path)
            if not real.is_file():
                raise ToolError(f"ファイルではありません: {path}")
            allow.check_file_size(real)
        except AccessDenied as e:
            raise ToolError(str(e)) from e
        try:
            lines = real.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError as e:
            raise ToolError(f"テキストとして読めないファイルです: {path}") from e
        start = max(int(args.get("start_line", 1)), 1)
        end = min(int(args.get("end_line", start + MAX_LINES - 1)), len(lines), start + MAX_LINES - 1)
        body = "\n".join(f"{i:>5}: {lines[i - 1]}" for i in range(start, end + 1)) if lines else "(空のファイル)"
        more = f"\n...(全 {len(lines)} 行。続きは start_line={end + 1} で読めます)" if end < len(lines) else ""
        return f"{allow.display(real)}(行 {start}-{end} / 全 {len(lines)} 行)\n{body}{more}"

    return [
        ToolSpec(
            name="list_dir",
            description="許可されたディレクトリの中身(ファイルとサブディレクトリ)を一覧します。読み取り専用。",
            input_schema={
                "type": "object",
                "properties": {"path": {"type": "string", "description": "リポジトリのルートからの相対パス。省略時はルート。"}},
                "required": [],
            },
            func=list_dir,
        ),
        ToolSpec(
            name="read_file",
            description=(
                "許可されたディレクトリ内のテキストファイルを、行番号付きで読みます。読み取り専用。"
                f"一度に最大 {MAX_LINES} 行。長いファイルは start_line / end_line で分けて読みます。"
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "リポジトリのルートからの相対パス"},
                    "start_line": {"type": "integer", "minimum": 1},
                    "end_line": {"type": "integer", "minimum": 1},
                },
                "required": ["path"],
            },
            func=read_file,
        ),
    ]
