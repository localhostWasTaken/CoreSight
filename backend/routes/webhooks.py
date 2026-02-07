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


router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


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
    - push - Process commits for skill extraction
    - pull_request - Process PR activity
    
    Configure your GitHub webhook to point to this endpoint.
    """
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
        
        if event_type == "push":
            # Extract commits from push event
            commits = webhook_data.get("commits", [])
            repository = webhook_data.get("repository", {}).get("name", "unknown")
            
            results = []
            for commit in commits:
                # Create commit record via the commits endpoint
                # This is a lightweight handler - actual processing happens in /api/commits
                results.append({
                    "commit_hash": commit.get("id"),
                    "message": commit.get("message"),
                    "author": commit.get("author", {}).get("email"),
                })
            
            return {
                "status": "processed",
                "event_type": event_type,
                "repository": repository,
                "commits_count": len(commits),
                "commits": results
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
        raise HTTPException(status_code=500, detail=str(e))
