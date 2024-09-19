import logging

def setup_logger():
    """Set up and return a logger with a basic configuration."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    return logging.getLogger()

logger = setup_logger()
