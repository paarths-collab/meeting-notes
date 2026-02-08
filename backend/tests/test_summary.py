import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.container import ServiceContainer
from backend.agents.summary_agent import GeminiSummaryAgent

# Initialize container (loads env vars)
container = ServiceContainer.from_env()

# Initialize agent with injected service
summary_agent = GeminiSummaryAgent(container.llm_service)

# Runtime data
transcript = 'We discussed frontend and backend work. We decided to use React for frontend.'
tasks = [{'task':'Frontend UI','owner':'Paarth','deadline':'Tomorrow'}]

# Generate
print("Generating summary...")
summary = summary_agent.generate_summary(transcript, tasks)
print("\n✅ Summary Generated:")
print(summary)
