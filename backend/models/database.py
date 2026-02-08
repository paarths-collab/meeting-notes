"""
Database Models - SQLAlchemy

Stores users, credentials, conversations, and tasks.
"""
print("🔄 LOADING CLEAN TASK MODEL (assigned_to)")
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User account for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    conversations = relationship("Conversation", back_populates="user")


class UserSettings(Base):
    """User's API credentials for Notion, Slack, Gemini."""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Notion
    notion_token = Column(String(255), nullable=True)
    notion_database_id = Column(String(255), nullable=True)
    notion_meeting_db_id = Column(String(255), nullable=True)
    notion_task_db_id = Column(String(255), nullable=True)
    
    # Slack
    slack_bot_token = Column(String(255), nullable=True)
    slack_channel_id = Column(String(255), nullable=True)
    
    # Gemini
    gemini_api_key = Column(String(255), nullable=True)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="settings")


class Conversation(Base):
    """Meeting conversation with transcript."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)  # Required
    transcript = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)  # Required
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="conversations")
    tasks = relationship("Task", back_populates="conversation")


class Task(Base):
    """Task extracted from a conversation."""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(String(255), nullable=True)  # Renamed from 'owner'
    deadline = Column(String(100), nullable=True)
    status = Column(String(50), default="pending")
    notion_page_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="tasks")
