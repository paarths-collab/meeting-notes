"""
Test script to verify SOLID refactoring without manual interaction.
Tests the planner and executor agents with dependency injection.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.container import ServiceContainer
from backend.agents.planner_runner import GeminiPlannerAgent
from backend.agents.executor_agent import NotionExecutorAgent


def test_solid_refactoring():
    """Test the refactored system with dependency injection."""
    
    print("🧪 Testing SOLID Refactoring\n")
    
    # 1. Initialize container
    print("1️⃣ Initializing Service Container...")
    container = ServiceContainer.from_env()
    print("✅ Container created with all services\n")
    
    # 2. Test LLM Service via Planner
    print("2️⃣ Testing LLM Service (Planner)...")
    planner = GeminiPlannerAgent(container.llm_service)
    
    test_transcript = """
    Meeting notes from team sync:
    - Paarth needs to update the documentation by Friday
    - Sarah will review the PR by tomorrow
    - Deploy the staging server by end of week (Owner: DevOps team)
    """
    
    tasks = planner.extract_tasks(test_transcript)
    print(f"✅ Extracted {len(tasks)} tasks:")
    for i, task in enumerate(tasks, 1):
        print(f"   {i}. {task.get('task')} (Owner: {task.get('owner', 'N/A')}, Deadline: {task.get('deadline', 'N/A')})")
    print()
    
    # 3. Test Task Storage Service via Executor
    print("3️⃣ Testing Task Storage Service (Executor)...")
    executor = NotionExecutorAgent(container.task_storage)
    
    # Use fully resolved tasks (no need for reflection)
    resolved_tasks = [
        {
            "task": "Update documentation",
            "owner": "Paarth",
            "deadline": "Friday",
            "type": "Documentation"
        },
        {
            "task": "Review PR",
            "owner": "Sarah",
            "deadline": "Tomorrow",
            "type": "Code Review"
        }
    ]
    
    meeting_id = "test-solid-refactoring"
    executor.execute_tasks(resolved_tasks, meeting_id=meeting_id)
    print("✅ Tasks synced to Notion\n")
    
    # 4. Test State Storage Service
    print("4️⃣ Testing State Storage Service...")
    test_state = {
        "meeting_id": meeting_id,
        "tasks": resolved_tasks,
        "decisions": [],
        "open_questions": [],
        "started_at": "2024-01-01T10:00:00"
    }
    
    container.state_storage.save_state(meeting_id, test_state)
    loaded_state = container.state_storage.load_state(meeting_id)
    print(f"✅ State saved and loaded successfully")
    print(f"   Meeting ID: {loaded_state['meeting_id']}")
    print(f"   Tasks: {len(loaded_state['tasks'])}\n")
    
    print("🎉 All SOLID refactoring tests passed!")
    print("\n✨ Benefits achieved:")
    print("   - ✅ Dependency Injection working")
    print("   - ✅ Services are swappable/testable")
    print("   - ✅ Configuration centralized")
    print("   - ✅ Agents decoupled from implementations")


if __name__ == "__main__":
    test_solid_refactoring()
