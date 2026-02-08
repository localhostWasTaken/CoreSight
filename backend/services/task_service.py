"""
Task Service for CoreSight

Handles task-related business logic including retrieval and updates.
"""

from typing import Dict, List, Optional, Any
from bson import ObjectId

from utils.database import DatabaseManager


class TaskService:
    """Service class for task operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID"""
        try:
            return await self.db.find_one("tasks", {"_id": ObjectId(task_id)})
        except Exception:
            return None
    
    async def get_task_by_external_id(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by external ID (e.g., Jira key)"""
        return await self.db.find_one("tasks", {"external_id": external_id})
    
    async def list_tasks(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        assignee_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List tasks with optional filters.
        
        Args:
            project_id: Filter by project
            status: Filter by status
            assignee_id: Filter by assignee
            
        Returns:
            List of matching tasks
        """
        filters = {}
        
        if project_id:
            filters["project_id"] = project_id
        if status:
            filters["status"] = status
        if assignee_id:
            filters["current_assignee_ids"] = assignee_id
        
        return await self.db.find_many("tasks", filters)
    
    async def update_task(self, task_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a task"""
        # Auto-move to in_progress if assigning user and currently todo
        if "current_assignee_ids" in update_data and update_data["current_assignee_ids"]:
            current_task = await self.get_task(task_id)
            if current_task and current_task.get("status") == "todo":
                # Only update status if not explicitly setting it to something else
                if "status" not in update_data:
                    update_data["status"] = "in_progress"

        return await self.db.update_one(
            "tasks",
            {"_id": ObjectId(task_id)},
            update_data
        )
    
    async def assign_user_to_task(self, task_id: str, user_id: str) -> bool:
        """Add a user to task assignees"""
        task = await self.get_task(task_id)
        if not task:
            return False
        
        current_assignees = task.get("current_assignee_ids", [])
        if user_id not in current_assignees:
            current_assignees.append(user_id)
        
        return await self.update_task(task_id, {"current_assignee_ids": current_assignees})
    
    async def unassign_user_from_task(self, task_id: str, user_id: str) -> bool:
        """Remove a user from task assignees"""
        task = await self.get_task(task_id)
        if not task:
            return False
        
        current_assignees = task.get("current_assignee_ids", [])
        if user_id in current_assignees:
            current_assignees.remove(user_id)
        
        return await self.update_task(task_id, {"current_assignee_ids": current_assignees})
    
    async def get_tasks_by_sprint(self, sprint_id: str) -> List[Dict[str, Any]]:
        """Get all tasks in a sprint"""
        return await self.db.find_many("tasks", {"sprint_id": sprint_id})
    
    async def get_unassigned_tasks(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tasks with no assignees"""
        filters = {"current_assignee_ids": {"$size": 0}}
        if project_id:
            filters["project_id"] = project_id
        
        return await self.db.find_many("tasks", filters)


# Convenience functions
async def get_task(db: DatabaseManager, task_id: str) -> Optional[Dict[str, Any]]:
    """Get a task by ID"""
    service = TaskService(db)
    return await service.get_task(task_id)


async def list_tasks(db: DatabaseManager) -> List[Dict[str, Any]]:
    """List all tasks"""
    service = TaskService(db)
    return await service.list_tasks()
