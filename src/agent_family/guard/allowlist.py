"""許可リスト(ガードレール)。

エージェントが読んでよい場所を、プログラム側で強制します(ADR-0009)。
LLM への「読まないでください」というお願いではなく、許可外のパスはここで必ず拒否します。

守ること:
- 許可したディレクトリ(roots)の外は読めない(`..` やシンボリックリンクで外に出ることも防ぐ)
- 許可ディレクトリの中でも、機密情報になりうるファイル(.env、鍵など)は読めない
- 大きすぎるファイルは読まない(コンテキストと費用の保護)
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path

# 許可ディレクトリの中でも読ませないもの(ファイル名・ディレクトリ名のパターン)
DEFAULT_DENY_PATTERNS: tuple[str, ...] = (
    ".env",
    ".env.*",
    "*.key",
    "*.pem",
    "*.p12",
    "id_rsa*",
    "id_ed25519*",
    "credentials*.json",
    "*token*",
    ".git",
    "secrets",
    ".ssh",
)


class AccessDenied(PermissionError):
    """許可リストによってアクセスが拒否されたことを表す例外。"""


@dataclass
class PathAllowlist:
    roots: list[Path]
    deny_patterns: tuple[str, ...] = DEFAULT_DENY_PATTERNS
    max_file_bytes: int = 200_000
    _resolved_roots: list[Path] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.roots:
            raise ValueError("roots(許可ディレクトリ)を 1 つ以上指定してください")
        self._resolved_roots = [Path(r).expanduser().resolve() for r in self.roots]

    @classmethod
    def from_paths(cls, *paths: str | Path, **kwargs) -> "PathAllowlist":
        return cls(roots=[Path(p) for p in paths], **kwargs)

    def resolve(self, path: str | Path) -> Path:
        """パスを検査し、許可されていれば絶対パスを返す。許可外なら AccessDenied。

        相対パスは最初の許可ディレクトリを基準に解釈します。
        """
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = self._resolved_roots[0] / p
        # resolve() はシンボリックリンクと `..` を解決するので、外への脱出を検出できる
        real = p.resolve()
        root = next((r for r in self._resolved_roots if real == r or r in real.parents), None)
        if root is None:
            raise AccessDenied(f"許可されていない場所です: {path}")
        for part in real.relative_to(root).parts:
            if any(fnmatch.fnmatch(part, pat) for pat in self.deny_patterns):
                raise AccessDenied(f"機密情報の可能性があるため読めません: {path}")
        return real

    def check_file_size(self, real: Path) -> None:
        size = real.stat().st_size
        if size > self.max_file_bytes:
            raise AccessDenied(
                f"ファイルが大きすぎます({size} bytes > 上限 {self.max_file_bytes} bytes): {real.name}"
            )

    def display(self, real: Path) -> str:
        """許可ディレクトリからの相対パス(LLM に見せる表記)。"""
        for r in self._resolved_roots:
            if real == r or r in real.parents:
                rel = real.relative_to(r)
                return str(rel) if str(rel) != "." else "."
        return str(real)
