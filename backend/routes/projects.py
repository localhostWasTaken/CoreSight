"""
Projects Router for CoreSight

Handles project management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from utils import get_db, serialize_doc
from services.project_service import ProjectService


router = APIRouter(prefix="/api/projects", tags=["Projects"])


# Request models
class ProjectCreate(BaseModel):
    name: str
    jira_space_id: Optional[str] = None
    repo_url: Optional[str] = None
    total_budget: float = 0.0


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    jira_space_id: Optional[str] = None
    repo_url: Optional[str] = None
    total_budget: Optional[float] = None


# Endpoints
@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate):
    """
    Create a new project.
    """
    try:
        db = get_db()
        service = ProjectService(db)
        
        project_doc = await service.create_project(project.model_dump())
        
        return {
            "message": "Project created successfully",
            "project": serialize_doc(project_doc)
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("", response_model=List[dict])
async def list_projects():
    """
    List all projects.
    """
    try:
        db = get_db()
        service = ProjectService(db)
        
        projects = await service.list_projects()
        
        from utils import serialize_docs
        return serialize_docs(projects)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/{project_id}", response_model=dict)
async def get_project(project_id: str):
    """
    Get a specific project by ID.
    """
    try:
        db = get_db()
        service = ProjectService(db)
        
        project = await service.get_project(project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return serialize_doc(project)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.patch("/{project_id}", response_model=dict)
async def update_project(project_id: str, project: ProjectUpdate):
    """
    Update a project.
    """
    try:
        db = get_db()
        service = ProjectService(db)
        
        # Filter out None values
        update_data = {k: v for k, v in project.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        success = await service.update_project(project_id, update_data)
        
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {"message": "Project updated successfully"}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.delete("/{project_id}", response_model=dict)
async def delete_project(project_id: str):
    """
    Delete a project.
    """
    try:
        db = get_db()
        service = ProjectService(db)
        
        success = await service.delete_project(project_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {"message": "Project deleted successfully"}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/{project_id}/contributors", response_model=List[dict])
async def get_project_contributors(project_id: str):
    """
    Get all contributors for a project with their stats.
    
    Returns user info, commit count, lines added/deleted, and last commit date.
    """
    try:
        db = get_db()
        service = ProjectService(db)
        
        contributors = await service.get_project_contributors(project_id)
        
        return contributors
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

