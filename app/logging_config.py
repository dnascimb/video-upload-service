import os
import logging

# Environment-based configuration (e.g., local or production)
env = os.getenv("ENVIRONMENT", "development")  # 'development' or 'production'

# Log file location and logging level configuration
LOG_FILE = "app.log" if env == "development" else None
LOG_LEVEL = logging.INFO if env == "development" else logging.WARNING

# Configure the logger
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE) if env == "development" else logging.StreamHandler(),  # Log to file or console
    ]
)

# Create and export the logger
logger = logging.getLogger()

