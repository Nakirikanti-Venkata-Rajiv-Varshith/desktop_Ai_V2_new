# tools/logger.py
import os
import logging
from config.settings import LOG_PATH

def setup_logger() -> logging.Logger:
    """Configures a centralized logging architecture for the agent."""
    logger = logging.getLogger("UbuntuDesktopAgentV2")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Safely extract log directory track and create it if missing
        log_dir = os.path.dirname(LOG_PATH)
        os.makedirs(log_dir, exist_ok=True)
        
        # File Logger
        file_handler = logging.FileHandler(LOG_PATH)
        file_handler.setFormatter(formatter)
        
        # Console Handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    return logger

agent_logger = setup_logger()