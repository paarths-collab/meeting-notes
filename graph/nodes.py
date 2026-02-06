from typing import Dict, Any, Callable
from agents.planner_runner import GeminiPlannerAgent
from agents.reflection_autogen import AutoGenReflectorAgent
from agents.executor_agent import NotionExecutorAgent
from memory.meeting_state import MeetingState as MeetingObj
from services.base import LLMService, TaskStorageService, StateStorageService


def make_planner_node(llm_service: LLMService, mem0_service = None) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Factory for planner node."""
    def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
        print("--- PLANNER NODE ---")
        
        # 1. Retrieve Context
        transcript = state["transcript"]
        if mem0_service:
            print("🧠 Retrieving context from Mem0...")
            # Use raw transcript snippet for search query? Or just "What are relevant tasks?"
            # Better to use LLM to generating a search query, but for now, let's use the first 100 chars.
            search_query = transcript[:200]
            context = mem0_service.search_memory(search_query, user_id="team_context")
            if context:
                print(f"   Found {len(context)} relevant memories.")
                transcript = f"Context from previous meetings:\n{context}\n\nCurrent Meeting:\n{transcript}"
            else:
                print("   No relevant context found.")

        planner = GeminiPlannerAgent(llm_service)
        tasks = planner.extract_tasks(transcript)
        
        needs_reflection = any(
            t.get("owner") is None or t.get("deadline") is None
            for t in tasks
        )
        
        return {
            "tasks": tasks,
            "needs_reflection": needs_reflection
        }
    return planner_node


def make_reflection_node(llm_service: LLMService) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Factory for reflection node."""
    def reflection_node(state: Dict[str, Any]) -> Dict[str, Any]:
        print("--- REFLECTION NODE ---")
        reflector = AutoGenReflectorAgent(llm_service)
        resolved_tasks = reflector.reflect_on_tasks(state["tasks"])
        return {
            "tasks": resolved_tasks,
            "needs_reflection": False
        }
    return reflection_node


def make_executor_node(task_storage: TaskStorageService) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Factory for executor node."""
    def executor_node(state: Dict[str, Any]) -> Dict[str, Any]:
        print("--- EXECUTOR NODE ---")
        executor = NotionExecutorAgent(task_storage)
        updates = executor.execute_tasks(state["tasks"], meeting_id=state["meeting_id"])
        return updates or {}
    return executor_node


def make_summary_node(llm_service: LLMService) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Factory for summary node."""
    def summary_node(state: Dict[str, Any]) -> Dict[str, Any]:
        print("--- SUMMARY NODE ---")
        from agents.summary_agent import GeminiSummaryAgent
        agent = GeminiSummaryAgent(llm_service)
        summary = agent.generate_summary(state["transcript"], state["tasks"])
        return {"summary": summary}
    return summary_node


from services.slack_service import SlackService

def make_broadcast_node(task_storage: TaskStorageService, slack_service: SlackService, slack_channel_id: str = None) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Factory for broadcast node."""
    def broadcast_node(state: Dict[str, Any]) -> Dict[str, Any]:
        print("--- BROADCAST NODE ---")
        summary = state.get("summary", {})
        
        # 1. Notion Page (Keep existing logic or wrapping)
        if hasattr(task_storage, 'create_meeting_summary') and isinstance(summary, dict):
            try:
                page_id = state.get("notion_page_id")
                task_storage.create_meeting_summary(summary, page_id)
                print(f"✅ Created Notion summary page: {page_id}")
            except Exception as e:
                print(f"❌ Failed to create Notion summary: {e}")

        # 2. Slack Broadcast (New Agent)
        from agents.slack_broadcast_agent import SlackBroadcastAgent
        
        try:
            from graph.state import MeetingState
            # Populate Pydantic model from state dict
            if isinstance(state, MeetingState):
                pydantic_state = state
            else:
                # Hydrate from dict
                pydantic_state = MeetingState(**state) 
            
            agent = SlackBroadcastAgent(slack_service)
            # Use injected channel ID or default to #meetings
            # target_channel = slack_channel_id or "#meetings"
            
            # VERIFICATION FIX: Force DM to Test User
            import os
            target_channel = os.getenv("SLACK_TEST_USER_ID")
            print(f"⚠️ Forcing Broadcast to DM: {target_channel}")
            
            updated_pydantic_state = agent.broadcast(pydantic_state, summary_channel=target_channel)
            
            # Return updates (slack_messages)
            return {"slack_messages": updated_pydantic_state.slack_messages}
            
        except Exception as e:
            print(f"❌ Slack Broadcast failed: {e}")
            return {}

    return broadcast_node


def make_memory_node(state_storage: StateStorageService, mem0_service = None) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Factory for memory node."""
    def memory_node(state: Dict[str, Any]) -> Dict[str, Any]:
        print("--- MEMORY NODE ---")
        try:
            # Save state directly (using JSONStateStorage which handles dicts)
            state_to_save = state
            if hasattr(state, "model_dump"):
                state_to_save = state.model_dump()
            elif hasattr(state, "dict"):
                state_to_save = state.dict()
                
            state_storage.save_state(state["meeting_id"], state_to_save)
            print(f"✅ State saved for {state['meeting_id']}")
            
            # Save to Long-Term Memory (Mem0)
            if mem0_service:
                summary = state.get("summary")
                tasks = state.get("tasks", [])
                
                # Format memory text
                memory_text = ""
                if isinstance(summary, dict):
                    memory_text += f"Meeting Summary: {summary.get('overview', '')}\n"
                    if summary.get("action_items"):
                        memory_text += f"Action Items: {summary.get('action_items')}\n"
                
                if tasks:
                    task_titles = [t.get("title", "") for t in tasks if isinstance(t, dict)]
                    memory_text += f"Tasks assigned: {', '.join(task_titles)}"
                
                if memory_text:
                    mem0_service.add_memory(memory_text, user_id="team_context")
                    print("🧠 Meeting insights added to Mem0.")
                    
        except Exception as e:
            print(f"❌ Failed to save state: {e}")
        return {}
    return memory_node

