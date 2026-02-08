import sys
import os
sys.path.append(os.getcwd())

from backend.core.container import ServiceContainer

def verify_config():
    """Verify dual-database configuration is loaded correctly."""
    print("🔍 Verifying Notion Database Configuration...\n")
    
    try:
        container = ServiceContainer.from_env()
        config = container.config
        
        print("✅ Config loaded successfully")
        print(f"   NOTION_DATABASE_ID (Legacy): {config.notion_database_id}")
        print(f"   NOTION_DATABASE_MEETING_ID: {config.notion_database_meeting_id}")
        print(f"   NOTION_DATABASE_TASK_ID: {config.notion_database_task_id}")
        
        # Verify service initialization
        service = container.task_storage
        print(f"\n✅ NotionTaskService initialized")
        print(f"   Meeting DB: {service.meeting_database_id}")
        print(f"   Task DB: {service.task_database_id}")
        
        # Test connection and dump schema
        print(f"\n🔗 Testing Notion API connection...")
        try:
            # Query meeting database
            meeting_db = service.client.databases.retrieve(service.meeting_database_id)
            print("   Available Keys:", list(meeting_db.keys()))
            print(f"✅ Meeting DB '{meeting_db['title'][0]['plain_text']}' accessible")
            print("   Schema Keys:", list(meeting_db['properties'].keys()))
            
            # Query task database
            task_db = service.client.databases.retrieve(service.task_database_id)
            print("   Task DB Available Keys:", list(task_db.keys()))
            if 'properties' in task_db:
                print("   Task DB Schema Keys:", list(task_db['properties'].keys()))
            else:
                print("   ⚠️ 'properties' missing from Task DB response")
            
            # Find Title Property
            for name, prop in task_db['properties'].items():
                if prop['type'] == 'title':
                    print(f"   👉 Title Property for Tasks is: '{name}'")
                    
            print("\n🎉 All checks passed! Dual-database architecture is ready.")
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")

if __name__ == "__main__":
    verify_config()
