import os
import sys
from notion_client import Client
from dotenv import load_dotenv

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

load_dotenv()

token = os.getenv("NOTION_TOKEN")
db_id = os.getenv("NOTION_DATABASE_MEETING_ID") or os.getenv("NOTION_DATABASE_ID")

print(f"Checking DB: {db_id}")

client = Client(auth=token)

try:
    db = client.databases.retrieve(database_id=db_id)
    print("✅ Database retrieved!")
    
    print(f"Object Type: {db.get('object')}")
    print(f"Keys: {list(db.keys())}")
    
    if "properties" in db:
        print("\nPROPERTIES:")
        for prop_name, prop_data in db["properties"].items():
            print(f"- '{prop_name}' ({prop_data['type']})")
    else:
        print("⚠️ No 'properties' key found!")


except Exception as e:
    print(f"❌ Error: {e}")
