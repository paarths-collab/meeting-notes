"""
Audio Extraction Module

Extracts audio from video files using ffmpeg.
Outputs 16kHz mono WAV for Whisper transcription.
"""
import subprocess
from pathlib import Path


def extract_audio(input_file: str) -> str:
    """
    Extract audio from video file to 16kHz mono WAV.
    
    Args:
        input_file: Path to video/audio file
        
    Returns:
        Path to extracted WAV file
    """
    input_path = Path(input_file)
    output_path = input_path.with_suffix(".wav")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", str(input_path),
            "-ar", "16000",
            "-ac", "1",
            str(output_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return str(output_path)
