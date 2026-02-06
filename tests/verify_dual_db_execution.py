import sys
import os
import uuid
import codecs

# Force UTF-8 for Windows console output
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.getcwd())

from core.container import ServiceContainer
from agents.executor_agent import NotionExecutorAgent

def verify_execution():
    print("🚀 Verifying Dual-Database Execution...\n")
    
    container = ServiceContainer.from_env()
    agent = NotionExecutorAgent(container.task_storage)
    
    # meeting_id = f"test-meeting-{str(uuid.uuid4())[:8]}"
    # print(f"Test Meeting ID: {meeting_id}")
    print("Test Meeting ID: (Generating from Date)")
    meeting_id = None
    
    tasks = [
        {
            "task": "Review API Specs",
            "owner": "Paarth", 
            "deadline": "2023-12-31",
            "type": "Engineering",
            "description": "Check the new endpoints"
        },
        {
            "task": "Update Documentation",
            "owner": "Unassigned",
            "deadline": None,
            "type": "Docs",
             "description": "Update readme"
        }
    ]
    
    print(f"Executing {len(tasks)} tasks...")
    try:
        agent.execute_tasks(tasks, meeting_id=meeting_id)
        print("\n✅ Execution finished without error.")
        print("👉 Please check your Notion 'Meetings' and 'Tasks' databases.")
        print("   You should see:")
        print(f"   1. A meeting row with ID '{meeting_id}'")
        print("   2. Two task rows linked to that meeting.")
        
    except Exception as e:
        import traceback
        with open("error_log.txt", "w") as f:
            f.write(str(e))
            f.write("\n")
            traceback.print_exc(file=f)
        print(f"\n❌ Execution failed: {e}")

if __name__ == "__main__":
    verify_execution()
