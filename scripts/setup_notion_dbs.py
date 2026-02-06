import os
import sys
from notion_client import Client
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def setup_databases():
    load_dotenv()
    
    notion_token = os.getenv("NOTION_TOKEN")
    parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")
    
    if not notion_token:
        print("❌ Error: NOTION_TOKEN not found in .env")
        return
        
    if not parent_page_id:
        print("❌ Error: NOTION_PARENT_PAGE_ID not found in .env")
        print("   Please add the page ID where you want these databases to live.")
        print("   Example: NOTION_PARENT_PAGE_ID=12345678...")
        return

    notion = Client(auth=notion_token)
    
    print(f"🚀 Creating databases under parent page: {parent_page_id}...")

    try:
        # --- 1. DETAILS DB ---
        print("\n1️⃣ Creating 'Meetings' Database...")
        meetings_db = notion.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[
                {"type": "text", "text": {"content": "Meetings"}}
            ],
            properties={
                "meeting_id": {"title": {}},
                "raw_transcript": {"rich_text": {}},
                "summary": {"rich_text": {}},
                "decisions": {"rich_text": {}},
                "status": {
                    "select": {
                        "options": [
                            {"name": "processing", "color": "yellow"},
                            {"name": "completed", "color": "green"},
                            {"name": "failed", "color": "red"}
                        ]
                    }
                }
            }
        )
        meetings_id = meetings_db["id"]
        print(f"✅ Created 'Meetings' DB: {meetings_id}")

        # --- 2. TASKS DB ---
        print("\n2️⃣ Creating 'Tasks' Database...")
        tasks_db = notion.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[
                {"type": "text", "text": {"content": "Tasks"}}
            ],
            properties={
                "task_id": {"title": {}},
                "meeting": {
                    "relation": {
                        "database_id": meetings_id,
                        "single_property": {} # Optional: Configure two-way sync if needed
                    }
                },
                "title": {"rich_text": {}},
                "description": {"rich_text": {}},
                "assignee": {"rich_text": {}},
                "deadline": {"date": {}},
                "priority": {
                    "select": {
                        "options": [
                            {"name": "low", "color": "blue"},
                            {"name": "medium", "color": "yellow"},
                            {"name": "high", "color": "red"}
                        ]
                    }
                },
                "status": {
                    "select": {
                        "options": [
                            {"name": "assigned", "color": "gray"},
                            {"name": "acknowledged", "color": "yellow"},
                            {"name": "done", "color": "green"}
                        ]
                    }
                },
                "transcript_snippet": {"rich_text": {}}
            }
        )
        tasks_id = tasks_db["id"]
        print(f"✅ Created 'Tasks' DB: {tasks_id}")
        
        print("\n🎉 SETUP COMPLETE!")
        print("\nPlease update your .env file with these IDs:")
        print(f"NOTION_MEETINGS_DB_ID={meetings_id}")
        print(f"NOTION_TASKS_DB_ID={tasks_id}")

    except Exception as e:
        print(f"\n❌ Error creating databases: {e}")

if __name__ == "__main__":
    setup_databases()
