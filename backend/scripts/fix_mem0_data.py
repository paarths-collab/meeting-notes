
import sys
import os
import json
from dotenv import load_dotenv

# Try loading from CWD .env
env_path = os.path.abspath(".env")
print(f"📄 Loading .env from: {env_path}")
load_dotenv(env_path, override=True)

# Debug
key = os.getenv("MEM0_API_KEY")
if key:
    print(f"🔑 MEM0_API_KEY found: {key[:5]}...")
else:
    print("❌ MEM0_API_KEY NOT FOUND in environment.")

# Adjust path for backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.services.mem0_service import Mem0Service

def fix_metadata(user_id="user_1"):
    print(f"🚀 Initializing Mem0 Service (Data Fix for {user_id})...")
    
    # Pass explicit API key! MEM0_API_KEY environment variable is loaded by dotenv
    mem0 = Mem0Service(api_key=os.getenv("MEM0_API_KEY"))
    
    if not mem0.client:
        print("❌ Mem0 Client failed to initialize. Check API Key.")
        return

    print("🔍 Fetching ALL raw memories (getting IDs)...")
    try:
        # Mem0 API requires filters even for get_all
        filters = {"user_id": user_id}
        print(f"   Using filters: {filters}")
        results = mem0.client.get_all(user_id=user_id, filters=filters)
        # mem0.client.get_all returns list of dicts with 'id', 'memory', 'metadata' etc.
        # Assuming format: [{'id': ..., 'memory': '...', 'metadata': ...}, ...]
        
        # Handle dict wrapper just in case
        if isinstance(results, dict):
            if 'results' in results: results = results['results']
            elif 'data' in results: results = results['data']
            else: results = [results]
            
        print(f"✅ Found {len(results)} raw memories.")
        
        amr_count = 0
        fixed_count = 0
        
        for mem in results:
            content = ""
            mem_id = None
            metadata = {}
            
            if isinstance(mem, dict):
                content = mem.get("memory", "") or mem.get("text", "")
                mem_id = mem.get("id")
                metadata = mem.get("metadata", {})
            elif hasattr(mem, "memory"):
                content = getattr(mem, "memory")
                mem_id = getattr(mem, "id", None)
                metadata = getattr(mem, "metadata", {})

            if "amr" in content.lower():
                print(f"\n--- Found potential target memory ---")
                print(f"ID: {mem_id}")
                print(f"Content Snippet: {content[:100]}...")
                print(f"Current Metadata: {metadata}")
                amr_count += 1
                
                # Need to update ID if it is 1, to 4.
                current_meeting_id = metadata.get("conversation_id")
                
                needs_update = False
                new_conversation_id = 4 # Target Meeting ID (Career Guidance)
                new_date = "2026-02-02"
                
                if current_meeting_id == 1:
                    print(f"⚠️ Meeting ID is 1 (Duplicate/Partial). Migrating to {new_conversation_id}...")
                    needs_update = True
                elif current_meeting_id is None:
                    print(f"⚠️ Metadata MISSING. Fixing to {new_conversation_id}...")
                    needs_update = True
                    
                if needs_update:
                    # New Metadata (preserve existing keys if safe? or overwrite?)
                    # Let's overwrite to ensure consistency.
                    new_metadata = {
                        "user_id": user_id,
                        "conversation_id": new_conversation_id, 
                        "meeting_date": new_date
                    }
                    
                    # Update
                    if mem_id:
                        try:
                            # mem0.update signature: memory_id, data (text), user_id (str), metadata (dict)
                            # Or just memory_id and kwargs?
                            # Docs say: update(memory_id, data="new text")
                            # Can we update metadata only?
                            # Usually mem0.update(memory_id, data=content, metadata=new_metadata) works.
                            print(f"   Executing UPDATE for ID: {mem_id}")
                            mem0.client.update(memory_id=mem_id, text=content, metadata=new_metadata) # user_id implied? 
                            # Often user_id is needed in update too?
                            # Let's try passing user_id just in case if client supports.
                            # mem0.client.update(memory_id, data=content, user_id=user_id, metadata=new_metadata) 
                            # Safe bet: pass memory_id and metadata.
                            
                            print("   ✅ Update Triggered.")
                            fixed_count += 1
                        except Exception as e:
                            print(f"   ❌ Update Failed: {e}")
                    else:
                         print("   ❌ Cannot update: No ID found.")
                else:
                    print("   ✅ Metadata looks OK (has conversation_id). Skipping.")
                    
        print(f"\nSummary: Found {amr_count} Amr memories. Fixed {fixed_count}.")

    except Exception as e:
        print(f"❌ Error listing/fixing memories: {e}")

if __name__ == "__main__":
    fix_metadata()
