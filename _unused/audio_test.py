import sounddevice as sd
import numpy as np

DEVICE_INDEX = 2          # CABLE Output (MME)
SAMPLE_RATE = 44100
CHANNELS = 2

def callback(indata, frames, time, status):
    volume = np.linalg.norm(indata)
    print(f"🔊 Volume: {volume:.6f}")

print("🎧 Testing raw audio capture...")
with sd.InputStream(
    device=DEVICE_INDEX,
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="float32",
    blocksize=2048,       # IMPORTANT for MME
    callback=callback
):
    input("Speak / play audio. Press ENTER to stop\n")
