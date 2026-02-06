from datetime import datetime
from typing import Any, Dict
from notion_client import Client
from dateutil import parser as date_parser
from services.base import TaskStorageService


class NotionTaskService(TaskStorageService):
    """Notion-based task storage implementation."""
    
    def __init__(self, auth_token: str, database_id: str, meeting_database_id: str = None, task_database_id: str = None):
        """
        Initialize Notion service.
        
        Args:
            auth_token: Notion integration token
            database_id: Legacy database ID (for backward compatibility)
            meeting_database_id: Database ID for meetings
            task_database_id: Database ID for tasks
        """
        self.client = Client(auth=auth_token)
        self.database_id = database_id  # Legacy
        self.meeting_database_id = meeting_database_id or database_id
        self.task_database_id = task_database_id or database_id
    
    def create_task(self, task: Dict[str, Any]) -> str:
        """
        Create a task in Notion.
        
        Args:
            task: Task dictionary with keys: title, status, task_type, 
                  description, due_date, meeting_id, assignee_id (optional)
        
        Returns:
            Created page ID
        """
        properties = {
            "Task name": {
                "title": [{"text": {"content": task["title"]}}]
            },
            "Status": {
                "status": {"name": task.get("status", "Not started")}
            },
            "Due date": {
                "date": {"start": task["due_date"]} if task.get("due_date") else None
            },
            "Task type": {
                "multi_select": [{"name": task["task_type"]}] if task.get("task_type") else []
            },
            "Description": {
                "rich_text": [{"text": {"content": task["description"]}}]
                if task.get("description") else []
            },
            "Meeting ID": {
                "rich_text": [{"text": {"content": task["meeting_id"]}}]
            } if task.get("meeting_id") else None
        }
        
        # Remove None values
        properties = {k: v for k, v in properties.items() if v is not None}
        
        # Add assignee if provided
        if task.get("assignee_id"):
            properties["Assignee"] = {
                "people": [{"id": task["assignee_id"]}]
            }
        
        page = self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=properties
        )
        
        return page["id"]
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> None:
        """Update a task in Notion."""
        # Convert updates to Notion property format
        properties = {}
        
        if "title" in updates:
            properties["Task name"] = {
                "title": [{"text": {"content": updates["title"]}}]
            }
        
        if "status" in updates:
            properties["Status"] = {
                "status": {"name": updates["status"]}
            }
        
        if properties:
            self.client.pages.update(page_id=task_id, properties=properties)
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Retrieve a task from Notion."""
        page = self.client.pages.retrieve(page_id=task_id)
        
        # Extract relevant properties
        props = page.get("properties", {})
        return {
            "id": page["id"],
            "title": props.get("Task name", {}).get("title", [{}])[0].get("text", {}).get("content", ""),
            "status": props.get("Status", {}).get("status", {}).get("name", ""),
        }
    
    def get_users(self) -> Dict[str, str]:
        """
        Fetch all users from Notion and return a Name -> ID mapping.
        Cached for performance.
        """
        if not hasattr(self, "_user_cache"):
            self._user_cache = {}
            try:
                users = self.client.users.list()
                for user in users.get("results", []):
                    if user["type"] == "person":
                        name = user.get("name", "").lower()
                        self._user_cache[name] = user["id"]
            except Exception as e:
                print(f"⚠️ Failed to fetch Notion users: {e}")
        return self._user_cache

    def resolve_user_id(self, name: str) -> str:
        """Resolve a name to a Notion User ID (simple fuzzy match)."""
        if not name or name == "Unassigned":
            return None
            
        users = self.get_users()
        name_lower = name.lower()
        
        # Exact match
        if name_lower in users:
            return users[name_lower]
        
        # Partial match (e.g. "Paarth" matches "Paarth Sharma")
        for u_name, u_id in users.items():
            if name_lower in u_name or u_name in name_lower:
                return u_id
                
        return None

    def map_agent_task_to_notion(self, agent_task: Dict[str, Any], meeting_id: str = None) -> Dict[str, Any]:
        """
        Map agent task format to Notion format.
        """
        owner = agent_task.get("owner", "Unassigned")
        assignee_id = self.resolve_user_id(owner)
        
        description = agent_task.get("description", "")
        
        notion_task = {
            "title": agent_task.get("title", agent_task.get("task", "Untitled Task")),
            "status": "Not started",
            "priority": "medium", # Default
            "description": description,
            "assignee": owner, # Keep name for fallback/logging
            "assignee_id": assignee_id, # Add resolved ID
            "transcript_snippet": "" 
        }
        
        # Parse deadline
        if agent_task.get("deadline"):
            try:
                parsed_date = date_parser.parse(agent_task["deadline"], fuzzy=True).date().isoformat()
                notion_task["due_date"] = parsed_date
            except Exception:
                notion_task["due_date"] = None
        
        return notion_task
    
    def _ensure_uuid_dash(self, resource_id: str) -> str:
        """Ensure UUID has dashes (8-4-4-4-12)."""
        if not resource_id or len(resource_id) != 32 or "-" in resource_id:
            return resource_id
        return f"{resource_id[:8]}-{resource_id[8:12]}-{resource_id[12:16]}-{resource_id[16:20]}-{resource_id[20:]}"

    def create_meeting_row(self, meeting_id: int, transcript: str = "") -> str:
        """Create a row in the Meetings database."""
        # Note: ID generation now handled by caller (Agent) using get_next_daily_id
            
        try:
            response = self.client.pages.create(
                parent={"database_id": self.meeting_database_id},
                properties={
                    "Summary": {"title": [{"text": {"content": f"Meeting {meeting_id}"}}]},
                    "Raw Transcript": {"rich_text": [{"text": {"content": transcript[:2000]}}]}, 
                    "Event Date": {"date": {"start": datetime.now().isoformat()}}
                }
            )
            return response["id"]
        except Exception as e:
            print(f"❌ Failed to create meeting row: {e}")
            return ""

    def create_task(self, task: Dict[str, Any], meeting_page_id: str = None, meeting_sequence_id: int = None) -> str:
        """
        Create a task in the Tasks database.
        """
        properties = {
            # "Task ID": {"rich_text": ...}, # Omitted: User property is likely Auto-Number
            "Title": {"title": [{"text": {"content": task.get("title", "Untitled")}}]},
            "Task Description": {"rich_text": [{"text": {"content": task.get("description", "")}}]},
            "Priority Level": {"select": {"name": task.get("priority", "medium")}},
            "Status": {"status": {"name": task.get("status", "assigned").replace("assigned", "Not started")}}, 
            "Assgined Date": {"date": {"start": datetime.now().isoformat()}}
        }

        # Add Meeting Link (if we had a relation field, we'd use it here, but numeric ID is banned)
        # properties["Meeting Page"] = {"relation": [{"id": meeting_page_id}]} 

        #    properties["Meeting Page"] = {"relation": [{"id": meeting_page_id}]}  # Hypothetical name

        # Add Assignee (Person)
        if task.get("assignee_id"):
             properties["Assigned To"] = {"people": [{"id": task["assignee_id"]}]}
        
        # Add Deadline
        if task.get("due_date"):
            properties["Due Date"] = {"date": {"start": task["due_date"]}}

        # Add Transcript Snippet
        if task.get("transcript_snippet"):
             properties["Transcript Snippet"] = {"rich_text": [{"text": {"content": task["transcript_snippet"]}}]}

        try:
            page = self.client.pages.create(
                parent={"database_id": self.task_database_id},
                properties=properties
            )
            return page["id"]
        except Exception as e:
            print(f"❌ Failed to create task row: {e}")
            return ""

    def create_meeting_summary(self, summary: Dict[str, Any], page_id: str) -> str:
        """Update the Meeting Row with summary details."""
        try:
            if not page_id:
                print("⚠️ No page_id provided for summary update.")
                return ""

            # Prepare content
            summary_content = ""
            if isinstance(summary, dict):
                 summary_content = summary.get("overview", "")
            elif isinstance(summary, str):
                 summary_content = summary
            
            # Create a separate child page for the summary
            response = self.client.pages.create(
                parent={"page_id": page_id},
                properties={
                    "title": {"title": [{"text": {"content": "Meeting Summary"}}]}
                },
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": summary_content[:2000]}}]
                        }
                    }
                ]
            )
            return response["id"]
            
        except Exception as e:
            print(f"❌ Failed to create summary page: {e}")
            return ""
