"""
Transcript Router

Single orchestrator that converts any input (text/file/url) to transcript.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from audio.extract import extract_audio
from asr.whisper_transcriber import transcribe_audio
from utils.download import download_file


def get_transcript(
    text: str = None,
    file_path: str = None,
    url: str = None
) -> str:
    """
    Convert any input to transcript text.
    
    Args:
        text: Raw transcript text (pass-through)
        file_path: Path to audio/video file
        url: URL to download recording from
        
    Returns:
        Transcript text
    """
    # Option 1: Direct text
    if text:
        return text.strip()

    # Option 2: URL → download → transcribe
    if url:
        downloaded = download_file(url, "inputs/downloads/recording.mp4")
        file_path = downloaded

    # Option 3: File → extract audio → transcribe
    if file_path:
        # Extract audio if not already WAV
        if not file_path.lower().endswith(".wav"):
            audio_path = extract_audio(file_path)
        else:
            audio_path = file_path
        
        return transcribe_audio(audio_path)

    raise ValueError("No valid input provided. Provide text, file_path, or url.")
