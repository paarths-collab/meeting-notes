import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.reflection_agent import reflect_on_tasks

if __name__ == "__main__":
    tasks = [
        {"task": "complete backend integration", "owner": "Ravi", "deadline": "Friday"},
        {"task": "work on frontend UI", "owner": None, "deadline": None}
    ]

    resolved = reflect_on_tasks(tasks)

    print("\n✅ Final Tasks:")
    for t in resolved:
        print(t)
