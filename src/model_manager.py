import logging
import os
import subprocess
import shutil
from pathlib import Path

import requests

# Import configuration
from config import ROOT_DIR, MODELS_DIR

# Import model information from the dedicated module
from models_data import AVAILABLE_MODELS

logger = logging.getLogger(__name__)
MODEL_DOWNLOAD_SCRIPT = "download-ggml-model.sh"
WHISPER_CPP_MODELS_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/models"


def ensure_model_dir():
    """Make sure models directory exists"""
    if not MODELS_DIR.exists():
        MODELS_DIR.mkdir(parents=True)
    return MODELS_DIR


def download_model_script():
    """
    Download the model download script from the whisper.cpp repo.
    This handles downloading the script without using symlinks.
    """
    script_path = MODELS_DIR / MODEL_DOWNLOAD_SCRIPT
    
    # Check if script exists but might be a symlink
    if script_path.exists() and os.path.islink(str(script_path)):
        logger.info(f"Removing symlink at {script_path}")
        os.unlink(str(script_path))
    
    if not script_path.exists() or os.path.islink(str(script_path)):
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
    
    # Check if model file is a symlink
    if model_file.exists() and os.path.islink(str(model_file)):
        # Get the target of the symlink
        target = os.readlink(str(model_file))
        logger.info(f"Found symlink for {model_file} pointing to {target}")
        
        if os.path.exists(target):
            # Copy the actual file to replace the symlink
            logger.info(f"Copying file from {target} to {model_file}")
            os.unlink(str(model_file))
            shutil.copy2(target, str(model_file))
        else:
            # Remove broken symlink
            logger.info(f"Removing broken symlink at {model_file}")
            os.unlink(str(model_file))

    if model_file.exists() and not os.path.islink(str(model_file)):
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
            
        # Double-check the file exists after download
        if not model_file.exists():
            logger.error(f"Download script completed but model file not found at {model_file}")
            raise RuntimeError(f"Model file not found after download: {model_file}")

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
        if model_file.exists() and not os.path.islink(str(model_file)):
            downloaded.append(model_name)
    return downloaded


def clean_model_symlinks():
    """
    Clean up any symlinks in the models directory and ensure all models
    are actual files, not symlinks.
    """
    logger.info("Cleaning up model symlinks...")
    ensure_model_dir()
    
    # Check for symlinks in main models directory
    for file_path in MODELS_DIR.glob("*"):
        if os.path.islink(str(file_path)):
            target = os.readlink(str(file_path))
            logger.info(f"Found symlink in models directory: {file_path} -> {target}")
            
            if os.path.exists(target):
                # Replace symlink with actual file
                logger.info(f"Replacing symlink with actual file: {file_path}")
                os.unlink(str(file_path))
                shutil.copy2(target, str(file_path))
            else:
                # Remove broken symlink
                logger.info(f"Removing broken symlink: {file_path}")
                os.unlink(str(file_path))
    
    # Check for src/models directory and handle it
    src_models_dir = ROOT_DIR / "src" / "models"
    if src_models_dir.exists():
        logger.info(f"Found duplicate models directory at {src_models_dir}")
        
        # Check for real files in src/models that should be in models/
        for file_path in src_models_dir.glob("*"):
            if file_path.is_file() and not os.path.islink(str(file_path)):
                # This is a real file in src/models/ - copy to models/ if not there
                dest_path = MODELS_DIR / file_path.name
                if not dest_path.exists() or os.path.getsize(str(dest_path)) != os.path.getsize(str(file_path)):
                    logger.info(f"Copying file from {file_path} to {dest_path}")
                    shutil.copy2(str(file_path), str(dest_path))
        
        # No need to keep src/models directory
        logger.info(f"Removing redundant directory: {src_models_dir}")
        shutil.rmtree(str(src_models_dir))
        
    logger.info("Model symlink cleanup complete")


if __name__ == "__main__":
    # Test downloading a small model
    print("Testing model download...")
    download_model("tiny.en")
    print("Available models:", list_available_models())
    print("Downloaded models:", list_downloaded_models())
