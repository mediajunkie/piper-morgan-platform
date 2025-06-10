# logger_config.py
import logging
import os
from logging.handlers import RotatingFileHandler
from config import app_config # Import our centralized config

# Define the log file path
LOG_FILE_PATH = "app.log"

def setup_logging():
    """
    Sets up the application-wide logging configuration.
    """
    # Overall logger level (e.g., DEBUG to capture everything for file)
    # This level determines the *minimum* severity that the logger *will process*.
    # Messages below this level are ignored by the logger entirely.
    overall_log_level_str = "DEBUG" # Always capture DEBUG or higher for the logger itself
    overall_log_level = getattr(logging, overall_log_level_str, logging.DEBUG)

    # Level for console output (from config)
    # This level determines what the console handler *will display*.
    console_log_level_str = app_config.LOG_LEVEL.upper()
    console_log_level = getattr(logging, console_log_level_str, logging.INFO)

    # Create logger
    logger = logging.getLogger("pm_agent_app")
    logger.setLevel(overall_log_level) # Set logger to capture lowest desired level (e.g., DEBUG)
    logger.propagate = False # Prevent messages from being passed to the root logger

    # Clear existing handlers to prevent duplicate logs during reloads (e.g., in development)
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)

    # Console Handler (for output to terminal)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_log_level) # Set console handler to its specific level (e.g., INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (for output to a text file)
    # This will write logs to 'app.log', with a max size of 10 MB and 5 backup files
    file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=10485760, backupCount=5) # 10 MB per file, 5 backups
    file_handler.setLevel(overall_log_level) # File handler captures everything the logger captures (e.g., DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Add a success message to the log
    logger.info("Logging configured successfully.")

# Call setup_logging immediately when this module is imported
setup_logging()

# Get the logger instance to be imported by other modules
logger = logging.getLogger("pm_agent_app")