from agents.planner_runner import extract_tasks

sample_transcript = """
Ravi will complete the backend integration by Friday.
I will work on the frontend UI.
Let’s review everything next Monday.
"""

tasks = extract_tasks(sample_transcript)

print("📋 Extracted Tasks:\n")
for t in tasks:
    print(t)
