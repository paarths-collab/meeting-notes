import os
from typing import List, Dict, Any

try:
    from mem0 import MemoryClient
except ImportError:
    MemoryClient = None

class Mem0Service:
    """Service for Long-Term Memory using Mem0 managed platform."""

    def __init__(self, api_key: str = None):
        """Initialize Mem0 client."""
        if not api_key:
            print("⚠️ MEM0_API_KEY not provided. Memory features disabled.")
            self.client = None
            return

        if MemoryClient is None:
            print("⚠️ mem0ai not installed. Memory features disabled.")
            self.client = None
            return

        # Initialize Managed Client
        try:
            self.client = MemoryClient(api_key=api_key)
            print("✅ Mem0 Managed Client initialized.")
        except Exception as e:
            print(f"❌ Failed to initialize Mem0 client: {e}")
            self.client = None

    def add_memory(self, text: str, user_id: str = "default_user", session_id: str = None, metadata: Dict[str, Any] = None):
        """Add a memory item."""
        if not self.client:
            return
            
        try:
            # Ensure metadata has user_id for filtering
            if metadata is None:
                metadata = {}
            metadata["user_id"] = user_id
            
            # Use session_id if provided
            add_kwargs = {
                "user_id": user_id,
                "metadata": metadata
            }
            if session_id:
                # Mem0 typically uses 'run_id' or 'session_id' depending on version
                # Checking SDK usually 'session_id' might be metadata key or dedicated param
                # Assuming SDK supports session_id param similar to add(..., session_id=...)
                # If not supported by older SDK, might need to be metadata
                # But recent Mem0 supports session_id
                add_kwargs["metadata"]["session_id"] = session_id

            print(f"🔍 DEBUG: Adding to Mem0: UserID='{user_id}', SessionID='{session_id}', Metadata={metadata}")
            self.client.add(text, **add_kwargs)
            print(f"🧠 Added to Mem0 for {user_id}")
        except Exception as e:
            print(f"❌ Failed to add memory: {e}")

    def search_memory(self, query: str, user_id: str = "default_user", filters: Dict[str, Any] = None, limit: int = 5):
        """Search memories."""
        if not self.client:
            return []
            
        try:
            # Mem0 requires filters in some versions
            print(f"🔍 DEBUG: Search Query='{query}', UserID='{user_id}', Filters={filters}")
            
            # Construct comprehensive filters
            search_kwargs = {"limit": limit}
            final_filters = {}
            if user_id:
                final_filters["user_id"] = user_id
            
            if filters:
                final_filters.update(filters)
            
            if final_filters:
                search_kwargs["filters"] = final_filters

            results = self.client.search(
                query, 
                user_id=user_id, 
                **search_kwargs
            )
            print(f"🔍 DEBUG: Client Search returned raw type: {type(results)}")
            
            # Mem0 API sometimes wraps results in a dict (e.g., {'results': [...]})
            if isinstance(results, dict):
                if 'results' in results:
                    results = results['results']
                elif 'data' in results:
                    results = results['data']
                else:
                    # If dict but no known key, convert to list (e.g., iterating keys?)
                    # Or maybe the dict IS the result? (Rare for search)
                    # Let's fallback to list conversion just in case
                    print(f"⚠️ Search returned unexpected dict keys: {list(results.keys())}")
                    results = [results]
            
            print(f"🔍 DEBUG: Search Results (Parsed List): {len(results)} items found.")
            
            final_results = []
            for r in results:
                # Handle dictionary
                if isinstance(r, dict):
                    # Check for 'memory' key first
                    if "memory" in r:
                        final_results.append(r.get("memory", ""))
                    # Check for 'text' key?
                    elif "text" in r:
                        final_results.append(r.get("text", ""))
                    else:
                        final_results.append(str(r))
                # Handle object (Pydantic model)
                elif hasattr(r, "memory"):
                    final_results.append(getattr(r, "memory"))
                # Handle string directly
                elif isinstance(r, str):
                    final_results.append(r)
                else:
                    final_results.append(str(r))
            
            return final_results
        except Exception as e:
            print(f"⚠️ Memory search failed: {e}")
            return []

    def get_all_memories(self, user_id: str = "default_user", filters: dict = None, limit: int = 100) -> List[str]:
        """Retrieve history."""
        if not self.client:
            return []
        try:
            # Construct filters for get_all too
            get_kwargs = {}
            if limit:
                get_kwargs["limit"] = limit
                
            # If explicit filters passed, use them. Otherwise default to user_id filter if needed.
            final_filters = {}
            if user_id:
                final_filters["user_id"] = user_id
                
            if filters:
                # Merge incoming filters (e.g. meeting_id) with user_id
                final_filters.update(filters)
            
            get_kwargs["filters"] = final_filters
            
            print(f"🔍 DEBUG: get_all_memories called with filters={final_filters}, limit={limit}")
            results = self.client.get_all(user_id=user_id, **get_kwargs)
            
            # Manual Limit enforcement if API ignores it
            if limit and isinstance(results, list) and len(results) > limit:
                results = results[:limit]
            
            # Robust parsing (same logic as search)
            final_results = []
            
            # Helper logic: handle dict wrapper
            if isinstance(results, dict):
                if 'results' in results: results = results['results']
                elif 'data' in results: results = results['data']
                else: 
                     print(f"⚠️ Get All returned unexpected dict keys: {list(results.keys())}")
                     results = [results]
            
            for r in results:
                if isinstance(r, dict):
                    if "memory" in r: final_results.append(r.get("memory", ""))
                    elif "text" in r: final_results.append(r.get("text", ""))
                    else: final_results.append(str(r))
                elif hasattr(r, "memory"):
                    final_results.append(getattr(r, "memory"))
                elif isinstance(r, str):
                    final_results.append(r)
                else:
                    final_results.append(str(r))
                    
            return final_results
        except Exception as e:
            print(f"Failed to get history: {e}")
            return []
