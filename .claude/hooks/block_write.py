#!/usr/bin/env python3
"""PreToolUse hook: Phase 1 read-only enforcement (PLAYBOOK P8 / P10).

Claude Code passes the pending tool call as JSON on stdin.
Exit 0  -> allow.   Exit 2 -> block (stderr is shown to Claude).

What it does
  * File tools (Write/Edit/MultiEdit/NotebookEdit): allowed only inside
    ALLOWED_DIRS / ALLOWED_FILES under the project. `.claude/` and CLAUDE.md
    are NEVER writable, so the agent cannot weaken its own guard.
  * Bash: blocks destructive commands, outbound/network-send commands,
    package installs, history-rewriting git, in-place edits, and output
    redirection to non-allowed paths.
  * Every block is appended to logs/hook_blocks.log (run-log material, P11).

Limits (be honest with yourself)
  This is a regex guard, not a sandbox. `python -c "open(...).write()"`,
  `julia -e ...`, or obfuscated shell can slip through. Treat it as the
  first layer, together with permissions.deny in settings.json and, for
  unattended runs, an OS-level sandbox/container.
"""
import datetime
import json
import os
import pathlib
import re
import sys

PROJECT = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())).resolve()

# Edit these to widen/narrow Phase 1.
ALLOWED_DIRS = ["logs", "evals", "scratch", "wiki"]
ALLOWED_FILES = ["PLAN.md"]
PROTECTED = [".claude", ".git", "CLAUDE.md", "CLAUDE.local.md"]

FILE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

# command names that are blocked when they appear in command position
BLOCKED_CMDS = [
    "rm", "rmdir", "mv", "shred", "truncate", "dd", "chmod", "chown", "sudo",
    "scp", "ssh", "sftp", "rsync", "nc", "ncat", "telnet", "ftp",
    "sendmail", "mail", "mutt", "kill", "pkill", "crontab",
]
# multi-word patterns (searched anywhere in the command)
BLOCKED_PATTERNS = [
    (r"\bgit\s+(push|reset|clean|rebase|filter-branch)\b", "history/remote-changing git"),
    (r"\bgit\s+checkout\s+--", "git checkout -- (discards changes)"),
    (r"\bgit\s+branch\s+-[dD]\b", "git branch delete"),
    (r"\b(pip3?|pipx|uv|conda|npm|pnpm|yarn|brew|apt(-get)?)\s+(install|add|remove|uninstall)\b", "package install/remove"),
    (r"Pkg\.(add|rm|update)\b", "Julia Pkg change"),
    (r"\bsed\s+(-[a-zA-Z]*i|--in-place)\b", "in-place sed"),
    (r"\bperl\s+(-[a-zA-Z]*i)\b", "in-place perl"),
    (r"\b(curl|wget)\b.*(\s-X\s*(POST|PUT|PATCH|DELETE)\b|\s(-d|--data\S*|-F|--form|-T|--upload-file)\b)", "HTTP request with a body"),
    (r"\|\s*(ba|z)?sh\b", "pipe into shell"),
]

CMD_BOUNDARY = r"(?:^|[;&|(`]|\$\()\s*(?:\w+=\S+\s+)*"


def log_block(reason: str, detail: str) -> None:
    try:
        d = PROJECT / "logs"
        d.mkdir(exist_ok=True)
        with open(d / "hook_blocks.log", "a", encoding="utf-8") as f:
            ts = datetime.datetime.now().isoformat(timespec="seconds")
            f.write(f"{ts}\t{reason}\t{detail[:300]!r}\n")
    except OSError:
        pass  # logging must never break the guard


def deny(reason: str, detail: str) -> None:
    log_block(reason, detail)
    sys.stderr.write(
        f"BLOCKED by Phase 1 read-only hook: {reason}. "
        "If this action is truly needed, ask the human to do it or to relax the hook.\n"
    )
    sys.exit(2)


def path_allowed(raw: str) -> bool:
    p = pathlib.Path(raw)
    if not p.is_absolute():
        p = PROJECT / p
    try:
        rel = p.resolve().relative_to(PROJECT)
    except ValueError:
        return False  # outside the project
    parts = rel.parts
    if not parts:
        return False
    if parts[0] in PROTECTED:
        return False
    if len(parts) == 1 and parts[0] in ALLOWED_FILES:
        return True
    return parts[0] in ALLOWED_DIRS and len(parts) > 1


def check_bash(cmd: str) -> None:
    for name in BLOCKED_CMDS:
        if re.search(CMD_BOUNDARY + r"(?:sudo\s+)?" + re.escape(name) + r"\b", cmd):
            deny(f"command '{name}' is not allowed in Phase 1", cmd)
    for pat, why in BLOCKED_PATTERNS:
        if re.search(pat, cmd):
            deny(why, cmd)
    # output redirection: `> file`, `>> file`, `1> file` ; `2>&1` and `>&2` are ignored
    for target in re.findall(r"\d*>>?\s*([^\s;|&<>]+)", cmd):
        if target in ("/dev/null", "/dev/stderr", "/dev/stdout"):
            continue
        if not path_allowed(target):
            deny(f"redirect to non-allowed path '{target}'", cmd)
    # tee <paths>
    m = re.search(CMD_BOUNDARY + r"tee\b([^;|&]*)", cmd)
    if m:
        for arg in m.group(1).split():
            if arg.startswith("-"):
                continue
            if not path_allowed(arg):
                deny(f"tee to non-allowed path '{arg}'", cmd)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception as e:  # fail closed: a safety hook must not silently pass
        sys.stderr.write(f"read-only hook could not parse input: {e}\n")
        sys.exit(2)

    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {}) or {}

    if tool in FILE_TOOLS:
        target = inp.get("file_path") or inp.get("notebook_path") or ""
        if not target or not path_allowed(target):
            deny(f"{tool} to non-allowed path '{target}'", target)
    elif tool == "Bash":
        check_bash(inp.get("command", ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
