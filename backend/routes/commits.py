"""
Commits Router for CoreSight

Handles commit analysis endpoints with AI-powered skill extraction.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel

from utils import get_db, serialize_doc
from services.commit_service import CommitService


router = APIRouter(prefix="/api/commits", tags=["Commits"])


# Request models
class CommitCreate(BaseModel):
    commit_hash: str
    commit_message: str
    diff: str = ""
    author_email: str
    author_name: str
    repository: str = "unknown"
    branch: str = "main"
    files_changed: int = 0
    lines_added: int = 0
    lines_deleted: int = 0


# Endpoints
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_commit(commit: CommitCreate):
    """
    Process a commit with AI-powered analysis.
    
    The AI pipeline will:
    1. Extract skills and summary from the diff
    2. Search for related tasks
    3. Link to task if found
    4. Check if user profile needs updating
    5. Update user skills if new skills detected
    
    This enables automatic profile evolution based on
    developer activity.
    """
    try:
        db = get_db()
        service = CommitService(db)
        
        result = await service.process_commit(commit.model_dump())
        
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("", response_model=List[dict])
async def list_commits(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    repository: Optional[str] = Query(None, description="Filter by repository")
):
    """
    List all commits with optional filters.
    """
    try:
        db = get_db()
        service = CommitService(db)
        
        commits = await service.list_commits(user_id, repository)
        
        # Remove embeddings and diff from response
        result = []
        for commit in commits:
            commit_data = serialize_doc(commit)
            commit_data.pop("summary_embedding", None)
            commit_data.pop("diff_content", None)
            result.append(commit_data)
        
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/{commit_id}", response_model=dict)
async def get_commit(commit_id: str):
    """
    Get a specific commit by ID.
    """
    try:
        db = get_db()
        service = CommitService(db)
        
        commit = await service.get_commit(commit_id)
        
        if not commit:
            raise HTTPException(status_code=404, detail="Commit not found")
        
        commit_data = serialize_doc(commit)
        commit_data.pop("summary_embedding", None)
        
        return commit_data
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/hash/{commit_hash}", response_model=dict)
async def get_commit_by_hash(commit_hash: str):
    """
    Get a commit by its git hash.
    """
    try:
        db = get_db()
        service = CommitService(db)
        
        commit = await service.get_commit_by_hash(commit_hash)
        
        if not commit:
            raise HTTPException(status_code=404, detail="Commit not found")
        
        commit_data = serialize_doc(commit)
        commit_data.pop("summary_embedding", None)
        
        return commit_data
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/user/{user_id}", response_model=List[dict])
async def get_commits_by_user(user_id: str):
    """
    Get all commits by a specific user.
    """
    try:
        db = get_db()
        service = CommitService(db)
        
        commits = await service.get_commits_by_user(user_id)
        
        # Remove embeddings and diff from response
        result = []
        for commit in commits:
            commit_data = serialize_doc(commit)
            commit_data.pop("summary_embedding", None)
            commit_data.pop("diff_content", None)
            result.append(commit_data)
        
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
