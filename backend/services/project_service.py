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
        # Check if project already exists by jira_space_id first, then by name
        existing = None
        if project_data.get("jira_space_id"):
            existing = await self.db.find_one("projects", {"jira_space_id": project_data["jira_space_id"]})
        if not existing:
            existing = await self.db.find_one("projects", {"name": project_data["name"]})
        if existing:
            return existing  # Return existing project instead of raising error
        
        project_doc = {
            "name": project_data["name"],
            "jira_space_id": project_data.get("jira_space_id"),
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
    
    async def get_project_by_jira_space_id(self, jira_space_id: str) -> Optional[Dict[str, Any]]:
        """Get a project by Jira space ID"""
        return await self.db.find_one("projects", {"jira_space_id": jira_space_id})
    
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
    
    async def get_or_create_project(
        self, 
        name: str, 
        repo_url: Optional[str] = None,
        jira_space_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get existing project or create new one"""
        # Try to find by jira_space_id first
        if jira_space_id:
            existing = await self.get_project_by_jira_space_id(jira_space_id)
            if existing:
                return existing
        
        # Then try by name
        existing = await self.get_project_by_name(name)
        if existing:
            return existing
        
        return await self.create_project({
            "name": name,
            "jira_space_id": jira_space_id,
            "repo_url": repo_url,
            "total_budget": 0.0
        })
    
    async def add_contributor(
        self,
        project_id: str,
        user_id: str
    ) -> bool:
        """
        Add a user as a contributor to a project (if not already added).
        
        Args:
            project_id: Project ID
            user_id: User ID to add as contributor
            
        Returns:
            True if successful
        """
        try:
            from datetime import datetime
            # Use $addToSet to avoid duplicates
            result = await self.db.update_one_raw(
                "projects",
                {"_id": ObjectId(project_id)},
                {
                    "$addToSet": {"contributors": user_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            return result
        except Exception as e:
            print(f"Error adding contributor: {e}")
            return False
    
    async def get_project_contributors(
        self,
        project_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get list of contributors for a project with their stats.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of contributor info with stats
        """
        try:
            project = await self.db.find_one("projects", {"_id": ObjectId(project_id)})
            
            if not project or "contributors" not in project:
                return []
            
            contributor_ids = project.get("contributors", [])
            
            if not contributor_ids:
                return []
            
            # Fetch user details
            users = await self.db.find_many("users", {
                "_id": {"$in": [ObjectId(uid) if isinstance(uid, str) else uid for uid in contributor_ids]}
            })
            
            # Get commit stats for each contributor
            contributors = []
            for user in users:
                user_id_str = str(user["_id"])
                
                # Count commits for this user in this project
                commits = await self.db.find_many("commits", {
                    "user_id": ObjectId(user_id_str),
                    "repository": project.get("name")
                })
                
                # Calculate stats
                commit_count = len(commits)
                total_lines_added = sum(c.get("lines_added", 0) for c in commits)
                total_lines_deleted = sum(c.get("lines_deleted", 0) for c in commits)
                last_commit = max((c.get("timestamp") for c in commits), default=None)
                
                contributors.append({
                    "user_id": user_id_str,
                    "name": user.get("name"),
                    "email": user.get("email"),
                    "skills": user.get("skills", []),
                    "commit_count": commit_count,
                    "lines_added": total_lines_added,
                    "lines_deleted": total_lines_deleted,
                    "last_commit": last_commit.isoformat() if last_commit else None
                })
            
            return contributors
            
        except Exception as e:
            print(f"Error getting project contributors: {e}")
            return []


# Convenience functions
async def get_project(db: DatabaseManager, project_id: str) -> Optional[Dict[str, Any]]:
    """Get a project by ID"""
    service = ProjectService(db)
    return await service.get_project(project_id)


async def list_projects(db: DatabaseManager) -> List[Dict[str, Any]]:
    """List all projects"""
    service = ProjectService(db)
    return await service.list_projects()
