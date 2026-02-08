"""
Whisper Transcription Module

Uses OpenAI Whisper for audio-to-text transcription.
"""
import whisper

# Load model once at module load
model = whisper.load_model("base")


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio file to text using Whisper.
    
    Args:
        audio_path: Path to audio file (WAV preferred)
        
    Returns:
        Transcribed text
    """
    result = model.transcribe(audio_path)
    return result["text"].strip()
