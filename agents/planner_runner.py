from typing import Any, Dict, List
from agents.base import PlannerAgent
from services.base import LLMService


SYSTEM_PROMPT = """You are a task extraction agent.
Extract actionable tasks from meeting transcripts.

For each task, identify:
- title: Short summary of the task (3-6 words)
- description: Detailed explanation of what needs to be done. Include context.
- owner: Who is responsible (if mentioned)
- deadline: When it's due (if mentioned)
- type: Category (e.g., "Feature request", "Bug fix", "Documentation")

Output ONLY valid JSON array of tasks.
"""


class GeminiPlannerAgent(PlannerAgent):
    """Planner agent using Gemini LLM service."""
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize planner with LLM service.
        
        Args:
            llm_service: LLM service for task extraction
        """
        self.llm_service = llm_service
    
    def extract_tasks(self, transcript: str) -> List[Dict[str, Any]]:
        """Extract tasks from transcript using LLM."""
        try:
            tasks = self.llm_service.generate_json(
                prompt=transcript,
                system_prompt=SYSTEM_PROMPT
            )
            
            # Handle {"tasks": [...]} wrapper
            if isinstance(tasks, dict) and "tasks" in tasks:
                tasks = tasks["tasks"]
            
            # Map 'task' to 'title' (and copy to description if missing) for robustness
            if isinstance(tasks, list):
                for t in tasks:
                    if "task" in t and "title" not in t:
                        t["title"] = t["task"]
                    if "description" not in t:
                        t["description"] = t.get("title", "")
            
            # Ensure we return a list
            if isinstance(tasks, dict):
                return [tasks]
            
            # GUARD: Ensure at least one task exists
            if not tasks:
                print("⚠️ Planner returned 0 tasks. Injecting default task.")
                return [{
                    "title": "Review Meeting Notes",
                    "description": "Review the summary and follow up on any unassigned items.",
                    "owner": "Unassigned",
                    "deadline": None,
                    "type": "General"
                }]
                
            return tasks
            
        except Exception as e:
            print(f"❌ Error extracting tasks: {e}")
            return []
