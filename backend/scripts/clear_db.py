import sys
import os

# Add parent directory to path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import engine, Base
from backend.models.database import User, UserSettings, Conversation, Task

def clear_database():
    print("🗑️ Clearing Database...")
    try:
        # Drop all tables in reverse order of dependency
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped.")
        
        # Recreate tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tables recreated.")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")

if __name__ == "__main__":
    clear_database()
