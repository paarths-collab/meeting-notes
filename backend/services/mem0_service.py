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

    def add_memory(self, text: str, user_id: str = "default_user", metadata: Dict[str, Any] = None):
        """Add a memory item."""
        if not self.client:
            return
            
        try:
            self.client.add(text, user_id=user_id, metadata=metadata)
            print(f"🧠 Added to Mem0 for {user_id}")
        except Exception as e:
            print(f"❌ Failed to add memory: {e}")

    def search_memory(self, query: str, user_id: str = "default_user", limit: int = 3) -> List[str]:
        """Search similar memories."""
        if not self.client:
            return []
            
        try:
            results = self.client.search(query, user_id=user_id, limit=limit)
            # Mem0 results structure: [{'memory': 'text', ...}]
            return [r.get('memory') for r in results]
        except Exception as e:
            print(f"⚠️ Memory search failed: {e}")
            return []

    def get_all_memories(self, user_id: str = "default_user") -> List[str]:
        """Retrieve history."""
        if not self.client:
            return []
        try:
            results = self.client.get_all(user_id=user_id)
            return [r.get('memory') for r in results]
        except Exception as e:
            print(f"Failed to get history: {e}")
            return []
