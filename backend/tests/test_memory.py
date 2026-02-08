import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from memory.meeting_state import MeetingState
from memory.storage import save_meeting_state, load_meeting_state

# Create meeting
state = MeetingState()
state.add_tasks([
    {"task": "backend integration", "owner": "Ravi", "deadline": "Friday"},
    {"task": "frontend UI", "owner": None, "deadline": None}
])

save_meeting_state(state)
print("Saved meeting:", state.meeting_id)

# Reload meeting
loaded = load_meeting_state(state.meeting_id)
print("Reloaded:", loaded.snapshot())
