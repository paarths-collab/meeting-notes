from typing import List, Any
from graph.state import MeetingState, Task
from services.slack_service import SlackService

class SlackBroadcastAgent:
    """
    Agent responsible for breaking down the meeting state 
    and delivering personal DMs + public summaries.
    """
    
    def __init__(self, slack_service: SlackService):
        self.slack_service = slack_service

    def _format_summary(self, summary: Any) -> str:
        """Format summary data into a readable string."""
        if isinstance(summary, str):
            return summary
        
        if isinstance(summary, dict):
            # Try to match GeminiSummaryAgent output
            title = summary.get("title", "Meeting Summary")
            overview = summary.get("overview", "")
            key_points = summary.get("key_points", [])
            decisions = summary.get("decisions", [])
            action_items = summary.get("action_items", [])
            
            lines = [f"*{title}*\n{overview}\n"]
            
            if key_points:
                lines.append("*Key Points:*")
                lines.extend([f"• {kp}" for kp in key_points])
            
            if decisions:
                lines.append("\n*Decisions:*")
                lines.extend([f"• {d}" for d in decisions])
                
            return "\n".join(lines)
            
        return str(summary)

    def build_manager_blocks(self, state: MeetingState) -> List[Any]:
        """Constructs the high-level summary for the management channel."""
        task_list = "\n".join([
            f"• *{t.title}* → {t.owner_name} ({t.deadline or 'No Date'})"
            for t in state.tasks
        ]) or "_No tasks assigned._"

        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📝 Meeting Summary"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": self._format_summary(state.summary)
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📌 Action Items & Tasks*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": task_list
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"🆔 Meeting ID: {state.meeting_id}"
                    }
                ]
            }
        ]

    def build_employee_blocks(self, task: Task) -> List[Any]:
        """Constructs a personal 'Action Card' for an employee."""
        # Clean description for Slack
        desc = task.description.replace(f"\n\n{task.owner_name}", "").strip()
        
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"👋 *Your Action Item*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*🎯 Task*\n{task.title}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*📅 Deadline*\n{task.deadline or 'Not specified'}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🧠 Context*\n{desc}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Acknowledge ✅"},
                        "style": "primary",
                        "value": f"ack_{task.title}"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View in Notion ↗️"},
                        "url": "https://notion.so", # Placeholder, ideally link to Notion Task URL
                        "value": "view_notion"
                    }
                ]
            }
        ]

    def broadcast(self, state: MeetingState, summary_channel: str = "#meetings") -> MeetingState:
        """
        Main execution method:
        1. Resolve Slack IDs
        2. Send DMs
        3. Send Manager Summary
        """
        print("📣 Starting Slack Broadcast...")
        
        # 1. Resolve IDs & Send DMs (DISABLED IN MVP)
        # User lookup requires users:read scope which is restricted.
        # We rely on the Manager Summary to notify everyone.
        for task in state.tasks:
             print(f"   ℹ️ Task for {task.owner_name}: {task.title} (DM skipped in MVP)")

        # 2. Send Manager Summary
        try:
            self.slack_service.send_message(
                channel=summary_channel,
                blocks=self.build_manager_blocks(state)
            )
            print(f"✅ Manager summary sent to {summary_channel}")
        except Exception as e:
            print(f"❌ Failed to post summary: {e}")
            
        return state
