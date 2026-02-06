import os
import uuid
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
# Force UTF-8 for Windows consoles
sys.stdout.reconfigure(encoding='utf-8')

from graph.graph import create_meeting_graph
from core.container import ServiceContainer


# Default transcript if file doesn't exist
DEFAULT_TRANSCRIPT = """
Meeting regarding the new dashboard.
Paarth needs to fix the login bug by tomorrow.
Ravi, please update the API docs by next Friday.
"""


def main():
    """Main entry point with dependency injection."""
    
    # Initialize service container from environment
    container = ServiceContainer.from_env()
    
    # Create graph with injected dependencies
    meeting_graph = create_meeting_graph(container)
    
    # Load transcript
    transcript_path = "data/transcripts.txt"
    if os.path.exists(transcript_path):
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()
    else:
        transcript = DEFAULT_TRANSCRIPT
    
    if not transcript.strip():
        transcript = DEFAULT_TRANSCRIPT
    
    # Create initial state
    initial_state = {
        "meeting_id": str(uuid.uuid4()),
        "transcript": transcript,
        "tasks": [],
        "needs_reflection": False
    }
    
    print(f"🚀 Starting Meeting Agent | ID: {initial_state['meeting_id']}")
    
    # Invoke graph
    import traceback
    try:
        final_state = meeting_graph.invoke(initial_state)
    except Exception:
        traceback.print_exc()
        return
    
    print("\n✅ Meeting completed")
    print("Final Tasks:", final_state["tasks"])


if __name__ == "__main__":
    main()
