import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.mem0_service import Mem0Service

load_dotenv()

def debug_search_user_1():
    print("🚀 Initializing Mem0 Service...")
    mem0 = Mem0Service(api_key=os.getenv("MEM0_API_KEY"))
    
    if not mem0.client:
        print("❌ Mem0 client failed to initialize")
        return

    user_id = "user_1"
    query = "Amr advice"
    print(f"\n🔍 Searching for '{query}' (User: {user_id})...")
    
    try:
        # Call search_memory directly (same as agent)
        results = mem0.search_memory(query, user_id=user_id, limit=5)
        
        if not results:
            print(f"❌ No results found for '{query}'.")
            
            # Try removing limit?
            print("Trying without limit...")
            results = mem0.search_memory(query, user_id=user_id, limit=100)
            print(f"No Limit Search: {len(results)} found.")
        
        else:
            print(f"✅ Found {len(results)} results.")
            for i, res in enumerate(results):
                print(f"--- Result {i+1} ---")
                print(res)
    
    except Exception as e:
        print(f"❌ Error during search: {e}")

if __name__ == "__main__":
    debug_search_user_1()
