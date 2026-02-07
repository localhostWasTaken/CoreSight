"""
Project Service for CoreSight

Handles project-related business logic including CRUD operations.
"""

from typing import Dict, List, Optional, Any
from bson import ObjectId

from utils.database import DatabaseManager


class ProjectService:
    """Service class for project operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    async def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            project_data: Project data including name, repo_url, etc.
            
        Returns:
            Created project document with ID
        """
        # Check if project already exists
        existing = await self.db.find_one("projects", {"name": project_data["name"]})
        if existing:
            return existing  # Return existing project instead of raising error
        
        project_doc = {
            "name": project_data["name"],
            "repo_url": project_data.get("repo_url"),
            "total_budget": project_data.get("total_budget", 0.0),
        }
        
        project_id = await self.db.insert_one("projects", project_doc)
        project_doc["_id"] = project_id
        
        return project_doc
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a project by ID"""
        try:
            return await self.db.find_one("projects", {"_id": ObjectId(project_id)})
        except Exception:
            return None
    
    async def get_project_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a project by name"""
        return await self.db.find_one("projects", {"name": name})
    
    async def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        return await self.db.find_many("projects", {})
    
    async def update_project(self, project_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a project"""
        return await self.db.update_one(
            "projects",
            {"_id": ObjectId(project_id)},
            update_data
        )
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        return await self.db.delete_one("projects", {"_id": ObjectId(project_id)})
    
    async def get_or_create_project(self, name: str, repo_url: Optional[str] = None) -> Dict[str, Any]:
        """Get existing project or create new one"""
        existing = await self.get_project_by_name(name)
        if existing:
            return existing
        
        return await self.create_project({
            "name": name,
            "repo_url": repo_url,
            "total_budget": 0.0
        })


# Convenience functions
async def get_project(db: DatabaseManager, project_id: str) -> Optional[Dict[str, Any]]:
    """Get a project by ID"""
    service = ProjectService(db)
    return await service.get_project(project_id)


async def list_projects(db: DatabaseManager) -> List[Dict[str, Any]]:
    """List all projects"""
    service = ProjectService(db)
    return await service.list_projects()
