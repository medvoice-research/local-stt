import logging
import subprocess
from pathlib import Path

import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

MODELS_DIR = Path("models")
MODEL_DOWNLOAD_SCRIPT = "download-ggml-model.sh"
WHISPER_CPP_MODELS_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/models"
AVAILABLE_MODELS = [
    "tiny",
    "tiny.en",
    "base",
    "base.en",
    "small",
    "small.en",
    "medium",
    "medium.en",
    "large-v1",
    "large-v2",
    "large-v3",
    "small.en-tdrz",  # Model with diarization support
]


def ensure_model_dir():
    """Make sure models directory exists"""
    if not MODELS_DIR.exists():
        MODELS_DIR.mkdir(parents=True)
    return MODELS_DIR


def download_model_script():
    """Download the model download script from the whisper.cpp repo"""
    script_path = MODELS_DIR / MODEL_DOWNLOAD_SCRIPT
    if not script_path.exists():
        logger.info(f"Downloading model download script to {script_path}")
        script_url = (
            f"https://raw.githubusercontent.com/ggml-org/whisper.cpp/"
            f"master/models/{MODEL_DOWNLOAD_SCRIPT}"
        )
        response = requests.get(script_url)
        response.raise_for_status()
        with open(script_path, "wb") as f:
            f.write(response.content)
        # Make the script executable
        script_path.chmod(0o755)
    return script_path


def download_model(model_name):
    """Download a specific model"""
    if model_name not in AVAILABLE_MODELS:
        raise ValueError(f"Model {model_name} is not available. Choose from {AVAILABLE_MODELS}")

    ensure_model_dir()
    script_path = download_model_script()
    model_file = MODELS_DIR / f"ggml-{model_name}.bin"

    if model_file.exists():
        logger.info(f"Model {model_name} already exists at {model_file}")
        return model_file

    logger.info(f"Downloading model {model_name}...")
    try:
        # Execute the download script
        result = subprocess.run(
            [str(script_path), model_name, str(MODELS_DIR)],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(f"Download output: {result.stdout}")

        if result.returncode != 0:
            logger.error(f"Error downloading model: {result.stderr}")
            raise RuntimeError(f"Failed to download model {model_name}")

        return model_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        raise RuntimeError(f"Failed to download model {model_name}")
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        raise


def list_available_models():
    """List all available models for download"""
    return AVAILABLE_MODELS


def list_downloaded_models():
    """List models that have been downloaded"""
    ensure_model_dir()
    downloaded = []
    for model_name in AVAILABLE_MODELS:
        model_file = MODELS_DIR / f"ggml-{model_name}.bin"
        if model_file.exists():
            downloaded.append(model_name)
    return downloaded


if __name__ == "__main__":
    # Test downloading a small model
    print("Testing model download...")
    download_model("tiny.en")
    print("Available models:", list_available_models())
    print("Downloaded models:", list_downloaded_models())
