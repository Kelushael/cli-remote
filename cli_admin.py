#!/usr/bin/env python3
"""Terminal admin for cli-remote. Drive client sessions and fire commands
without ever opening the web /admin page.

  pip install aiohttp
  python3 cli_admin.py wss://markyninox.com/ws/admin

Once a client has consented (hit YES), pick it and type commands; output
streams back here. Meta: /sessions  /use <id>  /quit
"""
import asyncio, json, sys
import aiohttp

async def run(url, token):
    sessions, selected = {}, None
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with aiohttp.ClientSession() as cs:
        async with cs.ws_connect(url, headers=headers) as ws:
            print(f"[connected] {url}")

            async def reader():
                async for msg in ws:
                    if msg.type != aiohttp.WSMsgType.TEXT:
                        continue
                    d = json.loads(msg.data)
                    t = d.get("type")
                    if t == "session_list":
                        for s in d.get("sessions", []):
                            sessions[s["session_id"]] = s
                        print(f"[sessions] {list(sessions) or 'none yet'}")
                    elif t == "client_connected":
                        sessions[d["session_id"]] = {"session_id": d["session_id"], "approved": False}
                        print(f"[+] client {d['session_id']} connected (awaiting consent)")
                    elif t == "session_approved":
                        sessions.setdefault(d["session_id"], {})["approved"] = True
                        print(f"[OK] {d['session_id']} consented — you are in")
                    elif t == "client_disconnected":
                        sessions.pop(d["session_id"], None)
                        print(f"[-] client {d['session_id']} gone")
                    elif t == "command_output":
                        print(d.get("output", ""), end="" if d.get("output","").endswith("\n") else "\n")

            async def writer():
                nonlocal selected
                loop = asyncio.get_event_loop()
                while True:
                    line = (await loop.run_in_executor(None, sys.stdin.readline))
                    if not line:
                        break
                    line = line.rstrip("\n")
                    if line in ("/quit", "/q"):
                        break
                    if line == "/sessions":
                        print(f"[sessions] {sessions}"); continue
                    if line.startswith("/use "):
                        selected = line.split(None, 1)[1].strip(); print(f"[using] {selected}"); continue
                    if not line:
                        continue
                    if selected is None:
                        approved = [s for s, v in sessions.items() if v.get("approved")]
                        if len(approved) == 1:
                            selected = approved[0]; print(f"[using] {selected}")
                        else:
                            print("[!] no session selected — /use <id>"); continue
                    await ws.send_json({"type": "command", "session_id": selected, "command": line})

            r = asyncio.ensure_future(reader())
            await writer()
            r.cancel()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "ws://localhost:8765/ws/admin"
    token = sys.argv[2] if len(sys.argv) > 2 else ""
    try:
        asyncio.run(run(url, token))
    except KeyboardInterrupt:
        pass
