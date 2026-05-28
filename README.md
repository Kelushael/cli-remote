# cli-remote

Consent-gated remote control, Chrome-Remote-Desktop style. A client hits **yes**, and from that moment an operator can run shell commands on that machine (and through them, operate software) — driven entirely from a terminal, with no web admin page and no need to visit the domain.

Three parts:
- **`server.py`** — a websocket relay (the public VPS). Pairs clients to operators.
- **`cli-agent.py`** — runs on the machine to be controlled. Does nothing until the user types `yes`.
- **`cli_admin.py`** — the operator's terminal. Lists consented sessions, sends commands, prints output.

## Admin from your CLI — the one command

No browser, no `/admin` page, no domain visit:

```bash
pip install aiohttp
python3 cli_admin.py wss://markyninox.com/ws/admin
```

Then: `/sessions` to list, `/use <id>` to pick one, type any command, `/quit` to exit. With one consented client it auto-selects.

## On the machine being controlled

```bash
pip install aiohttp
python3 cli-agent.py        # type 'yes' to grant control
```

…then open the relay page (e.g. `https://markyninox.com`) and click **CONNECT**. That CONNECT is the consent handshake — once they're in, they're in.

## Stand up the relay

```bash
git clone https://github.com/Kelushael/cli-remote && cd cli-remote
sudo ./deploy.sh            # service on :8765; nginx proxy snippet printed
```

## Security

The admin channel is **unauthenticated** — anyone who can reach `/ws/admin` can drive consented clients. Before exposing the relay publicly, gate it: `cli_admin.py` already sends `Authorization: Bearer <token>` if you pass a second arg (`python3 cli_admin.py <url> <token>`); add the matching check in `handle_admin` server-side.
