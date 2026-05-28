#!/usr/bin/env bash
# Run on the relay host (the public VPS). Installs the service on :8765.
set -e
APP=/opt/cli-remote
mkdir -p "$APP/static"
cp server.py "$APP/server.py"
cp static/client.html static/admin.html "$APP/static/"
pip3 install aiohttp --break-system-packages -q 2>/dev/null || pip3 install aiohttp -q

cat > /etc/systemd/system/cli-remote.service <<'SVC'
[Unit]
Description=CLI Remote
After=network.target
[Service]
Type=simple
WorkingDirectory=/opt/cli-remote
ExecStart=/usr/bin/python3 /opt/cli-remote/server.py
Restart=always
[Install]
WantedBy=multi-user.target
SVC

systemctl daemon-reload && systemctl enable cli-remote && systemctl restart cli-remote
systemctl is-active cli-remote && echo "cli-remote running on :8765"

cat <<'NGINX'

# nginx proxy (websocket-aware) — drop into /etc/nginx/sites-available/cli-remote:
# server{listen 80;server_name DOMAIN;location /{proxy_pass http://127.0.0.1:8765/;
#   proxy_http_version 1.1;proxy_set_header Upgrade $http_upgrade;
#   proxy_set_header Connection "upgrade";proxy_set_header Host $host;
#   proxy_read_timeout 86400;}}
NGINX
