#!/usr/bin/env bash
# Non-admin connecter installer (macOS). One line:
#   curl -fsSL https://raw.githubusercontent.com/Kelushael/cli-remote/main/v2/installers/macos/install.sh | bash
set -e
DEST="$HOME/.cli-remote"
RAW="https://raw.githubusercontent.com/Kelushael/cli-remote/main/agent.py"
mkdir -p "$DEST"
echo "Downloading client..."
curl -fsSL "$RAW" -o "$DEST/agent.py"
python3 -m pip install --quiet aiohttp 2>/dev/null \
  || python3 -m pip install --quiet --break-system-packages aiohttp 2>/dev/null \
  || pip3 install --quiet aiohttp
echo
exec python3 "$DEST/agent.py"
