"""
Jira Webhook Handlers for CoreSight
Processes Jira webhooks and performs intelligent task assignment
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.database import DatabaseManager
from entities import Task, TaskType, TaskStatus, Sprint, User, WorkSession
from ai import (
    extract_skills_from_task,
    generate_embedding,
    find_best_matching_users,
    evaluate_candidates_batch,
    generate_no_match_report
)


async def handle_issue_created(webhook_data: Dict[str, Any], db: DatabaseManager) -> Dict[str, Any]:
    """
    Handle jira:issue_created webhook event
    
    Workflow:
    1. Extract issue data from webhook
    2. Get or create project in database
    3. Extract required skills using LLM
    4. Generate embeddings for task description and skills
    5. Find matching users based on skill embeddings
    6. Validate assignment with LLM
    7. Assign task to best user in current sprint
    8. Create work session and update task
    """
    
    issue = webhook_data.get("issue", {})
    fields = issue.get("fields", {})
    
    # Extract core data
    issue_key = issue.get("key")
    issue_id = issue.get("id")
    summary = fields.get("summary", "Untitled Task")
    description = fields.get("description") or f"Task: {summary}"
    priority = fields.get("priority", {}).get("name", "Medium")
    status_name = fields.get("status", {}).get("name", "To Do")
    
    # Project data
    project_data = fields.get("project", {})
    project_key = project_data.get("key")
    project_name = project_data.get("name", "Unknown Project")
    project_id_jira = project_data.get("id")
    
    # Sprint data (customfield_10020 is typically sprint field)
    sprint_data = fields.get("customfield_10020", [])
    sprint_info = sprint_data[0] if sprint_data and isinstance(sprint_data, list) else None
    
    print(f"\n=== Processing Issue Created: {issue_key} ===")
    print(f"Summary: {summary}")
    print(f"Project: {project_name} ({project_key})")
    print(f"Status: {status_name}")
    
    # Map Jira issue type to our TaskType
    issue_type = fields.get("issuetype", {}).get("name", "Task")
    task_type = map_jira_issue_type(issue_type)
    
    # Map Jira status to our TaskStatus
    task_status = map_jira_status(status_name)
    
    # Step 1: Get or create project (prioritize jira_space_id lookup)
    project = None
    if project_id_jira:
        project = await db.find_one("projects", {"jira_space_id": project_id_jira})
    
    if not project:
        project = await db.find_one("projects", {"name": project_name})
    
    if not project:
        print(f"Creating new project: {project_name} (Jira ID: {project_id_jira})")
        project_id = await db.insert_one("projects", {
            "name": project_name,
            "jira_space_id": project_id_jira,
            "repo_url": None,
            "total_budget": 0.0,
        })
        project = await db.find_one("projects", {"_id": project_id})
    else:
        # Update existing project with jira_space_id if missing
        if project_id_jira and not project.get("jira_space_id"):
            await db.update_one("projects", {"_id": project["_id"]}, {"jira_space_id": project_id_jira})
            project["jira_space_id"] = project_id_jira
        print(f"Using existing project: {project_name}")
    
    project_id_str = str(project["_id"])
    
    # Step 2: Get or create sprint
    sprint_id_str = None
    if sprint_info:
        sprint_name = sprint_info.get("name", "Default Sprint")
        sprint_id_str = await get_or_create_sprint(db, project_id_str, sprint_info)
        print(f"Sprint: {sprint_name}")
    
    # Step 3: Extract required skills using AI
    print("\n🤖 Extracting required skills...")
    required_skills = extract_skills_from_task(summary, description, project_name)
    print(f"Required Skills: {', '.join(required_skills)}")
    
    # Step 4: Generate embeddings
    print("🧠 Generating embeddings...")
    task_text = f"{summary}. {description}"
    task_embeddings = generate_embedding(task_text)
    
    # Also embed the skills for matching
    skills_text = ", ".join(required_skills)
    skills_embeddings = generate_embedding(skills_text)
    
    # Step 5: Create task in database
    task_doc = {
        "external_id": issue_key,
        "title": summary,
        "description": description,
        "description_embeddings": task_embeddings,
        "type": task_type,
        "status": task_status,
        "priority": priority,
        "project_id": project_id_str,
        "sprint_id": sprint_id_str,
        "current_assignee_ids": [],
        "sprint_history": [sprint_id_str] if sprint_id_str else [],
        "rollover_count": 0,
        "total_time_spent_minutes": 0,
        "total_cost": 0.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    task_id = await db.insert_one("tasks", task_doc)
    print(f"✅ Task created in DB: {task_id}")
    
    # Step 6: Find matching users
    print("\n👥 Finding matching users...")
    all_users = await db.find_many("users", {})
    
    if not all_users:
        print("⚠️  No users in database!")
        report = await generate_no_match_report(
            summary, description, required_skills, 0
        )
        
        # Create JobRequisition for hiring
        requisition_id = await create_job_requisition(
            db, str(task_id), report, required_skills
        )
        
        return {
            "status": "no_users_available",
            "task_id": str(task_id),
            "issue_key": issue_key,
            "report": report,
            "requisition_id": str(requisition_id),
            "action_required": "fill_job_requisition"
        }
    
    # Convert MongoDB users to dict format
    users_list = []
    for user in all_users:
        users_list.append({
            "_id": user["_id"],
            "name": user.get("name"),
            "email": user.get("email"),
            "skills": user.get("skills", []),
            "work_profile_embeddings": user.get("work_profile_embeddings", []),
            "hourly_rate": user.get("hourly_rate", 50.0),
        })
    
    matching_users = find_best_matching_users(
        required_skills, task_embeddings, users_list, top_n=5
    )
    
    if not matching_users:
        print("❌ No matching users found!")
        report = await generate_no_match_report(
            summary, description, required_skills, len(all_users)
        )
        
        # Create JobRequisition for hiring
        requisition_id = await create_job_requisition(
            db, str(task_id), report, required_skills
        )
        
        return {
            "status": "no_match",
            "task_id": str(task_id),
            "issue_key": issue_key,
            "report": report,
            "requisition_id": str(requisition_id),
            "action_required": "fill_job_requisition"
        }
    
    print(f"[JIRA ASSIGNMENT] Found {len(matching_users)} potential matches:")
    for i, user in enumerate(matching_users[:3], 1):
        print(f"  {i}. {user['name']} - Match: {user['match_score']:.2%} - Skills: {user['skills']}")
    
    # Step 7: Validate with LLM (Batch Evaluation)
    print("\n🔍 Sending all candidates to LLM for critical evaluation...")
    evaluation = await evaluate_candidates_batch(
        candidates=matching_users,
        task_title=summary,
        task_description=description,
        required_skills=required_skills
    )
    
    print(f"[JIRA ASSIGNMENT] LLM Evaluation Result:")
    print(f"  Selected User ID: {evaluation.get('selected_user_id')}")
    print(f"  Confidence: {evaluation.get('confidence')}")
    print(f"  Reasoning: {evaluation.get('reasoning')}")
    
    selected_user_id = evaluation.get("selected_user_id")
    
    # Step 8: Assign task if LLM selected a user
    if selected_user_id:
        assigned_user = next((u for u in matching_users if str(u["_id"]) == selected_user_id), None)
        
        if assigned_user:
            user_id_str = str(assigned_user["_id"])
            
            # Update task with assignee
            await db.update_one(
                "tasks",
                {"_id": task_id},
                {"current_assignee_ids": [user_id_str]}
            )
            
            # Create work session
            work_session_doc = {
                "task_id": str(task_id),
                "user_id": user_id_str,
                "start_time": datetime.utcnow(),
                "end_time": None,
                "duration_minutes": 0.0,
                "assigned_by_user_id": None,  # System assigned
            }
            
            session_id = await db.insert_one("work_sessions", work_session_doc)
            
            print(f"✅ Task assigned to {assigned_user['name']}")
            print(f"📝 Work session created: {session_id}")
            
            return {
                "status": "assigned",
                "task_id": str(task_id),
                "issue_key": issue_key,
                "assigned_to": {
                    "user_id": user_id_str,
                    "name": assigned_user["name"],
                    "match_score": assigned_user["match_score"],
                },
                "validation": evaluation,
                "required_skills": required_skills,
            }
    
    # If LLM rejected all candidates, create job requisition
    print(f"⚠️  LLM rejected all candidates. Creating Job Requisition...")
    
    report = await generate_no_match_report(
        summary, description, required_skills, len(all_users)
    )
    
    # Add LLM reasoning to report
    if evaluation.get("reasoning"):
        report["llm_evaluation_reasoning"] = evaluation["reasoning"]
    
    requisition_id = await create_job_requisition(
        db, str(task_id), report, required_skills
    )
    
    return {
        "status": "no_qualified_match",
        "task_id": str(task_id),
        "issue_key": issue_key,
        "report": report,
        "requisition_id": str(requisition_id),
        "action_required": "admin_approval_required",
        "candidates_evaluated": len(matching_users),
        "llm_reasoning": evaluation.get("reasoning")
    }


async def handle_sprint_created(webhook_data: Dict[str, Any], db: DatabaseManager) -> Dict[str, Any]:
    """
    Handle sprint created webhook
    
    Creates sprint in database
    """
    sprint_data = webhook_data.get("sprint", {})
    
    sprint_name = sprint_data.get("name", "Sprint")
    sprint_id_jira = str(sprint_data.get("id"))
    
    # Extract project info (may vary by Jira setup)
    # For now, we'll need to manually associate sprints with projects
    
    print(f"\n=== Sprint Created: {sprint_name} ===")
    
    return {
        "status": "sprint_created",
        "sprint_name": sprint_name,
        "sprint_id_jira": sprint_id_jira,
    }


async def handle_sprint_started(webhook_data: Dict[str, Any], db: DatabaseManager) -> Dict[str, Any]:
    """
    Handle sprint started webhook
    
    Assigns pending tasks to users based on skills
    """
    sprint_data = webhook_data.get("sprint", {})
    sprint_name = sprint_data.get("name")
    
    print(f"\n=== Sprint Started: {sprint_name} ===")
    print("🚀 Auto-assigning pending tasks...")
    
    # TODO: Implement auto-assignment for sprint start
    # 1. Get all unassigned tasks in this sprint
    # 2. For each task, run the assignment algorithm
    # 3. Distribute tasks evenly among qualified users
    
    return {
        "status": "sprint_started",
        "sprint_name": sprint_name,
        "message": "Auto-assignment feature coming soon"
    }


# === HELPER FUNCTIONS ===

def map_jira_issue_type(jira_type: str) -> str:
    """Map Jira issue types to our TaskType enum"""
    type_map = {
        "bug": TaskType.BUG,
        "story": TaskType.FEATURE,
        "task": TaskType.FEATURE,
        "epic": TaskType.FEATURE,
        "technical debt": TaskType.DEBT,
        "documentation": TaskType.DOCUMENTATION,
    }
    
    normalized = jira_type.lower()
    return type_map.get(normalized, TaskType.FEATURE)


def map_jira_status(jira_status: str) -> str:
    """Map Jira status to our TaskStatus enum"""
    status_map = {
        "to do": TaskStatus.TODO,
        "in progress": TaskStatus.IN_PROGRESS,
        "in review": TaskStatus.REVIEW,
        "review": TaskStatus.REVIEW,
        "done": TaskStatus.DONE,
        "closed": TaskStatus.DONE,
    }
    
    normalized = jira_status.lower()
    return status_map.get(normalized, TaskStatus.TODO)


async def get_or_create_sprint(db: DatabaseManager, project_id: str, sprint_info: Dict) -> str:
    """Get or create sprint in database"""
    sprint_name = sprint_info.get("name", "Default Sprint")
    sprint_id_jira = sprint_info.get("id")
    
    # Try to find existing sprint by name and project
    existing_sprint = await db.find_one("sprints", {
        "project_id": project_id,
        "name": sprint_name
    })
    
    if existing_sprint:
        return str(existing_sprint["_id"])
    
    # Parse dates
    start_date_str = sprint_info.get("startDate")
    end_date_str = sprint_info.get("endDate")
    
    start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00")) if start_date_str else datetime.utcnow()
    end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00")) if end_date_str else datetime.utcnow()
    
    # Create new sprint
    sprint_doc = {
        "project_id": project_id,
        "name": sprint_name,
        "start_date": start_date,
        "end_date": end_date,
        "goal": sprint_info.get("goal", ""),
        "is_active": sprint_info.get("state") == "active",
    }
    
    sprint_id = await db.insert_one("sprints", sprint_doc)
    return str(sprint_id)


async def create_job_requisition(
    db: DatabaseManager,
    task_id: str,
    report: Dict[str, Any],
    required_skills: List[str]
) -> str:
    """
    Create a JobRequisition document when no matching users found.
    
    Args:
        db: Database manager
        task_id: Related task ID
        report: Report from generate_no_match_report
        required_skills: List of required skills
        
    Returns:
        Created requisition ID
    """
    print("\n📢 CREATING JOB REQUISITION")
    print(f"   Suggested Title: {report.get('suggested_job_title')}")
    print(f"   Required Skills: {', '.join(required_skills)}")
    
    requisition_doc = {
        "task_id": task_id,
        "suggested_title": report.get("suggested_job_title", f"Developer - {required_skills[0]}"),
        "description": report.get("suggested_job_description", ""),
        "required_skills": required_skills,
        "location": None,
        "workplace_type": "ON_SITE",
        "employment_type": "FULL_TIME",
        "status": "pending",
        "admin_approved": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": "system"
    }
    
    requisition_id = await db.insert_one("job_requisitions", requisition_doc)
    print(f"✅ JobRequisition created: {requisition_id}")
    print(f"   Next: Admin can update via /api/jobs/requisitions/{requisition_id} and approve")
    
    return requisition_id
