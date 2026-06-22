import os
import requests
import subprocess
import time


def ensure_cdp_running():

    try:
        requests.get(
            "http://localhost:9222/json",
            timeout=1
        )
        print("[CDP] Already Running")
        return True
    except Exception:
        print("[CDP] CDP Not Running")

    # Your explicit Snap installation pathway
    user_profile_dir = "/home/varshith-nakirikanti/snap/chromium/common/chromium"

    subprocess.Popen([
        "chromium",
        "--remote-debugging-port=9222",
        "--remote-allow-origins=*",
        f"--user-data-dir={user_profile_dir}"
    ])

    time.sleep(3)

    try:
        requests.get(
            "http://localhost:9222/json",
            timeout=1
        )
        print("[CDP] Started Successfully")
        return True
    except Exception:
        print(
            "[CDP] Failed. Chromium already running "
            "without remote debugging."
        )
        return False