"""
User Matching Functions for CoreSight
"""

from typing import List, Dict

from .embeddings import generate_embedding, calculate_cosine_similarity


def find_best_matching_users(
    task_skills: List[str],
    task_embeddings: List[float],
    available_users: List[Dict],
    top_n: int = 5
) -> List[Dict]:
    """
    Find best matching users for a task based on skill embeddings
    
    Args:
        task_skills: List of required skills for the task
        task_embeddings: Task description embeddings
        available_users: List of user dictionaries with skills and embeddings
        top_n: Number of top matches to return
        
    Returns:
        List of user dictionaries with match scores, sorted by best match
    """
    if not available_users:
        return []
    
    # Generate embedding for combined task skills
    task_skill_text = ", ".join(task_skills)
    task_skill_embedding = generate_embedding(task_skill_text)
    
    user_scores = []
    
    for user in available_users:
        # Calculate skill text similarity
        user_skills = user.get("skills", [])
        user_skill_text = ", ".join(user_skills)
        user_skill_embedding = generate_embedding(user_skill_text)
        
        skill_similarity = calculate_cosine_similarity(task_skill_embedding, user_skill_embedding)
        
        # Calculate work profile similarity (if available)
        user_profile_embedding = user.get("work_profile_embeddings", [])
        profile_similarity = calculate_cosine_similarity(task_embeddings, user_profile_embedding)
        
        # Combined score (weighted)
        combined_score = (skill_similarity * 0.7) + (profile_similarity * 0.3)
        
        user_scores.append({
            **user,
            "match_score": combined_score,
            "skill_similarity": skill_similarity,
            "profile_similarity": profile_similarity,
        })
    
    # Sort by match score descending
    user_scores.sort(key=lambda x: x["match_score"], reverse=True)
    
    return user_scores[:top_n]
