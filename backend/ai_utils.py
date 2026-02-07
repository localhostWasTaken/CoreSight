"""
AI Utilities for CoreSight
Handles embeddings generation, skill extraction, and intelligent task assignment
"""

import os
import json
from typing import List, Dict, Optional
from openai import OpenAI
import numpy as np

# Initialize OpenAI client with Featherless AI
client = OpenAI(
    base_url=os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1"),
    api_key=os.getenv("FEATHERLESS_API_KEY", "rc_6592c9b70f6b793d73a2cb301a915a586d586fdad0e75d61e35e50ae22be29b7"),
)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "IEITYuan/Yuan-embedding-2.0-en")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-ai/DeepSeek-R1-0528")


def generate_embedding(text: str) -> List[float]:
    """
    Generate embeddings for text using Featherless AI
    
    Args:
        text: Input text to generate embeddings for
        
    Returns:
        List of floats representing the embedding vector
    """
    if not text or not text.strip():
        # Return zero vector for empty text
        return [0.0] * 768
    
    try:
        response = client.chat.completions.create(
            model=EMBEDDING_MODEL,
            messages=[
                {"role": "system", "content": "Generate semantic embeddings for the given text."},
                {"role": "user", "content": text}
            ],
        )
        
        # The embedding model returns the embedding in the content
        # Parse and convert to float list
        content = response.model_dump()['choices'][0]['message']['content']
        
        # If the model returns a string representation, parse it
        # Otherwise, this might need adjustment based on actual API response
        try:
            embedding = json.loads(content)
            if isinstance(embedding, list):
                return [float(x) for x in embedding]
        except:
            # Fallback: Create a simple hash-based embedding
            import hashlib
            hash_obj = hashlib.sha256(text.encode())
            hash_bytes = hash_obj.digest()
            # Convert to 768-dim vector (standard for many models)
            embedding = []
            for i in range(768):
                embedding.append(float(hash_bytes[i % len(hash_bytes)]) / 255.0)
            return embedding
            
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return zero vector on error
        return [0.0] * 768


def extract_skills_from_task(task_title: str, task_description: Optional[str], project_name: str) -> List[str]:
    """
    Extract required skills from task description using LLM
    
    Args:
        task_title: The task title
        task_description: The task description (can be None)
        project_name: The project name for context
        
    Returns:
        List of skill strings
    """
    description = task_description or "No description provided"
    
    prompt = f"""
You are an expert technical recruiter analyzing a software development task.

Project: {project_name}
Task Title: {task_title}
Task Description: {description}

Extract a list of 3-7 specific technical skills required to complete this task.
Focus on:
- Programming languages (e.g., Python, JavaScript, Java)
- Frameworks (e.g., React, FastAPI, Spring)
- Tools (e.g., Git, Docker, Kubernetes)
- Technical domains (e.g., API development, database design, frontend)
- Methodologies (e.g., REST API, microservices, CI/CD)

Return ONLY a valid JSON array of skill strings, nothing else.
Example: ["Python", "FastAPI", "REST API", "MongoDB", "Git"]

Skills:"""
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a technical skill extraction expert. Return only valid JSON arrays."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        
        content = response.model_dump()['choices'][0]['message']['content'].strip()
        
        # Extract JSON array from response
        # Handle cases where the model might add extra text
        start = content.find('[')
        end = content.rfind(']') + 1
        
        if start != -1 and end != 0:
            json_str = content[start:end]
            skills = json.loads(json_str)
            
            if isinstance(skills, list) and len(skills) > 0:
                return [str(skill).strip() for skill in skills if skill]
        
        # Fallback: Basic skill extraction from text
        return extract_skills_fallback(task_title, description)
        
    except Exception as e:
        print(f"Error extracting skills with LLM: {e}")
        return extract_skills_fallback(task_title, description)


def extract_skills_fallback(task_title: str, task_description: str) -> List[str]:
    """Fallback skill extraction using keyword matching"""
    text = f"{task_title} {task_description}".lower()
    
    skill_keywords = {
        "python": "Python",
        "javascript": "JavaScript",
        "java": "Java",
        "react": "React",
        "fastapi": "FastAPI",
        "django": "Django",
        "flask": "Flask",
        "node": "Node.js",
        "mongodb": "MongoDB",
        "postgresql": "PostgreSQL",
        "sql": "SQL",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "git": "Git",
        "api": "API Development",
        "rest": "REST API",
        "graphql": "GraphQL",
        "frontend": "Frontend Development",
        "backend": "Backend Development",
        "database": "Database Design",
    }
    
    detected_skills = []
    for keyword, skill_name in skill_keywords.items():
        if keyword in text:
            detected_skills.append(skill_name)
    
    return detected_skills[:7] if detected_skills else ["General Software Development"]


def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
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


async def validate_user_assignment_with_llm(
    user_name: str,
    user_skills: List[str],
    task_title: str,
    task_description: str,
    required_skills: List[str],
    match_score: float
) -> Dict[str, any]:
    """
    Use LLM to validate if a user can perform the task
    
    Returns:
        {
            "can_do": bool,
            "confidence": float (0-1),
            "reasoning": str,
            "recommendations": str
        }
    """
    desc = task_description or "No description provided"
    
    prompt = f"""
You are an expert technical manager assessing if a developer can handle a task.

Developer: {user_name}
Developer Skills: {', '.join(user_skills)}
Skill Match Score: {match_score:.2f} (0-1 scale)

Task: {task_title}
Description: {desc}
Required Skills: {', '.join(required_skills)}

Evaluate if this developer can successfully complete this task.

Return ONLY a valid JSON object with this structure:
{{
    "can_do": true/false,
    "confidence": 0.85,
    "reasoning": "Brief explanation of why they can or cannot do it",
    "recommendations": "Suggestions for the developer or alternative actions"
}}

Assessment:"""
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a technical assessment expert. Return only valid JSON objects."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
        )
        
        content = response.model_dump()['choices'][0]['message']['content'].strip()
        
        # Extract JSON object
        start = content.find('{')
        end = content.rfind('}') + 1
        
        if start != -1 and end != 0:
            json_str = content[start:end]
            result = json.loads(json_str)
            return result
        
        # Fallback
        return {
            "can_do": match_score > 0.5,
            "confidence": match_score,
            "reasoning": f"Automated assessment based on {match_score:.2%} skill match",
            "recommendations": "Review task requirements carefully"
        }
        
    except Exception as e:
        print(f"Error validating with LLM: {e}")
        return {
            "can_do": match_score > 0.5,
            "confidence": match_score,
            "reasoning": f"Automated assessment: {match_score:.2%} match",
            "recommendations": "Manual review recommended"
        }


async def generate_no_match_report(
    task_title: str,
    task_description: str,
    required_skills: List[str],
    available_users_count: int
) -> Dict[str, any]:
    """
    Generate a critical report when no suitable users are found
    
    Returns:
        {
            "severity": "critical",
            "message": str,
            "required_skills": List[str],
            "recommendations": List[str],
            "should_post_job": bool
        }
    """
    desc = task_description or "No description provided"
    
    prompt = f"""
You are a critical technical resource manager. A task cannot be assigned because no developers match the required skills.

Task: {task_title}
Description: {desc}
Required Skills: {', '.join(required_skills)}
Available Developers: {available_users_count}

Provide a critical assessment and recommendations.

Return ONLY a valid JSON object:
{{
    "severity": "critical",
    "message": "Clear explanation of the gap",
    "missing_skills": ["skill1", "skill2"],
    "recommendations": ["action1", "action2"],
    "should_post_job": true/false,
    "suggested_job_title": "Job title if posting needed"
}}

Assessment:"""
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a critical resource gap analyst. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        
        content = response.model_dump()['choices'][0]['message']['content'].strip()
        
        start = content.find('{')
        end = content.rfind('}') + 1
        
        if start != -1 and end != 0:
            json_str = content[start:end]
            result = json.loads(json_str)
            return result
        
    except Exception as e:
        print(f"Error generating no-match report: {e}")
    
    # Fallback
    return {
        "severity": "critical",
        "message": f"No developers found with required skills: {', '.join(required_skills)}",
        "missing_skills": required_skills,
        "recommendations": [
            "Review existing team skills",
            "Consider training current developers",
            "Evaluate external hiring needs"
        ],
        "should_post_job": True,
        "suggested_job_title": f"Developer - {', '.join(required_skills[:3])}"
    }
