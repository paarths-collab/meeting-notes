# FFmpeg -> rolling WAV files
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import subprocess
import os
import time

FFMPEG_PATH = r"C:\Program Files\CapCut\Apps\3.7.0.1379\ffmpeg.exe"
OUT_DIR = "data/chunks"
CHUNK_SECONDS = 5

os.makedirs(OUT_DIR, exist_ok=True)

def start_recording():
    cmd = [
        FFMPEG_PATH,
        "-thread_queue_size", "1024",
        "-f", "dshow", "-i", "audio=Microphone Array (Realtek(R) Audio)",
        "-thread_queue_size", "1024",
        "-f", "dshow", "-i", "audio=CABLE Output (VB-Audio Virtual Cable)",
        "-filter_complex", "amix=inputs=2:normalize=1",
        "-ac", "1",
        "-ar", "16000",
        "-f", "segment",
        "-segment_time", str(CHUNK_SECONDS),
        "-reset_timestamps", "1",
        f"{OUT_DIR}/chunk_%03d.wav"
    ]

    subprocess.run(cmd)

if __name__ == "__main__":
    start_recording()
