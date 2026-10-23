#!/usr/bin/env python3
"""Inside an author sandbox: relay 127.0.0.1:3128 to the egress proxy's unix socket.

usage: sandbox-relay.py <socket>
derives: AGENTS.md rule 4; log 2026-10-23 "author isolation"
Runs under the sandbox's own python (/usr/bin/python3). It decides nothing; egress-proxy.py, outside, does.
"""
import asyncio, sys

SOCK = sys.argv[1]


async def pipe(r, w):
    try:
        while data := await r.read(65536):
            w.write(data)
            await w.drain()
    except ConnectionError:
        pass
    finally:
        w.close()


async def handle(cr, cw):
    try:
        ur, uw = await asyncio.open_unix_connection(SOCK)
    except OSError:
        cw.close()
        return
    await asyncio.gather(pipe(cr, uw), pipe(ur, cw))


async def main():
    server = await asyncio.start_server(handle, "127.0.0.1", 3128)
    async with server:
        await server.serve_forever()


asyncio.run(main())
