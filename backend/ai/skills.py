"""
Skill Extraction Functions for CoreSight
"""

import json
from typing import List, Optional

from .client import client, LLM_MODEL


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
