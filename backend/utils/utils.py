"""
Utilities for CoreSight

Common utility functions and dependencies used across the application.
"""

from typing import Optional
from functools import lru_cache

from database import DatabaseManager


# Global database manager reference (set by main.py lifespan)
_db_manager: Optional[DatabaseManager] = None


def set_db_manager(db: DatabaseManager) -> None:
    """Set the global database manager instance"""
    global _db_manager
    _db_manager = db


def get_db_manager() -> DatabaseManager:
    """
    Get the database manager instance.
    
    Returns:
        DatabaseManager instance
        
    Raises:
        RuntimeError: If database is not initialized
    """
    if _db_manager is None:
        raise RuntimeError("Database not initialized. Server may still be starting.")
    return _db_manager


def get_db() -> DatabaseManager:
    """Alias for get_db_manager - FastAPI dependency compatible"""
    return get_db_manager()


# Response helpers
def success_response(data: dict, message: str = "Success") -> dict:
    """Create a standardized success response"""
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(message: str, details: Optional[dict] = None) -> dict:
    """Create a standardized error response"""
    response = {
        "success": False,
        "message": message
    }
    if details:
        response["details"] = details
    return response


# Serialization helpers
def serialize_doc(doc: dict) -> dict:
    """
    Serialize a MongoDB document for JSON response.
    Converts ObjectId to string.
    """
    if doc is None:
        return None
    
    result = {}
    for key, value in doc.items():
        if key == "_id":
            result["id"] = str(value)
        elif hasattr(value, "__str__") and type(value).__name__ == "ObjectId":
            result[key] = str(value)
        else:
            result[key] = value
    
    return result


def serialize_docs(docs: list) -> list:
    """Serialize a list of MongoDB documents"""
    return [serialize_doc(doc) for doc in docs]
