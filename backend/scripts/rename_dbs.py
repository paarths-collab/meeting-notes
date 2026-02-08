import os
import sys
from notion_client import Client
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.core.container import ServiceContainer

def rename_databases():
    container = ServiceContainer.from_env()
    client = container.task_storage.client
    
    # Rename Meeting DB
    meeting_id = container.config.notion_database_meeting_id
    if meeting_id:
        print(f"Renaming Meeting DB ({meeting_id}) to 'Meeting Page'...")
        client.databases.update(
            database_id=meeting_id,
            title=[{"text": {"content": "Meeting Page"}}]
        )
        print("✅ Done.")
        
    # Rename Task DB
    task_id = container.config.notion_database_task_id
    if task_id:
        print(f"Renaming Task DB ({task_id}) to 'Task Page'...")
        client.databases.update(
            database_id=task_id,
            title=[{"text": {"content": "Task Page"}}]
        )
        print("✅ Done.")

if __name__ == "__main__":
    rename_databases()
