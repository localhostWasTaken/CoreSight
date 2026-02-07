"""
Issues Router for CoreSight

Handles issue tracking endpoints with AI-powered analysis.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel

from utils import get_db, serialize_doc
from services.issue_service import IssueService


router = APIRouter(prefix="/api/issues", tags=["Issues"])


# Request models
class IssueCreate(BaseModel):
    title: str
    description: str = ""
    priority: str = "medium"
    source: str = "api"
    external_id: Optional[str] = None
    project_id: Optional[str] = None


class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    assigned_user_id: Optional[str] = None
    assignment_status: Optional[str] = None


# Endpoints
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_issue(issue: IssueCreate):
    """
    Create a new issue with AI-powered analysis.
    
    The AI pipeline will:
    1. Generate embeddings for the issue
    2. Check for duplicate issues
    3. Extract required skills
    4. Find matching developers
    5. Validate and assign to best match
    
    If no matching developers are found, a job requisition
    will be created automatically.
    """
    try:
        db = get_db()
        service = IssueService(db)
        
        result = await service.create_issue(issue.model_dump())
        
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("", response_model=List[dict])
async def list_issues(
    status: Optional[str] = Query(None, description="Filter by assignment status"),
    is_duplicate: Optional[bool] = Query(None, description="Filter by duplicate status")
):
    """
    List all issues with optional filters.
    """
    try:
        db = get_db()
        service = IssueService(db)
        
        issues = await service.list_issues(status, is_duplicate)
        
        # Remove embeddings from response
        result = []
        for issue in issues:
            issue_data = serialize_doc(issue)
            issue_data.pop("description_embedding", None)
            issue_data.pop("skill_embeddings", None)
            result.append(issue_data)
        
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/{issue_id}", response_model=dict)
async def get_issue(issue_id: str):
    """
    Get a specific issue by ID.
    """
    try:
        db = get_db()
        service = IssueService(db)
        
        issue = await service.get_issue(issue_id)
        
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        issue_data = serialize_doc(issue)
        issue_data.pop("description_embedding", None)
        issue_data.pop("skill_embeddings", None)
        
        return issue_data
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.patch("/{issue_id}", response_model=dict)
async def update_issue(issue_id: str, issue: IssueUpdate):
    """
    Update an issue.
    """
    try:
        db = get_db()
        service = IssueService(db)
        
        # Filter out None values
        update_data = {k: v for k, v in issue.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        success = await service.update_issue(issue_id, update_data)
        
        if not success:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        return {"message": "Issue updated successfully"}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
