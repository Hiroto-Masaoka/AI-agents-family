# Scorecard

One row per change. Keep a change only if success rises and cost/time stay acceptable,
and the gain survives a token-matched comparison (PLAYBOOK P14).

| Date | Change (one variable) | Benchmark / check | Result | Tokens (in/out) | Decision | Notes |
|------|----------------------|-------------------|--------|-----------------|----------|-------|
| 2026-11-24 | Add Phase 1 read-only PreToolUse hook (`.claude/hooks/block_write.py`) + `permissions.deny` | Unit tests `src/tests/test_block_write_hook.py` (29 tool-call cases, malformed-input fail-closed, block logging) | 31/31 pass | n/a (no LLM calls) | Adopt provisionally | Regex guard, not a sandbox: `python -c` / `julia -e` writes are not detected. **Not yet verified inside a real Claude Code session.** |

## Open checks
- [ ] In real Claude Code, ask the agent to run `rm` on a scratch file; confirm it is blocked and a line appears in `logs/hook_blocks.log`.
- [ ] Confirm a normal read-only task (e.g. literature digest writing to `wiki/` and `logs/runs.md`) still completes without false blocks.
- [ ] Before unattended (L4) runs: add OS-level isolation (container/sandbox).
