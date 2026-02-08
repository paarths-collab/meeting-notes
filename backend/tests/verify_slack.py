import sys
import os
import codecs
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.getcwd())

from backend.services.slack_service import SlackService
from dotenv import load_dotenv

load_dotenv()

print("🚀 Starting Slack Verification...")

token = os.getenv("SLACK_BOT_TOKEN")
if not token:
    print("❌ Missing SLACK_BOT_TOKEN")
    exit(1)

slack = SlackService(token)

user_id = os.getenv("SLACK_TEST_USER_ID")
channel_id = os.getenv("SLACK_CHANNEL_ID")

if not user_id and not channel_id:
    print("❌ No Slack channel or test user configured")
    exit(1)

try:
    if user_id:
        print(f"👉 Sending DM to User ID: {user_id}")
        slack.send_dm(
            user_id=user_id,
            text="✅ Slack DM test successful!"
        )
        print("✅ DM sent successfully")
    else:
        print(f"👉 Sending message to Channel ID: {channel_id}")
        slack.send_channel_message(
            channel_id=channel_id,
            text="✅ Slack channel test successful!"
        )
        print("✅ Channel message sent successfully")

except Exception as e:
    print("❌ Slack test FAILED:", e)
    import traceback
    traceback.print_exc()
    exit(1)
