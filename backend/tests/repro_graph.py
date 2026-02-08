
import sys
import os
sys.path.append(os.getcwd())

from langgraph.graph import StateGraph, END
from backend.graph.state import MeetingState, Task
from typing import Dict, Any

from backend.services.slack_service import SlackService
from backend.agents.slack_broadcast_agent import SlackBroadcastAgent

def planner_node(state):
    print("Planner Node Running")
    tasks = [{"title": "Test Task", "description": "Desc", "owner": "Paarth"}]
    return {"tasks": tasks}

def broadcast_node(state):
    print("Broadcast Node Running")
    # Mock service
    service = SlackService("") 
    agent = SlackBroadcastAgent(service)
    try:
        if isinstance(state, MeetingState):
            pydantic_state = state
        else:
            pydantic_state = MeetingState(**state)
            
        agent.broadcast(pydantic_state)
    except Exception as e:
        print(f"Broadcast Intentional Fail: {e}")
    return {}

def create_repro_graph():
    graph = StateGraph(MeetingState)
    graph.add_node("planner", planner_node)
    graph.add_node("broadcast", broadcast_node)
    graph.set_entry_point("planner")
    graph.add_edge("planner", "broadcast")
    graph.add_edge("broadcast", END)
    return graph.compile()

if __name__ == "__main__":
    app = create_repro_graph()
    try:
        initial_state = {
            "meeting_id": "123", 
            "transcript": "Test", 
            "tasks": [], 
            "summary": "", 
            "decisions": [], 
            "participants": [], 
            "slack_messages": {}
        }
        print("Invoking graph...")
        app.invoke(initial_state)
        print("Success")
    except Exception as e:
        import traceback
        traceback.print_exc()
