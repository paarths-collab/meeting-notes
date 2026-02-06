from typing import Optional
from core.config import AppConfig
from services.llm_service import GeminiLLMService
from services.notion_service import NotionTaskService
from services.state_service import JSONStateStorage
from services.slack_service import SlackService
from services.base import LLMService, TaskStorageService, StateStorageService


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
        """Lazy load Mem0 service."""
        # Using implicit import to avoid circular dependencies if any
        if not hasattr(self, "_mem0_service"):
            from services.mem0_service import Mem0Service
            self._mem0_service = Mem0Service(api_key=self.config.mem0_api_key)
        return self._mem0_service

    
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
