import os
import logging
import shutil
from pathlib import Path
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from model_manager import download_model, list_available_models, list_downloaded_models, MODELS_DIR
from transcription_service import TranscriptionService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
TEMP_UPLOAD_DIR = Path("temp_uploads")
WHISPER_BIN_PATH = os.environ.get("WHISPER_BIN_PATH", "whisper-cli")  # Default to whisper-cli in PATH
DEFAULT_MODEL = "base.en"

# Ensure temp directory exists
if not TEMP_UPLOAD_DIR.exists():
    TEMP_UPLOAD_DIR.mkdir(parents=True)

# Define models for responses
class ModelInfo(BaseModel):
    name: str
    path: str
    supports_diarization: bool
    is_downloaded: bool

class TranscriptionRequest(BaseModel):
    model: str = DEFAULT_MODEL
    enable_diarization: bool = False

class TranscriptionResponse(BaseModel):
    text: str
    segments: List[dict]
    language: str

# Path to static files
STATIC_DIR = Path("static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event for FastAPI"""
    # Code to run on startup
    logger.info("Starting up the FastAPI application")
    # Ensure temp directory exists
    if not TEMP_UPLOAD_DIR.exists():
        TEMP_UPLOAD_DIR.mkdir(parents=True)
        logger.info(f"Created temporary upload directory: {TEMP_UPLOAD_DIR}")
    yield
    # Cleanup on shutdown
    try:
        # Clean up temp_uploads directory
        if TEMP_UPLOAD_DIR.exists():
            # Remove all files but keep the directory
            for file_path in TEMP_UPLOAD_DIR.glob('*'):
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
            logger.info(f"Cleaned up temporary upload directory: {TEMP_UPLOAD_DIR}")
    except Exception as e:
        logger.error(f"Error cleaning up temporary upload directory: {str(e)}")

# Initialize FastAPI with lifespan
app = FastAPI(
    title="Whisper.cpp API",
    description="API for transcribing audio files using whisper.cpp",
    version="1.0.0",
    lifespan=lifespan
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
                model_path=model_path,
                whisper_bin=WHISPER_BIN_PATH,
                temp_dir=TEMP_UPLOAD_DIR
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
        ]
    }

@app.get("/models", response_model=List[ModelInfo])
async def get_models():
    """List all available models and their status"""
    available_models = list_available_models()
    downloaded_models = list_downloaded_models()
    
    models_info = []
    for model_name in available_models:
        is_downloaded = model_name in downloaded_models
        supports_diarization = "tdrz" in model_name
        model_path = str(MODELS_DIR / f"ggml-{model_name}.bin") if is_downloaded else ""
        
        models_info.append(ModelInfo(
            name=model_name,
            path=model_path,
            supports_diarization=supports_diarization,
            is_downloaded=is_downloaded
        ))
    
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

@app.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    model: str = Form(DEFAULT_MODEL),
    enable_diarization: bool = Form(False)
):
    """Transcribe an uploaded audio file"""
    global transcription_service, current_model
    
    # Check if we need to change models
    if not current_model or current_model != model:
        success = initialize_transcription_service(model)
        if not success:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to initialize model {model}. Please check if it's available."
            )
    
    if not transcription_service:
        raise HTTPException(
            status_code=500, 
            detail="Transcription service not initialized"
        )
    
    # Save uploaded file to temp directory
    file_path = TEMP_UPLOAD_DIR / audio_file.filename
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(audio_file.file, f)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving uploaded file: {str(e)}"
        )
    finally:
        audio_file.file.close()
    
    try:
        # Check diarization capability
        model_info = transcription_service.get_model_info()
        if enable_diarization and not model_info["supports_diarization"]:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Diarization requested but current model does not support it. Please use a model with '-tdrz' suffix."
                }
            )
        
        # Process the transcription
        result = transcription_service.transcribe(
            audio_path=file_path,
            enable_diarization=enable_diarization
        )
        
        # Check for errors
        if "error" in result:
            return JSONResponse(
                status_code=500,
                content=result
            )
        
        return result
    except Exception as e:
        logger.exception("Error during transcription")
        raise HTTPException(
            status_code=500,
            detail=f"Transcription error: {str(e)}"
        )
    finally:
        # Clean up the uploaded file
        if file_path.exists():
            os.unlink(file_path)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the whisper.cpp FastAPI service")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the service on (default: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the service on (default: 0.0.0.0)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on file changes")
    
    args = parser.parse_args()
    
    logger.info(f"Starting server on {args.host}:{args.port}")
    uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload)
