from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Agent(ABC):
    """Base class for all agents in the system."""
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """Process input and return output."""
        pass


class PlannerAgent(ABC):
    """Interface for planner agents that extract tasks from transcripts."""
    
    @abstractmethod
    def extract_tasks(self, transcript: str) -> List[Dict[str, Any]]:
        """Extract actionable tasks from a transcript."""
        pass


class ReflectorAgent(ABC):
    """Interface for reflection agents that validate and fill missing task information."""
    
    @abstractmethod
    def reflect_on_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate tasks and prompt for missing information."""
        pass


class ExecutorAgent(ABC):
    """Interface for executor agents that persist tasks to external systems."""
    
    @abstractmethod
    def execute_tasks(self, tasks: List[Dict[str, Any]], meeting_id: str = None) -> None:
        """Execute tasks by persisting them to an external system."""
        pass


class SummaryAgent(ABC):
    """Interface for summary agents that generate meeting summaries."""
    
    @abstractmethod
    def generate_summary(self, transcript: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a structured summary from transcript and extracted tasks."""
        pass
