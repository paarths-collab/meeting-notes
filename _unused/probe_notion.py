import os
import sys
from notion_client import Client
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
load_dotenv()

token = os.getenv("NOTION_TOKEN")
db_id = os.getenv("NOTION_DATABASE_MEETING_ID") or os.getenv("NOTION_DATABASE_ID")

client = Client(auth=token)

print(f"Probing DB: {db_id}")

try:
    page = client.pages.create(
        parent={"database_id": db_id},
        properties={} 
    )
    print("✅ Created page!")
    print("PROPERTIES FOUND:")
    for key in page["properties"].keys():
        print(f"- {key}")

    # Cleanup (archive the probe page)
    client.pages.update(page_id=page["id"], archived=True)
    print("🗑 Archived probe page.")

except Exception as e:
    print(f"❌ Error: {e}")
