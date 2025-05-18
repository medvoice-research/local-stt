import logging
import os
import shutil
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from model_manager import MODELS_DIR, download_model, list_available_models, list_downloaded_models
from transcription_service import TranscriptionService

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
TEMP_UPLOAD_DIR = Path("temp_uploads")
WHISPER_BIN_PATH = os.environ.get(
    "WHISPER_BIN_PATH", "whisper-cli"
)  # Default to whisper-cli in PATH
DEFAULT_MODEL = "base.en"
STATIC_DIR = Path("static")


# Define models for responses
class ModelInfo(BaseModel):
    name: str
    path: str
    supports_diarization: bool
    is_downloaded: bool
    size_mb: int
    multilingual: bool
    params: str
    quantized: bool
    quantization_method: Optional[str] = None


class TranscriptionRequest(BaseModel):
    model: str = DEFAULT_MODEL
    enable_diarization: bool = False


class TranscriptionResponse(BaseModel):
    text: str
    segments: List[dict]
    language: str


def ensure_temp_directory():
    """Ensure the temporary upload directory exists"""
    if not TEMP_UPLOAD_DIR.exists():
        TEMP_UPLOAD_DIR.mkdir(parents=True)
        logger.info(f"Created temporary upload directory: {TEMP_UPLOAD_DIR}")
    return TEMP_UPLOAD_DIR


def clean_temp_directory():
    """Clean up files in the temporary upload directory"""
    try:
        # Clean up temp_uploads directory
        if TEMP_UPLOAD_DIR.exists():
            # Remove all files but keep the directory
            for file_path in TEMP_UPLOAD_DIR.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
            logger.info(f"Cleaned up temporary upload directory: {TEMP_UPLOAD_DIR}")
        return True
    except Exception as e:
        logger.error(f"Error cleaning up temporary upload directory: {str(e)}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event for FastAPI"""
    # Code to run on startup
    logger.info("Starting up the FastAPI application")
    ensure_temp_directory()
    yield
    # Cleanup on shutdown
    clean_temp_directory()


# Initialize FastAPI with lifespan
app = FastAPI(
    title="Whisper.cpp API",
    description="API for transcribing audio files using whisper.cpp",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track active model
current_model = None
transcription_service = None


def initialize_transcription_service(model_name: str):
    """Initialize or update the transcription service with the specified model"""
    global transcription_service, current_model

    try:
        model_path = download_model(model_name)
        if model_path and model_path.exists():
            transcription_service = TranscriptionService(
                model_path=model_path, whisper_bin=WHISPER_BIN_PATH, temp_dir=TEMP_UPLOAD_DIR
            )
            current_model = model_name
            logger.info(f"Initialized transcription service with model {model_name}")
            return True
        else:
            logger.error(f"Failed to initialize model {model_name}")
            return False
    except Exception as e:
        logger.error(f"Error initializing transcription service: {str(e)}")
        return False


# Ensure temp directory exists at startup
ensure_temp_directory()

# Initialize with default model
initialize_transcription_service(DEFAULT_MODEL)

# Mount static files directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
async def get_html():
    """Serve the HTML UI"""
    html_file = STATIC_DIR / "index.html"
    with open(html_file, "r") as f:
        return f.read()


@app.get("/api")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Whisper.cpp API",
        "version": "1.0.0",
        "description": "API for transcribing audio files using whisper.cpp",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "This information"},
            {"path": "/models", "method": "GET", "description": "List available models"},
            {"path": "/transcribe", "method": "POST", "description": "Transcribe an audio file"},
        ],
    }


@app.get("/models", response_model=List[ModelInfo])
async def get_models():
    """List all available models and their status"""
    from models_data import MODEL_INFO

    available_models = list_available_models()
    downloaded_models = list_downloaded_models()

    models_info = []
    for model_name in available_models:
        is_downloaded = model_name in downloaded_models
        model_info: Dict[str, Any] = MODEL_INFO[model_name]
        model_path = str(MODELS_DIR / f"ggml-{model_name}.bin") if is_downloaded else ""

        # Determine if model supports diarization
        supports_diarization = bool(model_info.get("diarization", False) or "tdrz" in model_name)

        # Get quantization method if applicable
        quantization_method = model_info.get("quantization")

        models_info.append(
            ModelInfo(
                name=model_name,
                path=model_path,
                supports_diarization=supports_diarization,
                is_downloaded=is_downloaded,
                size_mb=int(model_info["size_mb"]),
                multilingual=bool(model_info["multilingual"]),
                params=str(model_info["params"]),
                quantized=bool(model_info["quantized"]),
                quantization_method=str(quantization_method) if quantization_method else None,
            )
        )

    return models_info


@app.post("/models/{model_name}/download")
async def download_specific_model(model_name: str, background_tasks: BackgroundTasks):
    """Download a specific model"""
    try:
        # Start download in background
        background_tasks.add_task(download_model, model_name)
        return {"status": "success", "message": f"Download of model {model_name} started"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading model: {str(e)}")


def save_uploaded_file(upload_file: UploadFile) -> Path:
    """Save an uploaded file to the temp directory and return the path"""
    if not upload_file.filename:
        raise HTTPException(status_code=400, detail="Missing filename in uploaded file")
    file_path = TEMP_UPLOAD_DIR / upload_file.filename
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(upload_file.file, f)
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving uploaded file: {str(e)}")
    finally:
        upload_file.file.close()


@app.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    model: str = Form(DEFAULT_MODEL),
    enable_diarization: bool = Form(False),
):
    """Transcribe an uploaded audio file"""
    global transcription_service, current_model

    # Check if we need to change models
    if not current_model or current_model != model:
        success = initialize_transcription_service(model)
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize model {model}. Please check if it's available.",
            )

    if not transcription_service:
        raise HTTPException(status_code=500, detail="Transcription service not initialized")

    # Save uploaded file to temp directory
    file_path = save_uploaded_file(audio_file)

    try:
        # Check diarization capability
        model_info = transcription_service.get_model_info()
        if enable_diarization and not model_info["supports_diarization"]:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Diarization requested but current model does not support it. "
                    "Please use a model with '-tdrz' suffix."
                },
            )

        # Process the transcription
        result = transcription_service.transcribe(
            audio_path=file_path, enable_diarization=enable_diarization
        )

        # Check for errors
        if "error" in result:
            return JSONResponse(status_code=500, content=result)

        return result
    except Exception as e:
        logger.exception("Error during transcription")
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
    finally:
        # Clean up the uploaded file
        if file_path.exists():
            os.unlink(file_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the whisper.cpp FastAPI service")
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to run the service on (default: 8000)"
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host to run the service on (default: 0.0.0.0)"
    )
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on file changes")

    args = parser.parse_args()

    logger.info(f"Starting server on {args.host}:{args.port}")
    uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload)
