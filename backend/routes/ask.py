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

router = APIRouter(prefix="/api/ask", tags=["ask"])


class AskRequest(BaseModel):
    question: str


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
    llm = GeminiLLMService(api_key=gemini_key, model_name="gemini-2.5-flash")
    
    if not mem0.client:
        raise HTTPException(status_code=500, detail="Memory service unavailable")
    
    # Search Mem0 for relevant meeting context
    user_mem_id = f"user_{current_user.id}"
    relevant_memories = mem0.search_memory(
        query=request.question,
        user_id=user_mem_id,
        limit=5
    )
    
    if not relevant_memories:
        return AskResponse(
            answer="I don't have any meeting information to answer this question. Please process some meetings first!",
            sources=[]
        )
    
    # Build context from memories
    context = "\n\n---\n\n".join(relevant_memories)
    
    # Extract source meeting titles from context
    sources = []
    for mem in relevant_memories:
        if "Meeting:" in mem:
            title_line = mem.split("\n")[0]
            title = title_line.replace("Meeting:", "").strip()
            if title and title not in sources:
                sources.append(title)
    
    # Create prompt for LLM
    prompt = f"""You are a helpful AI assistant that answers questions about past meetings.

Based on the following meeting information, answer the user's question.
Be specific, cite which meeting the information comes from, and format your answer nicely.
If the question cannot be answered from the context, say so politely.

MEETING CONTEXT:
{context}

USER QUESTION: {request.question}

Answer in a clear, helpful manner:"""

    # Get answer from LLM
    try:
        answer = llm.generate(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {e}")
    
    return AskResponse(
        answer=answer,
        sources=sources[:5]  # Limit to 5 sources
    )


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
