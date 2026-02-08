import os
import sys
from dotenv import load_dotenv

# Add project root to path
# __file__ is backend/scripts/test_mem0_debug.py
# dirname 1 = backend/scripts
# dirname 2 = backend
# dirname 3 = project_root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.mem0_service import Mem0Service

load_dotenv()

def debug_mem0():
    print("🚀 Initializing Mem0 Service...")
    mem0 = Mem0Service(api_key=os.getenv("MEM0_API_KEY"))
    
    if not mem0.client:
        print("❌ Mem0 client failed to initialize")
        return

    # Simulate query with Dummy User ID
    user_id = "user_debug_test_1"
    
    print(f"\n🚀 Creating dummy memory for User: {user_id}...")
    try:
        mem0.add_memory(
            text="Amr advised Paarth to always double check the API response format.",
            user_id=user_id,
            metadata={"category": "test_advice"}
        )
        print("✅ Added memory.")
        
        # Wait a moment for indexing (though usually fast)
        import time
        time.sleep(2)
        
        query = "Amr advice"
        print(f"\n🔍 Searching for '{query}' (User: {user_id})...")
    
        try:
            results = mem0.search_memory(query, user_id=user_id, limit=5)
            print(f"\n✅ Search Results found: {len(results)}")
            for i, res in enumerate(results):
                print(f"Result {i+1}: {res[:100]}...") # truncate
            
            if not results:
                print("⚠️ No results found even after adding!")
            else:
                print("✅ Found newly added memory!")
                
        except Exception as e:
            print(f"❌ Error during search: {e}")
            
    except Exception as e:
        print(f"❌ Error during add: {e}")

if __name__ == "__main__":
    debug_mem0()
