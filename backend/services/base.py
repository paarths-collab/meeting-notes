from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class LLMService(ABC):
    """Abstract base class for Language Model services."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text based on prompt."""
        pass
    
    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Any:
        """Generate JSON response based on prompt."""
        pass


class TaskStorageService(ABC):
    """Abstract base class for task storage services (e.g., Notion, Jira)."""
    
    @abstractmethod
    def create_task(self, task: Dict[str, Any]) -> str:
        """Create a task and return its ID."""
        pass
    
    @abstractmethod
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> None:
        """Update an existing task."""
        pass
    
    @abstractmethod
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Retrieve a task by ID."""
        pass


class StateStorageService(ABC):
    """Abstract base class for meeting state storage."""
    
    @abstractmethod
    def save_state(self, meeting_id: str, state: Dict[str, Any]) -> None:
        """Save meeting state."""
        pass
    
    @abstractmethod
    def load_state(self, meeting_id: str) -> Dict[str, Any]:
        """Load meeting state by ID."""
        pass
    
    @abstractmethod
    def list_states(self) -> List[str]:
        """List all meeting IDs."""
        pass


class NotificationService(ABC):
    """Abstract base class for notification services (e.g., Slack, Email)."""
    
    @abstractmethod
    def send_notification(self, message: str, channel: str = None) -> bool:
        """Send a notification message."""
        pass
