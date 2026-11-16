"""読み取り専用の検証:試験の前後でファイルの SHA-256 一覧を比べる(ADR-0009)。

ハーネス自身が書く logs/runtime/ と、Git の内部(.git/)は比較の対象外です。
"""

from __future__ import annotations

import hashlib
from pathlib import Path

EXCLUDE_DIRS = {".git", "logs", "__pycache__", ".pytest_cache", ".venv", "venv", ".mypy_cache"}


def manifest(root: Path) -> dict[str, str]:
    root = Path(root).resolve()
    out: dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if any(part in EXCLUDE_DIRS for part in rel.parts) or not p.is_file():
            continue
        out[str(rel)] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def diff_manifests(before: dict[str, str], after: dict[str, str]) -> dict[str, list[str]]:
    return {
        "added": sorted(set(after) - set(before)),
        "removed": sorted(set(before) - set(after)),
        "changed": sorted(k for k in set(before) & set(after) if before[k] != after[k]),
    }
