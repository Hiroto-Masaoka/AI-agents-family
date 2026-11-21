"""コマンドラインの入口。

    agent-family check                         # 環境の確認(何が使える状態か)
    agent-family ask --track b "質問"           # 1 つの質問を実行(a=Agent SDK・Pro 枠 / b=API 直接)
    agent-family eval --tracks a,b evals/p1-0_smoke.json   # 試験課題を両方式で実行して比較表を出す

`pip install -e .` していない場合は `python -m agent_family.cli ...`(src を PYTHONPATH に入れて実行)。
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

from .guard import PathAllowlist
from .runtimes import RunConfig
from .runtimes.base import DEFAULT_MODEL
from .runtimes.pricing import SpendLedger
from .tools import ToolRegistry, filesystem_tools

LOG_DIR = Path("logs/runtime")


def make_runtime(track: str, root: Path, model: str, max_steps: int, max_cost: float):
    tools = ToolRegistry(filesystem_tools(PathAllowlist.from_paths(root)))
    cfg = RunConfig(model=model, max_steps=max_steps, max_cost_usd=max_cost)
    if track in ("a", "A", "A-sdk", "sdk"):
        from .runtimes.sdk_runtime import SdkRuntime
        return SdkRuntime(tools, cfg, trace_dir=LOG_DIR, cwd=root)
    if track in ("b", "B", "B-api", "api"):
        from .runtimes.api_runtime import ApiRuntime, load_dotenv
        load_dotenv()
        return ApiRuntime(tools, cfg, trace_dir=LOG_DIR, ledger=SpendLedger(LOG_DIR / "spend.jsonl"))
    raise SystemExit(f"不明な track です: {track}(a または b)")


def cmd_check(_: argparse.Namespace) -> int:
    from .runtimes.api_runtime import load_dotenv
    load_dotenv()
    ok = lambda b: "✅" if b else "❌"  # noqa: E731
    sdk = importlib.util.find_spec("claude_agent_sdk") is not None
    cli = shutil.which("claude") is not None
    api = importlib.util.find_spec("anthropic") is not None
    key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    ledger = SpendLedger(LOG_DIR / "spend.jsonl")
    print("== Track A(Agent SDK・Pro 枠)")
    print(f"  {ok(sdk)} claude-agent-sdk パッケージ")
    print(f"  {ok(cli)} claude コマンド(Claude Code)  ※未ログインなら `claude` を起動して /login")
    print("== Track B(API 直接・従量課金)")
    print(f"  {ok(api)} anthropic パッケージ")
    print(f"  {ok(key)} ANTHROPIC_API_KEY(値は表示しません)")
    print(f"  今月のローカル記録の利用額: ${ledger.month_total():.4f} / 予算 ${ledger.monthly_budget_usd:.2f}")
    print("== 共通")
    print(f"  {ok(Path('.gitignore').exists())} .gitignore(.env が除外されていること)")
    return 0


def cmd_ask(a: argparse.Namespace) -> int:
    rt = make_runtime(a.track, Path(a.root), a.model, a.max_steps, a.max_cost)
    res = rt.run(a.prompt)
    print(res.answer or "(回答なし)")
    print("\n---")
    print(json.dumps({k: v for k, v in res.to_dict().items() if k != "answer"}, ensure_ascii=False, indent=1))
    if res.trace is not None and res.trace.path:
        print(f"トレース: {res.trace.path}")
    return 0 if res.ok else 1


def cmd_eval(a: argparse.Namespace) -> int:
    from .eval import EvalSuite, run_suite, to_markdown
    suite = EvalSuite.load(Path(a.suite))
    root = Path(a.root)
    runtimes = {}
    for t in a.tracks.split(","):
        rt = make_runtime(t.strip(), root, a.model, a.max_steps, a.max_cost)
        runtimes[rt.track] = rt.run
    summary = run_suite(suite, runtimes, integrity_root=root, out_dir=LOG_DIR)
    print(to_markdown(summary))
    if "saved_to" in summary:
        print(f"\n詳細: {summary['saved_to']}")
    return 0 if all(r["passed"] for r in summary["rows"]) else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="agent-family", description="AI-agents-family Phase 1(読み取り専用)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="環境の確認").set_defaults(func=cmd_check)

    def common(sp):
        sp.add_argument("--root", default=".", help="読んでよいディレクトリ(既定: 現在のディレクトリ)")
        sp.add_argument("--model", default=DEFAULT_MODEL)
        sp.add_argument("--max-steps", type=int, default=12)
        sp.add_argument("--max-cost", type=float, default=0.5, help="1 回の実行の費用上限 USD")

    sp = sub.add_parser("ask", help="1 つの質問を実行")
    sp.add_argument("--track", required=True, help="a=Agent SDK(Pro 枠) / b=API 直接")
    sp.add_argument("prompt")
    common(sp)
    sp.set_defaults(func=cmd_ask)

    sp = sub.add_parser("eval", help="試験課題を実行して比較表を出す")
    sp.add_argument("suite", help="試験課題の JSON ファイル")
    sp.add_argument("--tracks", default="a,b")
    common(sp)
    sp.set_defaults(func=cmd_eval)

    a = p.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
