#!/usr/bin/env python3
"""PreToolUse hook (Bash): refuse a steward command that may run host git inside an author checkout.
derives: steward-practice "Host git never runs in an author checkout" (failed as a memory rule: 10-23 rule, recurred 10-27,
log L999); practice audit 2026-11-18, proposal 1, rule 26. An author can write its checkout's .git; its config
(gpg.ssh.program, core.fsmonitor, a pager, a filter) would run on the host. Take work out with author-export.sh.
An author checkout is a directory /home/tony/projects/tupay-<name> other than tupay-private, tupay-homes, tupay-box-rehearsal.
Rule (deliberately coarse, after two automated security reviews on 2026-11-23): block if the substring "git" appears
anywhere in the command AND either the session's working directory is in an author checkout, or the command contains
an author-checkout name in any form (a path, a GIT_DIR value, a quoted or escaped string). Over-blocking is accepted:
edits that mention such names go through the file tool. It guards against the steward's lapses; it is not a sandbox.
Fails closed on unreadable input. Exit 2 blocks the call. Mutation pair: no-host-git-check.sh."""
import json, os, re, sys
NOT_AUTHOR = {"tupay-private", "tupay-homes", "tupay-box-rehearsal"}
PROJ = "/home/tony/projects/"

def is_author(name):
    return name not in NOT_AUTHOR and not name.endswith(".bundle")

def cwd_author(cwd):
    rp = os.path.realpath(cwd)
    if not rp.startswith(PROJ): return None
    top = rp[len(PROJ):].split("/")[0]
    return top if top.startswith("tupay-") and is_author(top) else None

def block(why):
    print(f"blocked: {why} (practice rule: host git never runs in an author checkout; use author-export.sh, copy the "
          f"files out as data, or use the file tool for an edit that only mentions the name)", file=sys.stderr)
    sys.exit(2)

try:
    d = json.load(sys.stdin)
    cmd = str(d.get("tool_input", {}).get("command", ""))
    cwd = str(d.get("cwd") or os.getcwd())
except Exception:
    block("hook input unreadable, failing closed")
    raise SystemExit(2)

flat = cmd.replace("\\", "").replace("'", "").replace('"', "")
if "git" not in flat.lower():
    sys.exit(0)
a = cwd_author(cwd)
if a: block(f"'git' in a command while the working directory is in author checkout {a}")
for name in re.findall(r"tupay-[A-Za-z0-9._-]+", flat):
    name = name.rstrip("./")
    if is_author(name): block(f"'git' in a command that names author checkout {name}")
sys.exit(0)
