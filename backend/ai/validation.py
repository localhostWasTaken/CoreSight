"""
LLM Validation Functions for CoreSight
"""

import json
from typing import List, Dict

from .client import client, LLM_MODEL


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
