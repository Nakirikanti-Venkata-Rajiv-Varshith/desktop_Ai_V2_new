# config/settings.py
import os
from pathlib import Path

# Resolves the root project folder dynamically
BASE_DIR = Path(__file__).resolve().parent.parent

LOG_PATH = os.path.join(BASE_DIR, "logs", "agent.log")
DATA_DIR = os.path.join(BASE_DIR, "data")

COMMANDS_JSON_PATH = os.path.join(DATA_DIR, "commands.json")
WEBSITES_JSON_PATH = os.path.join(DATA_DIR, "websites.json")

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:8b"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
CHROME_COMMAND = "chromium"
FIREFOX_COMMAND = "firefox"
TERMINAL_COMMAND = "gnome-terminal"
VSCODE_COMMAND = "code"