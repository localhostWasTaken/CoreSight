"""
Webhooks Router for CoreSight

Handles Jira and GitHub webhook endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request
import json

from utils import get_db
from services.jira_handlers import (
    handle_issue_created,
    handle_sprint_created,
    handle_sprint_started,
)


router = APIRouter(prefix="/api/webhook", tags=["Webhooks"])


@router.post("/jira")
async def handle_jira_webhook(request: Request):
    """
    Handle incoming Jira webhooks.
    
    Supported events:
    - jira:issue_created - Creates task and auto-assigns
    - sprint_created - Logs sprint creation
    - sprint_started - Can trigger auto-assignment
    
    Configure your Jira webhook to point to this endpoint.
    """
    try:
        db = get_db()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    
    try:
        # Parse webhook body
        body = await request.body()
        webhook_data = json.loads(body)
        
        # Log webhook for debugging
        event_type = webhook_data.get("webhookEvent", "unknown")
        print(f"\n=== Received Jira Webhook: {event_type} ===")
        
        # Route to appropriate handler
        if event_type == "jira:issue_created":
            result = await handle_issue_created(webhook_data, db)
            return result
        
        elif event_type == "sprint_created":
            result = await handle_sprint_created(webhook_data, db)
            return result
        
        elif event_type == "sprint_started":
            result = await handle_sprint_started(webhook_data, db)
            return result
        
        else:
            # Log unknown events but return success
            print(f"Unhandled webhook event: {event_type}")
            return {
                "status": "acknowledged",
                "event_type": event_type,
                "message": "Event type not processed"
            }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        print(f"Error processing Jira webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/github")
async def handle_github_webhook(request: Request):
    """
    Handle incoming GitHub webhooks.
    
    Supported events:
    - push - Process commits for skill extraction and profile evolution
    - pull_request - Process PR activity
    
    Pipeline for push events:
    1. Aggregate diffs from all commits (using ||| delimiter)
    2. Extract skills from combined diff via LLM
    3. Compare with user's existing skills
    4. Update user profile embeddings if new skills detected
    
    Configure your GitHub webhook to point to this endpoint.
    """
    from services.commit_service import CommitService
    
    try:
        db = get_db()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    
    try:
        # Get event type from header
        event_type = request.headers.get("X-GitHub-Event", "unknown")
        
        # Parse webhook body
        body = await request.body()
        webhook_data = json.loads(body)

        print(f"\n=== Received GitHub Webhook: {event_type} ===")
        print(f"Webhook data: {webhook_data}")
        
        # Extract GitHub username from webhook payload
        github_username = None
        pusher_email = None
        pusher_name = None
        
        if event_type == "push":
            github_username = webhook_data.get("pusher", {}).get("name")
            pusher_email = webhook_data.get("pusher", {}).get("email")
            pusher_name = github_username
        elif event_type == "pull_request":
            github_username = webhook_data.get("pull_request", {}).get("user", {}).get("login")
        else:
            # For other events, try sender
            github_username = webhook_data.get("sender", {}).get("login")
        
        # Check if a user with this GitHub username exists
        existing_user = None
        if github_username:
            existing_user = await db.find_one("users", {"github_username": github_username})
            if not existing_user:
                print(f"GitHub webhook ignored: No user found with github_username '{github_username}'")
                return {
                    "status": "ignored",
                    "event_type": event_type,
                    "message": f"No user found with GitHub username '{github_username}'"
                }
        else:
            print(f"GitHub webhook ignored: Could not extract GitHub username from payload")
            return {
                "status": "ignored",
                "event_type": event_type,
                "message": "Could not extract GitHub username from webhook payload"
            }
        
        print(f"\n=== Received GitHub Webhook: {event_type} ===")
        
        if event_type == "push":
            # Extract commits and repository info
            commits = webhook_data.get("commits", [])
            repository_data = webhook_data.get("repository", {})
            repository_name = repository_data.get("name", "unknown")
            repository_url = repository_data.get("html_url", "")
            ref = webhook_data.get("ref", "refs/heads/main")
            branch = ref.split("/")[-1] if "/" in ref else ref
            
            if not commits:
                return {
                    "status": "acknowledged",
                    "event_type": event_type,
                    "message": "No commits in push event"
                }
            
            # Auto-create or get project for this repository
            from services.project_service import ProjectService
            project_service = ProjectService(db)
            
            project = await project_service.get_or_create_project(
                name=repository_name,
                repo_url=repository_url
            )
            project_id = str(project["_id"])
            
            print(f"📦 Project: {repository_name} (ID: {project_id})")
            
            # Add user as contributor to this project
            user_id = str(existing_user["_id"])
            await project_service.add_contributor(project_id, user_id)
            
            # Aggregate all diffs from commits using ||| delimiter
            all_diffs = []
            all_messages = []
            for commit in commits:
                diff = commit.get("diff", "")
                if diff:
                    all_diffs.append(diff)
                all_messages.append(commit.get("message", ""))
            
            combined_diff = "|||".join(all_diffs) if all_diffs else ""
            combined_message = "\n".join(all_messages)
            
            # Use the user's email from the database, fallback to pusher email
            author_email = existing_user.get("email", pusher_email or "unknown@example.com")
            author_name = existing_user.get("name", pusher_name or "Unknown")
            
            # Create combined commit data for processing
            combined_commit = {
                "commit_hash": commits[-1].get("id", "unknown"),  # Use latest commit hash
                "commit_message": combined_message,
                "diff": combined_diff,
                "author_email": author_email,
                "author_name": author_name,
                "user_id": user_id,  # Explicitly pass the user_id we found
                "repository": repository_name,
                "branch": branch,
                "created_at": commits[-1].get("timestamp"),  # Extract timestamp from last commit
                "files_changed": sum(1 for c in commits for _ in [c.get("diff")] if c.get("diff")),
                "lines_added": sum(1 for line in combined_diff.split('\n') if line.startswith('+') and not line.startswith('+++')),
                "lines_deleted": sum(1 for line in combined_diff.split('\n') if line.startswith('-') and not line.startswith('---')),
                "project_id": project_id,  # Link to project
            }
            
            # Process through CommitService (handles skill extraction, profile update)
            service = CommitService(db)
            result = await service.process_commit(combined_commit)
            
            return {
                "status": "processed",
                "event_type": event_type,
                "repository": repository_name,
                "repository_url": repository_url,
                "project_id": project_id,
                "branch": branch,
                "commits_count": len(commits),
                "commit_id": result.get("commit_id"),
                "analysis": result.get("analysis"),
                "profile_update": result.get("profile_update"),
                "linked_task": result.get("linked_task"),
            }
        
        elif event_type == "pull_request":
            action = webhook_data.get("action")
            pr = webhook_data.get("pull_request", {})
            
            return {
                "status": "acknowledged",
                "event_type": event_type,
                "action": action,
                "pr_number": pr.get("number"),
                "pr_title": pr.get("title")
            }
        
        else:
            return {
                "status": "acknowledged",
                "event_type": event_type,
                "message": "Event type not processed"
            }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        print(f"Error processing GitHub webhook: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
