import subprocess
import sys
import numpy as np

FFMPEG_PATH = r"C:\Program Files\CapCut\Apps\3.7.0.1379\ffmpeg.exe"

FFMPEG_CMD = [
    FFMPEG_PATH,
    "-f", "dshow", "-i", "audio=Microphone Array (Realtek(R) Audio)",
    "-f", "dshow", "-i", "audio=CABLE Output (VB-Audio Virtual Cable)",
    "-filter_complex", "amix=inputs=2:normalize=1",
    "-ac", "1",
    "-ar", "16000",
    "-f", "s16le",
    "-"
]

def audio_stream(chunk_seconds=5):
    samples_per_chunk = 16000 * chunk_seconds
    bytes_per_chunk = samples_per_chunk * 2  # s16le = 2 bytes

    proc = subprocess.Popen(
        FFMPEG_CMD,
        stdout=subprocess.PIPE,
        stderr=sys.stderr
    )

    while True:
        raw = proc.stdout.read(bytes_per_chunk)
        if not raw:
            break

        audio = np.frombuffer(raw, dtype=np.int16).astype("float32") / 32768.0
        yield audio
