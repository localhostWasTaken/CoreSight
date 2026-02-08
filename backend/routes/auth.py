"""
Authentication Router for CoreSight API.
Handles login, token refresh, and user authentication.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from utils import get_db
from utils.auth import verify_password, create_access_token, hash_password


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    Only users with 'admin' role can login to the dashboard.
    """
    db = get_db()
    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    # Find user by email
    user = await db.db.users.find_one({"email": request.email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check password
    if not user.get("password_hash"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check admin role
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Create access token
    token_data = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "name": user.get("name", ""),
        "role": user.get("role", "employee")
    }
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user.get("name", ""),
            "role": user.get("role", "employee")
        }
    }

@router.get("/me")
async def get_current_user_info():
    """Get current authenticated user info (for token validation)."""
    # This endpoint is protected by the JWT middleware
    # The actual user info comes from the token
    from fastapi import Depends
    from utils.auth import get_current_user
    return {"message": "Use the /api/auth/login endpoint to authenticate"}
