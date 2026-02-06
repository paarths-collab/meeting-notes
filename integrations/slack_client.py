from typing import Dict, Any, List

def post_meeting_summary(summary: Dict[str, Any], channel: str = None) -> bool:
    """
    Post a meeting summary to Slack.
    Wrapper around NotificationService for backward/script compatibility.
    
    Args:
        summary: Dictionary containing summary fields (title, overview, etc.)
        channel: Optional channel override
    """
    # Lazy import to avoid circular dependency
    from core.container import ServiceContainer
    
    # Initialize container (loads env config)
    try:
        container = ServiceContainer.from_env()
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return False
        
    # Format message
    message_text = _format_slack_message(summary)
    
    # Determine channel
    target_channel = channel or container.config.slack_channel_id
    if not target_channel:
        print("❌ No Slack channel configured (passed or env)")
        return False

    # Structure as blocks
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message_text
            }
        }
    ]
    
    # Send
    print(f"🚀 Sending summary to Slack channel: {target_channel}...")
    try:
        return container.slack_service.send_message(target_channel, blocks)
    except Exception as e:
        print(f"❌ Failed to send Slack message: {e}")
        return False


def _format_slack_message(summary: Dict[str, Any]) -> str:
    """Format summary dictionary into a Slack-friendly markdown string."""
    title = summary.get("title", "Meeting Summary")
    overview = summary.get("overview", "")
    key_points = summary.get("key_points", [])
    decisions = summary.get("decisions", [])
    action_items = summary.get("action_items", [])
    next_steps = summary.get("next_steps", "")
    
    lines = [
        f"*📝 {title}*",
        f"_{overview}_\n"
    ]
    
    if key_points:
        lines.append("*Key Points:*")
        for point in key_points:
            lines.append(f"• {point}")
        lines.append("")
        
    if decisions:
        lines.append("*✅ Decisions:*")
        for decision in decisions:
            lines.append(f"• {decision}")
        lines.append("")
        
    if action_items:
        lines.append("*🚀 Action Items:*")
        for item in action_items:
            lines.append(f"• {item}")
        lines.append("")
            
    if next_steps:
        lines.append(f"*⏭️ Next Steps:* {next_steps}")
        
    return "\n".join(lines)
