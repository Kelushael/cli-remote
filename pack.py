#!/usr/bin/env python3
import zipfile, os

FILES = {
    "agent.py": "agent.py",
    "client/build.bat": "build.bat",
    "client/build.command": "build.command",
    "client/README.txt": "README.txt",
}
os.makedirs("static", exist_ok=True)
out = "static/cli-remote-client.zip"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for src, arc in FILES.items():
        zi = zipfile.ZipInfo(f"cli-remote-client/{arc}")
        zi.external_attr = (0o755 if arc == "build.command" else 0o644) << 16
        z.writestr(zi, open(src, "rb").read())
print("built", out)
