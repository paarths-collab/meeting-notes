import os
import sys
from typing import TypedDict, List, Annotated
import operator
from langgraph.graph import StateGraph, END

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agents.planner_runner import extract_tasks_from_transcript
from backend.agents.reflection_autogen import run_reflection
from backend.agents.executor_agent import execute_tasks
from memory.meeting_state import MeetingState
from memory.storage import save_meeting_state, load_meeting_state

# --- STATE DEFINITION ---
class AgentState(TypedDict):
    meeting_id: str
    transcript: str
    tasks: Annotated[List[dict], operator.add]  # Append tasks
    original_tasks: List[dict] # Intermediate storage

# --- NODES ---

def planner_node(state: AgentState):
    print("\n🤔 PLANNER: Analyzing transcript...")
    transcript = state["transcript"]
    # 1. Plan
    raw_tasks = extract_tasks_from_transcript(transcript)
    return {"original_tasks": raw_tasks}

def reflector_node(state: AgentState):
    print("\n🧐 REFLECTOR: Checking for missing details...")
    tasks = state.get("original_tasks", [])
    if not tasks:
        return {"tasks": []}
    
    # 2. Reflect (Human-in-the-loop if needed)
    resolved_tasks = run_reflection(tasks)
    return {"tasks": resolved_tasks}

def executor_node(state: AgentState):
    print("\n🚀 EXECUTOR: Syncing to Notion...")
    tasks = state.get("tasks", [])
    meeting_id = state.get("meeting_id")
    
    if tasks:
        # 3. Execute
        execute_tasks(tasks, meeting_id=meeting_id)
    
    return {}

def memory_node(state: AgentState):
    print("\n🧠 MEMORY: Saving state...")
    meeting_id = state.get("meeting_id")
    tasks = state.get("tasks", [])
    
    if meeting_id:
        try:
            current_state = load_meeting_state(meeting_id)
        except FileNotFoundError:
            current_state = MeetingState()
            current_state.meeting_id = meeting_id
        
        current_state.add_tasks(tasks)
        save_meeting_state(current_state)
    
    return {}

# --- GRAPH CONSTRUCTION ---

def create_graph():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("reflector", reflector_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("memory", memory_node)

    # Set Entry Point
    workflow.set_entry_point("planner")

    # Add Edges
    workflow.add_edge("planner", "reflector")
    workflow.add_edge("reflector", "executor")
    workflow.add_edge("executor", "memory")
    workflow.add_edge("memory", END)

    # Compile
    return workflow.compile()

if __name__ == "__main__":
    # Test Run
    graph = create_graph()
    
    test_transcript = "We need to update the website homepage by Friday. Paarth will handle it."
    test_id = "test-graph-run"
    
    print("--- STARTING GRAPH ---")
    result = graph.invoke({
        "meeting_id": test_id,
        "transcript": test_transcript,
        "tasks": [],
        "original_tasks": []
    })
    print("--- FINISHED GRAPH ---")
    print(result)
