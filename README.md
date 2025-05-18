# Whisper.cpp FastAPI Service

This project provides a FastAPI web service for offline transcription and diarization using whisper.cpp, allowing you to run high-quality speech recognition locally without sending data to external services.

![Whisper.cpp FastAPI Service](https://user-images.githubusercontent.com/1991296/235238348-05d0f6a4-da44-4900-a1de-d0707e75b763.jpeg)

## Key Features

- **Web UI**: Easy-to-use web interface for transcription and diarization
- **API Access**: RESTful API for programmatic access
- **Multiple Models**: Support for various model sizes (tiny, base, small, medium, large)
- **Diarization**: Speaker segmentation with compatible models
- **Offline Operation**: All processing happens locally, no data leaves your machine
- **On-demand Model Downloads**: Automatic model management with visual indicators for download status
- **Support for Various Audio Formats**: Through FFmpeg integration

## Prerequisites

1. **whisper.cpp** - The service expects `whisper-cli` binary to be available in your PATH or configured via environment variables
2. **FFmpeg** - Required for audio conversion
3. **Python 3.8+** - Required to run the FastAPI service

## Quick Start

### Native Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/whispercpp-experimental.git
   cd whispercpp-experimental
   ```

2. You have several options to set up the service:

   **Option 1: Complete setup (recommended for first-time users)**
   ```bash
   # Creates virtual environment, installs dependencies,
   # builds whisper.cpp, creates symlink, and downloads base models
   make setup-all
   ```

   **Option 2: Step-by-step setup**
   ```bash
   # Create a virtual environment (optional)
   make venv
   
   # Install Python dependencies
   make install
   
   # Build whisper.cpp from source
   make build-whisper
   
   # Create a symlink to whisper-cli
   make link-whisper
   
   # Download specific models (e.g., base.en, small.en-tdrz)
   make download-model MODEL=base.en
   make download-model MODEL=small.en-tdrz
   ```

3. Run the service:
   ```bash
   make start
   ```

4. Open your browser and go to `http://localhost:8000`

5. Additional commands:
   ```bash
   # List available models
   make models
   
   # Stop the running service
   make stop
   
   # Clean temporary files
   make clean
   ```

## Configuration

The service can be configured using environment variables:

- `WHISPER_BIN_PATH`: Path to the whisper-cli binary (default: looks in PATH)
- `DEFAULT_MODEL`: The default model to use (default: "base.en")

## Available Models

The service supports all models provided by whisper.cpp:

| Model | Size | Memory Required | Relative Speed | Languages | Diarization |
|-------|------|-----------------|----------------|-----------|-------------|
| tiny.en | 75 MB  | ~273 MB | Fastest | English only | No |
| base.en | 142 MB | ~388 MB | Fast | English only | No |
| small.en | 466 MB | ~852 MB | Moderate | English only | No |
| small.en-tdrz | ~466 MB | ~852 MB | Moderate | English only | Yes |
| medium.en | 1.5 GB | ~2.1 GB | Slow | English only | No |
| large | 2.9 GB | ~3.9 GB | Slowest | Multilingual | No |

Each model is available in English-only variants (e.g., `tiny.en`) which are generally faster and more accurate for English content.

## Diarization Support

For speaker diarization (identifying different speakers), use models with the `-tdrz` suffix, such as `small.en-tdrz`. Diarization will mark speaker changes in the transcription output with `[SPEAKER_TURN]` markers.

These diarization models are from the [TinyDiarize repository](https://github.com/akashmjn/tinydiarize) and provide speaker segmentation capabilities.

## Using the Web Interface

1. Browse to `http://localhost:8000`
2. The interface shows:
   - Audio file upload section
   - Model selection dropdown
   - Speaker diarization toggle
   - Available models section with download buttons

3. To transcribe:
   - Upload an audio file
   - Select a model (must be downloaded first)
   - Enable diarization if needed and if the model supports it
   - Click "Transcribe Audio"

4. The transcription results will show:
   - Full transcription text
   - Segments with timestamps
   - Speaker turns highlighted (if diarization was enabled)

## API Usage

### API Documentation

Full API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### List available models:

```bash
curl -X GET http://localhost:8000/models
```

Example response:
```json
[
  {
    "name": "base.en",
    "path": "models/ggml-base.en.bin",
    "supports_diarization": false,
    "is_downloaded": true
  },
  {
    "name": "small.en-tdrz",
    "path": "models/ggml-small.en-tdrz.bin",
    "supports_diarization": true,
    "is_downloaded": true
  }
]
```

### Download a model:

```bash
curl -X POST http://localhost:8000/models/small.en-tdrz/download
```

### Transcribe an audio file:

```bash
curl -X POST http://localhost:8000/transcribe \
  -F "audio_file=@example.mp3" \
  -F "model=base.en" \
  -F "enable_diarization=false"
```

## Development

### Linting and Code Quality

This project uses several linting and code quality tools to maintain consistent code style and catch potential issues:

1. **Black**: Code formatter that enforces a consistent style
2. **isort**: Sorts and organizes import statements
3. **flake8**: Checks for PEP 8 compliance and common errors
4. **mypy**: Static type checker for Python
5. **pylint**: In-depth code analysis for bugs and quality issues

You can run all linters at once with:
```bash
make lint
```

Or run individual linters:
```bash
make lint-black     # Check code formatting with Black
make lint-flake8    # Run flake8 linter
make lint-mypy      # Run type checking
make lint-isort     # Check import sorting
make lint-pylint    # Run pylint
```

To automatically format your code:
```bash
make format         # Runs black and isort to format code
```


## Project Structure

- `src/`: Python source code for the FastAPI service
  - `main.py`: FastAPI application entry point
  - `model_manager.py`: Manages whisper.cpp models
  - `transcription_service.py`: Interfaces with whisper.cpp
  - `static/`: Contains web UI files
- `models/`: Directory for downloaded whisper models
- `temp_uploads/`: Temporary storage for uploaded files
- `run_service.sh`: Script to run the service locally
- `pyproject.toml`: Configuration for Black, mypy, and isort
- `setup.cfg`: Configuration for flake8
- `.pylintrc`: Configuration for pylint

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [whisper.cpp](https://github.com/ggml-org/whisper.cpp): High-performance inference of OpenAI's Whisper model
- [TinyDiarize](https://github.com/akashmjn/tinydiarize): Speaker diarization extension for whisper.cpp
- [FastAPI](https://fastapi.tiangolo.com/): Modern web framework for building APIs
- [FFmpeg](https://ffmpeg.org/): Multimedia framework for audio/video processing
