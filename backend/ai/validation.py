"""
LLM Validation Functions for CoreSight
Using Featherless AI (OpenAI-compatible)
"""

import json
from typing import List, Dict, Optional

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
    """
    desc = task_description or "No description provided"
    
    prompt = f"""You are an expert technical manager assessing if a developer can handle a task.

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
}}"""
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        
        content = response.choices[0].message.content.strip()
        
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


async def evaluate_candidates_batch(
    candidates: List[Dict],
    task_title: str,
    task_description: str,
    required_skills: List[str]
) -> Dict[str, any]:
    """
    Evaluate multiple candidates and pick the best one using LLM.
    
    Args:
        candidates: List of user dicts (name, skills, match_score, _id)
        task_title: Task title
        task_description: Task description
        required_skills: List of required skills
        
    Returns:
        Dict with 'selected_user_id' (or None), 'reasoning', 'confidence'
    """
    if not candidates:
        return {"selected_user_id": None, "reasoning": "No candidates provided", "confidence": 0}
        
    desc = task_description or "No description provided"
    
    # Format candidates for prompt
    candidates_text = ""
    for i, user in enumerate(candidates):
        candidates_text += f"""
Candidate {i+1}:
- Name: {user.get('name')}
- ID: {str(user.get('_id'))}
- Skills: {', '.join(user.get('skills', []))}
- Vector Match Score: {user.get('match_score', 0):.2f}
"""

    prompt = f"""You are an expert technical manager assigning a task to the best available developer. You are CRITICAL and STRICT about requirements.

Task: {task_title}
Description: {desc}
Required Skills: {', '.join(required_skills)}

Available Candidates (ranked by vector similarity):
{candidates_text}

Analyze these candidates. Select the ONE best candidate who can definitely complete the task.
CRITICAL INSTRUCTION:
- Do NOT pick a candidate just to pick someone.
- If a candidate lacks essential skills or seems underqualified, do NOT select them.
- If NO candidate is fully qualified, you MUST select "None".
- It is better to hire a new person (select None) than to assign an unqualified developer.

Return ONLY a valid JSON object with this structure:
{{
    "selected_candidate_index": 1 (or null if none),
    "selected_user_id": "string_id_from_candidate" (or null if none),
    "confidence": 0.9,
    "reasoning": "Detailed explanation of why this candidate was chosen, or why all were rejected (citing missing skills)."
}}"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, # Lower temperature for decision making
        )
        
        content = response.choices[0].message.content.strip()
        
        # Extract JSON object
        start = content.find('{')
        end = content.rfind('}') + 1
        
        if start != -1 and end != 0:
            json_str = content[start:end]
            result = json.loads(json_str)
            return result
        
        return {"selected_user_id": None, "reasoning": "Failed to parse LLM decision", "confidence": 0}

    except Exception as e:
        print(f"Error in batch evaluation: {e}")
        return {"selected_user_id": None, "reasoning": f"Error: {str(e)}", "confidence": 0}
