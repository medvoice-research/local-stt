# Whisper.cpp FastAPI Service

This project provides a FastAPI web service for offline transcription and diarization using whisper.cpp, allowing you to run high-quality speech recognition locally without sending data to external services.

![Whisper.cpp FastAPI Service](https://user-images.githubusercontent.com/1991296/235238348-05d0f6a4-da44-4900-a1de-d0707e75b763.jpeg)

## Key Features

- **Web UI**: Easy-to-use web interface for transcription and diarization
- **API Access**: RESTful API for programmatic access
- **Multiple Models**: Support for various model sizes (tiny, base, small, medium, large)
- **Diarization**: Speaker segmentation using both built-in tinydiarize (English-only) and advanced pyannote/speaker-diarization (multilingual)
- **Offline Operation**: All processing happens locally, no data leaves your machine
- **On-demand Model Downloads**: Automatic model management with visual indicators for download status
- **Support for Various Audio Formats**: Through FFmpeg integration

## Prerequisites

1. **whisper.cpp** - The service expects `whisper-cli` binary to be available in your PATH or configured via environment variables
2. **FFmpeg** - Required for audio conversion
3. **Python 3.8+** - Required to run the FastAPI service
4. **Hugging Face Token** - Required for advanced speaker diarization using pyannote.audio (optional)

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

### Environment Variables

The service can be configured using environment variables. You can set them directly or through a `.env` file (recommended):

1. Copy the example configuration file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to customize settings:
   ```
   # Whisper.cpp Configuration
   WHISPER_BIN_PATH=whisper-cli  # Path to the whisper.cpp binary
   DEFAULT_MODEL=base.en         # Default model to use for transcription

   # Speaker Diarization Configuration
   HF_TOKEN=your_token_here      # Hugging Face token for pyannote/speaker-diarization

   # Server Configuration
   HOST=0.0.0.0                  # Host to bind the server to
   PORT=8000                     # Port to run the server on
   DEBUG=false                   # Enable debug mode (true/false)
   ```

### Key Configuration Options

- `WHISPER_BIN_PATH`: Path to the whisper-cli binary (default: looks in PATH)
- `DEFAULT_MODEL`: The default model to use (default: "base.en")
- `HF_TOKEN`: Hugging Face access token for using pyannote/speaker-diarization (required for advanced diarization)
- `HOST`: The host address to bind the server to (default: "0.0.0.0")
- `PORT`: The port number to run the service on (default: 8000)
- `DEBUG`: Enable debug mode with auto-reload on file changes (default: false)

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

Each model is available in English-only variants (e.g., `tiny.en`) which are generally faster and more accurate for English content. For multilingual support, use models without the `.en` suffix.

## Diarization Support

The service offers two methods for speaker diarization:

### Method 1: Built-in Tinydiarize (English-only)

For English-only speaker diarization, use models with the `-tdrz` suffix, such as `small.en-tdrz`. This uses the built-in diarization capability in specific whisper.cpp models from the [TinyDiarize repository](https://github.com/akashmjn/tinydiarize).

**Key characteristics:**
- Only works with English language content
- Faster processing time
- Works without additional setup
- Uses models with `-tdrz` suffix
- Diarization will mark speaker changes in the transcription output with `[SPEAKER_TURN]` markers

### Method 2: Pyannote Speaker Diarization (Multilingual)

For more advanced speaker diarization that works with any language, the service integrates with the [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) model from Hugging Face. This latest version runs in pure PyTorch (without onnxruntime) for easier deployment and potentially faster inference.

**Key characteristics:**
- Works with any language supported by whisper.cpp
- More accurate speaker identification
- Returns individual speaker labels (e.g., "SPEAKER_00", "SPEAKER_01")
- Can specify the exact number of speakers or min/max speaker range
- Requires a Hugging Face access token

To use the advanced diarization:

1. Get a Hugging Face token from [Hugging Face](https://huggingface.co/settings/tokens)
2. Accept the user agreement for [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
3. Set the `HF_TOKEN` environment variable before starting the service:
   ```bash
   export HF_TOKEN="your_hugging_face_token_here"
   ```
   
The service automatically selects the appropriate diarization method based on the model and available dependencies.

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

Basic usage:
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "audio_file=@example.mp3" \
  -F "model=base.en" \
  -F "enable_diarization=false"
```

With built-in tinydiarize (English only):
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "audio_file=@example.mp3" \
  -F "model=small.en-tdrz" \
  -F "enable_diarization=true"
```

With pyannote speaker diarization (works with any model and language):
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "audio_file=@meeting.mp3" \
  -F "model=medium" \
  -F "enable_diarization=true" \
  -F "num_speakers=3"  # Optional: specify exact number of speakers
```

With pyannote speaker diarization using speaker range:
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "audio_file=@meeting.mp3" \
  -F "model=medium" \
  -F "enable_diarization=true" \
  -F "min_speakers=2" \
  -F "max_speakers=5"  # Optional: specify range of speakers
```

Specifying a language (using Vietnamese as an example):
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "audio_file=@vietnamese_speech.mp3" \
  -F "model=medium" \
  -F "language=vi" \
  -F "enable_diarization=true"
```

## Development

### Linting and Code Quality

You can run all linters at once with:
```bash
make lint
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [whisper.cpp](https://github.com/ggml-org/whisper.cpp): High-performance inference of OpenAI's Whisper model
- [TinyDiarize](https://github.com/akashmjn/tinydiarize): Speaker diarization extension for whisper.cpp
- [Pyannote Audio](https://github.com/pyannote/pyannote-audio): Speaker diarization toolkit
- [FastAPI](https://fastapi.tiangolo.com/): Modern web framework for building APIs
- [FFmpeg](https://ffmpeg.org/): Multimedia framework for audio/video processing
