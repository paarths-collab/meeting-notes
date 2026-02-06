import os
import sys
import uuid
import argparse

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

from asr.whisper_worker import transcribe_file
from graph.graph import create_meeting_graph
from core.container import ServiceContainer

def process_audio(file_path: str):
    """
    1. Transcribe audio file
    2. Run Meeting Pipeline
    """
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    print(f"🎧 Transcribing {file_path}...")
    try:
        transcript = transcribe_file(file_path)
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        return

    if not transcript.strip():
        print("⚠️ Transcript is empty. Aborting.")
        return

    print("\n📝 Transcript:")
    print("-" * 40)
    print(transcript[:500] + ("..." if len(transcript) > 500 else ""))
    print("-" * 40)
    
    # Initialize Pipeline
    print(f"\n🚀 Starting Meeting Agent...")
    container = ServiceContainer.from_env()
    meeting_graph = create_meeting_graph(container)
    
    # Create State
    initial_state = {
        "meeting_id": str(uuid.uuid4()),
        "transcript": transcript,
        "tasks": [],
        "needs_reflection": False
    }
    
    # Run Graph
    try:
        final_state = meeting_graph.invoke(initial_state)
        print("\n✅ Meeting completed successfully")
        print("Final Tasks:", final_state["tasks"])
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a meeting audio file.")
    parser.add_argument("file", help="Path to audio file (mp3/wav)")
    args = parser.parse_args()
    
    process_audio(args.file)
