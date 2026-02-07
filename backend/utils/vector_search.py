"""
Vector Search Module for CoreSight
Handles similarity search for issues and commits using embeddings
"""

import numpy as np
from typing import List, Dict, Optional
from bson import ObjectId


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    if not vec1 or not vec2:
        return 0.0
    
    try:
        arr1 = np.array(vec1)
        arr2 = np.array(vec2)
        
        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0


async def search_similar_issues(
    db_manager,
    query_embedding: List[float],
    top_k: int = 5,
    min_similarity: float = 0.7
) -> List[Dict]:
    """
    Search for similar issues using vector similarity
    
    Args:
        db_manager: DatabaseManager instance
        query_embedding: Embedding vector to search for
        top_k: Number of top results to return
        min_similarity: Minimum similarity threshold (0-1)
        
    Returns:
        List of issue documents with similarity scores
    """
    try:
        # Fetch all issues with embeddings
        issues = await db_manager.find_many("issues", {})
        
        if not issues:
            return []
        
        # Calculate similarities
        results = []
        for issue in issues:
            embedding = issue.get("description_embedding", [])
            if not embedding:
                continue
            
            similarity = cosine_similarity(query_embedding, embedding)
            
            if similarity >= min_similarity:
                issue["similarity_score"] = similarity
                results.append(issue)
        
        # Sort by similarity descending
        results.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        
        return results[:top_k]
        
    except Exception as e:
        print(f"Error searching similar issues: {e}")
        return []


async def search_similar_tasks_for_commit(
    db_manager,
    query_embedding: List[float],
    top_k: int = 3,
    min_similarity: float = 0.6
) -> List[Dict]:
    """
    Search for similar tasks (from Task collection) for commit linking
    
    Args:
        db_manager: DatabaseManager instance
        query_embedding: Commit summary embedding vector
        top_k: Number of top results to return
        min_similarity: Minimum similarity threshold
        
    Returns:
        List of task documents with similarity scores
    """
    try:
        # Fetch all tasks with embeddings
        tasks = await db_manager.find_many("tasks", {})
        
        if not tasks:
            return []
        
        # Calculate similarities
        results = []
        for task in tasks:
            embedding = task.get("description_embeddings", [])
            if not embedding:
                continue
            
            similarity = cosine_similarity(query_embedding, embedding)
            
            if similarity >= min_similarity:
                task["similarity_score"] = similarity
                results.append(task)
        
        # Sort by similarity descending
        results.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        
        return results[:top_k]
        
    except Exception as e:
        print(f"Error searching similar tasks: {e}")
        return []


async def find_matching_users_by_skills(
    db_manager,
    required_skills: List[str],
    skill_embedding: List[float],
    top_k: int = 5,
    min_similarity: float = 0.5
) -> List[Dict]:
    """
    Find users whose skills match the required skills
    
    Args:
        db_manager: DatabaseManager instance
        required_skills: List of required skill strings
        skill_embedding: Embedding of required skills
        top_k: Number of top matches to return
        min_similarity: Minimum similarity threshold
        
    Returns:
        List of user documents with match scores
    """
    try:
        # Fetch all users
        users = await db_manager.find_many("users", {})
        
        if not users:
            return []
        
        results = []
        for user in users:
            user_skills = user.get("skills", [])
            user_embedding = user.get("work_profile_embeddings", [])
            
            # Calculate skill overlap
            skill_overlap = len(set(required_skills) & set(user_skills))
            skill_overlap_ratio = skill_overlap / len(required_skills) if required_skills else 0
            
            # Calculate embedding similarity
            embedding_similarity = 0.0
            if user_embedding:
                embedding_similarity = cosine_similarity(skill_embedding, user_embedding)
            
            # Combined score (weighted)
            combined_score = (skill_overlap_ratio * 0.6) + (embedding_similarity * 0.4)
            
            if combined_score >= min_similarity:
                user["match_score"] = combined_score
                user["skill_overlap"] = skill_overlap
                user["embedding_similarity"] = embedding_similarity
                results.append(user)
        
        # Sort by match score descending
        results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        return results[:top_k]
        
    except Exception as e:
        print(f"Error finding matching users: {e}")
        return []


async def find_user_by_email(db_manager, email: str) -> Optional[Dict]:
    """
    Find a user by email address
    
    Args:
        db_manager: DatabaseManager instance
        email: User email address
        
    Returns:
        User document or None
    """
    try:
        user = await db_manager.find_one("users", {"email": email})
        return user
    except Exception as e:
        print(f"Error finding user by email: {e}")
        return None


async def create_issue_document(
    db_manager,
    issue_data: Dict
) -> Optional[str]:
    """
    Create a new issue document in the database
    
    Args:
        db_manager: DatabaseManager instance
        issue_data: Issue data dictionary
        
    Returns:
        Created issue ID as string or None
    """
    try:
        result = await db_manager.insert_one("issues", issue_data)
        return str(result)
    except Exception as e:
        print(f"Error creating issue: {e}")
        return None


async def create_commit_document(
    db_manager,
    commit_data: Dict
) -> Optional[str]:
    """
    Create a new commit document in the database
    
    Args:
        db_manager: DatabaseManager instance
        commit_data: Commit data dictionary
        
    Returns:
        Created commit ID as string or None
    """
    try:
        result = await db_manager.insert_one("commits", commit_data)
        return str(result)
    except Exception as e:
        print(f"Error creating commit: {e}")
        return None


async def update_issue(
    db_manager,
    issue_id: str,
    update_data: Dict
) -> bool:
    """
    Update an existing issue
    
    Args:
        db_manager: DatabaseManager instance
        issue_id: Issue ID string
        update_data: Dictionary of fields to update
        
    Returns:
        True if updated successfully
    """
    try:
        result = await db_manager.update_one(
            "issues",
            {"_id": ObjectId(issue_id)},
            update_data
        )
        return result
    except Exception as e:
        print(f"Error updating issue: {e}")
        return False


async def update_user_profile(
    db_manager,
    user_id: str,
    new_skills: List[str],
    new_embedding: List[float],
    profile_text: Optional[str] = None
) -> bool:
    """
    Update user's skills and profile embedding
    
    Args:
        db_manager: DatabaseManager instance
        user_id: User ID string
        new_skills: Updated skills list
        new_embedding: New work profile embedding
        profile_text: Optional new profile text
        
    Returns:
        True if updated successfully
    """
    try:
        update_data = {
            "skills": new_skills,
            "work_profile_embeddings": new_embedding
        }
        
        if profile_text:
            update_data["profile_text"] = profile_text
        
        result = await db_manager.update_one(
            "users",
            {"_id": ObjectId(user_id)},
            update_data
        )
        return result
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return False
