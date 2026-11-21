"""P1-0 の雛形の試験。LLM には接続せず、偽の応答(Track B)と SDK の設定生成(Track A)で確かめる。"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from agent_family.eval import EvalSuite, EvalTask, diff_manifests, judge, manifest, run_suite, to_markdown
from agent_family.guard import AccessDenied, PathAllowlist
from agent_family.runtimes import RunConfig
from agent_family.runtimes.api_runtime import ApiRuntime
from agent_family.runtimes.pricing import BudgetExceeded, SpendLedger, estimate_cost
from agent_family.tools import ToolError, ToolRegistry, ToolSpec, filesystem_tools


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text("# Demo\n現在は Phase 1 です。\n", encoding="utf-8")
    (tmp_path / "docs" / "a.md").write_text("\n".join(f"line {i}" for i in range(1, 11)), encoding="utf-8")
    (tmp_path / ".env").write_text("ANTHROPIC_API_KEY=sk-ant-SECRET\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    return tmp_path


@pytest.fixture()
def tools(repo: Path) -> ToolRegistry:
    return ToolRegistry(filesystem_tools(PathAllowlist.from_paths(repo)))


# ---------- 許可リスト ----------
def test_allowlist_blocks_escape_and_secrets(repo: Path, tmp_path_factory):
    allow = PathAllowlist.from_paths(repo)
    assert allow.resolve("README.md").name == "README.md"
    with pytest.raises(AccessDenied):
        allow.resolve("../outside.txt")
    with pytest.raises(AccessDenied):
        allow.resolve("/etc/passwd")
    with pytest.raises(AccessDenied):
        allow.resolve(".env")
    with pytest.raises(AccessDenied):
        allow.resolve(".git/config")
    outside = tmp_path_factory.mktemp("outside")
    (outside / "secret.txt").write_text("x")
    (repo / "link").symlink_to(outside)  # シンボリックリンクで外に出ようとしても拒否
    with pytest.raises(AccessDenied):
        allow.resolve("link/secret.txt")


# ---------- ツール ----------
def test_list_dir_hides_secrets(tools: ToolRegistry):
    out = tools.get("list_dir").func({})
    assert "README.md" in out and "docs/" in out
    assert ".env" not in out and ".git" not in out


def test_read_file_with_line_range(tools: ToolRegistry):
    out = tools.get("read_file").func({"path": "docs/a.md", "start_line": 3, "end_line": 4})
    assert "line 3" in out and "line 4" in out and "line 5" not in out


def test_read_file_denied_is_tool_error(tools: ToolRegistry):
    with pytest.raises(ToolError):
        tools.get("read_file").func({"path": ".env"})


def test_registry_rejects_write_tools():
    with pytest.raises(ValueError):
        ToolRegistry([ToolSpec("write_file", "x", {"type": "object", "properties": {}}, lambda a: "", read_only=False)])


# ---------- Track B:偽の LLM で自作ループを確かめる ----------
class FakeMessages:
    """1 回目は read_file を呼びたいと答え、2 回目に最終回答を返す偽の LLM。"""

    def __init__(self, script: list[dict]):
        self.script = list(script)
        self.calls: list[dict] = []

    def create(self, **kw):
        self.calls.append(json.loads(json.dumps(kw, default=str)))
        return self.script.pop(0)


def _tool_use(name, inp, i="tu1"):
    return {"stop_reason": "tool_use", "usage": {"input_tokens": 100, "output_tokens": 20},
            "content": [{"type": "tool_use", "id": i, "name": name, "input": inp}]}


def _final(text):
    return {"stop_reason": "end_turn", "usage": {"input_tokens": 150, "output_tokens": 30},
            "content": [{"type": "text", "text": text}]}


def test_api_runtime_loop(tools: ToolRegistry, tmp_path: Path):
    fake = FakeMessages([_tool_use("read_file", {"path": "README.md"}), _final("Phase 1 です。参照: README.md")])
    rt = ApiRuntime(tools, RunConfig(model="claude-sonnet-5-5"), client=fake, trace_dir=tmp_path / "logs")
    res = rt.run("今のフェーズは?")
    assert res.ok and res.answer.startswith("Phase 1")
    assert (res.steps, res.tool_calls, res.input_tokens, res.output_tokens) == (2, 1, 250, 50)
    assert res.cost_usd == pytest.approx(estimate_cost("claude-sonnet-5-5", 250, 50))
    # 2 回目の呼び出しには tool_result が含まれている(LLM にツールの結果を返している)
    last = fake.calls[1]["messages"][-1]
    assert last["role"] == "user" and last["content"][0]["type"] == "tool_result"
    assert "Phase 1" in last["content"][0]["content"]
    # トレースがファイルに JSON Lines で書かれている
    kinds = [json.loads(line)["event"] for line in res.trace.path.read_text().splitlines()]
    assert kinds == ["run_start", "llm_call", "tool_call", "llm_call", "run_end"]


def test_api_runtime_denied_tool_is_reported_not_crashed(tools: ToolRegistry):
    fake = FakeMessages([_tool_use("read_file", {"path": ".env"}), _final("読めませんでした。")])
    res = ApiRuntime(tools, client=fake).run(".env を見せて")
    assert res.ok
    call = res.trace.tool_calls()[0]
    assert call["ok"] is False and "sk-ant" not in call["output_preview"]
    assert fake.calls[1]["messages"][-1]["content"][0]["is_error"] is True


def test_api_runtime_stops_at_max_steps(tools: ToolRegistry):
    fake = FakeMessages([_tool_use("list_dir", {}, f"t{i}") for i in range(5)])
    res = ApiRuntime(tools, RunConfig(max_steps=3), client=fake).run("x")
    assert res.steps == 3 and "max_steps" in (res.error or "")


def test_budget_ledger(tmp_path: Path):
    ledger = SpendLedger(tmp_path / "spend.jsonl", monthly_budget_usd=1.0)
    ledger.add(0.8, "r1", "claude-sonnet-5-5")
    assert ledger.month_total() == pytest.approx(0.8)
    with pytest.raises(BudgetExceeded):
        ledger.check(0.5)
    ledger.check(0.1)


def test_api_runtime_refuses_when_over_budget(tools: ToolRegistry, tmp_path: Path):
    ledger = SpendLedger(tmp_path / "spend.jsonl", monthly_budget_usd=0.1)
    fake = FakeMessages([_final("x")])
    res = ApiRuntime(tools, RunConfig(max_cost_usd=0.5), client=fake, ledger=ledger).run("x")
    assert "予算" in (res.error or "") and fake.calls == []  # LLM を一度も呼んでいない


# ---------- Track A:SDK の設定(LLM には接続しない) ----------
def test_sdk_options_are_read_only(tools: ToolRegistry):
    pytest.importorskip("claude_agent_sdk")
    from agent_family.runtimes.sdk_runtime import build_options, sdk_tool_name
    from agent_family.trace import TraceRecorder

    opts = build_options(tools, RunConfig(), TraceRecorder("A-sdk"))
    assert opts.tools == []  # 組み込みツールはすべて無効
    assert set(opts.allowed_tools) == {sdk_tool_name("list_dir"), sdk_tool_name("read_file")}
    assert "Write" in opts.disallowed_tools and "Bash" in opts.disallowed_tools
    assert opts.setting_sources == []
    assert opts.system_prompt == RunConfig().system_prompt  # Track B と同じ指示文


def test_sdk_tool_handler_shares_trace_format(tools: ToolRegistry):
    pytest.importorskip("claude_agent_sdk")
    from agent_family.runtimes.sdk_runtime import build_sdk_tools
    from agent_family.trace import TraceRecorder

    trace = TraceRecorder("A-sdk")
    sdk_tools = {t.name: t for t in build_sdk_tools(tools, trace)}
    ok = asyncio.run(sdk_tools["read_file"].handler({"path": "README.md"}))
    ng = asyncio.run(sdk_tools["read_file"].handler({"path": ".env"}))
    assert ok["is_error"] is False and "Phase 1" in ok["content"][0]["text"]
    assert ng["is_error"] is True and "sk-ant" not in ng["content"][0]["text"]
    assert [c["ok"] for c in trace.tool_calls()] == [True, False]


def test_subscription_env_removes_api_key(monkeypatch):
    from agent_family.runtimes.sdk_runtime import subscription_auth_env
    import os

    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-x")
    with subscription_auth_env():
        assert "ANTHROPIC_API_KEY" not in os.environ  # 実行中は Pro のログインが使われる
    assert os.environ["ANTHROPIC_API_KEY"] == "sk-ant-x"


# ---------- 評価ハーネス ----------
def test_harness_compares_tracks_and_checks_integrity(tools: ToolRegistry, repo: Path, tmp_path: Path):
    def runner(answer):
        def run(prompt):
            fake = FakeMessages([_tool_use("read_file", {"path": "README.md"}), _final(answer)])
            return ApiRuntime(tools, client=fake).run(prompt)
        return run

    suite = EvalSuite("demo", [EvalTask("S1", "q", [{"type": "used_tool", "values": ["read_file"]},
                                                     {"type": "contains_any", "values": ["Phase 1"]}])])
    summary = run_suite(suite, {"A-sdk": runner("Phase 1"), "B-api": runner("不明")},
                        integrity_root=repo, out_dir=tmp_path / "out")
    assert [r["passed"] for r in summary["rows"]] == [True, False]
    assert summary["integrity"]["unchanged"] is True
    md = to_markdown(summary)
    assert "| S1 | A-sdk | ✅" in md and "| S1 | B-api | ❌" in md


def test_integrity_detects_change(repo: Path):
    before = manifest(repo)
    (repo / "README.md").write_text("changed")
    assert diff_manifests(before, manifest(repo))["changed"] == ["README.md"]


def test_smoke_suite_file_is_valid():
    suite = EvalSuite.load(Path(__file__).resolve().parents[2] / "evals" / "p1-0_smoke.json")
    assert [t.id for t in suite.tasks] == ["S1", "S2", "S3"]
