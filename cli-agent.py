#!/usr/bin/env python3
"""Client-side control agent. Run this on the machine you want driven.
It does NOTHING until you explicitly consent — Chrome-Remote-Desktop style.
After 'yes', the relay's admin can run commands here until you Ctrl-C.

  pip install aiohttp
  python3 cli-agent.py
"""
import subprocess
from aiohttp import web

CONSENT = (
    "\n  ── REMOTE CONTROL CONSENT ──\n"
    "  Starting this agent lets a paired operator run shell commands on THIS\n"
    "  computer (and through them, operate software) until you stop it.\n"
    "  Type 'yes' to grant control, anything else to cancel: "
)

@web.middleware
async def cors(request, handler):
    resp = web.Response() if request.method == "OPTIONS" else await handler(request)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp

async def handle_exec(request):
    cmd = (await request.json()).get("command", "")
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        out = p.stdout + p.stderr
    except Exception as e:
        out = f"{type(e).__name__}: {e}"
    return web.json_response({"output": out or "(no output)"})

def main():
    if input(CONSENT).strip().lower() not in ("yes", "y"):
        print("declined — no control granted.")
        return
    app = web.Application(middlewares=[cors])
    app.router.add_post("/exec", handle_exec)
    app.router.add_route("OPTIONS", "/exec", lambda r: web.Response())
    print("control GRANTED — agent live on http://localhost:9999")
    print("now open the relay page and CONNECT.  Ctrl-C revokes control.")
    web.run_app(app, port=9999, print=None)

if __name__ == "__main__":
    main()
