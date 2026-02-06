import time
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from asr.whisper_worker import transcribe_file

CHUNK_DIR = "data/chunks"
TRANSCRIPT_FILE = "data/transcripts.txt"

processed = set()

def watch():
    print("👀 Watcher started. Waiting for audio chunks...\n")

    while True:
        files = sorted(os.listdir(CHUNK_DIR))

        if not files:
            print("⏳ No chunks yet...")
            time.sleep(2)
            continue

        for f in files:
            if f.endswith(".wav") and f not in processed:
                path = os.path.join(CHUNK_DIR, f)
                print(f"🎧 Processing {f}")

                try:
                    text = transcribe_file(path)

                    if text.strip():
                        print("📝", text)
                        with open(TRANSCRIPT_FILE, "a", encoding="utf-8") as out:
                            out.write(text + "\n")

                    processed.add(f)
                    os.remove(path)
                    print(f"🗑 Deleted {f}\n")

                except Exception as e:
                    print("⚠️ Error:", e)

        time.sleep(1)

if __name__ == "__main__":
    watch()
