import logging
import os

# Get the log file path from environment variable or set default
log_file = os.getenv("LOG_FILE", "app.log")

# Create logger
logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

# Create handlers
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Example: Log to verify it works
logger.info("Logger is set up.")
