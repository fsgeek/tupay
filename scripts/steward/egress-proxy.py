#!/usr/bin/env python3
"""Allowlisting HTTP CONNECT proxy for an author sandbox, listening on a unix socket.

usage: egress-proxy.py <socket> <log> <allowlist-file | --learn>
derives: AGENTS.md rule 4; log 2026-10-23 "author isolation" (a sandboxed shell still reached github.com/fsgeek/tupay)

The sandbox has no network of its own (bwrap --unshare-net); its only route out is this socket, through the relay
inside it (sandbox-relay.py). Every request is logged, allowed or denied, so the log is the steward's record of
what an author tried to reach. --learn allows everything and logs it, for building an allowlist from a probe run.
Allowlist lines are host names; a line ".example.com" allows that domain's subdomains.
"""
import asyncio, os, sys, time

SOCK, LOG, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
LEARN = MODE == "--learn"
ALLOW = set() if LEARN else {l.strip() for l in open(MODE) if l.strip() and not l.startswith("#")}


def allowed(host):
    if LEARN or host in ALLOW:
        return True
    return any(a.startswith(".") and host.endswith(a) for a in ALLOW)


def log(verdict, target):
    with open(LOG, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {verdict} {target}\n")


async def pipe(r, w):
    try:
        while data := await r.read(65536):
            w.write(data)
            await w.drain()
    except (ConnectionError, asyncio.CancelledError):
        pass
    finally:
        w.close()


async def handle(cr, cw):
    try:
        head = await cr.readuntil(b"\r\n\r\n")
    except (asyncio.IncompleteReadError, asyncio.LimitOverrunError):
        cw.close()
        return
    line = head.split(b"\r\n", 1)[0].decode("latin-1")
    parts = line.split()
    if len(parts) < 2 or parts[0] != "CONNECT":   # plain HTTP is refused: every harness endpoint is HTTPS
        log("DENY-NONCONNECT", line[:200])
        cw.write(b"HTTP/1.1 403 Forbidden\r\n\r\n")
        cw.close()
        return
    host, _, port = parts[1].rpartition(":")
    if not allowed(host) or port != "443":
        log("DENY", parts[1])
        cw.write(b"HTTP/1.1 403 Forbidden\r\n\r\n")
        cw.close()
        return
    try:
        ur, uw = await asyncio.open_connection(host, int(port))
    except OSError as e:
        log("FAIL", f"{parts[1]} {e}")
        cw.write(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
        cw.close()
        return
    log("ALLOW", parts[1])
    cw.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
    await asyncio.gather(pipe(cr, uw), pipe(ur, cw))


async def main():
    if os.path.exists(SOCK):
        os.unlink(SOCK)
    server = await asyncio.start_unix_server(handle, SOCK)
    log("START", "learn" if LEARN else f"allowlist {MODE}")
    async with server:
        await server.serve_forever()


asyncio.run(main())
