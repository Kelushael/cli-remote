@echo off
title CLI Remote - Connect
echo Setting up...
python -m pip install --quiet aiohttp 2>nul || py -m pip install --quiet aiohttp
echo.
python "%~dp0agent.py" || py "%~dp0agent.py"
pause
