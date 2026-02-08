from notion_client import Client
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("NOTION_TOKEN")
client = Client(auth=token)

print("Attributes of client.databases:")
print(dir(client.databases))
