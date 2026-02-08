from langgraph.graph import StateGraph, END
from langgraph.graph import StateGraph, END
# from functools import partial (Removed)
from backend.graph.state import MeetingState
from graph import nodes
from backend.core.container import ServiceContainer


def create_meeting_graph(container: ServiceContainer):
    """
    Create meeting graph with injected services.
    
    Args:
        container: Service container with all dependencies
    
    Returns:
        Compiled LangGraph
    """
    graph = StateGraph(MeetingState)
    
    # Create nodes with injected services using factory functions
    planner_node = nodes.make_planner_node(container.llm_service, container.mem0_service)
    reflection_node = nodes.make_reflection_node(container.llm_service)
    executor_node = nodes.make_executor_node(container.task_storage)
    summary_node = nodes.make_summary_node(container.llm_service)
    broadcast_node = nodes.make_broadcast_node(container.task_storage, container.slack_service, container.config.slack_channel_id)
    memory_node = nodes.make_memory_node(container.state_storage, container.mem0_service)
    
    # Register nodes
    graph.add_node("planner", planner_node)
    graph.add_node("reflection", reflection_node)
    graph.add_node("executor", executor_node)
    graph.add_node("summary", summary_node)
    graph.add_node("broadcast", broadcast_node)
    graph.add_node("memory", memory_node)
    
    # Entry point
    graph.set_entry_point("planner")
    
    # Conditional routing
    def route_after_planner(state):
        if state["needs_reflection"]:
            print("-> Needs Reflection")
            return "reflection"
        print("-> Straight to Execution")
        return "executor"
    
    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "reflection": "reflection",
            "executor": "executor"
        }
    )
    
    # Linear edges
    graph.add_edge("reflection", "executor")
    graph.add_edge("executor", "summary")
    graph.add_edge("summary", "broadcast")
    graph.add_edge("broadcast", "memory")
    graph.add_edge("memory", END)
    
    return graph.compile()
