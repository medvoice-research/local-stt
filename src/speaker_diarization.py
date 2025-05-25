import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import torch
from pyannote.audio import Pipeline
from pyannote.core import Annotation

# Import configuration
from config import HF_TOKEN as DEFAULT_HF_TOKEN

logger = logging.getLogger(__name__)


class SpeakerDiarizationService:
    def __init__(self, hf_token: Optional[str] = None):
        """
        Initialize the speaker diarization service using pyannote/speaker-diarization.

        Args:
            hf_token: Hugging Face access token (required to use the pyannote models)
                      If None, will use the HF_TOKEN from environment variables
        """
        self.pipeline = None
        self.hf_token = hf_token if hf_token is not None else DEFAULT_HF_TOKEN
        self._initialized = False

        if not self.hf_token:
            logger.warning(
                "No Hugging Face token provided for speaker diarization. "
                "Set HF_TOKEN environment variable or provide token in constructor."
            )

    def initialize(self):
        """Initialize the pyannote speaker diarization pipeline"""
        if self._initialized:
            return

        logger.info("Initializing pyannote speaker diarization pipeline")
        try:
            # Load the speaker diarization model from Hugging Face
            # Use the latest 3.1 model which runs in pure PyTorch
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.hf_token,
            )

            # Use CUDA if available
            if torch.cuda.is_available() and self.pipeline is not None:
                logger.info("Using CUDA for speaker diarization")
                self.pipeline = self.pipeline.to(torch.device("cuda"))

            self._initialized = True
            logger.info("Speaker diarization pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize speaker diarization pipeline: {e}")
            raise

    def diarize(
        self,
        audio_path: Union[str, Path],
        num_speakers: Optional[int] = None,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
    ) -> Dict:
        """
        Perform speaker diarization on an audio file.

        Args:
            audio_path: Path to the audio file
            num_speakers: Exact number of speakers in the audio (if known)
            min_speakers: Minimum number of speakers expected
            max_speakers: Maximum number of speakers expected

        Returns:
            A dictionary of diarization results
        """
        if not self._initialized:
            self.initialize()

        try:
            audio_path = str(audio_path) if isinstance(audio_path, Path) else audio_path

            # Prepare input for pyannote
            file = {"uri": "audio", "audio": audio_path}

            # Set speaker count constraints if provided
            diarization_params = {}
            if num_speakers is not None:
                diarization_params["num_speakers"] = num_speakers
            else:
                if min_speakers is not None:
                    diarization_params["min_speakers"] = min_speakers
                if max_speakers is not None:
                    diarization_params["max_speakers"] = max_speakers

            # Apply diarization
            if self.pipeline is None:
                raise ValueError("Diarization pipeline not initialized properly")
            diarization = self.pipeline(file, **diarization_params)

            # Convert pyannote Annotation to a more usable format
            results = self._process_diarization(diarization)

            return results

        except Exception as e:
            logger.error(f"Speaker diarization failed: {e}")
            raise

    def _process_diarization(self, diarization: Annotation) -> Dict:
        """
        Process diarization results to a usable format.

        Args:
            diarization: PyAnnote diarization result

        Returns:
            Dictionary with processed diarization segments
        """
        segments = []

        # Process each segment from the diarization result
        for segment, track, speaker in diarization.itertracks(yield_label=True):
            segments.append(
                {
                    "speaker": speaker,
                    "start": segment.start,
                    "end": segment.end,
                    "duration": segment.end - segment.start,
                }
            )

        # Sort segments by start time
        segments.sort(key=lambda s: s["start"])

        return {"segments": segments, "num_speakers": len(diarization.labels())}

    def align_diarization_with_transcription(
        self, diarization_result: Dict, transcription_segments: List[Dict]
    ) -> List[Dict]:  # type: ignore [no-any-return]
        """
        Align speaker diarization results with whisper transcription segments.

        Args:
            diarization_result: Output from diarize() method
            transcription_segments: List of segments from whisper transcription

        Returns:
            List of transcription segments with speaker labels
        """
        if not diarization_result or not transcription_segments:
            return transcription_segments

        diarization_segments = diarization_result["segments"]

        # Create a function to find the best speaker for a given time range
        def get_speaker_for_segment(start: float, end: float) -> str:
            # Find overlapping diarization segments
            overlaps = []
            for segment in diarization_segments:
                overlap_start = max(segment["start"], start)
                overlap_end = min(segment["end"], end)

                if overlap_end > overlap_start:  # There is an overlap
                    overlap_duration = overlap_end - overlap_start
                    overlaps.append((segment["speaker"], overlap_duration))

            if not overlaps:
                return "UNKNOWN"

            # Return the speaker with the most overlap
            overlaps.sort(key=lambda x: x[1], reverse=True)
            return overlaps[0][0]

        # Assign speakers to transcription segments
        for segment in transcription_segments:
            segment["speaker"] = get_speaker_for_segment(segment["start"], segment["end"])

        return transcription_segments


if __name__ == "__main__":
    # Simple test
    import os

    # Get HF token from environment variable for testing
    hf_token = os.environ.get("HF_TOKEN")

    if not hf_token:
        print("HF_TOKEN environment variable not set. Cannot test speaker diarization.")
        exit(1)

    service = SpeakerDiarizationService(hf_token=hf_token)

    # Test on a sample file (replace with an actual path)
    test_file = "sample.wav"
    if os.path.exists(test_file):
        result = service.diarize(test_file)
        print(f"Found {result['num_speakers']} speakers")
        for segment in result["segments"][:10]:  # Print first 10 segments
            print(f"Speaker {segment['speaker']}: {segment['start']:.2f}s - {segment['end']:.2f}s")
    else:
        print(f"Test file {test_file} not found")
