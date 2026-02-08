import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agents.reflection_autogen import run_reflection

tasks = [
    {"task": "work on frontend UI", "owner": None, "deadline": None},
    {"task": "backend integration", "owner": "Ravi", "deadline": "Friday"},
]

result = run_reflection(tasks)

print("\n✅ Final Output:")
print(result)
