import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.notion_service import NotionTaskService
from core.config import AppConfig

def test_assignee_mapping():
    print("🧪 Testing Smart Assignee Mapping...\n")
    
    # Load config
    try:
        config = AppConfig.from_env()
    except Exception as e:
        print(f"❌ Config error: {e}")
        return

    # Initialize Service
    service = NotionTaskService(config.notion_token, config.notion_database_id)
    
    # 1. Fetch Users
    print("1️⃣ Fetching Notion Users...")
    users = service.get_users()
    print(f"✅ Found {len(users)} users: {list(users.keys())}\n")
    
    if not users:
        print("⚠️ No users found in Notion workspace. Is the integration shared with the workspace?")
        return

    # 2. Test Resolution
    print("2️⃣ Testing Name Resolution...")
    test_names = ["Paarth", "Sarah", "Unknown User", "Me"]
    
    for name in test_names:
        user_id = service.resolve_user_id(name)
        status = f"✅ Resolved to {user_id}" if user_id else "❌ Not found"
        print(f"   - '{name}' -> {status}")

    # 3. Create Test Task
    print("\n3️⃣ Creating Test Task with Assignee...")
    task = {
        "task": "Test Assignee Mapping Logic",
        "owner": "Paarth",  # Should map if "Paarth" exists in workspace
        "deadline": "Tomorrow",
        "type": "Code Review"
    }
    
    mapped_task = service.map_agent_task_to_notion(task, meeting_id="test-assignee-123")
    print(f"   Mapped Task: {mapped_task}")
    
    if mapped_task.get("assignee_id"):
        try:
            page_id = service.create_task(mapped_task)
            print(f"✅ Created Task: {page_id} (Assignee ID: {mapped_task['assignee_id']})")
        except Exception as e:
            print(f"❌ Failed to create task: {e}")
    else:
        print("⚠️ Skipping creation (No assignee resolved for 'Paarth')")

if __name__ == "__main__":
    test_assignee_mapping()
