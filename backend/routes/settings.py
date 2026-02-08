"""
Settings Routes - User API credentials management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.database import User, UserSettings
from backend.models.schemas import SettingsUpdate, SettingsResponse
from backend.auth import get_current_user

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/", response_model=SettingsResponse)
def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's settings status."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    if not settings:
        return SettingsResponse(
            notion_configured=False,
            slack_configured=False,
            gemini_configured=False
        )
    
    return SettingsResponse(
        notion_configured=bool(settings.notion_token),
        slack_configured=bool(settings.slack_bot_token),
        gemini_configured=bool(settings.gemini_api_key)
    )


@router.put("/")
def update_settings(
    settings_data: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's API credentials."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    
    # Update only provided fields
    update_data = settings_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # Ignore None, empty strings, and masked values (***)
        if value is not None and value != "" and not str(value).startswith("***"):
            setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return {"message": "Settings updated successfully"}


@router.get("/full")
def get_full_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get full settings (masked)."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    if not settings:
        return {}
    
    def mask(value):
        if not value:
            return None
        return value[:8] + "..." if len(value) > 8 else "***"
    
    return {
        "notion_token": mask(settings.notion_token),
        "notion_database_id": settings.notion_database_id,
        "notion_meeting_db_id": settings.notion_meeting_db_id,
        "notion_task_db_id": settings.notion_task_db_id,
        "slack_bot_token": mask(settings.slack_bot_token),
        "slack_channel_id": settings.slack_channel_id,
        "gemini_api_key": mask(settings.gemini_api_key),
    }
