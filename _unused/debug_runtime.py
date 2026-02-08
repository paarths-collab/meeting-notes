import services.notion_service
import services.slack_service
import inspect

print("--- RUNTIME SOURCE CHECK ---")
print(f"Notion Service File: {services.notion_service.__file__}")
print(f"Slack Service File: {services.slack_service.__file__}")

try:
    src = inspect.getsource(services.notion_service.NotionTaskService)
    if "get_next_daily_id" in src:
        print("❌ CRITICAL: get_next_daily_id IS PRESENT in runtime Service!")
    else:
        print("✅ Notion Service is CLEAN.")
except Exception as e:
    print(f"Error inspecting Notion: {e}")

try:
    src_slack = inspect.getsource(services.slack_service.SlackService)
    if "resolve_user" in src_slack:
       print("❌ CRITICAL: resolve_user IS PRESENT in runtime Slack!")
    else:
       print("✅ Slack Service is CLEAN.")
except Exception as e:
    print(f"Error inspecting Slack: {e}")
