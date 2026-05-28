#!/usr/bin/env bash
# Non-admin connecter installer (Termux/Android). One line:
#   curl -fsSL https://raw.githubusercontent.com/Kelushael/cli-remote/main/v2/installers/termux/install.sh | bash
set -e
DEST="$HOME/.cli-remote"
RAW="https://raw.githubusercontent.com/Kelushael/cli-remote/main/agent.py"
command -v python3 >/dev/null || pkg install -y python
command -v curl >/dev/null || pkg install -y curl
mkdir -p "$DEST"
echo "Downloading client..."
curl -fsSL "$RAW" -o "$DEST/agent.py"
python3 -m pip install --quiet aiohttp
echo
exec python3 "$DEST/agent.py"
