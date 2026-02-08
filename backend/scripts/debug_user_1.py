import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.mem0_service import Mem0Service

load_dotenv()

def debug_user_1():
    print("🚀 Initializing Mem0 Service...")
    mem0 = Mem0Service(api_key=os.getenv("MEM0_API_KEY"))
    
    if not mem0.client:
        print("❌ Mem0 client failed to initialize")
        return

    user_id = "user_1"
    print(f"\n🔍 Listing ALL Memories for User: {user_id}...")
    
    try:
        memories = mem0.get_all_memories(user_id=user_id)
        if not memories:
            print(f"❌ No memories found for {user_id}.")
        
        else:
            print(f"✅ Found {len(memories)} memories.")
            amr_count = 0
            for i, mem in enumerate(memories):
                content = ""
                if isinstance(mem, dict):
                    content = mem.get("memory", "")
                elif hasattr(mem, "memory"):
                     content = getattr(mem, "memory")
                else:
                    content = str(mem)
                
                if "amr" in content.lower():
                    print(f"--- Memory {i+1} (Contains 'Amr') ---")
                    print(content)
                    # Try to find ID
                    mem_id = None
                    if isinstance(mem, dict):
                        mem_id = mem.get("id")
                    elif hasattr(mem, "id"):
                        mem_id = getattr(mem, "id")
                        
                    print(f"ID: {mem_id}")
                    
                    if isinstance(mem, dict) and "metadata" in mem:
                        print(f"Metadata: {mem['metadata']}")
                    elif hasattr(mem, "metadata"):
                        print(f"Metadata: {getattr(mem, 'metadata')}")
                    else:
                        print("No Metadata found.")
                    amr_count += 1
            
            if amr_count == 0:
                print("\n❌ No memory contains keyword 'Amr'.")
                print("Try searching for 'career guidance'?")
    
    except Exception as e:
        print(f"❌ Error during list: {e}")

if __name__ == "__main__":
    debug_user_1()
