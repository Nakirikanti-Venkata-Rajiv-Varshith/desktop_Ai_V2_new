# app.py

import sys
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow
from tools.logger import agent_logger
from browser.bootstrap import ensure_cdp_running


def main():
    try:
        agent_logger.info("Initializing Ubuntu AI Desktop Agent UI Engine...")

        # Ensure Chromium CDP is running
        agent_logger.info("Ensuring Chromium CDP session is active...")
        cdp_ready = ensure_cdp_running()

        if not cdp_ready:
            agent_logger.error("Failed to initialize Chromium CDP on port 9222.")
            return 1

        # Create Qt application
        app = QApplication(sys.argv)

        print("Starting Chromium CDP...")
        # Create and show main window
        window = MainWindow()
        window.show()

        agent_logger.info("Application lifecycle started successfully.")

        return app.exec()

    except Exception:
        agent_logger.exception("Fatal application startup failure")
        return 1


if __name__ == "__main__":
    sys.exit(main())