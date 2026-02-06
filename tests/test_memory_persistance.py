import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from memory.meeting_state import MeetingState
from memory.storage import save_meeting_state, load_meeting_state

state = MeetingState()
state.add_tasks([
    {"task": "deploy backend", "owner": "Ravi", "deadline": "Friday"}
])

save_meeting_state(state)

loaded = load_meeting_state(state.meeting_id)

print("Loaded:", loaded.snapshot())
