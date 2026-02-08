"""
Report Generation Functions for CoreSight
Using Featherless AI (OpenAI-compatible)
"""

import json
from typing import List, Dict, Optional

from .client import client, LLM_MODEL


async def generate_no_match_report(
    task_title: str,
    task_description: str,
    required_skills: List[str],
    available_users_count: int
) -> Dict[str, any]:
    """
    Generate a critical report when no suitable users are found.
    Also generates job posting data for the careers page.
    """
    desc = task_description or "No description provided"
    
    prompt = f"""You are a critical technical resource manager and expert job description writer. 
A task cannot be assigned because no developers match the required skills.

Task: {task_title}
Description: {desc}
Required Skills: {', '.join(required_skills)}
Available Developers: {available_users_count}

Generate a comprehensive assessment AND a job posting for hiring the needed talent.

Return ONLY a valid JSON object with this structure:
{{
    "severity": "critical",
    "message": "Clear explanation of the skills gap",
    "missing_skills": ["skill1", "skill2"],
    "recommendations": ["action1", "action2"],
    "should_post_job": true,
    "suggested_job_title": "Concise professional job title (e.g., 'Senior Python Developer')",
    "suggested_job_description": "<h2>About the Role</h2><p>Brief engaging intro...</p><h2>Responsibilities</h2><ul><li>Key responsibility 1</li><li>Key responsibility 2</li></ul><h2>Requirements</h2><ul><li>Skill requirement 1</li><li>Skill requirement 2</li></ul><h2>Nice to Have</h2><ul><li>Optional skill</li></ul>",
    "required_experience_years": 3
}}

IMPORTANT: 
- The job description must be valid HTML
- Keep it professional and engaging
- Focus on the specific skills needed for the task"""
    
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
            
            # Ensure all required fields are present
            if "suggested_job_description" not in result:
                result["suggested_job_description"] = generate_fallback_job_description(
                    result.get("suggested_job_title", f"Developer - {', '.join(required_skills[:3])}"),
                    required_skills,
                    task_description
                )
            if "required_experience_years" not in result:
                result["required_experience_years"] = 2
                
            return result
        
    except Exception as e:
        print(f"Error generating no-match report: {e}")
    
    # Fallback
    suggested_title = f"Developer - {', '.join(required_skills[:2])}" if len(required_skills) > 1 else f"{required_skills[0]} Developer"
    
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
        "suggested_job_title": suggested_title,
        "suggested_job_description": generate_fallback_job_description(
            suggested_title, required_skills, task_description
        ),
        "required_experience_years": 2
    }


def generate_fallback_job_description(
    job_title: str,
    required_skills: List[str],
    task_description: Optional[str]
) -> str:
    """Generate a basic HTML job description when LLM fails"""
    skills_list = "".join([f"<li>{skill}</li>" for skill in required_skills])
    task_context = task_description or "Various development tasks"
    
    return f"""
<h2>About the Role</h2>
<p>We are looking for a talented {job_title} to join our team and help deliver high-quality software solutions.</p>

<h2>Responsibilities</h2>
<ul>
<li>Develop and maintain software according to project requirements</li>
<li>Collaborate with cross-functional teams</li>
<li>Participate in code reviews and technical discussions</li>
<li>Context: {task_context[:200]}...</li>
</ul>

<h2>Requirements</h2>
<ul>
{skills_list}
<li>Strong problem-solving skills</li>
<li>Excellent communication abilities</li>
</ul>

<h2>Nice to Have</h2>
<ul>
<li>Experience with agile methodologies</li>
<li>Open source contributions</li>
</ul>
"""
