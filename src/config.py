"""
Configuration management for the whisper.cpp API service.
Loads environment variables from .env file.
"""

import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Define project root directory
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
load_dotenv(ROOT_DIR / ".env")

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.info(f"ROOT_DIR is set to: {ROOT_DIR}")

# Whisper.cpp configuration
WHISPER_BIN_PATH = os.getenv("WHISPER_BIN_PATH", "whisper-cli")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "base.en")

# Directories
MODELS_DIR = ROOT_DIR / "models"
TEMP_UPLOAD_DIR = ROOT_DIR / "temp_uploads"
STATIC_DIR = ROOT_DIR / "src" / "static"

# Kaggle configuration
KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
KAGGLE_KEY = os.getenv("KAGGLE_KEY")
KAGGLE_DATASET = os.getenv("KAGGLE_DATASET", "wiradkp/mini-speech-diarization")

# Speaker diarization
HF_TOKEN = os.getenv("HF_TOKEN")

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


# Ensure required directories exist
def ensure_directories():
    """Create required directories if they don't exist."""
    for directory in [MODELS_DIR, TEMP_UPLOAD_DIR, STATIC_DIR]:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")


# Initialize directories
ensure_directories()

# Log configuration (sensitive info redacted)
logger.info(f"Configuration loaded from: {ROOT_DIR / '.env'}")
logger.info(f"WHISPER_BIN_PATH: {WHISPER_BIN_PATH}")
logger.info(f"DEFAULT_MODEL: {DEFAULT_MODEL}")
logger.info(f"MODELS_DIR: {MODELS_DIR}")
logger.info(f"TEMP_UPLOAD_DIR: {TEMP_UPLOAD_DIR}")
logger.info(f"STATIC_DIR: {STATIC_DIR}")
logger.info(f"HF_TOKEN: {'[SET]' if HF_TOKEN else '[NOT SET]'}")
logger.info(f"KAGGLE_USERNAME: {'[SET]' if KAGGLE_USERNAME else '[NOT SET]'}")
logger.info(f"KAGGLE_KEY: {'[SET]' if KAGGLE_KEY else '[NOT SET]'}")
logger.info(f"KAGGLE_DATASET: {KAGGLE_DATASET}")
logger.info(f"Server will run on {HOST}:{PORT} (Debug: {DEBUG})")
