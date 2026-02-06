# memory/meeting_state.py

from datetime import datetime
import uuid

class MeetingState:
    def __init__(self):
        self.meeting_id = str(uuid.uuid4())
        self.started_at = datetime.utcnow()

        self.tasks = []
        self.decisions = []
        self.open_questions = []

    # ---------- TASK MEMORY ----------
    def add_tasks(self, new_tasks):
        """
        Avoid duplicates by task name
        """
        existing_task_names = {t["task"].lower() for t in self.tasks}

        for task in new_tasks:
            if task["task"].lower() not in existing_task_names:
                self.tasks.append(task)

    def update_task(self, task_name, updates):
        for task in self.tasks:
            if task["task"].lower() == task_name.lower():
                task.update({k: v for k, v in updates.items() if v})
                return

    # ---------- SNAPSHOT ----------
    def snapshot(self):
        return {
            "meeting_id": self.meeting_id,
            "tasks": self.tasks,
            "decisions": self.decisions,
            "open_questions": self.open_questions,
            "started_at": self.started_at.isoformat()
        }


from typing import List, Dict, Optional
from pydantic import BaseModel

class Task(BaseModel):
    title: str
    description: str
    owner_name: str
    owner_slack_id: Optional[str]
    deadline: Optional[str]
    transcript_refs: List[str]

class MeetingState(BaseModel):
    meeting_id: str
    transcript: str
    summary: str
    tasks: List[Task]
    decisions: List[str]
    participants: List[str]
    slack_messages: Dict[str, str] = {}
