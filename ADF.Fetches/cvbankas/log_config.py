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

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create formatters
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s", "%Y/%m/%d %H:%M:%S"
)

# Create handlers
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Get the base directory from environment variables
base_dir = os.getenv("BASE_DIR")
log_file_path = os.path.join(base_dir, "logs/app.log")

file_handler = logging.FileHandler(log_file_path)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
