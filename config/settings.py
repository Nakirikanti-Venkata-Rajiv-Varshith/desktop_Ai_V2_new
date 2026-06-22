# config/settings.py
import os
from pathlib import Path

# Dynamically resolve root 'Desktop_Agent_V2' workspace
BASE_DIR = Path(__file__).resolve().parent.parent

# Centralized data and stream targets
LOG_PATH = os.path.join(BASE_DIR, "logs", "agent.log")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

COMMANDS_JSON_PATH = os.path.join(DATA_DIR, "commands.json")
WEBSITES_JSON_PATH = os.path.join(DATA_DIR, "websites.json")

# Local LLM Parameters
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:8b"

# Operating System Native Hooks
CHROME_COMMAND = "chromium"
FIREFOX_COMMAND = "firefox"
TERMINAL_COMMAND = "gnome-terminal"
VSCODE_COMMAND = "code"