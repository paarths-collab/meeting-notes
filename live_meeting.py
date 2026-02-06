import subprocess
import os
import sys
import time
import signal
from datetime import datetime

# Import processing logic
from process_file import process_audio

# Configuration from recorder.py
FFMPEG_PATH = r"C:\Program Files\CapCut\Apps\3.7.0.1379\ffmpeg.exe"
OUT_DIR = "data"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = f"{OUT_DIR}/live_meeting_{TIMESTAMP}.wav"

def record_meeting():
    print(f"🎙️ Recording Meeting to {OUTPUT_FILE}...")
    print("🔴 PRESS CTRL+C TO STOP AND PROCESS 🔴")
    
    # Modified command: Capture Microphone ONLY first (to reduce fail points)
    cmd = [
        FFMPEG_PATH,
        "-y", # Overwrite
        "-f", "dshow", "-i", "audio=Microphone Array (Realtek(R) Audio)",
        "-ac", "1",
        "-ar", "16000",
        OUTPUT_FILE
    ]

    # Start FFmpeg
    try:
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print(f"❌ Failed to start FFmpeg: {e}")
        return

    print("🎙️ Recording started! (Speak now)")
    print("🔴 PRESS CTRL+C TO STOP 🔴")

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping recording...")
        process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=2)
            if process.returncode != 0 and process.returncode != 255: # 255 is often term signal
                print(f"⚠️ FFmpeg warning: {stderr.decode('utf-8', errors='ignore')[-500:]}")
        except subprocess.TimeoutExpired:
            process.kill()
        
        # Check if file exists and has size
        if not os.path.exists(OUTPUT_FILE) or os.path.getsize(OUTPUT_FILE) < 1000:
            print("❌ Recording failed! Audio file is empty.")
            return

        print("✅ Recording saved.")
        time.sleep(1) 
        
        # Trigger Pipeline
        print("\n🚀 Processing Meeting...")
        process_audio(OUTPUT_FILE)

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    if not os.path.exists(FFMPEG_PATH):
        print(f"❌ FFmpeg not found at {FFMPEG_PATH}")
        sys.exit(1)
        
    record_meeting()
