import json
import os
from tools.logger import agent_logger

def load_json_data(file_path: str) -> dict:
    """Safely loads tracking and registration JSON maps from data directory."""
    if not os.path.exists(file_path):
        agent_logger.warning(f"Data file missing at {file_path}. Returning empty context.")
        return {}
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        agent_logger.error(f"Failed parsing data file {file_path}: {str(e)}")
        return {}