import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

# Import configuration
try:
    from config.config import LOGGING
except ImportError:
    # Default logging configuration if config is not available
    LOGGING = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "log_file": "stock_pattern_detector.log",
        "log_dir": "logs"
    }

def _get_logs_dir():
    """Get the logs directory from environment or config."""
    logs_dir = os.environ.get('LOGS_DIR')
    if not logs_dir:
        if "log_dir" in LOGGING:
            if not os.path.isabs(LOGGING["log_dir"]):
                logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), LOGGING["log_dir"])
            else:
                logs_dir = LOGGING["log_dir"]
        else:
            logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')

    # Make sure the directory exists
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: The name of the logger. If None, returns the root logger.

    Returns:
        A configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name)
    # Only configure logger if it hasn't been configured yet
    if not logger.handlers:
        # Set level from config (default to INFO if not specified)
        level = getattr(logging, LOGGING.get("level", "INFO"))
        logger.setLevel(level)

        # Create formatters
        log_format = LOGGING.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        formatter = logging.Formatter(log_format)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Get logs directory dynamically each time
        logs_dir = _get_logs_dir()

        # Create file handler with daily rotation
        log_filename = LOGGING.get("log_file", "stock_pattern_detector.log")
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = os.path.join(logs_dir, f"{log_filename.replace('.log', '')}_{today}.log")

        file_handler = TimedRotatingFileHandler(
            log_path,
            when='midnight',
            backupCount=7  # Keep logs for 7 days
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Prevent propagation to avoid duplicate logs
        logger.propagate = False

    return logger

# Initialize the root logger
root_logger = get_logger()

# Export the get_logger function as the main API
__all__ = ['get_logger']
logger = get_logger("default_logger")
