import subprocess
import time

def focus_chromium():

    try:

        subprocess.run(
            ["wmctrl", "-a", "Chromium"],
            check=False
        )

        time.sleep(0.5)

        return True

    except Exception:

        return False