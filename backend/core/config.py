import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class AppConfig:
    """Application configuration."""
    
    # API Keys
    gemini_api_key: str
    notion_token: str
    
    # Service Configuration
    notion_database_id: str  # Legacy single DB (kept for compatibility)
    notion_database_meeting_id: Optional[str] = None
    notion_database_task_id: Optional[str] = None
    gemini_model: str = "gemini-1.5-flash"
    slack_bot_token: Optional[str] = None
    slack_channel_id: Optional[str] = None
    mem0_api_key: Optional[str] = None
    
    # Storage Configuration
    state_storage_dir: str = "memory/sessions"
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables."""
        load_dotenv()
        
        # Required fields
        gemini_key = os.getenv("GEMINI_API_KEY")
        notion_token = os.getenv("NOTION_TOKEN")
        notion_db = os.getenv("NOTION_DATABASE_ID")
        
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        if not notion_token:
            raise ValueError("NOTION_TOKEN environment variable is required")
        if not notion_db:
            raise ValueError("NOTION_DATABASE_ID environment variable is required")
        
        return cls(
            gemini_api_key=gemini_key,
            notion_token=notion_token,
            notion_database_id=notion_db,
            notion_database_meeting_id=os.getenv("NOTION_DATABASE_MEETING_ID"),
            notion_database_task_id=os.getenv("NOTION_DATABASE_TASK_ID"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
            slack_bot_token=os.getenv("SLACK_BOT_TOKEN"),
            slack_channel_id=os.getenv("SLACK_CHANNEL_ID"),
            mem0_api_key=os.getenv("MEM0_API_KEY"),
            state_storage_dir=os.getenv("STATE_STORAGE_DIR", "memory/sessions")
        )
