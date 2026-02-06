from typing import Any, Dict, List
from agents.base import ExecutorAgent
from services.base import TaskStorageService


class NotionExecutorAgent(ExecutorAgent):
    """Executor agent using Notion task storage service."""
    
    def __init__(self, task_storage: TaskStorageService):
        """
        Initialize executor with task storage service.
        
        Args:
            task_storage: Task storage service (e.g., Notion)
        """
        self.task_storage = task_storage
    
    def execute_tasks(self, tasks: List[Dict[str, Any]], meeting_id: str = None) -> Dict[str, Any]:
        """
        Execute tasks by persisting to storage.
        
        Args:
            tasks: List of tasks from planner/reflector
            meeting_id: Optional meeting ID to associate
        """
        # 1. Create/Get Meeting Row first
        meeting_page_id = None
        meeting_sequence_id = None
        
        if hasattr(self.task_storage, 'create_meeting_row'):
            try:
                # Generate Sequential ID if needed (or if UUID passed)
                meeting_id_to_use = meeting_id
                
                # Check if meeting_id is non-numeric (e.g. UUID from run_meeting.py)
                is_numeric_id = False
                if meeting_id:
                     try:
                         int(meeting_id)
                         is_numeric_id = True
                     except ValueError:
                         pass
                
                if (not meeting_id or not is_numeric_id):
                    # Local Sequence ID (e.g. 2024101401)
                    from datetime import datetime
                    meeting_sequence_id = int(datetime.now().strftime('%y%m%d%H%M%S'))
                    meeting_id_to_use = meeting_sequence_id
                
                meeting_page_id = self.task_storage.create_meeting_row(meeting_id_to_use)
                print(f"✅ meeting row established: {meeting_id_to_use} -> {meeting_page_id}")
                
                # Return state update if possible (requires graph node capability)
                return {"notion_page_id": meeting_page_id}
            except Exception as e:
                import traceback
                with open("error_log.txt", "w") as f:
                    f.write(str(e))
                print(f"⚠️ Failed to create meeting row: {e}")

        for task in tasks:
            # Convert Pydantic model to dict if needed
            task_data = task
            if hasattr(task, "model_dump"):
                task_data = task.model_dump()
            elif hasattr(task, "dict"):
                 task_data = task.dict()
            
            # Map agent task format to storage format
            storage_task = self._map_task(task_data, meeting_id)
            
            try:
                # Pass both page_id (for relation if supported) and sequence_id (for number link)
                if hasattr(self.task_storage, 'create_task') and 'meeting_sequence_id' in self.task_storage.create_task.__code__.co_varnames:
                     task_id = self.task_storage.create_task(storage_task, meeting_page_id=meeting_page_id, meeting_sequence_id=meeting_sequence_id)
                else:
                     task_id = self.task_storage.create_task(storage_task, meeting_page_id=meeting_page_id)
                
                print(f"✅ Created task: {storage_task['title']} (ID: {task_id})")
            except Exception as e:
                import traceback
                with open("error_log.txt", "w") as f:
                    f.write(str(e))
                print(f"❌ Failed to create task: {storage_task['title']}: {e}")
        
        return {"notion_page_id": meeting_page_id} if meeting_page_id else {}
    
    def _map_task(self, agent_task: Dict[str, Any], meeting_id: str = None) -> Dict[str, Any]:
        """
        Map agent task format to storage service format.
        
        This delegates to the Notion service's mapping logic if available.
        """
        # Check if service has custom mapping
        if hasattr(self.task_storage, 'map_agent_task_to_notion'):
            return self.task_storage.map_agent_task_to_notion(agent_task, meeting_id)
        
        # Default mapping
        return {
            "title": agent_task.get("task"),
            "status": "Not started",
            "task_type": agent_task.get("type", "Feature request"),
            "description": f"Owner: {agent_task.get('owner', 'Unassigned')}",
            "due_date": agent_task.get("deadline"),
            "meeting_id": meeting_id
        }
