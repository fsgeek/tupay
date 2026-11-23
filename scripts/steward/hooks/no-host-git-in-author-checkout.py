#!/usr/bin/env python3
"""PreToolUse hook (Bash): refuse a steward command that runs host git inside an author checkout.
derives: steward-practice "Host git never runs in an author checkout" (failed as a memory rule: 10-23 rule, recurred 10-27,
log L999); practice audit 2026-11-18, proposal 1, rule 26. An author can write its checkout's .git; its config
(gpg.ssh.program, core.fsmonitor, a pager, a filter) would run on the host. Take work out with author-export.sh.
An author checkout is a sibling directory ../tupay-<name> that is not tupay-private, tupay-homes or tupay-box-rehearsal.
Exit 2 blocks the call and shows the reason to the steward. Mutation pair: no-host-git-check.sh."""
import json, re, sys
NOT_AUTHOR = {"tupay-private", "tupay-homes", "tupay-box-rehearsal"}
try: cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
except Exception: sys.exit(0)
if not re.search(r"(^|[\s;&|(`])git(\s|$)", cmd): sys.exit(0)
for m in re.finditer(r"(?:^|[\s'\"=/])(?:\.\./|/home/tony/projects/)(tupay-[A-Za-z0-9._-]+)", cmd):
    name = m.group(1).rstrip("/")
    if name not in NOT_AUTHOR and not name.endswith(".bundle"):
        print(f"blocked: host git with author checkout {name} on the command line (practice rule: host git never runs in an "
              f"author checkout; use author-export.sh, or copy the files out as data)", file=sys.stderr); sys.exit(2)
sys.exit(0)
