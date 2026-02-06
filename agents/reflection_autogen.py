from typing import Any, Dict, List
from autogen import AssistantAgent, UserProxyAgent
import json
import re
from agents.base import ReflectorAgent
from services.base import LLMService


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
    """Reflection agent using AutoGen with pluggable LLM service."""
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize reflector with LLM service.
        
        Args:
            llm_service: LLM service for reflection
        """
        self.llm_service = llm_service
    
    def reflect_on_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate tasks and prompt for missing information.
        
        Uses AutoGen for interactive human-in-the-loop validation.
        """
        # Note: AutoGen requires specific config format
        # For now, we'll use environment-based config
        # In a full DI implementation, we'd pass this through the service
        import os
        
        config_list = [{
            "model": "gemini-2.5-flash",
            "api_key": os.environ.get("GEMINI_API_KEY"),
            "api_type": "google"
        }]
        
        assistant = AssistantAgent(
            name="ReflectionAgent",
            llm_config={
                "config_list": config_list,
                "temperature": 0,
            },
            system_message=REFLECTION_SYSTEM_MESSAGE
        )
        
        human = UserProxyAgent(
            name="Human",
            human_input_mode="ALWAYS",
            max_consecutive_auto_reply=0,
            code_execution_config=False,
        )
        
        conversation = f"""
Tasks:
{tasks}

If any task has missing owner or deadline:
Ask the human.
When resolved, output ONLY valid JSON.
"""
        
        result = human.initiate_chat(
            assistant,
            message=conversation
        )
        
        return self._extract_last_json(result.chat_history)
    
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
