"""
Tasks Router for CoreSight

Handles task management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from utils import get_db, serialize_doc, serialize_docs
from services.task_service import TaskService


router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get("", response_model=List[dict])
async def list_tasks(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    assignee_id: Optional[str] = Query(None, description="Filter by assignee ID")
):
    """
    List all tasks with optional filters.
    """
    try:
        db = get_db()
        service = TaskService(db)
        
        tasks = await service.list_tasks(
            project_id=project_id,
            status=status,
            assignee_id=assignee_id
        )
        
        # Remove embeddings from response
        result = []
        for task in tasks:
            task_data = serialize_doc(task)
            task_data.pop("description_embeddings", None)
            result.append(task_data)
        
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/{task_id}", response_model=dict)
async def get_task(task_id: str):
    """
    Get a specific task by ID.
    """
    try:
        db = get_db()
        service = TaskService(db)
        
        task = await service.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_data = serialize_doc(task)
        task_data.pop("description_embeddings", None)
        
        return task_data
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/external/{external_id}", response_model=dict)
async def get_task_by_external_id(external_id: str):
    """
    Get a task by its external ID (e.g., Jira key like PROJ-123).
    """
    try:
        db = get_db()
        service = TaskService(db)
        
        task = await service.get_task_by_external_id(external_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_data = serialize_doc(task)
        task_data.pop("description_embeddings", None)
        
        return task_data
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/{task_id}/assign/{user_id}", response_model=dict)
async def assign_user_to_task(task_id: str, user_id: str):
    """
    Assign a user to a task.
    """
    try:
        db = get_db()
        service = TaskService(db)
        
        success = await service.assign_user_to_task(task_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"message": "User assigned to task successfully"}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.delete("/{task_id}/assign/{user_id}", response_model=dict)
async def unassign_user_from_task(task_id: str, user_id: str):
    """
    Remove a user from a task.
    """
    try:
        db = get_db()
        service = TaskService(db)
        
        success = await service.unassign_user_from_task(task_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"message": "User unassigned from task successfully"}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/sprint/{sprint_id}", response_model=List[dict])
async def get_tasks_by_sprint(sprint_id: str):
    """
    Get all tasks in a sprint.
    """
    try:
        db = get_db()
        service = TaskService(db)
        
        tasks = await service.get_tasks_by_sprint(sprint_id)
        
        result = []
        for task in tasks:
            task_data = serialize_doc(task)
            task_data.pop("description_embeddings", None)
            result.append(task_data)
        
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/unassigned", response_model=List[dict])
async def get_unassigned_tasks(
    project_id: Optional[str] = Query(None, description="Filter by project ID")
):
    """
    Get all unassigned tasks.
    """
    try:
        db = get_db()
        service = TaskService(db)
        
        tasks = await service.get_unassigned_tasks(project_id)
        
        result = []
        for task in tasks:
            task_data = serialize_doc(task)
            task_data.pop("description_embeddings", None)
            result.append(task_data)
        
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
