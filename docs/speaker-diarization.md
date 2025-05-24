# Speaker Diarization in whisper.cpp

This document explains how to use speaker diarization features in the whisper.cpp API.

## Overview

Speaker diarization is the process of determining "who spoke when" in an audio recording. This API supports two methods for speaker diarization:

1. **Built-in tinydiarize** - Limited to English language only, uses the `-tdrz` models.
2. **Pyannote-based diarization** - Supports all languages, uses the [pyannote/speaker-diarization](https://huggingface.co/pyannote/speaker-diarization) model.

## Setup Instructions

### Tinydiarize (Built-in whisper.cpp)

For English-only diarization, you can use the built-in tinydiarize feature by downloading models with the `-tdrz` suffix (e.g., `small.en-tdrz`).

```bash
# Download a tinydiarize model
python -m src.model_manager small.en-tdrz
```

### Pyannote Speaker Diarization

For multilingual diarization or improved performance, you can use Pyannote speaker diarization:

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Get a Hugging Face access token:
   - Go to [Hugging Face](https://huggingface.co/settings/tokens)
   - Create a new token with read access
   - Accept the user agreement for [pyannote/speaker-diarization](https://huggingface.co/pyannote/speaker-diarization)

3. Set the environment variable:
   ```bash
   export HF_TOKEN="your_hugging_face_token_here"
   ```

4. Run the service:
   ```bash
   ./run_service.sh
   ```

## Usage

### API Endpoint

The transcription endpoint supports diarization parameters:

```
POST /transcribe
```

### Form Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| audio_file | File | Audio file to transcribe |
| model | String | Model name (e.g., "base", "small.en-tdrz") |
| enable_diarization | Boolean | Whether to enable speaker diarization |
| num_speakers | Integer (optional) | Exact number of speakers in the audio |
| min_speakers | Integer (optional) | Minimum number of speakers expected |
| max_speakers | Integer (optional) | Maximum number of speakers expected |

### Example cURL Request

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "audio_file=@meeting.wav" \
  -F "model=small.en" \
  -F "enable_diarization=true" \
  -F "min_speakers=2" \
  -F "max_speakers=4"
```

### Response Format

```json
{
  "text": "Full transcription text",
  "segments": [
    {
      "text": "Hello, my name is Alice.",
      "start": 0.0,
      "end": 2.5,
      "speaker": "SPEAKER_00"
    },
    {
      "text": "And I'm Bob, nice to meet you.",
      "start": 2.8,
      "end": 5.2,
      "speaker": "SPEAKER_01"
    },
    ...
  ],
  "language": "en",
  "diarization": {
    "num_speakers": 2,
    "method": "pyannote"
  }
}
```

## Diarization Method Selection

The API automatically selects the appropriate diarization method based on:

1. If you're using a `-tdrz` model and enable diarization, it uses built-in tinydiarize.
2. Otherwise, if pyannote is available and HF_TOKEN is set, it uses pyannote diarization.
3. If neither is available, an error is returned.

## Performance Considerations

- **Built-in tinydiarize** is faster but limited to English and may be less accurate
- **Pyannote diarization** is more accurate and works with any language but requires more computational resources

## Troubleshooting

If you encounter issues with pyannote diarization:

1. Verify your HF_TOKEN is set correctly
2. Ensure you've accepted the model's terms of use on Hugging Face
3. Check that PyTorch and CUDA versions are compatible if using GPU acceleration
4. For large audio files, consider splitting them into smaller segments
