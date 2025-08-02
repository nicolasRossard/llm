import logging
import os
from logging.handlers import TimedRotatingFileHandler

from pydantic_settings import BaseSettings

# ---------------------------------------- Directories and filepath ----------------------------------------
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_APP_DIR = os.path.join(ROOT_DIR, "logs")

for directory in [LOGS_APP_DIR, ]:
    os.makedirs(directory, exist_ok=True)

# ------------------------------------------------ Settings -------------------------------------------------

class Settings(BaseSettings):
    PROJECT_NAME: str = "Alfred"
    API_V1_STR: str = "/api/v1"


SETTINGS = Settings()

# ------------------------------------------------ LOGS -------------------------------------------------
# Define log file path
log_file = os.path.join(LOGS_APP_DIR, "app.log")

# Set up file handler for logging with daily rotation
file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=30)
file_handler.suffix = '%Y-%m-%d'
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Set up console handler
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Configure the root logger
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(file_handler)
logging.getLogger().addHandler(console_handler)
