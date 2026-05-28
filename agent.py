#!/usr/bin/env python3
"""Self-connecting control agent — the downloadable client.
Launched by build.bat / build.command. Asks consent, then dials the relay
directly (no browser) and takes operator commands until Ctrl-C.
"""
import asyncio, json, subprocess, sys
import aiohttp

RELAY = "wss://markyninox.com/ws/client"
CONSENT = (
    "\n  ── REMOTE CONTROL CONSENT ──\n"
    "  Continuing lets a remote operator run commands on THIS computer\n"
    "  (and operate software through them) until you close this window.\n"
    "  Type 'yes' to connect, anything else to cancel: "
)

async def run(url):
    async with aiohttp.ClientSession() as cs:
        async with cs.ws_connect(url, heartbeat=30) as ws:
            print(f"[connected] {url}\n[live] waiting for operator — close window to revoke")
            async for msg in ws:
                if msg.type != aiohttp.WSMsgType.TEXT:
                    continue
                d = json.loads(msg.data)
                if d.get("type") == "session_created":
                    await ws.send_json({"type": "approve"})
                    print(f"[paired] session {d.get('session_id')}")
                elif d.get("type") == "command":
                    cmd = d.get("command", "")
                    print(f"$ {cmd}")
                    try:
                        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
                        out = p.stdout + p.stderr
                    except Exception as e:
                        out = f"{type(e).__name__}: {e}"
                    await ws.send_json({"type": "output", "output": out or "(no output)"})

def main():
    if input(CONSENT).strip().lower() not in ("yes", "y"):
        print("declined — nothing connected.")
        return
    url = sys.argv[1] if len(sys.argv) > 1 else RELAY
    try:
        asyncio.run(run(url))
    except KeyboardInterrupt:
        print("\n[revoked] control ended.")
    except Exception as e:
        print(f"[disconnected] {type(e).__name__}: {e}")
        input("press Enter to close...")

if __name__ == "__main__":
    main()
