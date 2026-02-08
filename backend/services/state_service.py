import json
import os
from datetime import datetime
from typing import Any, Dict, List
from backend.services.base import StateStorageService


class JSONStateStorage(StateStorageService):
    """JSON file-based state storage implementation."""
    
    def __init__(self, storage_dir: str = "memory/sessions"):
        """
        Initialize JSON storage.
        
        Args:
            storage_dir: Directory to store session files
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def save_state(self, meeting_id: str, state: Dict[str, Any]) -> None:
        """Save meeting state to JSON file."""
        path = os.path.join(self.storage_dir, f"{meeting_id}.json")
        
        # Ensure datetime objects are serialized
        serializable_state = self._prepare_for_json(state)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serializable_state, f, indent=2)
    
    def load_state(self, meeting_id: str) -> Dict[str, Any]:
        """Load meeting state from JSON file."""
        path = os.path.join(self.storage_dir, f"{meeting_id}.json")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Meeting {meeting_id} not found")
        
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        # Parse datetime strings back
        if "started_at" in state and isinstance(state["started_at"], str):
            state["started_at"] = datetime.fromisoformat(state["started_at"])
        
        return state
    
    def list_states(self) -> List[str]:
        """List all meeting IDs."""
        if not os.path.exists(self.storage_dir):
            return []
        
        files = os.listdir(self.storage_dir)
        return [f.replace(".json", "") for f in files if f.endswith(".json")]
    
    def _prepare_for_json(self, obj: Any) -> Any:
        """Recursively convert non-JSON-serializable objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._prepare_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._prepare_for_json(item) for item in obj]
        return obj
