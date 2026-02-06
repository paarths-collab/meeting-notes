import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.executor_agent import execute_tasks

tasks = [
    {
        "task": "Publish release notes",
        "owner": "Paarth",
        "deadline": "28 Feb 2025"
    }
]

from notion_client.errors import APIResponseError

try:
    execute_tasks(tasks, meeting_id="test-meeting-123")
    print("✅ Sent to MindMinutes")
except APIResponseError as e:
    print(f"❌ API Error: {e}")
    print(f"Body: {e.body}")
    raise
