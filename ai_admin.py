#!/usr/bin/env python3
"""AI admin for cli-remote — the orchestrator layer.

You give goals in natural language. An LLM drives the consented remote shell
command-by-command, reads each output, and iterates until done. No pasting,
no middleman.

  pip install aiohttp
  python3 ai_admin.py ws://2.24.201.163:8765/ws/admin      # by IP now
  python3 ai_admin.py wss://markyninox.com/ws/admin        # once TLS is up

Env (defaults to the sovereign Qwen node):
  MODEL_URL   default http://108.181.162.206:8186/v1/chat/completions
  MODEL_KEY   default axis-vox-2026
  MODEL_NAME  default qwen
  AUTO=0      pause for y/N on destructive commands (default: auto-run everything)

Session control:  /use <id>   /sessions   /quit
"""
import asyncio, json, os, re, sys
import aiohttp

MODEL_URL  = os.environ.get("MODEL_URL", "http://108.181.162.206:8186/v1/chat/completions")
MODEL_KEY  = os.environ.get("MODEL_KEY", "axis-vox-2026")
MODEL_NAME = os.environ.get("MODEL_NAME", "qwen")
AUTO       = os.environ.get("AUTO", "1") != "0"

DANGER = re.compile(r"\brm\s+-rf?\b|\bmkfs|\bdd\s+if=|>\s*/dev/[sh]d|\bshutdown\b|\breboot\b|:\(\)\s*\{|chmod\s+-R\s+777\s+/| > /etc/")

SYSTEM = """You are a remote operations agent driving a shell on a CONSENTED remote computer.
The human gives a high-level goal. Accomplish it by issuing ONE shell command at a time and reading its output.

Reply with EXACTLY one line, one of:
  RUN: <a single shell command>
  ASK: <a short question, only if you truly cannot proceed>
  DONE: <one-line summary of what you accomplished>

Rules:
- One command per RUN, no explanation around it.
- The target may be macOS or Linux — run `uname` first if it matters.
- Diagnose before you mutate. Never run destructive commands without first inspecting.
- Quote paths with spaces. When the goal is met, reply DONE."""


def clean_cmd(s):
    s = s.strip()
    if s.startswith("```"):
        s = s.strip("`")
        s = re.sub(r"^(bash|sh|shell)\n", "", s)
    return s.strip().strip("`").strip()


async def call_model(http, messages):
    payload = {"model": MODEL_NAME, "messages": messages, "temperature": 0.2, "max_tokens": 400}
    headers = {"Authorization": f"Bearer {MODEL_KEY}", "Content-Type": "application/json"}
    async with http.post(MODEL_URL, json=payload, headers=headers, timeout=120) as r:
        data = await r.json()
    return data["choices"][0]["message"]["content"].strip()


class Admin:
    def __init__(self, ws):
        self.ws = ws
        self.sessions = {}
        self.selected = None
        self.outq = asyncio.Queue()

    async def reader(self):
        async for msg in self.ws:
            if msg.type != aiohttp.WSMsgType.TEXT:
                continue
            d = json.loads(msg.data)
            t = d.get("type")
            if t == "session_list":
                for s in d.get("sessions", []):
                    self.sessions[s["session_id"]] = s
            elif t == "client_connected":
                self.sessions[d["session_id"]] = {"session_id": d["session_id"], "approved": False}
                print(f"\n[+] client {d['session_id']} (awaiting consent)")
            elif t == "session_approved":
                self.sessions.setdefault(d["session_id"], {})["approved"] = True
                if self.selected is None:
                    self.selected = d["session_id"]
                print(f"\n[OK] {d['session_id']} consented — driving this session")
            elif t == "client_disconnected":
                self.sessions.pop(d["session_id"], None)
                if self.selected == d["session_id"]:
                    self.selected = None
                print(f"\n[-] client {d['session_id']} gone")
            elif t == "command_output" and d.get("session_id") == self.selected:
                await self.outq.put(d.get("output", ""))

    async def run_command(self, cmd, timeout=130):
        while not self.outq.empty():
            self.outq.get_nowait()
        await self.ws.send_json({"type": "command", "session_id": self.selected, "command": cmd})
        try:
            return await asyncio.wait_for(self.outq.get(), timeout)
        except asyncio.TimeoutError:
            return "(no output / timed out)"

    async def pursue(self, http, goal):
        messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": f"Goal: {goal}"}]
        loop = asyncio.get_event_loop()
        for _ in range(25):
            reply = await call_model(http, messages)
            messages.append({"role": "assistant", "content": reply})
            print(f"\n  ai> {reply}")
            if reply.startswith("DONE"):
                return
            if reply.startswith("ASK"):
                ans = await loop.run_in_executor(None, sys.stdin.readline)
                messages.append({"role": "user", "content": ans.strip()})
                continue
            m = re.match(r"RUN:\s*(.+)", reply, re.S)
            if not m:
                messages.append({"role": "user", "content": "Reply with RUN:, ASK:, or DONE: only."})
                continue
            cmd = clean_cmd(m.group(1))
            if not AUTO and DANGER.search(cmd):
                prompt = f"  ⚠ destructive: {cmd}\n  run it? [y/N] "
                ans = (await loop.run_in_executor(None, lambda: input(prompt))).strip().lower()
                if ans not in ("y", "yes"):
                    messages.append({"role": "user", "content": "Human declined that command. Use a safer approach."})
                    continue
            out = await self.run_command(cmd)
            print(f"  $ {cmd}\n  {out[:1500]}")
            messages.append({"role": "user", "content": f"OUTPUT of `{cmd}`:\n{out[:4000]}"})
        print("  (step limit reached — give another goal or refine)")


async def main(url):
    async with aiohttp.ClientSession() as http:
        async with http.ws_connect(url, heartbeat=30) as ws:
            admin = Admin(ws)
            r = asyncio.ensure_future(admin.reader())
            print(f"[connected] {url}\nWaiting for a consented client, then type goals in plain English.")
            loop = asyncio.get_event_loop()
            while True:
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                line = line.strip()
                if line in ("/quit", "/q"):
                    break
                if line == "/sessions":
                    print(admin.sessions); continue
                if line.startswith("/use "):
                    admin.selected = line.split(None, 1)[1].strip(); print("driving", admin.selected); continue
                if not line:
                    continue
                if admin.selected is None:
                    print("no consented session yet — have the client hit DOWNLOAD, run it, type yes")
                    continue
                await admin.pursue(http, line)
            r.cancel()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "ws://localhost:8765/ws/admin"
    try:
        asyncio.run(main(url))
    except KeyboardInterrupt:
        pass
