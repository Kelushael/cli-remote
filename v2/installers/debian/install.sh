#!/usr/bin/env bash
# Non-admin connecter installer (Debian/Ubuntu). One line:
#   curl -fsSL https://raw.githubusercontent.com/Kelushael/cli-remote/main/v2/installers/debian/install.sh | bash
set -e
DEST="$HOME/.cli-remote"
RAW="https://raw.githubusercontent.com/Kelushael/cli-remote/main/agent.py"
command -v python3 >/dev/null || sudo apt-get update -qq && sudo apt-get install -y python3 python3-pip
mkdir -p "$DEST"
echo "Downloading client..."
curl -fsSL "$RAW" -o "$DEST/agent.py"
python3 -m pip install --quiet aiohttp 2>/dev/null \
  || python3 -m pip install --quiet --break-system-packages aiohttp
echo
exec python3 "$DEST/agent.py"
