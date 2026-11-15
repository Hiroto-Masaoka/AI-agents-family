# 参考資料: AI-Agent Family Playbook(公開情報のまとめ)

> **位置付け:** 2026-11-13 に claude.ai で公開情報(Web 記事・論文)を調査してまとめたもの(LOG-20261113-01)。**本プロジェクトでは未検証(Unverified)** の一般的知見です。本プロジェクトで確認できた内容は `docs/KNOWLEDGE.md` に移してください。原文は英語のまま収録しています。

---

# AI-Agent Family Playbook (v0.1, 2026-11)

A distilled, opinionated guide for building and optimizing a "family" of AI agents
for any purpose (research, web, games, money management...). Each rule cites
where it comes from so you can check and update it.

---

## 0. The one-paragraph version

Start with **one** capable agent and a good project file. Add a specialist only
when you can point to a concrete bottleneck (context too noisy, work that can run
in parallel, or work that must be checked by someone who did not do it). Use one
**orchestrator** that writes precise briefs to **workers**, keep all shared state
in **files** (plan, wiki, run log), let an **independent verifier** check results,
put hard rules in **permissions/hooks** rather than in prose, and improve the
family with a **fixed set of test tasks** where you change one thing at a time.

---

## 1. Design principles

| # | Principle | Why / source |
|---|-----------|--------------|
| P1 | **Start small: 1 agent → 2–3 agents.** Grow only when a measured bottleneck appears. | Coordination overhead grows non-linearly with agent count; practitioners running 35+ agents advise starting with 2–3. Cognition (Devin) argues simpler designs are more reliable. |
| P2 | **One orchestrator, many workers** (supervisor → worker). Pipeline or fan-out/fan-in only inside a worker's job. | Most-recommended production pattern; Anthropic's Research system uses orchestrator-worker. |
| P3 | **Split by context, not by persona.** Make a new agent when a task (a) can run in parallel, (b) floods the context with noise (search, logs), or (c) needs an independent check. "Agent named Einstein" adds nothing. | Anthropic: multi-agent wins mostly by spending more tokens across separate context windows (token use explained ~80% of performance variance). |
| P4 | **Teach the orchestrator to delegate.** Every brief states: objective, inputs, output format, tools allowed, boundaries, and "done when...". | Anthropic: vague briefs caused duplicated or wrong work by subagents. |
| P5 | **Scale effort to the task.** Fact check: 1 agent, 3–10 tool calls. Comparison: 2–4 workers. Open research: 10+ workers with divided scope. | Anthropic's embedded scaling rules. |
| P6 | **Shared state lives in files**, not in chat history: `PLAN.md`, wiki, `logs/runs.md`. Agents re-read them; long tasks survive context limits. | Anthropic saves the plan to memory so it is not lost when context overflows; Cognition: failures come from agents acting on conflicting assumptions. |
| P7 | **Never let work grade itself.** A verifier with *no access to the producer's reasoning* re-derives or tests the result. | Multi-agent failures are often silent; the science-agent literature warns of "agent sleepwalking" (drifting from instructions). |
| P8 | **Enforce with permissions/hooks, guide with CLAUDE.md, store know-how in skills, isolate with subagents.** | Claude Code docs/best-practice guides: CLAUDE.md is advisory, hooks are deterministic. |
| P9 | **Route models by job.** Strongest model for the orchestrator and the verifier; cheaper/faster ones for search and bulk work. Track tokens from day one (multi-agent ≈ 15× chat tokens). | Anthropic used Opus lead + Sonnet workers; cost is the biggest operational surprise. |
| P10 | **Human gates for anything irreversible** (send, publish, delete, spend, submit). Start agents read-only; widen permissions as trust is earned. | Production guides and lab-agent maturity frameworks recommend read-only and human-in-loop phases first. |
| P11 | **Log every run.** Task, agents used, tokens/cost, outcome, failure reason. You can't optimize what you can't see. | Anthropic built custom tracing because standard logging was not enough. |
| P12 | **Deterministic graders where possible.** For science: unit tests, known-answer simulations, conservation checks, re-derivation in a second language. | Science-agent evaluations: execution and verification lag planning. |

---

## 2. The building blocks (Claude Code vocabulary; other tools have equivalents)

| Block | What it is | Put here |
|-------|-----------|----------|
| `CLAUDE.md` | Always-loaded project brief | Goal, conventions, where state lives, the family roster. Keep it short (< ~150 lines). |
| Subagent (`.claude/agents/*.md`) | Worker with its own context, tools, model | Researcher, analyst, verifier, scribe... |
| Skill (`.claude/skills/*/SKILL.md`) | Know-how loaded only when relevant | Procedures: "how we review an analysis report", "how we write a delegation brief". |
| Slash command | Named, user-triggered workflow | `/new-round`, `/review-report`. |
| Hook | Script that *always* runs at an event | Block dangerous commands, append to run log, run tests after edits. |
| Settings / permissions | Allow/deny lists, model defaults | Read-only by default; deny destructive commands. |
| MCP server | Connection to an outside system | arXiv/ADS, GitHub, databases, calendars. |

---

## 3. Standard roles (pick 2–5, rename to taste)

1. **Orchestrator** (usually *you + the main session*): plans, writes briefs, merges results, owns `PLAN.md`.
2. **Scout / Researcher**: literature, docs, web. Returns sources + short claims. Read-only.
3. **Builder / Analyst**: writes code, runs pipelines, produces figures.
4. **Verifier**: independently checks a claim/result. Gets the *claim and the inputs*, not the builder's transcript.
5. **Scribe**: updates wiki/paper/changelog; keeps state files consistent.
6. *(optional)* **Critic / Devil's advocate**: attacks the plan before work starts. Good for ideas and papers.
7. *(optional)* **Architect**: designs new families (see `architect/`).

---

## 4. The optimization loop ("trial and error, but measured")

```
define tasks → run → log → diagnose → change ONE thing → re-run → keep or revert
```

1. **Benchmark set**: 5–20 real tasks from your domain with pass criteria (`evals/tasks.md`).
   Mix easy/hard, and include at least two where you already know the right answer.
2. **Baseline**: run with a single agent. Record success, time, cost.
3. **Diagnose failures** with the taxonomy below.
4. **Change one variable**: prompt wording, a tool, model choice, add/remove an agent, a hook.
5. **Re-run the whole set** (not just the failed task) to catch regressions.
6. **Keep the change only if** success ↑ and cost/time acceptable. Record in `evals/scorecard.md`.
7. Every ~10 runs, prune: delete agents/skills that never fire or never help.

### Failure taxonomy (tag every failed run)
- **F1 Brief**: worker misunderstood the task → fix the brief template.
- **F2 Context**: missing/stale info → fix state files or retrieval.
- **F3 Tool**: tool missing, wrong, or misused → fix tool description/permissions.
- **F4 Reasoning**: wrong method/physics → add skill/reference, stronger model, verifier.
- **F5 Drift**: ignored instructions ("sleepwalking") → shorten prompt, add hook/check.
- **F6 Coordination**: duplicate/conflicting work → clearer ownership, fewer agents.
- **F7 Cost/latency**: too slow/expensive → cheaper worker model, less fan-out, caching.

---

## 5. Maturity ladder (don't skip rungs)

| Level | What the family does | Gate to move up |
|-------|---------------------|-----------------|
| L0 | Chat assistant, no state | — |
| L1 | One agent + `CLAUDE.md` + state files + run log | 10 logged runs |
| L2 | + Verifier (independent check) | Verifier catches ≥1 real error |
| L3 | + Parallel workers, orchestrator briefs | Benchmark success ≥ baseline at acceptable cost |
| L4 | Scheduled/unattended runs, read-only | 2 weeks with no harmful action |
| L5 | Limited write/act permissions behind human gates | You trust the logs |

---

## 6. Domain notes

- **Science/research**: the bottleneck is *verification*, not ideas. Invest in the verifier and known-answer tests. Agents' execution still lags their planning; keep humans on interpretation.
- **Web/software**: tests are your grader; hooks run them after every edit.
- **Games**: separate design (critic loop) from implementation; playtest agent with scripted checks.
- **Money management**: agents categorize, reconcile, forecast, and flag; **humans decide and execute**. No agent moves money or trades.

---

## Sources
- [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Vellum — Multi-agent systems & context engineering (incl. Cognition's critique)](https://vellum.ai/blog/multi-agent-systems-building-with-context-engineering)
- [Maxim — Production-ready multi-agent systems](https://www.getmaxim.ai/articles/best-practices-for-building-production-ready-multi-agent-systems.md)
- [DEV — Multi-agent orchestration best practices 2026](https://dev.to/bitpixelcoders/multi-agent-orchestration-best-practices-in-2026-building-reliable-ai-systems-at-scale-2omn)
- [DEV — Multi-agent systems that actually work (2–3 agents first)](https://dev.to/the_bookmaster/how-to-build-multi-agent-ai-systems-that-actually-work-a-2026-practical-guide-4k1g)
- [SmartScope — Claude Code surfaces: hooks vs skills vs subagents (JP/EN)](https://smartscope.blog/generative-ai/claude/claude-code-best-practices-advanced-2026/)
- [Claude Code Crash Course — hooks are guarantees](https://colocodes.substack.com/p/claude-code-crash-course)
- [ARIA — Can an AI Scientist really discover knowledge? (Albert architecture)](https://aria.org.uk/insights/can-an-ai-scientist-really-discover-knowledge)
- [Scripps — How autonomous AI scientists are evaluated](https://scripps-ai-enablement.github.io/sci-ai-enabler/autonomous-science/evaluation.html)
- [Autonomous Science Bench (arXiv 2610.18449)](https://papers.cool/arxiv/2610.18449)
