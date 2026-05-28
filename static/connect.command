#!/bin/bash
cd "$HOME"
DEST="$HOME/.cli-remote"; mkdir -p "$DEST"
echo "Getting ready..."
curl -fsSL https://raw.githubusercontent.com/Kelushael/cli-remote/main/agent.py -o "$DEST/agent.py"
python3 -m pip install --quiet aiohttp 2>/dev/null || python3 -m pip install --quiet --break-system-packages aiohttp 2>/dev/null
echo
python3 "$DEST/agent.py"
