#!/usr/bin/env python3
"""PreToolUse hook (Bash): refuse a steward command that runs host git inside an author checkout.
derives: steward-practice "Host git never runs in an author checkout" (failed as a memory rule: 10-23 rule, recurred 10-27,
log L999); practice audit 2026-11-18, proposal 1, rule 26. An author can write its checkout's .git; its config
(gpg.ssh.program, core.fsmonitor, a pager, a filter) would run on the host. Take work out with author-export.sh.
An author checkout is a directory /home/tony/projects/tupay-<name> other than tupay-private, tupay-homes, tupay-box-rehearsal.
Checks the session's working directory (it persists between calls) and every author path on the command line, with
~, $HOME and .. resolved; matches git by name or path (/usr/bin/git). Fails closed on unreadable input.
It guards against the steward's own lapses; it is not a sandbox, and a command built to evade it would evade it.
Revised 2026-11-23 after an automated security review (cwd, path-qualified git, ~ and $HOME, fail closed).
Exit 2 blocks the call and shows the reason to the steward. Mutation pair: no-host-git-check.sh."""
import json, os, re, sys
NOT_AUTHOR = {"tupay-private", "tupay-homes", "tupay-box-rehearsal"}
PROJ = "/home/tony/projects/"
HOME = "/home/tony"

def author(path):
    """The author checkout a path lies in, or None."""
    rp = os.path.realpath(path)
    if not rp.startswith(PROJ): return None
    top = rp[len(PROJ):].split("/")[0]
    return top if top.startswith("tupay-") and top not in NOT_AUTHOR and not top.endswith(".bundle") else None

def block(why):
    print(f"blocked: {why} (practice rule: host git never runs in an author checkout; use author-export.sh, or copy "
          f"the files out as data)", file=sys.stderr)
    sys.exit(2)

try:
    d = json.load(sys.stdin)
    cmd = d.get("tool_input", {}).get("command", "")
    cwd = d.get("cwd") or os.getcwd()
except Exception:
    block("hook input unreadable, failing closed")

if not re.search(r"(^|[\s;&|(`/])git(\s|$)", cmd):     # git, /usr/bin/git, ./git
    sys.exit(0)
a = author(cwd)
if a: block(f"host git while the session's working directory is in author checkout {a}")
text = cmd.replace("${HOME}", HOME).replace("$HOME", HOME)
for m in re.finditer(r"(?:^|[\s'\"=:])((?:~|\.\.|/)[^\s'\";&|)]*tupay-[A-Za-z0-9._-]+)", text):
    p = m.group(1)
    if p.startswith("~"): p = HOME + p[1:]
    if not p.startswith("/"): p = os.path.join(cwd, p)
    a = author(p)
    if a: block(f"host git with author checkout {a} on the command line")
sys.exit(0)
