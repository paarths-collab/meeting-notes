"""
Live Meeting Recorder with Real-Time Transcription
Uses sounddevice for reliable audio capture from VB-Audio Cable
"""
import warnings
# Suppress ALL FutureWarnings before any other imports
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import sys
import time
import threading
import uuid
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
import librosa

# Import project dependencies
from asr.whisper_worker import transcribe_file
from core.container import ServiceContainer
from graph.graph import create_meeting_graph

# ============ CONFIGURATION ============
# Device index from sd.query_devices()
# Index 9 = CABLE Output (VB-Audio Virtual Cable), Windows DirectSound
# DirectSound works without loopback flags (more compatible)
DEVICE_INDEX = 9
CAPTURE_RATE = 48000  # Device native rate
WHISPER_RATE = 16000  # Whisper expects 16kHz
CHANNELS = 2  # Stereo
CHUNK_SECONDS = 3  # Transcribe every 3 seconds

# Paths
CHUNK_DIR = "data/chunks"
os.makedirs(CHUNK_DIR, exist_ok=True)

# Global state
is_recording = True
audio_buffer = []
transcript_accumulated = []
chunk_counter = 0


def resample_to_16k(audio, orig_sr):
    """Resample audio from capture rate to Whisper's 16kHz."""
    return librosa.resample(audio, orig_sr=orig_sr, target_sr=WHISPER_RATE)


def audio_callback(indata, frames, time_info, status):
    """Called for each audio block. Prints volume for debugging."""
    global audio_buffer
    
    if status:
        print(f"⚠️ Status: {status}")
    
    # Convert stereo to mono by averaging channels
    if indata.ndim > 1:
        mono = indata.mean(axis=1)
    else:
        mono = indata.flatten()
    
    # Debug: Print volume
    volume = np.linalg.norm(mono)
    print(f"🔊 Volume: {volume:.4f}", end="\r")
    
    audio_buffer.append(mono.copy())


def transcription_worker():
    """Background thread that transcribes accumulated audio chunks."""
    global chunk_counter, audio_buffer, transcript_accumulated
    
    print("👀 Transcription worker started...")
    
    while is_recording:
        # Wait for enough audio (CHUNK_SECONDS worth at CAPTURE_RATE)
        samples_needed = CAPTURE_RATE * CHUNK_SECONDS
        
        # Check buffer length
        total_samples = sum(len(chunk) for chunk in audio_buffer)
        
        if total_samples >= samples_needed:
            # Concatenate and clear buffer
            audio_data = np.concatenate(audio_buffer)
            audio_buffer.clear()
            
            # Keep only what we need, put rest back
            chunk = audio_data[:samples_needed]
            if len(audio_data) > samples_needed:
                audio_buffer.append(audio_data[samples_needed:])
            
            # Check if audio is not silence
            max_sample = np.max(np.abs(chunk))
            print(f"\n📊 Max sample: {max_sample:.4f}")
            
            if max_sample < 0.001:
                print("   (silence, skipping)")
                continue
            
            # Resample to 16kHz for Whisper
            chunk_16k = resample_to_16k(chunk, CAPTURE_RATE)
            
            # Save to temp file for Whisper
            chunk_file = f"{CHUNK_DIR}/chunk_{chunk_counter:03d}.wav"
            chunk_counter += 1
            
            # Normalize to int16 for wav file
            audio_int16 = (chunk_16k * 32767).astype(np.int16)
            wavfile.write(chunk_file, WHISPER_RATE, audio_int16)
            
            # Transcribe
            try:
                text = transcribe_file(chunk_file)
                if text.strip():
                    print(f"📝 {text}")
                    transcript_accumulated.append(text)
            except Exception as e:
                print(f"❌ Transcription error: {e}")
        
        time.sleep(0.1)
    
    # Process remaining audio after stop
    if audio_buffer:
        audio_data = np.concatenate(audio_buffer)
        if len(audio_data) > CAPTURE_RATE:  # At least 1 second
            chunk_16k = resample_to_16k(audio_data, CAPTURE_RATE)
            chunk_file = f"{CHUNK_DIR}/chunk_final.wav"
            audio_int16 = (chunk_16k * 32767).astype(np.int16)
            wavfile.write(chunk_file, WHISPER_RATE, audio_int16)
            try:
                text = transcribe_file(chunk_file)
                if text.strip():
                    print(f"📝 {text}")
                    transcript_accumulated.append(text)
            except:
                pass


def main():
    global is_recording
    
    # Clean old chunks
    for f in os.listdir(CHUNK_DIR):
        if f.endswith(".wav"):
            os.remove(os.path.join(CHUNK_DIR, f))
    
    print(f"🎙️ Using device index {DEVICE_INDEX}")
    print(f"   Device: {sd.query_devices(DEVICE_INDEX)['name']}")
    print(f"   Capture: {CAPTURE_RATE}Hz → Resample → {WHISPER_RATE}Hz")
    print("🔴 PRESS CTRL+C TO STOP 🔴\n")
    
    # Start transcription worker
    t_trans = threading.Thread(target=transcription_worker, daemon=True)
    t_trans.start()
    
    # Start audio stream
    try:
        with sd.InputStream(
            device=DEVICE_INDEX,
            samplerate=CAPTURE_RATE,
            channels=CHANNELS,
            dtype="float32",
            callback=audio_callback,
            blocksize=int(CAPTURE_RATE * 0.1)  # 100ms blocks
        ):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping...")
        is_recording = False
        time.sleep(1)  # Let worker finish
    except Exception as e:
        print(f"❌ Audio error: {e}")
        print("   Try changing DEVICE_INDEX at the top of this file")
        return
    
    # Final transcript
    full_transcript = "\n".join(transcript_accumulated)
    print("\n" + "="*50)
    print("✅ Final Transcript:")
    print("="*50)
    print(full_transcript if full_transcript else "(empty)")
    print("="*50)
    
    if not full_transcript.strip():
        print("⚠️ No speech detected. Check:")
        print("   1. Windows audio routing (Playback → CABLE Input)")
        print("   2. Volume levels")
        print("   3. Device index (run: python -c \"import sounddevice as sd; print(sd.query_devices())\")")
        return
    
    # Run meeting pipeline
    print("\n🚀 Processing Meeting Pipeline...")
    container = ServiceContainer.from_env()
    meeting_graph = create_meeting_graph(container)
    
    initial_state = {
        "meeting_id": str(uuid.uuid4()),
        "transcript": full_transcript,
        "tasks": [],
        "needs_reflection": False
    }
    
    meeting_graph.invoke(initial_state)
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
