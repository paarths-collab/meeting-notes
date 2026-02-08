import pyaudio
import numpy as np
import threading
import queue
import time
import sys

# --- CONFIGURATION ---
DEVICE_INDEX = 9 
CHUNK_SIZE = 1024
TARGET_RATE = 16000 
TARGET_CHANNELS = 1

# SETTING A MAXSIZE prevents the 'OOM' (Out of Memory) crash
# If the worker is too slow, we drop old data rather than crashing the PC
audio_queue = queue.Queue(maxsize=100) 
stop_event = threading.Event()

def transcription_worker():
    """
    Processes audio in the background. 
    Throttled to prevent terminal buffer overflows.
    """
    print("👀 Transcription worker started...")
    last_ui_update = 0
    
    while not stop_event.is_set():
        try:
            # Short timeout to keep checking stop_event
            item = audio_queue.get(timeout=0.1)
            if item is None: break
            
            raw_data, current_rate, current_channels = item
            
            # Convert and check for data validity
            audio_np = np.frombuffer(raw_data, dtype=np.float32).copy()
            if not np.all(np.isfinite(audio_np)):
                audio_np = np.nan_to_num(audio_np)
            
            # Downsample/Mono logic
            if current_channels == 2:
                audio_np = audio_np.reshape(-1, 2).mean(axis=1)
            if current_rate == 48000:
                audio_np = audio_np[::3]
            
            # --- STABLE UI UPDATE ---
            # Updating too fast causes VS Code 'OOM' crashes. 
            # We limit this to once per second.
            now = time.time()
            if now - last_ui_update > 1.0:
                volume = np.sqrt(np.mean(audio_np**2))
                if volume < 1e-6:
                    # Clear line then print to avoid terminal scroll issues
                    sys.stdout.write("\r🔇 [Status] Device active but silent...          ")
                else:
                    sys.stdout.write(f"\r🔊 [Status] Capturing Audio | Vol: {volume:.4f}  ")
                sys.stdout.flush()
                last_ui_update = now
                
        except queue.Empty:
            continue
        except Exception:
            # Silent fail on worker errors to prevent terminal spam
            continue

def capture_thread_func(p, stream, rate, channels):
    """
    Reads hardware data and puts it in the queue.
    """
    while not stop_event.is_set():
        try:
            if stream.is_active():
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                # Use put_nowait or block with timeout to prevent hang
                try:
                    audio_queue.put((data, rate, channels), block=False)
                except queue.Full:
                    # If queue is full, worker is too slow. 
                    # Drop the oldest to save memory.
                    try:
                        audio_queue.get_nowait()
                        audio_queue.put((data, rate, channels), block=False)
                    except: pass
        except Exception:
            break

def get_audio_stream():
    p = pyaudio.PyAudio()
    # Try standardized 16k Mono first
    try:
        stream = p.open(format=pyaudio.paFloat32, channels=1, rate=16000,
                        input=True, input_device_index=DEVICE_INDEX, frames_per_buffer=CHUNK_SIZE)
        return p, stream, 16000, 1
    except:
        pass
    # Try native 48k Stereo
    try:
        stream = p.open(format=pyaudio.paFloat32, channels=2, rate=48000,
                        input=True, input_device_index=DEVICE_INDEX, frames_per_buffer=CHUNK_SIZE)
        return p, stream, 48000, 2
    except Exception as e:
        print(f"\n❌ Hardware Error: {e}")
        p.terminate()
        return None

def main():
    result = get_audio_stream()
    if not result: return
    
    p, stream, active_rate, active_channels = result
    
    t_worker = threading.Thread(target=transcription_worker, daemon=True)
    t_capture = threading.Thread(target=capture_thread_func, args=(p, stream, active_rate, active_channels), daemon=True)
    
    t_worker.start()
    t_capture.start()

    print(f"\n✅ Stream Open: {active_rate}Hz, {active_channels}ch")
    print("🔴 PRESS CTRL+C TO STOP (Closing terminal safely) 🔴\n")

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        stop_event.set()
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Finalizing...")
        time.sleep(0.5) 

if __name__ == "__main__":
    main()
