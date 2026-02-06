from notion_client import Client
import os
from dotenv import load_dotenv

load_dotenv()

try:
    client = Client(auth=os.getenv("NOTION_TOKEN", "fake_token"))
    print("Client created successfully.")
    print(f"Client type: {type(client)}")
    
    if hasattr(client, 'databases'):
        print("client.databases exists.")
        print(f"client.databases type: {type(client.databases)}")
        print(f"Attributes of client.databases: {dir(client.databases)}")
        
        if hasattr(client.databases, 'query'):
            print("✅ client.databases.query EXISTS")
        else:
            print("❌ client.databases.query MISSING")
    else:
        print("❌ client.databases MISSING")

except Exception as e:
    print(f"Error during inspection: {e}")
