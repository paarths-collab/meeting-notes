"""
Live Audio Capture with Speaker Diarization

Captures system audio from VB-Audio Cable and transcribes in real-time
using AssemblyAI with speaker identification. Falls back to Whisper if offline.

Usage:
    python audio/live_capture.py
"""
import pyaudio
import numpy as np
import threading
import queue
import time
import sys
import os
import tempfile
import wave

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

# --- CONFIGURATION ---
SEARCH_KEYWORD = "CABLE Output"
CHUNK_SIZE = 1024
TARGET_RATE = 16000
TARGET_CHANNELS = 1
SILENCE_THRESHOLD = 0.003  # RMS threshold for silence detection
SILENCE_DURATION = 2.5     # Seconds of silence before processing chunk
MIN_AUDIO_LENGTH = 1.0     # Minimum audio length in seconds to process
TRANSCRIPT_FILE = "data/transcripts.txt"

# Check if AssemblyAI is available
USE_ASSEMBLYAI = bool(os.getenv("ASSEMBLYAI_API_KEY"))

# Thread-safe structures
audio_queue = queue.Queue(maxsize=100)
stop_event = threading.Event()

# Load appropriate model
if USE_ASSEMBLYAI:
    print("🔄 Using AssemblyAI with speaker diarization...")
    import assemblyai as aai
    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
    model = None  # Will use API
else:
    print("🔄 Loading local Whisper model...")
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    
print("✅ Ready!")


def find_cable_device(p):
    """Automatically finds the index for VB-Audio Cable."""
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    
    for i in range(num_devices):
        dev_info = p.get_device_info_by_host_api_device_index(0, i)
        if SEARCH_KEYWORD.lower() in dev_info.get('name').lower():
            return i
    return None


def save_audio_to_wav(audio_np, filepath):
    """Save numpy audio array to WAV file."""
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(TARGET_RATE)
        audio_int16 = (audio_np * 32767).astype(np.int16)
        wf.writeframes(audio_int16.tobytes())


def transcribe_with_assemblyai(audio_np):
    """Transcribe with AssemblyAI (includes speaker diarization)."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name
    
    try:
        save_audio_to_wav(audio_np, temp_path)
        
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            language_code="en"
        )
        
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(temp_path, config=config)
        
        if transcript.status == aai.TranscriptStatus.error:
            return f"[Error: {transcript.error}]"
        
        # Format with speaker labels
        lines = []
        for utterance in transcript.utterances:
            lines.append(f"Speaker {utterance.speaker}: {utterance.text}")
        
        return "\n".join(lines) if lines else transcript.text or ""
    
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass


def transcribe_with_whisper(audio_np):
    """Transcribe with local Whisper model."""
    if len(audio_np) < TARGET_RATE * MIN_AUDIO_LENGTH:
        return ""
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name
    
    try:
        save_audio_to_wav(audio_np, temp_path)
        
        segments, _ = model.transcribe(
            temp_path,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        return " ".join(seg.text.strip() for seg in segments).strip()
    
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass


def transcribe_audio_chunk(audio_np):
    """Transcribe audio using configured backend."""
    if USE_ASSEMBLYAI:
        return transcribe_with_assemblyai(audio_np)
    else:
        return transcribe_with_whisper(audio_np)


def transcription_worker():
    """Processes audio chunks and transcribes in the background."""
    print("👀 Transcription worker active...")
    
    speech_buffer = []
    last_speech_time = time.time()
    is_speaking = False
    last_ui_update = 0
    
    while not stop_event.is_set():
        try:
            item = audio_queue.get(timeout=0.1)
            if item is None:
                break
            
            raw_data, current_rate, current_channels = item
            audio_np = np.frombuffer(raw_data, dtype=np.float32).copy()
            
            # Clean invalid values
            if not np.all(np.isfinite(audio_np)):
                audio_np = np.nan_to_num(audio_np)
            
            # Stereo to mono
            if current_channels == 2:
                audio_np = audio_np.reshape(-1, 2).mean(axis=1)
            
            # Downsample 48kHz -> 16kHz
            if current_rate == 48000:
                audio_np = audio_np[::3]
            
            # Calculate volume
            volume = np.sqrt(np.mean(audio_np**2))
            now = time.time()
            
            # Update UI periodically
            if now - last_ui_update > 0.5:
                if volume < SILENCE_THRESHOLD:
                    status = "🔇 [Waiting for Audio]"
                else:
                    bars = int(min(volume * 100, 30))
                    status = f"🔊 [Capturing] {'█' * bars}"
                sys.stdout.write(f"\r{status:<50}")
                sys.stdout.flush()
                last_ui_update = now
            
            # Speech detection and buffering
            if volume > SILENCE_THRESHOLD:
                speech_buffer.append(audio_np)
                last_speech_time = now
                if not is_speaking:
                    is_speaking = True
                    print("\n👂 Speech detected...")
            else:
                # Check for silence after speech
                if is_speaking and (now - last_speech_time > SILENCE_DURATION):
                    if speech_buffer:
                        full_audio = np.concatenate(speech_buffer)
                        duration = len(full_audio) / TARGET_RATE
                        
                        if duration >= MIN_AUDIO_LENGTH:
                            backend = "AssemblyAI" if USE_ASSEMBLYAI else "Whisper"
                            print(f"\n☁️  Transcribing {duration:.1f}s with {backend}...")
                            
                            text = transcribe_audio_chunk(full_audio)
                            
                            if text:
                                print(f"\n{'='*50}")
                                print(text)
                                print(f"{'='*50}\n")
                                
                                # Save to transcript file
                                os.makedirs(os.path.dirname(TRANSCRIPT_FILE), exist_ok=True)
                                with open(TRANSCRIPT_FILE, "a", encoding="utf-8") as f:
                                    f.write(text + "\n\n")
                        
                        speech_buffer = []
                    is_speaking = False
                    
        except queue.Empty:
            continue
        except Exception as e:
            print(f"\n⚠️ Worker error: {e}")
            continue


def capture_thread_func(p, stream, rate, channels):
    """Reads audio data and puts it in the queue."""
    while not stop_event.is_set():
        try:
            if stream.is_active():
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                try:
                    audio_queue.put((data, rate, channels), block=False)
                except queue.Full:
                    try:
                        audio_queue.get_nowait()
                        audio_queue.put((data, rate, channels), block=False)
                    except:
                        pass
        except Exception:
            break


def get_audio_stream():
    """Initialize PyAudio and open stream from VB-Audio Cable."""
    p = pyaudio.PyAudio()
    
    idx = find_cable_device(p)
    if idx is None:
        print(f"❌ Could not find '{SEARCH_KEYWORD}'. Check your Sound Control Panel.")
        print("\n💡 Setup Instructions:")
        print("   1. Install VB-Audio Cable: https://vb-audio.com/Cable/")
        print("   2. Set 'CABLE Input' as your meeting app's audio output")
        print("   3. Run this script again")
        p.terminate()
        return None
    
    device_name = p.get_device_info_by_index(idx)['name']
    print(f"✅ Found Loopback Device: {device_name} at index {idx}")

    # Try 16k Mono first
    try:
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=16000,
            input=True,
            input_device_index=idx,
            frames_per_buffer=CHUNK_SIZE
        )
        return p, stream, 16000, 1
    except:
        pass

    # Fallback: 48k Stereo
    try:
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=2,
            rate=48000,
            input=True,
            input_device_index=idx,
            frames_per_buffer=CHUNK_SIZE
        )
        return p, stream, 48000, 2
    except Exception as e:
        print(f"\n❌ Hardware Error on index {idx}: {e}")
        p.terminate()
        return None


def main():
    result = get_audio_stream()
    if not result:
        return
    
    p, stream, active_rate, active_channels = result
    
    # Start worker threads
    t_worker = threading.Thread(target=transcription_worker, daemon=True)
    t_capture = threading.Thread(target=capture_thread_func, args=(p, stream, active_rate, active_channels), daemon=True)
    
    t_worker.start()
    t_capture.start()

    backend = "AssemblyAI (with speakers)" if USE_ASSEMBLYAI else "Whisper (local)"
    
    print("\n" + "="*60)
    print("🚀 LIVE MEETING TRANSCRIPTION")
    print("="*60)
    print(f"🎙️  Backend: {backend}")
    print(f"📁 Saving to: {TRANSCRIPT_FILE}")
    print("🔴 PRESS CTRL+C TO STOP\n")

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping transcription...")
    finally:
        stop_event.set()
        audio_queue.put(None)
        if stream:
            stream.stop_stream()
            stream.close()
        p.terminate()
        time.sleep(0.5)
        
        # Summary
        if os.path.exists(TRANSCRIPT_FILE):
            with open(TRANSCRIPT_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"\n✅ Transcription saved!")
            print(f"📍 File: {os.path.abspath(TRANSCRIPT_FILE)}")
            print("\n💡 Run 'python run_meeting.py' to process the transcript")


if __name__ == "__main__":
    main()
