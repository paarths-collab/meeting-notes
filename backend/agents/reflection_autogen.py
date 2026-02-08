from typing import Any, Dict, List
import json
import re
from backend.agents.base import ReflectorAgent
from backend.services.base import LLMService

# AutoGen v0.4+ has breaking API changes - disabled for now
# Will be re-enabled when API stabilizes
HAS_AUTOGEN = False

REFLECTION_SYSTEM_MESSAGE = """You are a reflection agent.

Your job:
- Detect missing task fields (owner, deadline)
- Ask the human ONLY what is missing
- Extract answers cleanly
- When all tasks are complete, OUTPUT ONLY VALID JSON
- After outputting valid JSON, STOP the conversation

Do not ask for feedback after JSON output.
Never guess.
"""


class AutoGenReflectorAgent(ReflectorAgent):
    """Reflection agent - currently uses simple fallback due to AutoGen API changes."""
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize reflector with LLM service.
        
        Args:
            llm_service: LLM service for reflection
        """
        self.llm_service = llm_service
    
    def reflect_on_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate tasks and fill in missing information.
        
        Currently uses simple fallback - AutoGen integration disabled
        due to breaking API changes in v0.4+.
        """
        # Simple fallback: fill in missing fields with defaults
        resolved_tasks = []
        for task in tasks:
            task_copy = dict(task)
            if not task_copy.get("owner"):
                task_copy["owner"] = "Unassigned"
            if not task_copy.get("deadline"):
                task_copy["deadline"] = "TBD"
            if not task_copy.get("type"):
                task_copy["type"] = "Task"
            resolved_tasks.append(task_copy)
        
        return resolved_tasks
    
    def _extract_last_json(self, chat_history: List[Dict]) -> List[Dict[str, Any]]:
        """Extract the last valid JSON array from chat history."""
        for msg in reversed(chat_history):
            content = msg.get("content", "")
            stripped = content.strip()
            
            if stripped.startswith("[") or stripped.startswith("{"):
                try:
                    return json.loads(stripped)
                except Exception:
                    # Try to extract JSON from within text
                    json_match = re.search(r'(\[.*\])', content, re.DOTALL)
                    if json_match:
                        try:
                            return json.loads(json_match.group(1))
                        except Exception:
                            continue
        return []

