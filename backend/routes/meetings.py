"""
Meetings Routes - Process meetings and get history
"""
import sys
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Add project root to path for existing services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database import get_db
from backend.models.database import User, UserSettings, Conversation, Task
from backend.models.schemas import MeetingInput, ConversationResponse, ConversationListItem, TaskResponse
from backend.auth import get_current_user

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


def get_user_services(settings: UserSettings):
    """Create service instances with user's credentials."""
    from backend.services.llm_service import GeminiLLMService
    from backend.services.notion_service import NotionTaskService
    from backend.services.slack_service import SlackService
    
    # Build config from user settings
    llm = GeminiLLMService(
        api_key=settings.gemini_api_key or os.getenv("GEMINI_API_KEY"),
        model_name="gemini-2.5-flash"
    )
    
    notion = None
    if settings.notion_token:
        notion = NotionTaskService(
            auth_token=settings.notion_token,
            database_id=settings.notion_database_id or "",
            meeting_database_id=settings.notion_meeting_db_id or "",
            task_database_id=settings.notion_task_db_id or ""
        )
        print("✅ Notion service initialized")
    else:
        print("⚠️ Notion not configured (no token in settings)")
    
    slack = None
    if settings.slack_bot_token:
        slack = SlackService(settings.slack_bot_token)
        print(f"✅ Slack service initialized (channel: {settings.slack_channel_id})")
    else:
        print("⚠️ Slack not configured (no bot token in settings)")
    
    return llm, notion, slack


@router.post("/process", response_model=ConversationResponse)
def process_meeting(
    meeting: MeetingInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process a meeting transcript and extract tasks."""
    # Get user settings
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        raise HTTPException(status_code=400, detail="Please configure your settings first")
    
    transcript = meeting.transcript
    
    # Check for file inputs
    if not transcript:
        from backend.utils.content import get_content_from_url, get_content_from_file
        
        if meeting.file_url:
            transcript = get_content_from_url(meeting.file_url)
        elif meeting.file_path:
            transcript = get_content_from_file(meeting.file_path)
            
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript, file URL, or file path is required")
    
    # Get services with user's credentials
    llm, notion, slack = get_user_services(settings)
    
    # Extract tasks using planner
    try:
        from backend.agents.planner_runner import GeminiPlannerAgent
        planner = GeminiPlannerAgent(llm)
        tasks_data = planner.extract_tasks(transcript)
    except Exception as e:
        print(f"⚠️ Task extraction failed (likely quota limit): {e}")
        tasks_data = []
    
    # Fill in missing fields
    for task in tasks_data:
        if not task.get("owner"):
            task["owner"] = "Unassigned"  # LLM uses 'owner', we'll map to 'assigned_to' when saving
        if not task.get("deadline"):
            task["deadline"] = "TBD"
    
    # Generate summary
    from backend.agents.summary_agent import GeminiSummaryAgent
    summary_agent = GeminiSummaryAgent(llm)
    summary = summary_agent.generate_summary(transcript, tasks_data)
    
    # Validate summary generation - MUST have valid output
    if not summary or not isinstance(summary, dict):
        raise HTTPException(
            status_code=422, 
            detail="Summary generation failed. Meeting was NOT saved to database. Please try again."
        )
    
    summary_text = summary.get("overview", "")
    # Use manual title if provided, otherwise fall back to LLM-generated
    title = meeting.title or summary.get("title", "") or (summary_text[:100] if summary_text else "")
    
    # Require title and summary
    if not title or not summary_text:
        raise HTTPException(
            status_code=422,
            detail="Could not generate title or summary. Meeting was NOT saved. Please provide a clearer transcript or enter a title manually."
        )
    
    # Check for duplicate transcript (same user, same content)
    import hashlib
    transcript_hash = hashlib.md5(transcript.encode()).hexdigest()
    existing = db.query(Conversation).filter(
        Conversation.user_id == current_user.id,
        Conversation.transcript == transcript
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"This meeting transcript already exists (ID: {existing.id}). Duplicate not added."
        )
    
    # Save conversation to DB (now with validated data)
    from datetime import datetime
    # Use manual date if provided, otherwise use current time
    if meeting.meeting_date:
        try:
            created_at = datetime.fromisoformat(meeting.meeting_date.replace('Z', '+00:00'))
        except:
            created_at = datetime.utcnow()
    else:
        created_at = datetime.utcnow()
        
    conversation = Conversation(
        user_id=current_user.id,
        title=title[:100],
        transcript=transcript,
        summary=summary_text,
        created_at=created_at
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    # Save tasks to DB
    from backend.utils.normalization import normalize_task_data
    
    db_tasks = []
    for task_data in tasks_data:
        # Normalize and sanitize task data
        clean_task = normalize_task_data(task_data)
        
        # Skip if title is empty even after normalization
        if not clean_task["title"]:
            continue
            
        task = Task(
            conversation_id=conversation.id,
            title=clean_task["title"],
            description=clean_task["description"],
            assigned_to=clean_task["assigned_to"],
            deadline=clean_task["deadline"],
            status=clean_task["status"]
        )
        db.add(task)
        db_tasks.append(task)
    
    db.commit()
    
    # Store meeting in Mem0 for semantic search/Q&A
    try:
        from backend.services.mem0_service import Mem0Service
        mem0 = Mem0Service(api_key=os.getenv("MEM0_API_KEY"))
        if mem0.client:
            # Create structured memory content
            task_list = "\n".join([f"- {t.title} (Assigned: {t.assigned_to}, Due: {t.deadline})" for t in db_tasks])
            key_points_text = "\n".join([f"- {kp}" for kp in summary.get("key_points", [])]) if isinstance(summary, dict) else ""
            decisions_text = "\n".join([f"- {d}" for d in summary.get("decisions", [])]) if isinstance(summary, dict) else ""
            
            memory_content = f"""Meeting: {title}
Date: {conversation.created_at.strftime('%Y-%m-%d')}
Summary: {summary_text}

Key Points:
{key_points_text}

Decisions Made:
{decisions_text}

Action Items:
{task_list}

Full Transcript:
{transcript[:3000]}"""  # Limit transcript length for Mem0
            
            mem0.add_memory(
                text=memory_content,
                user_id=f"user_{current_user.id}",
                metadata={
                    "conversation_id": conversation.id,
                    "title": title,
                    "date": conversation.created_at.isoformat()
                }
            )
            print(f"🧠 Meeting stored in Mem0 for user {current_user.id}")
    except Exception as e:
        print(f"⚠️ Mem0 storage failed: {e}")
    
    # Create tasks in Notion if configured
    if notion:
        try:
            # First create meeting row
            meeting_page_id = notion.create_meeting_row(conversation.id, transcript)
            if meeting_page_id:
                # Add summary as child page
                notion.create_meeting_summary(summary, meeting_page_id)
            
            # Create tasks
            for task in db_tasks:
                # Map task to Notion format (resolves assignee)
                notion_task = notion.map_agent_task_to_notion({
                    "title": task.title,
                    "description": task.description,
                    "owner": task.assigned_to,  # Use assigned_to for Notion
                    "deadline": task.deadline,
                    "status": "Not started",
                    "task_type": "Action Item"
                })
                
                # Create in Tasks setup
                notion.create_task(notion_task, meeting_page_id)
                
        except Exception as e:
            print(f"Notion error: {e}")
    
    # Send Slack notification if configured
    if slack and settings.slack_channel_id:
        try:
            # Build Block Kit message
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📝 New Meeting Processed",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{summary_text[:200]}...*" if len(summary_text) > 200 else f"*{summary_text}*"
                    }
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📋 Extracted Tasks ({len(db_tasks)})*"
                    }
                }
            ]
            
            # Add tasks (max 10 to avoid limit)
            for i, task in enumerate(db_tasks[:10]):
                icon = "🟢" if task.status == "pending" else "⚪"
                deadline = f" (Due: {task.deadline})" if task.deadline and task.deadline != "TBD" else ""
                assignee = f" invalid-user" if task.assigned_to == "Unassigned" else f" <@{task.assigned_to}>" # basic fallback
                # Better assignee formatting if we had Slack IDs, for now just name
                assignee_display = f"👤 {task.assigned_to}"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{icon} *{task.title}*\n{assignee_display}{deadline}"
                    }
                })
                
            if len(db_tasks) > 10:
                blocks.append({
                    "type": "context",
                    "elements": [{"type": "mrkdwn", "text": f"...and {len(db_tasks) - 10} more tasks"}]
                })
                
            slack.send_message(settings.slack_channel_id, blocks=blocks, text="New Meeting Processed")
        except Exception as e:
            print(f"Slack error: {e}")
    
    # Build response with summary fields
    return {
        "id": conversation.id,
        "title": conversation.title,
        "transcript": conversation.transcript,
        "summary": summary_text,
        "key_points": summary.get("key_points", []) if isinstance(summary, dict) else [],
        "decisions": summary.get("decisions", []) if isinstance(summary, dict) else [],
        "created_at": conversation.created_at,
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "assigned_to": t.assigned_to,
                "deadline": t.deadline,
                "status": t.status
            } for t in db_tasks
        ]
    }


@router.get("/conversations", response_model=List[ConversationListItem])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all conversations for current user."""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at.desc()).all()
    
    return [
        ConversationListItem(
            id=c.id,
            title=c.title,
            created_at=c.created_at,
            task_count=len(c.tasks)
        )
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation with tasks."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation
