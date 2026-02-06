import json
import os
from datetime import datetime
from memory.meeting_state import MeetingState

SESSIONS_DIR = "memory/sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)


def save_meeting_state(state: MeetingState):
    path = f"{SESSIONS_DIR}/{state.meeting_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state.snapshot(), f, indent=2)


def load_meeting_state(meeting_id: str) -> MeetingState:
    path = f"{SESSIONS_DIR}/{meeting_id}.json"
    if not os.path.exists(path):
        raise FileNotFoundError("Meeting not found")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Reconstruct state
    state = MeetingState()
    # Manually set attributes
    state.meeting_id = data["meeting_id"]
    state.tasks = data["tasks"]
    state.decisions = data["decisions"]
    state.open_questions = data["open_questions"]
    # Parse date string back to datetime
    state.started_at = datetime.fromisoformat(data["started_at"])

    return state
