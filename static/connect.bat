@echo off
title CLI Remote - Connecting
set "DEST=%USERPROFILE%\.cli-remote"
if not exist "%DEST%" mkdir "%DEST%"
echo Getting ready...
powershell -NoProfile -Command "Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/Kelushael/cli-remote/main/agent.py' -OutFile '%DEST%\agent.py'"
python -m pip install --quiet aiohttp 2>nul || py -m pip install --quiet aiohttp 2>nul
echo.
python "%DEST%\agent.py" 2>nul || py "%DEST%\agent.py"
echo.
pause
