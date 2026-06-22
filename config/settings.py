import os
from pathlib import Path

# ====================================================================
# File System Path Constants
# ====================================================================
# Resolves the root 'computer-agent' directory dynamically
BASE_DIR = Path(__file__).resolve().parent.parent

# Centralized output pathways for storage files and log streams
LOG_PATH = os.path.join(BASE_DIR, "logs", "agent.log")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Absolute paths to required persistent local tracking maps
COMMANDS_JSON_PATH = os.path.join(DATA_DIR, "commands.json")
WEBSITES_JSON_PATH = os.path.join(DATA_DIR, "websites.json")


# ====================================================================
# Local LLM (Ollama) Operational Targets
# ====================================================================
# The network address pointing directly to your local Ollama daemon api
OLLAMA_URL = "http://localhost:11434/api/generate"

# The specific parameters matching the local model context requirements
OLLAMA_MODEL = "qwen3:8b"


# ====================================================================
# Operating System Execution Maps (Ubuntu Binaries)
# ====================================================================
# Native system call hooks utilized by subprocess.Popen
# Swapped to "chromium" to match your target system installation cleanly
CHROME_COMMAND = "chromium"
FIREFOX_COMMAND = "firefox"
TERMINAL_COMMAND = "gnome-terminal"
VSCODE_COMMAND = "code"

# Fallback browser target used when opening open-ended web lookups
DEFAULT_BROWSER = "chromium"