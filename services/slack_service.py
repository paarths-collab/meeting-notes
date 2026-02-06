from slack_sdk import WebClient

class SlackService:
    def __init__(self, token: str):
        self.client = WebClient(token=token)

    def send_dm(self, user_id: str, text: str):
        """Send a Direct Message to a user."""
        try:
            # maintain backward compatibility for "blocks" arg? 
            # The user code replaced send_dm signature to (user_id, text).
            # I should inspect if any other code calls send_dm with blocks.
            # Only `executor_agent`? No, executor uses `notification_service` (slack_client wrapper).
            # `slack_client.py` calls `send_message` (which I renamed/removed?).
            # Wait, `integrations/slack_client.py` calls `container.slack_service.send_message(target_channel, blocks)`.
            # So I MUST keep `send_message` accepting blocks!
            
            pass 
        except:
            pass

    # REVISING CONTENT TO SUPPORT BOTH USER TEST AND APP CODE
    
    def send_dm(self, user_id: str, text: str = None, blocks: list = None):
        if blocks and not text:
            text = "New DM from Meeting Agent"

        channel = self.client.conversations_open(
            users=user_id
        )["channel"]["id"]

        self.client.chat_postMessage(
            channel=channel,
            text=text,
            blocks=blocks
        )

    def send_channel_message(self, channel_id: str, text: str = None, blocks: list = None):
        self.client.chat_postMessage(
            channel=channel_id,
            text=text,
            blocks=blocks
        )

    def send_message(self, channel: str, blocks: list = None, text: str = None):
        """Legacy/Generic method for app integration."""
        if blocks and not text:
            text = "New message from Meeting Agent"
            
        self.client.chat_postMessage(
            channel=channel,
            blocks=blocks,
            text=text
        )


