from typing import Any, Dict, List
from agents.base import SummaryAgent
from services.base import LLMService

class GeminiSummaryAgent(SummaryAgent):
    """Summary agent using Gemini LLM service."""
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize summary agent with LLM service.
        
        Args:
            llm_service: LLM service for summary generation
        """
        self.llm_service = llm_service
    
    def generate_summary(self, transcript: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate meeting summary."""
        prompt = self._build_summary_prompt(transcript, tasks)
        
        try:
            return self.llm_service.generate_json(prompt)
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            return {}

    def _build_summary_prompt(self, transcript: str, tasks: List[Dict[str, Any]]) -> str:
        return f"""
You are an executive meeting assistant.

Transcript:
{transcript}

Tasks:
{tasks}

Generate a meeting summary in JSON with:
- title
- overview (2–3 sentences)
- key_points (list)
- decisions (list, empty if none)
- action_items (list)
- next_steps (string)

Return ONLY valid JSON.
"""

def generate_meeting_summary(transcript: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Helper function for backward compatibility.
    Bootstraps the service container and uses GeminiSummaryAgent.
    """
    # Lazy import to avoid circular dependencies if any
    from core.container import ServiceContainer
    
    # Bootstrap container from env
    container = ServiceContainer.from_env()
    
    # Create agent
    agent = GeminiSummaryAgent(container.llm_service)
    
    # Generate
    return agent.generate_summary(transcript, tasks)
