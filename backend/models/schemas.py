"""
Pydantic Schemas for API request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# Auth
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Settings
class SettingsUpdate(BaseModel):
    notion_token: Optional[str] = None
    notion_database_id: Optional[str] = None
    notion_meeting_db_id: Optional[str] = None
    notion_task_db_id: Optional[str] = None
    slack_bot_token: Optional[str] = None
    slack_channel_id: Optional[str] = None
    gemini_api_key: Optional[str] = None


class SettingsResponse(BaseModel):
    notion_configured: bool
    slack_configured: bool
    gemini_configured: bool
    
    class Config:
        from_attributes = True


# Meeting
class MeetingInput(BaseModel):
    transcript: Optional[str] = None
    file_url: Optional[str] = None
    file_path: Optional[str] = None
    title: Optional[str] = None  # Manual title for link/file inputs
    meeting_date: Optional[str] = None  # Manual date for link/file inputs


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    assigned_to: Optional[str]  # Renamed from 'owner'
    deadline: Optional[str]
    status: str
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    title: Optional[str]
    transcript: str
    summary: Optional[str]
    key_points: List[str] = []
    decisions: List[str] = []
    created_at: datetime
    tasks: List[TaskResponse] = []
    
    class Config:
        from_attributes = True


class ConversationListItem(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime
    task_count: int
    
    class Config:
        from_attributes = True
