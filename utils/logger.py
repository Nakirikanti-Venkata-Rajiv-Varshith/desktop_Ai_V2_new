import logging
from utils.settings import LOG_PATH

def setup_logger() -> logging.Logger:
    """Configures centralized logging architecture."""
    logger = logging.getLogger("ComputerAgentV1")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(LOG_PATH)
        file_handler.setFormatter(formatter)
        
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    return logger

agent_logger = setup_logger()