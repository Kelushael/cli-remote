# cli-remote

Consent-gated remote control, Chrome-Remote-Desktop style. A client hits **yes**, and from that moment an operator can run shell commands on that machine (and through them, operate software) — driven entirely from a terminal, with no web admin page and no need to visit the domain.

Parts:
- **`server.py`** — websocket relay (public VPS). Pairs clients to operators.
- **`agent.py`** + **`client/`** — the downloadable client. Self-connects to the relay after consent; bundled into `static/cli-remote-client.zip` with one-click `build.bat` (Windows) / `build.command` (Mac).
- **`cli_admin.py`** — the operator's terminal. Lists consented sessions, sends commands, prints output.
- **`cli-agent.py`** — legacy browser-relay agent (kept; superseded by self-connecting `agent.py`).

## Admin from your CLI — the one command

No browser, no `/admin` page, no domain visit:

```bash
pip install aiohttp
python3 cli_admin.py wss://markyninox.com/ws/admin
```

Then: `/sessions` to list, `/use <id>` to pick one, type any command, `/quit` to exit. With one consented client it auto-selects.

## AI admin — talk, don't type commands

`ai_admin.py` puts an LLM on the admin side. You give goals in natural language; the model drives the consented remote shell command-by-command, reads each output, and iterates until done — no pasting, no middleman.

```bash
pip install aiohttp
python3 ai_admin.py ws://2.24.201.163:8765/ws/admin     # by IP now
python3 ai_admin.py wss://markyninox.com/ws/admin        # once TLS is up
```

Then just say what you want: *"clean up his disk and fix whatever's wrong with his CLI."* Defaults to the sovereign Qwen node; override with `MODEL_URL` / `MODEL_KEY` / `MODEL_NAME`. Destructive commands prompt for confirmation unless `AUTO=1`.

## On the machine being controlled — the download flow

1. Visit the domain (e.g. `https://markyninox.com`) and click **DOWNLOAD**.
2. Unzip, double-click **build.bat** (Windows) or **build.command** (Mac).
3. Type **yes** at the consent prompt.

It connects itself to the relay — no browser, no CONNECT button. Closing the window revokes control. The bundle is `static/cli-remote-client.zip`; rebuild it with `./pack.sh` after editing `agent.py` or the launchers.

## Stand up the relay

```bash
git clone https://github.com/Kelushael/cli-remote && cd cli-remote
sudo ./deploy.sh            # service on :8765; nginx proxy snippet printed
```

---

# V2 — Native Host Architecture

V1 works like a terminal-native relay.

V2 evolves this into a real installable remote-host platform:

```text
Website
→ download installer
→ install local host service
→ desktop shortcut/app
→ consent screen
→ persistent host connection
→ remote command/control
```

The browser itself never silently controls the terminal.
The installed host becomes the trusted bridge.

## V2 Goals

- Windows `.exe` installer
- macOS `.dmg` app
- Debian/Ubuntu installer
- Termux installer
- Protocol launcher support (`cliremote://`)
- Native background service/daemon
- Tokenized session auth
- Persistent reconnect
- Clipboard-assisted onboarding
- Optional PyInstaller packaging

## Planned structure

```text
v2/
├── host/
│   ├── cli_remote_host.py
│   ├── launcher.py
│   └── consent_ui.py
├── installers/
│   ├── windows/
│   ├── macos/
│   ├── debian/
│   └── termux/
├── packaging/
│   ├── pyinstaller/
│   └── assets/
└── web/
    ├── onboarding/
    └── protocol-launch/
```

## Example install flows

### Windows

```powershell
irm https://raw.githubusercontent.com/Kelushael/cli-remote/main/v2/installers/windows/install.ps1 | iex
```

### macOS

```bash
curl -fsSL https://raw.githubusercontent.com/Kelushael/cli-remote/main/v2/installers/macos/install.sh | bash
```

### Debian

```bash
curl -fsSL https://raw.githubusercontent.com/Kelushael/cli-remote/main/v2/installers/debian/install.sh | bash
```

### Termux

```bash
curl -fsSL https://raw.githubusercontent.com/Kelushael/cli-remote/main/v2/installers/termux/install.sh | bash
```

## Security

The admin channel is **unauthenticated** in V1 — anyone who can reach `/ws/admin` can drive consented clients.

V2 is intended to add:

- signed sessions
- authenticated operators
- host registration
- explicit permission prompts
- visible local execution logs
- revocable trust
- per-command approval modes
