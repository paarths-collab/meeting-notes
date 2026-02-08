"""
Data Normalization Utilities
"""
from typing import Dict, Any, Optional

def normalize_task_data(raw_task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize raw LLM task data to match Database Schema.
    
    Handles:
    - Mapping 'owner' -> 'assigned_to'
    - Defaulting missing fields
    - Ensuring required fields are present
    - Cleaning strings
    """
    # 1. Title (Required)
    title = raw_task.get("title")
    if not title:
        # Fallback if title is missing but description exists
        desc = raw_task.get("description", "")
        title = desc[:50] + "..." if desc else "Untitled Task"
    
    # 2. Assigned To (Map from owner)
    # LLM might return 'owner', 'assignee', or 'assigned_to'
    assigned_to = (
        raw_task.get("assigned_to") or 
        raw_task.get("owner") or 
        raw_task.get("assignee") or 
        "Unassigned"
    )
    
    # 3. Description
    description = raw_task.get("description") or raw_task.get("summary") or ""
    
    # 4. Deadline
    deadline = raw_task.get("deadline") or "TBD"
    
    # 5. Status
    status = raw_task.get("status", "pending").lower()
    
    return {
        "title": str(title).strip(),
        "description": str(description).strip(),
        "assigned_to": str(assigned_to).strip(),
        "deadline": str(deadline).strip(),
        "status": status
    }
