#!/usr/bin/env bash
cd "$(dirname "$0")"
echo "Setting up..."
python3 -m pip install --quiet aiohttp 2>/dev/null || python3 -m pip install --quiet --break-system-packages aiohttp 2>/dev/null
echo
python3 agent.py
