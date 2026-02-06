# Reflection Agent (Conflict Resolution)
# agents/reflection_agent.py

def reflect_on_tasks(tasks):
    """
    Takes planner output.
    Asks user for missing info.
    Returns completed tasks.
    """

    resolved_tasks = []

    for task in tasks:
        print("\n📝 Task detected:")
        print(f"  ➤ Task: {task['task']}")

        # Owner clarification
        if task.get("owner") is None:
            owner = input("❓ Who is responsible for this task? ")
            task["owner"] = owner.strip() if owner else None

        # Deadline clarification
        if task.get("deadline") is None:
            deadline = input("❓ What is the deadline? ")
            task["deadline"] = deadline.strip() if deadline else None

        resolved_tasks.append(task)

    return resolved_tasks
