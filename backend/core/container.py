from typing import Optional
from backend.core.config import AppConfig
from backend.services.llm_service import GeminiLLMService
from backend.services.notion_service import NotionTaskService
from backend.services.state_service import JSONStateStorage
from backend.services.slack_service import SlackService
from backend.services.base import LLMService, TaskStorageService, StateStorageService


class ServiceContainer:
    """
    Dependency injection container for managing service instances.
    Implements lazy initialization for services.
    """
    
    def __init__(self, config: AppConfig):
        """
        Initialize container with configuration.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self._llm_service: Optional[LLMService] = None
        self._task_storage: Optional[TaskStorageService] = None
        self._state_storage: Optional[StateStorageService] = None
        self._slack_service: Optional[SlackService] = None
    
    @property
    def llm_service(self) -> LLMService:
        """Get or create LLM service instance."""
        if self._llm_service is None:
            self._llm_service = GeminiLLMService(
                api_key=self.config.gemini_api_key,
                model_name=self.config.gemini_model
            )
        return self._llm_service
    
    @property
    def task_storage(self) -> TaskStorageService:
        """Get or create task storage service instance."""
        if self._task_storage is None:
            self._task_storage = NotionTaskService(
                auth_token=self.config.notion_token,
                database_id=self.config.notion_database_id,
                meeting_database_id=self.config.notion_database_meeting_id,
                task_database_id=self.config.notion_database_task_id
            )
        return self._task_storage

    @property
    def slack_service(self) -> SlackService:
        """Lazy load Slack service."""
        if not self._slack_service:
            if not self.config.slack_bot_token:
                print("⚠️ No Slack Bot Token configured")
            self._slack_service = SlackService(self.config.slack_bot_token or "")
        return self._slack_service

    @property
    def mem0_service(self):
        """Mem0 disabled for now due to API issues."""
        return None

    
    @property
    def state_storage(self) -> StateStorageService:
        """Get or create state storage service instance."""
        if self._state_storage is None:
            self._state_storage = JSONStateStorage(
                storage_dir=self.config.state_storage_dir
            )
        return self._state_storage
    
    @classmethod
    def from_env(cls) -> "ServiceContainer":
        """Create container from environment variables."""
        config = AppConfig.from_env()
        return cls(config)
