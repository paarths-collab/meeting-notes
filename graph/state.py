from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field

class Task(BaseModel):
    title: str
    description: str
    owner_name: Optional[str] = Field(default="Unassigned", alias="owner")
    owner_slack_id: Optional[str] = None
    deadline: Optional[str] = None
    transcript_refs: List[str] = Field(default_factory=list)
    # Fields from legacy agents (to be mapped or deprecated)
    task_type: Optional[str] = Field(None, alias="type")  
    status: str = "Not started"
    
    class Config:
        populate_by_name = True

class MeetingState(BaseModel):
    meeting_id: str
    transcript: str
    summary: Union[str, Dict[str, Any]] = ""
    tasks: List[Task] = Field(default_factory=list)
    decisions: List[str] = Field(default_factory=list)
    participants: List[str] = Field(default_factory=list)
    slack_messages: Dict[str, str] = Field(default_factory=dict)
    notion_page_id: Optional[str] = None
    needs_reflection: bool = False
    
    # LangGraph compatibility: Allow dict access
    def __getitem__(self, item):
        return getattr(self, item)
    
    def get(self, item, default=None):
        return getattr(self, item, default)
