import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from audio.ffmpeg_stream import audio_stream
from backend.agents.transcription_agent import WhisperMCPClient

client = WhisperMCPClient()

print("🎤 Listening... speak or play system audio\n")

for chunk in audio_stream(5):
    text = client.transcribe_chunk(chunk)
    if text.strip():
        print("LIVE:", text)
