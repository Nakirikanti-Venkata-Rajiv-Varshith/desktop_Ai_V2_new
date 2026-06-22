import os
import subprocess
import requests

class AppTool:

    APPS = {
        "chrome": "chromium",
        "chromium": "chromium",
        "firefox": "firefox",
        "terminal": "gnome-terminal",
        "vscode": "code"
    }

    @staticmethod
    def open(app):

        cmd = AppTool.APPS.get(app)

        if not cmd:
            return f"Unknown App: {app}"

        if app in ["chrome", "chromium"]:
            try:
                requests.get("http://localhost:9222/json", timeout=1)
                return "Chromium already running"
            except Exception:
                user_profile_dir = "/home/varshith-nakirikanti/snap/chromium/common/chromium"
                subprocess.Popen([
                    "chromium",
                    "--remote-debugging-port=9222",
                    "--remote-allow-origins=*",
                    f"--user-data-dir={user_profile_dir}"
                ])
                return "Opened chromium"
        else:
            subprocess.Popen([cmd])

        return f"Opened {app}"