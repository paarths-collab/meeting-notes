import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from audio.ffmpeg_stream import audio_stream

for chunk in audio_stream(3):
    print("Audio chunk samples:", len(chunk))
