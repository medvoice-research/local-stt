import os
import subprocess
import json
import tempfile
import logging
from pathlib import Path
import ffmpeg

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self, model_path, whisper_bin="whisper-cli", temp_dir="temp_uploads"):
        """
        Initialize the transcription service
        
        Args:
            model_path: Path to the whisper model file
            whisper_bin: Path to the whisper-cli binary
            temp_dir: Directory to store temporary files
        """
        self.model_path = Path(model_path)
        self.whisper_bin = whisper_bin
        self.temp_dir = Path(temp_dir)
        
        if not self.temp_dir.exists():
            self.temp_dir.mkdir(parents=True)
            
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at {model_path}")

    def convert_audio_to_wav(self, audio_path):
        """Convert audio file to 16-bit WAV format required by whisper.cpp"""
        output_path = self.temp_dir / f"{Path(audio_path).stem}_converted.wav"
        
        try:
            ffmpeg.input(audio_path).output(
                str(output_path), 
                acodec='pcm_s16le',  # 16-bit PCM
                ar=16000,            # 16 kHz
                ac=1                  # mono
            ).run(quiet=True, overwrite_output=True)
            
            logger.info(f"Converted {audio_path} to {output_path}")
            return output_path
        except ffmpeg.Error as e:
            logger.error(f"Error converting audio: {e.stderr.decode() if e.stderr else str(e)}")
            raise
    
    def transcribe(self, audio_path, enable_diarization=False):
        """
        Transcribe audio file using whisper.cpp
        
        Args:
            audio_path: Path to the audio file
            enable_diarization: Whether to enable speaker diarization (requires compatible model)
            
        Returns:
            A dictionary with the transcription results
        """
        wav_path = None
        try:
            wav_path = self.convert_audio_to_wav(audio_path)
            
            # Prepare command
            cmd = [
                self.whisper_bin,
                "-m", str(self.model_path),
                "-f", str(wav_path),
                "-oj",  # Output JSON
            ]
            
            if enable_diarization:
                # Add diarization parameter if model supports it (e.g. small.en-tdrz)
                if "tdrz" in str(self.model_path):
                    cmd.append("-tdrz")
                else:
                    logger.warning("Diarization requested but model does not support it. Using regular transcription.")
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            try:
                result = subprocess.run(
                    cmd,
                    check=False,
                    capture_output=True,
                    text=True
                )
            except FileNotFoundError:
                logger.error(f"Error: whisper-cli not found at '{self.whisper_bin}'")
                return {
                    "error": f"whisper-cli not found. Please install whisper.cpp and ensure the binary is in your PATH or set the WHISPER_BIN_PATH environment variable."
                }
                
            # Get the output
            output = result.stdout.strip()
            logger.debug(f"Raw output: {output}")
                
            if not output:
                logger.error("No output from transcription command")
                return {"error": "No output from transcription command: " + result.stderr}
            
            try:
                # Try to parse as JSON first (if -oj flag worked as expected)
                transcription_result = json.loads(output)
                return transcription_result
            except json.JSONDecodeError:
                logger.info("Output is not JSON format, parsing as text")
                
                # Parse text output format: [timestamp --> timestamp] text
                segments = []
                full_text = ""
                lines = output.split("\n")
                
                for line in lines:
                    # Skip empty lines
                    if not line.strip():
                        continue
                        
                    # Try to match the timestamp pattern [HH:MM:SS.mmm --> HH:MM:SS.mmm]
                    import re
                    match = re.match(r'\[(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)\]\s+(.*)', line)
                    if match:
                        start_time = match.group(1)
                        end_time = match.group(2)
                        text = match.group(3)
                        
                        # Convert HH:MM:SS.mmm to seconds
                        def time_to_seconds(time_str):
                            h, m, s = time_str.split(':')
                            return float(h) * 3600 + float(m) * 60 + float(s)
                        
                        t0 = time_to_seconds(start_time)
                        t1 = time_to_seconds(end_time)
                        
                        segments.append({
                            "text": text.strip(),
                            "t0": t0,
                            "t1": t1
                        })
                        
                        full_text += text.strip() + " "
                
                return {
                    "text": full_text.strip(),
                    "segments": segments,
                    "language": "en"  # Assuming English by default
                }
                    
        except subprocess.CalledProcessError as e:
            error_message = e.stderr if e.stderr else str(e)
            logger.error(f"Transcription failed: {error_message}")
            return {"error": f"Transcription failed: {error_message}"}
        finally:
            # Clean up temporary WAV file
            if wav_path and os.path.exists(wav_path):
                os.unlink(wav_path)
                
    def get_model_info(self):
        """Get information about the current model"""
        model_name = self.model_path.stem.replace("ggml-", "")
        is_diarization_capable = "tdrz" in model_name
        
        return {
            "model_name": model_name,
            "model_path": str(self.model_path),
            "supports_diarization": is_diarization_capable
        }
