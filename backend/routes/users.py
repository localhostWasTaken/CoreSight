"""
Users Router for CoreSight

Handles user management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from utils import get_db, serialize_doc, serialize_docs
from services.user_service import UserService


router = APIRouter(prefix="/api/users", tags=["Users"])


# Request/Response models
class UserCreate(BaseModel):
    name: str
    email: str  # Using str instead of EmailStr to avoid email-validator dependency
    role: str = "employee"
    hourly_rate: float = 50.0
    skills: List[str] = []
    github_username: Optional[str] = None
    jira_account_id: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    hourly_rate: Optional[float] = None
    skills: Optional[List[str]] = None
    github_username: Optional[str] = None
    jira_account_id: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    hourly_rate: float
    skills: List[str]
    github_username: Optional[str] = None
    jira_account_id: Optional[str] = None


# Endpoints
@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Create a new user with generated work profile embeddings.
    
    The user's skills will be used to generate semantic embeddings
    for intelligent task matching.
    """
    try:
        db = get_db()
        service = UserService(db)
        
        user_doc = await service.create_user(user.model_dump())
        
        return {
            "message": "User created successfully",
            "user": serialize_doc(user_doc)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("", response_model=List[dict])
async def list_users():
    """
    List all users in the system.
    """
    try:
        db = get_db()
        service = UserService(db)
        
        users = await service.list_users()
        
        # Remove embeddings from response (too large)
        result = []
        for user in users:
            user_data = serialize_doc(user)
            user_data.pop("work_profile_embeddings", None)
            result.append(user_data)
        
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/{user_id}", response_model=dict)
async def get_user(user_id: str):
    """
    Get a specific user by ID.
    """
    try:
        db = get_db()
        service = UserService(db)
        
        user = await service.get_user(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = serialize_doc(user)
        user_data.pop("work_profile_embeddings", None)
        
        return user_data
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.patch("/{user_id}", response_model=dict)
async def update_user(user_id: str, user: UserUpdate):
    """
    Update a user's information.
    
    If skills are updated, embeddings will be regenerated.
    """
    try:
        db = get_db()
        service = UserService(db)
        
        # Filter out None values
        update_data = {k: v for k, v in user.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        success = await service.update_user(user_id, update_data)
        
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User updated successfully"}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: str):
    """
    Delete a user.
    """
    try:
        db = get_db()
        service = UserService(db)
        
        success = await service.delete_user(user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User deleted successfully"}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
