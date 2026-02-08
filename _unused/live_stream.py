import numpy as np
import pyaudio # Note: Consider 'pip install pyaudiowpatch' for easier loopback
import threading
import queue
import time
import sys
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
SILENCE_THRESHOLD = 600 
SILENCE_DURATION = 2.0   # Slightly longer for meetings to catch natural pauses
API_KEY = os.getenv("GEMINI_API_KEY") 

# Initialize Gemini
if not API_KEY:
    print("❌ Error: GEMINI_API_KEY not found in .env")
    sys.exit(1)

genai.configure(api_key=API_KEY)
# Using a known stable model for audio
model = genai.GenerativeModel('gemini-2.0-flash-exp') 

class AudioProcessor:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.is_running = True
        self.p = pyaudio.PyAudio()
        self.speech_buffer = []
        self.last_speech_time = time.time()
        self.is_speaking = False

    def find_loopback_device(self):
        """
        Scans for a 'Loopback' or 'Stereo Mix' device.
        This is what allows capturing Google Meet/System audio.
        """
        print("🔍 Scanning for System Audio (Loopback) devices...")
        try:
            # Look for WASAPI Loopback devices if using pyaudiowpatch
            # Fallback to standard device search
            default_device_info = self.p.get_default_input_device_info()
            default_index = default_device_info['index']
            
            found_index = None

            for i in range(self.p.get_device_count()):
                dev = self.p.get_device_info_by_index(i)
                name = dev['name']
                # 'Stereo Mix' is a common built-in Windows loopback
                # If using VB-Cable, look for 'CABLE Output'
                if "Stereo Mix" in name or "Loopback" in name or "CABLE Output" in name:
                    print(f"✅ Found Loopback Device: {name} at index {i}")
                    found_index = i
                    # Prefer CABLE Output if available as it's cleaner
                    if "CABLE Output" in name:
                        return i
            
            if found_index is not None:
                return found_index

            print(f"⚠️ No specific loopback found. Using default mic ({default_device_info['name']}).")
            return default_index
        except Exception as e:
            print(f"❌ Error scanning devices: {e}")
            return None

    def transcribe_audio(self, audio_data):
        try:
            audio_bytes = np.concatenate(audio_data).tobytes()
            # Instructions to Gemini: focus on extracting investment tickers/context from the meeting
            prompt = "You are an AI Investment Assistant. Transcribe this meeting audio. Focus on extracting tickers (like AAPL, RELIANCE) and sentiment."
            
            # Exponential backoff
            for delay in [1, 2, 4]:
                try:
                    response = model.generate_content([
                        prompt,
                        {"mime_type": "audio/l16;rate=16000", "data": audio_bytes}
                    ])
                    return response.text
                except Exception as e:
                    print(f"API Retry ({delay}s): {e}")
                    time.sleep(delay)
            return "[Error: API failed after retries]"

        except Exception as e:
            return f"[Transcription Error: {str(e)}]"

    def transcription_worker(self):
        print("👀 AI Transcription worker active...")
        while self.is_running:
            if not self.audio_queue.empty():
                speech_to_process = self.audio_queue.get()
                print("\n☁️  Analyzing Meeting Context...")
                text = self.transcribe_audio(speech_to_process)
                print(f"📝 Meeting Note: {text}")
            else:
                time.sleep(0.1)

    def start(self):
        device_index = self.find_loopback_device()
        
        try:
            stream = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK
            )
        except Exception as e:
            print(f"❌ Could not start stream: {e}")
            return

        threading.Thread(target=self.transcription_worker, daemon=True).start()
        print("\n🚀 ARBITER LIVE: Capturing Meeting Audio...")
        print("💡 Tip: Ensure your Google Meet audio is playing through your default speakers.")
        print("🔴 Press CTRL+C to stop.")

        try:
            while self.is_running:
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_np = np.frombuffer(data, dtype=np.int16)
                
                # Safe volume calculation
                if len(audio_np) > 0:
                     vol = np.sqrt(np.mean(audio_np.astype(np.float32)**2))
                else:
                     vol = 0

                if vol > SILENCE_THRESHOLD:
                    self.speech_buffer.append(audio_np)
                    self.last_speech_time = time.time()
                    if not self.is_speaking:
                        self.is_speaking = True
                        sys.stdout.write("\n👂 Recording Speech...")
                else:
                    if self.is_speaking and (time.time() - self.last_speech_time > SILENCE_DURATION):
                        self.audio_queue.put(list(self.speech_buffer))
                        self.speech_buffer = []
                        self.is_speaking = False
                        sys.stdout.write(" ✅ Chunk Captured.")
                
                if self.is_speaking:
                    sys.stdout.write(".")
                    sys.stdout.flush()

        except KeyboardInterrupt:
            print("\n\n🛑 Stopping...")
        finally:
            self.is_running = False
            try:
                stream.stop_stream()
                stream.close()
                self.p.terminate()
            except:
                pass

if __name__ == "__main__":
    processor = AudioProcessor()
    processor.start()
