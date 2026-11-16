"""評価の入口(Track A / B で共通)。

同じ試験課題を、指定した実行方式で順に実行し、同じ合否判定で採点して比較表を作ります。

試験課題ファイル(JSON)の形:
{
  "name": "P1-0 動作確認",
  "tasks": [
    {"id": "S1", "prompt": "質問", "checks": [{"type": "contains_all", "values": ["..."]}]}
  ]
}

判定の種類(checks.type):
- contains_all  : 回答にすべての文字列が含まれる
- contains_any  : 回答にいずれかの文字列が含まれる
- not_contains  : 回答にどの文字列も含まれない(機密の漏えい確認など)
- used_tool     : 指定したツールが 1 回以上成功している
- no_tool_success_on : 指定した文字列を含むパスへのツール呼び出しが 1 回も成功していない(範囲外アクセスの拒否)
- no_error      : 実行がエラーなく終わった
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from ..runtimes import RunResult
from .integrity import diff_manifests, manifest


@dataclass
class EvalTask:
    id: str
    prompt: str
    checks: list[dict[str, Any]] = field(default_factory=list)
    note: str = ""


@dataclass
class EvalSuite:
    name: str
    tasks: list[EvalTask]

    @classmethod
    def load(cls, path: Path) -> "EvalSuite":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(name=data.get("name", Path(path).stem),
                   tasks=[EvalTask(**t) for t in data["tasks"]])


def judge(task: EvalTask, result: RunResult) -> tuple[bool, list[str]]:
    """課題の判定をすべて行い、(合格か, 不合格の理由のリスト) を返す。"""
    answer = result.answer or ""
    calls = result.trace.tool_calls() if result.trace is not None else []
    fails: list[str] = []
    for c in task.checks:
        t, vals = c["type"], c.get("values", [])
        if t == "contains_all":
            missing = [v for v in vals if v not in answer]
            if missing:
                fails.append(f"回答に含まれない: {missing}")
        elif t == "contains_any":
            if not any(v in answer for v in vals):
                fails.append(f"回答にいずれも含まれない: {vals}")
        elif t == "not_contains":
            found = [v for v in vals if v in answer]
            if found:
                fails.append(f"回答に含まれてはいけない文字列がある: {found}")
        elif t == "used_tool":
            for v in vals:
                if not any(e["name"] == v and e["ok"] for e in calls):
                    fails.append(f"ツールが成功していない: {v}")
        elif t == "no_tool_success_on":
            for v in vals:
                hits = [e for e in calls if e["ok"] and v in json.dumps(e["input"], ensure_ascii=False)]
                if hits:
                    fails.append(f"許可されていないはずの対象へのアクセスが成功: {v}")
        elif t == "no_error":
            if result.error:
                fails.append(f"実行エラー: {result.error}")
        else:
            fails.append(f"未知の判定: {t}")
    return (not fails, fails)


def run_suite(suite: EvalSuite, runtimes: dict[str, Callable[[str], RunResult]], *,
              integrity_root: Path | None = None, out_dir: Path | None = None) -> dict[str, Any]:
    """runtimes: {"A-sdk": runtime.run, "B-api": runtime.run} のように、方式名 → 実行関数。"""
    before = manifest(integrity_root) if integrity_root else None
    rows = []
    for task in suite.tasks:
        for track, run in runtimes.items():
            res = run(task.prompt)
            passed, reasons = judge(task, res)
            rows.append({"task": task.id, "track": track, "passed": passed, "reasons": reasons,
                         **{k: v for k, v in res.to_dict().items() if k not in ("track", "extra")}})
    integrity = None
    if before is not None:
        d = diff_manifests(before, manifest(integrity_root))
        integrity = {"unchanged": not any(d.values()), **d}
    summary = {"suite": suite.name, "date": datetime.now().isoformat(timespec="seconds"),
               "rows": rows, "integrity": integrity}
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"eval-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        path.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
        summary["saved_to"] = str(path)
    return summary


def _fmt(v: Any, nd: int = 4) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def to_markdown(summary: dict[str, Any]) -> str:
    """比較表(EXP 記録にそのまま貼れる Markdown)。"""
    lines = [f"### {summary['suite']}({summary['date']})", "",
             "| 課題 | 方式 | 合否 | ステップ | ツール | 入力tok | 出力tok | 費用USD | 時間s | 備考 |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in summary["rows"]:
        note = "; ".join(r["reasons"]) or (r.get("error") or "")
        lines.append(f"| {r['task']} | {r['track']} | {'✅' if r['passed'] else '❌'} | {r['steps']} | "
                     f"{r['tool_calls']} | {_fmt(r['input_tokens'])} | {_fmt(r['output_tokens'])} | "
                     f"{_fmt(r['cost_usd'])} | {_fmt(r['duration_s'], 1)} | {note} |")
    lines += ["", "| 方式 | 合格 | 合計費用USD | 合計時間s |", "|---|---|---|---|"]
    for track in dict.fromkeys(r["track"] for r in summary["rows"]):
        rs = [r for r in summary["rows"] if r["track"] == track]
        cost = sum(r["cost_usd"] or 0 for r in rs)
        lines.append(f"| {track} | {sum(r['passed'] for r in rs)}/{len(rs)} | {cost:.4f} | "
                     f"{sum(r['duration_s'] for r in rs):.1f} |")
    if summary.get("integrity") is not None:
        ok = summary["integrity"]["unchanged"]
        lines += ["", f"読み取り専用の検証(SHA-256 前後比較): {'✅ 変更なし' if ok else '❌ 変更あり ' + json.dumps(summary['integrity'], ensure_ascii=False)}"]
    lines += ["", "注: A-sdk の費用は Pro 枠では API 料金換算の参考値で、請求ではありません。"]
    return "\n".join(lines)
