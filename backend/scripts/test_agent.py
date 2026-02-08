import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.mem0_service import Mem0Service
from backend.services.llm_service import GeminiLLMService
from backend.agents.meeting_query_agent import MeetingQueryAgent

load_dotenv()

def test_agent():
    print("🚀 Initializing Agent Services...")
    
    # Needs valid keys
    if not os.getenv("MEM0_API_KEY") or not os.getenv("GEMINI_API_KEY"):
        print("❌ Missing API Keys in .env")
        return

    mem0 = Mem0Service(api_key=os.getenv("MEM0_API_KEY"))
    llm = GeminiLLMService(api_key=os.getenv("GEMINI_API_KEY"))
    
    agent = MeetingQueryAgent(llm_service=llm, mem0_service=mem0)
    
    user_id = "user_debug_test_1" # Dummy user
    
    # Test 1: Chit-chat
    print("\n--- Test 1: Chit Chat ---")
    q1 = "Hi, how are you?"
    ans1, src1 = agent.run(q1, user_id)
    print(f"Q: {q1}")
    print(f"A: {ans1}")
    print(f"Sources: {src1}")
    
    # Test 2: Search Query
    print("\n--- Test 2: Meeting Query ---")
    q2 = "What did Amr advise about API?"
    # It might search for "Amr advice API" or similar.
    # We added a dummy memory earlier for user_debug_test_1: "Amr advised Paarth to always double check..."
    ans2, src2 = agent.run(q2, user_id)
    print(f"Q: {q2}")
    print(f"A: {ans2}")
    print(f"Sources: {src2}")

if __name__ == "__main__":
    test_agent()
