import mem0
import inspect
import os
from dotenv import load_dotenv

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", ".env")))

api_key = os.getenv("MEM0_API_KEY")
print(f"Mem0 Version: {mem0.__version__ if hasattr(mem0, '__version__') else 'Unknown'}")
print("Inspecting MemoryClient.update...")
try:
    c = mem0.MemoryClient(api_key=api_key)
    print(inspect.signature(c.update))
except Exception as e:
    print(f"Error inspecting: {e}")
