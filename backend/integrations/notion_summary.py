from typing import Dict, Any

def create_meeting_summary_page(summary: Dict[str, Any], meeting_id: str) -> None:
    """
    Create a meeting summary page in Notion.
    Wrapper compatible with user script, using ServiceContainer.
    
    Args:
        summary: Dictionary with title, overview, etc.
        meeting_id: Unique meeting identifier
    """
    # Lazy import
    from backend.core.container import ServiceContainer
    from backend.services.notion_service import NotionTaskService
    
    try:
        container = ServiceContainer.from_env()
        
        # Check if service is NotionTaskService (to access custom method)
        if hasattr(container.task_storage, 'create_meeting_summary'):
            page_id = container.task_storage.create_meeting_summary(summary, meeting_id)
            print(f"✅ Created Notion summary page: {page_id}")
        else:
            print("❌ Configured TaskStorageService does not support meeting summaries.")
            
    except Exception as e:
        print(f"❌ Failed to create Notion summary: {e}")
