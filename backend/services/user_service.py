"""
User Service for CoreSight

Handles user-related business logic including CRUD operations
and profile embedding generation.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from bson import ObjectId

from utils.database import DatabaseManager
from ai import generate_embedding


class UserService:
    """Service class for user operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user with generated work profile embeddings.
        
        Args:
            user_data: User data including name, email, skills, etc.
            
        Returns:
            Created user document with ID
        """
        # Check if user already exists
        existing = await self.db.find_one("users", {"email": user_data["email"]})
        if existing:
            raise ValueError(f"User with email {user_data['email']} already exists")
        
        # Generate work profile embeddings from skills
        skills = user_data.get("skills", [])
        skills_text = ", ".join(skills) if skills else "General Software Development"
        embeddings = generate_embedding(skills_text)
        
        # Build user document
        user_doc = {
            "name": user_data["name"],
            "email": user_data["email"],
            "role": user_data.get("role", "employee"),
            "hourly_rate": user_data.get("hourly_rate", 50.0),
            "skills": skills,
            "work_profile_embeddings": embeddings,
            "project_metrics": user_data.get("project_metrics", {}),
            "github_username": user_data.get("github_username"),
            "jira_account_id": user_data.get("jira_account_id"),
            "created_at": datetime.utcnow(),
        }
        
        user_id = await self.db.insert_one("users", user_doc)
        user_doc["_id"] = user_id
        
        return user_doc
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID"""
        try:
            return await self.db.find_one("users", {"_id": ObjectId(user_id)})
        except Exception:
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by email address"""
        return await self.db.find_one("users", {"email": email})
    
    async def list_users(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """List all employees (excludes admins)"""
        query = {"role": "employee"}
        if filters:
            query.update(filters)
        return await self.db.find_many("users", query)
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update a user's information.
        
        If skills are updated, regenerate embeddings.
        """
        # If skills are being updated, regenerate embeddings
        if "skills" in update_data:
            skills_text = ", ".join(update_data["skills"])
            update_data["work_profile_embeddings"] = generate_embedding(skills_text)
        
        return await self.db.update_one(
            "users",
            {"_id": ObjectId(user_id)},
            update_data
        )
    
    async def update_user_skills(
        self,
        user_id: str,
        new_skills: List[str],
        new_embedding: Optional[List[float]] = None
    ) -> bool:
        """
        Update user's skills and optionally their embeddings.
        
        Args:
            user_id: User ID
            new_skills: New skills list
            new_embedding: Optional new embedding vector
            
        Returns:
            True if updated successfully
        """
        update_data = {"skills": new_skills}
        
        if new_embedding:
            update_data["work_profile_embeddings"] = new_embedding
        else:
            # Generate new embedding from skills
            skills_text = ", ".join(new_skills)
            update_data["work_profile_embeddings"] = generate_embedding(skills_text)
        
        return await self.db.update_one(
            "users",
            {"_id": ObjectId(user_id)},
            update_data
        )
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        return await self.db.delete_one("users", {"_id": ObjectId(user_id)})


# Convenience functions for use without class instantiation
async def create_user(db: DatabaseManager, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a user using the UserService"""
    service = UserService(db)
    return await service.create_user(user_data)


async def get_user(db: DatabaseManager, user_id: str) -> Optional[Dict[str, Any]]:
    """Get a user by ID"""
    service = UserService(db)
    return await service.get_user(user_id)


async def list_users(db: DatabaseManager) -> List[Dict[str, Any]]:
    """List all employees (excludes admins)"""
    service = UserService(db)
    return await service.list_users()
