"""
Ask Routes - Q&A over past meetings using Mem0 semantic search
"""
import os
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.database import User, UserSettings
from backend.auth import get_current_user
from backend.services.mem0_service import Mem0Service
from backend.services.llm_service import GeminiLLMService

from backend.agents.meeting_query_agent import MeetingQueryAgent

router = APIRouter(prefix="/api/ask", tags=["ask"])


class AskRequest(BaseModel):
    question: str
    meeting_id: Optional[int] = None
    date: Optional[str] = None  # YYYY-MM-DD


class AskResponse(BaseModel):
    answer: str
    sources: list[str]  # Meeting titles used as context


@router.post("", response_model=AskResponse)
def ask_question(
    request: AskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a question about past meetings using Mem0 semantic search."""
    
    # Get user settings for Gemini key
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    gemini_key = settings.gemini_api_key if settings else None
    gemini_key = gemini_key or os.getenv("GEMINI_API_KEY")
    
    if not gemini_key:
        raise HTTPException(status_code=400, detail="Please configure your Gemini API key in settings")
    
    # Initialize services
    mem0 = Mem0Service(api_key=os.getenv("MEM0_API_KEY"))
    llm = GeminiLLMService(
        api_key=gemini_key, 
        model_name=os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    )
    
    if not mem0.client:
        raise HTTPException(status_code=500, detail="Memory service unavailable")
    
    # Compute filters and context
    user_mem_id = f"user_{current_user.id}"
    filters = None
    if request.meeting_id:
        filters = {"metadata": {"conversation_id": request.meeting_id}}
    elif request.date:
        filters = {"metadata": {"meeting_date": request.date}}
        
    try:
        # Initialize and run agent
        agent = MeetingQueryAgent(llm_service=llm, mem0_service=mem0)
        answer, sources = agent.run(
            query=request.question,
            user_id=user_mem_id,
            filters=filters
        )
        
        return AskResponse(
            answer=answer,
            sources=sources[:5]
        )
        
    except Exception as e:
        print(f"❌ Agent error: {e}")
        # Fallback to simple answer?
        raise HTTPException(status_code=500, detail=f"Agent failed to process request: {e}")


@router.get("/memories")
def get_memory_count(
    current_user: User = Depends(get_current_user)
):
    """Get count of stored memories for debugging."""
    mem0 = Mem0Service(api_key=os.getenv("MEM0_API_KEY"))
    
    if not mem0.client:
        return {"count": 0, "status": "Mem0 not configured"}
    
    user_mem_id = f"user_{current_user.id}"
    memories = mem0.get_all_memories(user_id=user_mem_id)
    
    return {
        "count": len(memories),
        "status": "ok"
    }
