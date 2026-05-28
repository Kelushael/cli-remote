# Non-admin connecter installer (Windows). One line in PowerShell:
#   irm https://raw.githubusercontent.com/Kelushael/cli-remote/main/v2/installers/windows/install.ps1 | iex
$ErrorActionPreference = "Stop"
$dest = Join-Path $env:USERPROFILE ".cli-remote"
$raw  = "https://raw.githubusercontent.com/Kelushael/cli-remote/main/agent.py"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Write-Host "Downloading client..."
Invoke-WebRequest -UseBasicParsing $raw -OutFile (Join-Path $dest "agent.py")
$py = "python"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { $py = "py" }
& $py -m pip install --quiet aiohttp
Write-Host ""
& $py (Join-Path $dest "agent.py")
