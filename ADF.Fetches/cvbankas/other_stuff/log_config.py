# https://docs.python.org/3/howto/logging.html


# DEBUG - Detailed information, typically of interest only when diagnosing problems.
# INFO - Confirmation that things are working as expected.
# WARNING - An indication that something unexpected happened, or indicative of
# some problem in the near future (e.g. 'disk space low'). The software is still working as expected.
# ERROR - Due to a more serious problem, the software has not been able to perform some function.
# CRITICAL - A serious error, indicating that the program itself may be unable to continue running.

import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get log level from environment or fallback to INFO
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(funcName)s - %(message)s",
    "%Y/%m/%d %H:%M:%S",
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Get the base directory from environment variables
base_dir = os.getenv("BASE_DIR", os.getcwd())

# Construct full log path
log_dir = os.path.join(base_dir, "data/logs")
log_file_path = os.path.join(log_dir, "app.log")

# Ensure the log directory exists
os.makedirs(log_dir, exist_ok=True)

# File handler
file_handler = logging.FileHandler(log_file_path)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
