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
        
        # Collect all user IDs to fetch names
        user_ids = set()
        for task in tasks:
            current_assignees = task.get("current_assignee_ids", [])
            for uid in current_assignees:
                if uid:
                    user_ids.add(uid)
        
        # Fetch users
        users_map = {}
        if user_ids:
            try:
                from bson import ObjectId
                # Convert string IDs to ObjectId if needed, currently assuming strings in list
                # But typically DB IDs are ObjectIds. user_ids from task doc might be strings or ObjectIds.
                # Let's handle both or assume standard string format if that's what's stored.
                # Safely trying to fetch users.
                users_cursor = await db["users"].find({"_id": {"$in": [ObjectId(uid) for uid in user_ids]}}).to_list(length=None)
                for user in users_cursor:
                    users_map[str(user["_id"])] = user.get("name", "Unknown")
            except Exception:
                # Fallback if IDs are not valid ObjectIds or other error
                pass

        # Serialize and populate details
        result = []
        for task in tasks:
            task_data = serialize_doc(task)
            task_data.pop("description_embeddings", None)
            
            # Populate assignee details
            assignee_ids = task.get("current_assignee_ids", [])
            if assignee_ids:
                # For now, just show the first assignee as the primary one, or join names
                # The frontend expectation seems to be singular 'assignee_name'
                first_id = assignee_ids[0]
                task_data["assignee_id"] = str(first_id)
                task_data["assignee_name"] = users_map.get(str(first_id), "Unknown User")
                
                # Also provide formatted list if needed later
                task_data["assignees"] = [
                    {"id": str(uid), "name": users_map.get(str(uid), "Unknown")}
                    for uid in assignee_ids
                ]
            
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
