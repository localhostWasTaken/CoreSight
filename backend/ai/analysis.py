"""
Issue and Commit Analysis Functions for CoreSight
Using Featherless AI (OpenAI-compatible)
"""

import json
from typing import List, Dict

from .client import client, LLM_MODEL


async def check_issue_duplicate_with_llm(
    new_issue_title: str,
    new_issue_description: str,
    similar_issues: List[Dict]
) -> Dict[str, any]:
    """
    Use LLM to determine if new issue is duplicate of existing issues
    """
    if not similar_issues:
        return {
            "is_duplicate": False,
            "parent_task_id": None,
            "confidence": 1.0,
            "reasoning": "No similar issues found",
            "priority_change": None,
            "new_skills_required": []
        }
    
    # Format similar issues for LLM
    similar_issues_text = "\n\n".join([
        f"Issue {i+1} (ID: {issue.get('_id', 'N/A')}):\n"
        f"Title: {issue.get('title', 'N/A')}\n"
        f"Description: {issue.get('description', 'N/A')}\n"
        f"Priority: {issue.get('priority', 'N/A')}\n"
        f"Skills: {', '.join(issue.get('required_skills', []))}"
        for i, issue in enumerate(similar_issues[:3])
    ])
    
    prompt = f"""You are an expert issue tracker analyst. Analyze if a new issue is a duplicate or related to existing issues.

NEW ISSUE:
Title: {new_issue_title}
Description: {new_issue_description}

SIMILAR EXISTING ISSUES:
{similar_issues_text}

Determine:
1. Is this a duplicate or continuation of an existing issue?
2. If yes, which issue is it related to (provide the Issue ID)?
3. Does this indicate a priority change (more urgent, less urgent, or no change)?
4. Are there new technical skills required beyond what the existing issue needed?

Return ONLY a valid JSON object:
{{
    "is_duplicate": true/false,
    "parent_task_id": "issue_id" or null,
    "confidence": 0.85,
    "reasoning": "Clear explanation of why it is or isn't duplicate",
    "priority_change": "increased" or "decreased" or null,
    "new_skills_required": ["skill1", "skill2"] or []
}}"""
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        
        content = response.choices[0].message.content.strip()
        
        start = content.find('{')
        end = content.rfind('}') + 1
        
        if start != -1 and end != 0:
            json_str = content[start:end]
            result = json.loads(json_str)
            return result
        
    except Exception as e:
        print(f"Error checking duplicate with LLM: {e}")
    
    # Fallback - use similarity threshold
    return {
        "is_duplicate": False,
        "parent_task_id": None,
        "confidence": 0.5,
        "reasoning": "LLM analysis unavailable, defaulting to new issue",
        "priority_change": None,
        "new_skills_required": []
    }


async def extract_skills_from_commit_diff(
    commit_message: str,
    diff_content: str,
    repository: str
) -> Dict[str, any]:
    """
    Extract problem summary and skills from a commit diff using LLM
    """
    # Truncate diff if too long (keep first 2000 chars)
    diff_preview = diff_content[:2000] + "..." if len(diff_content) > 2000 else diff_content
    
    prompt = f"""You are a senior code reviewer analyzing a git commit to understand what was accomplished.

Repository: {repository}
Commit Message: {commit_message}

Diff Preview:
{diff_preview}

Analyze this commit and extract:
1. A clear summary of the problem solved or feature built (1-2 sentences)
2. The technical skills demonstrated in this specific commit (3-7 skills)
3. Impact assessment: minor, moderate, or significant

Return ONLY a valid JSON object:
{{
    "summary": "Brief description of what was accomplished",
    "skills_used": ["Python", "FastAPI", "MongoDB", "REST API"],
    "impact_assessment": "moderate"
}}"""
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        
        content = response.choices[0].message.content.strip()
        
        start = content.find('{')
        end = content.rfind('}') + 1
        
        if start != -1 and end != 0:
            json_str = content[start:end]
            result = json.loads(json_str)
            return result
        
    except Exception as e:
        print(f"Error extracting commit skills with LLM: {e}")
    
    # Fallback
    return {
        "summary": commit_message or "Code changes",
        "skills_used": ["Software Development"],
        "impact_assessment": "minor"
    }


async def check_profile_update_needed(
    current_profile: str,
    current_skills: List[str],
    new_commit_skills: List[str],
    commit_summary: str
) -> Dict[str, any]:
    """
    Determine if user's profile needs updating based on new commit skills
    """
    prompt = f"""You are an expert career development analyst evaluating if a developer's profile needs updating.

CURRENT PROFILE:
Skills: {', '.join(current_skills)}
Profile: {current_profile or "No profile text"}

NEW COMMIT ACTIVITY:
Summary: {commit_summary}
Skills Demonstrated: {', '.join(new_commit_skills)}

Determine if this commit demonstrates:
1. New skills not in their current profile that should be added
2. A shift in expertise level that warrants profile update
3. New technical domains they're now working in

Return ONLY a valid JSON object:
{{
    "needs_update": true/false,
    "reasoning": "Clear explanation of why profile should or shouldn't be updated",
    "new_skills_to_add": ["skill1", "skill2"] or [],
    "updated_profile_text": "Enhanced profile text" or null
}}"""
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        
        content = response.choices[0].message.content.strip()
        
        start = content.find('{')
        end = content.rfind('}') + 1
        
        if start != -1 and end != 0:
            json_str = content[start:end]
            result = json.loads(json_str)
            return result
        
    except Exception as e:
        print(f"Error checking profile update with LLM: {e}")
    
    # Fallback - check if there are truly new skills
    new_skills = [skill for skill in new_commit_skills if skill not in current_skills]
    
    return {
        "needs_update": len(new_skills) > 0,
        "reasoning": f"Detected {len(new_skills)} new skills" if new_skills else "No new skills detected",
        "new_skills_to_add": new_skills,
        "updated_profile_text": None
    }
