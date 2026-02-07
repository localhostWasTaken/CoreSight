"""
CoreSight API
AI-Driven Enterprise Delivery & Workforce Intelligence System

Version: 1.0.0 - Intelligence Engine
Hackathon: DataZen - Somaiya Vidyavihar University
"""

import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from database import DatabaseManager
from jira_handlers import handle_issue_created, handle_sprint_created, handle_sprint_started

# Load environment variables
load_dotenv()

# Global database manager
db_manager: DatabaseManager = None
@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_manager
    
    print("CoreSight Intelligence Engine starting...")
    
    # Initialize MongoDB connection
    try:
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "coresight")
        
        print(f"Connecting to MongoDB: {mongodb_url}")
        mongo_client = AsyncIOMotorClient(mongodb_url)
        db = mongo_client[db_name]
        db_manager = DatabaseManager(db)
        
        # Test connection
        await db.command("ping")
        print("✅ MongoDB connected successfully")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("⚠️  Running without database - webhook processing will fail")
        db_manager = None
    
    yield
    
    print("CoreSight shutting down...")
    if db_manager:
        db_manager.close()


# Initialize FastAPI application
app = FastAPI(
    title="CoreSight Intelligence API",
    description="""
    ## AI-Driven Enterprise Delivery & Workforce Intelligence
    
    Transform raw engineering activity into **actionable business intelligence**.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """API root - service information."""
    return {
        "service": "CoreSight Intelligence API",
        "version": "1.0.0",
        "description": "AI-Driven Enterprise Delivery & Workforce Intelligence",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.post("/api/webhook/jira")
async def jira_webhook(request: Request):
    """
    Jira Webhook Endpoint
    
    Handles:
    - jira:issue_created - New issue created
    - jira:issue_updated - Issue updated
    - sprint:created - Sprint created
    - sprint:started - Sprint started
    """
    
    if not db_manager:
        return JSONResponse(
            status_code=503,
            content={"error": "Database not available"}
        )
    
    try:
        # Parse webhook payload
        body = await request.body()
        webhook_data = json.loads(body.decode('utf-8'))
        
        webhook_event = webhook_data.get("webhookEvent", "")
        
        print(f"\n{'='*60}")
        print(f"📥 Jira Webhook: {webhook_event}")
        print(f"{'='*60}")
        
        result = None
        
        # Route to appropriate handler
        if webhook_event == "jira:issue_created":
            result = await handle_issue_created(webhook_data, db_manager)
            
        elif webhook_event == "jira:issue_updated":
            # TODO: Implement issue update handler
            print("ℹ️  Issue updated - handler not yet implemented")
            result = {"status": "acknowledged", "event": "issue_updated"}
            
        elif webhook_event == "sprint:created":
            result = await handle_sprint_created(webhook_data, db_manager)
            
        elif webhook_event == "sprint:started":
            result = await handle_sprint_started(webhook_data, db_manager)
            
        else:
            print(f"⚠️  Unhandled webhook event: {webhook_event}")
            result = {"status": "unhandled", "event": webhook_event}
        
        print(f"\n✅ Webhook processed successfully")
        print(f"{'='*60}\n")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Webhook processed",
                "event": webhook_event,
                "result": result
            }
        )
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in webhook: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON payload"}
        )
        
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        import traceback
        traceback.print_exc()
        
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# === USER MANAGEMENT APIs ===

@app.post("/api/users")
async def create_user(request: Request):
    """
    Create a new user with skills
    
    Body:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "role": "employee",
        "hourly_rate": 75.0,
        "skills": ["Python", "FastAPI", "MongoDB"],
        "github_username": "johndoe",
        "jira_account_id": "..."
    }
    """
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        data = await request.json()
        
        # Generate work profile embeddings from skills
        from ai_utils import generate_embedding
        skills_text = ", ".join(data.get("skills", []))
        embeddings = generate_embedding(skills_text)
        
        user_doc = {
            "name": data["name"],
            "email": data["email"],
            "role": data.get("role", "employee"),
            "hourly_rate": data.get("hourly_rate", 50.0),
            "skills": data.get("skills", []),
            "work_profile_embeddings": embeddings,
            "project_metrics": {},
            "github_username": data.get("github_username"),
            "jira_account_id": data.get("jira_account_id"),
        }
        
        user_id = await db_manager.insert_one("users", user_doc)
        
        return JSONResponse(
            status_code=201,
            content={
                "user_id": str(user_id),
                "message": "User created successfully"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users")
async def list_users():
    """List all users"""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    users = await db_manager.find_many("users", {})
    
    return JSONResponse(content={
        "count": len(users),
        "users": [
            {
                "id": str(u["_id"]),
                "name": u.get("name"),
                "email": u.get("email"),
                "skills": u.get("skills", []),
                "role": u.get("role")
            }
            for u in users
        ]
    })


@app.get("/api/tasks")
async def list_tasks():
    """List all tasks"""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    tasks = await db_manager.find_many("tasks", {})
    
    return JSONResponse(content={
        "count": len(tasks),
        "tasks": [
            {
                "id": str(t["_id"]),
                "external_id": t.get("external_id"),
                "title": t.get("title"),
                "status": t.get("status"),
                "priority": t.get("priority"),
                "assignees": t.get("current_assignee_ids", []),
            }
            for t in tasks
        ]
    })


@app.get("/api/tasks/{task_id}/recommendations")
async def get_task_recommendations(task_id: str):
    """
    Get recommended users for a task
    """
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        from bson import ObjectId
        from ai_utils import extract_skills_from_task, find_best_matching_users
        
        # Get task
        task = await db_manager.find_one("tasks", {"_id": ObjectId(task_id)})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Extract skills
        skills = extract_skills_from_task(
            task.get("title", ""),
            task.get("description"),
            "Project"
        )
        
        # Get all users
        users = await db_manager.find_many("users", {})
        users_list = [
            {
                "_id": u["_id"],
                "name": u.get("name"),
                "email": u.get("email"),
                "skills": u.get("skills", []),
                "work_profile_embeddings": u.get("work_profile_embeddings", []),
                "hourly_rate": u.get("hourly_rate", 50.0),
            }
            for u in users
        ]
        
        # Find matches
        matches = find_best_matching_users(
            skills,
            task.get("description_embeddings", []),
            users_list,
            top_n=10
        )
        
        return JSONResponse(content={
            "task_id": task_id,
            "required_skills": skills,
            "recommendations": [
                {
                    "user_id": str(m["_id"]),
                    "name": m["name"],
                    "match_score": m["match_score"],
                    "skill_similarity": m["skill_similarity"],
                    "user_skills": m["skills"]
                }
                for m in matches
            ]
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects")
async def list_projects():
    """List all projects"""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    projects = await db_manager.find_many("projects", {})
    
    return JSONResponse(content={
        "count": len(projects),
        "projects": [
            {
                "id": str(p["_id"]),
                "name": p.get("name"),
                "repo_url": p.get("repo_url"),
                "total_budget": p.get("total_budget", 0.0)
            }
            for p in projects
        ]
    })


@app.get("/api/sprints")
async def list_sprints():
    """List all sprints"""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    sprints = await db_manager.find_many("sprints", {})
    
    return JSONResponse(content={
        "count": len(sprints),
        "sprints": [
            {
                "id": str(s["_id"]),
                "name": s.get("name"),
                "project_id": s.get("project_id"),
                "is_active": s.get("is_active", False),
                "start_date": s.get("start_date").isoformat() if s.get("start_date") else None,
                "end_date": s.get("end_date").isoformat() if s.get("end_date") else None,
            }
            for s in sprints
        ]
    })


# === LINKEDIN INTEGRATION APIs ===

@app.get("/api/linkedin/search")
async def search_linkedin_parameters(
    type: str,
    query: str,
    limit: int = 10
):
    """
    Search LinkedIn for autocomplete parameters
    
    Use this to populate UI dropdowns for:
    - LOCATION: Geographic locations for job posting
    - JOB_TITLE: Standard LinkedIn job titles
    - COMPANY: Companies
    - INDUSTRY: Industries
    
    Query params:
        type: One of LOCATION, JOB_TITLE, COMPANY, INDUSTRY
        query: Search string
        limit: Max results (default 10)
    """
    try:
        from linkedin_service import LinkedinSearchType, get_unipile_client
        
        # Validate type
        try:
            search_type = LinkedinSearchType(type.upper())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid search type. Must be one of: {[t.value for t in LinkedinSearchType]}"
            )
        
        client = get_unipile_client()
        result = await client.search_linkedin_parameters(search_type, query, limit)
        
        return JSONResponse(content={
            "type": search_type.value,
            "query": query,
            "results": [r.model_dump() for r in result.results],
            "total_count": result.total_count
        })
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"LinkedIn search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === JOB REQUISITION APIs ===

@app.get("/api/jobs/requisitions")
async def list_job_requisitions(status: str = None):
    """
    List all job requisitions.
    
    Query params:
        status: Optional filter by status (pending, ready, posted, closed)
    """
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    filter_dict = {}
    if status:
        filter_dict["status"] = status
    
    requisitions = await db_manager.find_many("job_requisitions", filter_dict)
    
    return JSONResponse(content={
        "count": len(requisitions),
        "requisitions": [
            {
                "id": str(r["_id"]),
                "suggested_title": r.get("suggested_title"),
                "required_skills": r.get("required_skills", []),
                "status": r.get("status"),
                "linkedin_job_title_text": r.get("linkedin_job_title_text"),
                "linkedin_location_text": r.get("linkedin_location_text"),
                "workplace_type": r.get("workplace_type"),
                "employment_type": r.get("employment_type"),
                "created_at": r.get("created_at").isoformat() if r.get("created_at") else None,
                "task_id": r.get("task_id"),
            }
            for r in requisitions
        ]
    })


@app.get("/api/jobs/requisitions/{requisition_id}")
async def get_job_requisition(requisition_id: str):
    """Get a specific job requisition by ID"""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    from bson import ObjectId
    
    try:
        requisition = await db_manager.find_one(
            "job_requisitions",
            {"_id": ObjectId(requisition_id)}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid requisition ID")
    
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")
    
    return JSONResponse(content={
        "id": str(requisition["_id"]),
        "task_id": requisition.get("task_id"),
        "suggested_title": requisition.get("suggested_title"),
        "description": requisition.get("description"),
        "required_skills": requisition.get("required_skills", []),
        "linkedin_job_title_id": requisition.get("linkedin_job_title_id"),
        "linkedin_job_title_text": requisition.get("linkedin_job_title_text"),
        "linkedin_location_id": requisition.get("linkedin_location_id"),
        "linkedin_location_text": requisition.get("linkedin_location_text"),
        "workplace_type": requisition.get("workplace_type"),
        "employment_type": requisition.get("employment_type"),
        "status": requisition.get("status"),
        "linkedin_job_id": requisition.get("linkedin_job_id"),
        "created_at": requisition.get("created_at").isoformat() if requisition.get("created_at") else None,
        "updated_at": requisition.get("updated_at").isoformat() if requisition.get("updated_at") else None,
    })


@app.patch("/api/jobs/requisitions/{requisition_id}")
async def update_job_requisition(requisition_id: str, request: Request):
    """
    Update a job requisition with LinkedIn search values.
    
    Body (all optional):
    {
        "linkedin_job_title_id": "from search API",
        "linkedin_job_title_text": "Software Engineer",
        "linkedin_location_id": "from search API",
        "linkedin_location_text": "San Francisco, CA",
        "workplace_type": "ON_SITE" | "REMOTE" | "HYBRID",
        "employment_type": "FULL_TIME" | "PART_TIME" | "CONTRACT" | "INTERNSHIP"
    }
    """
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    from bson import ObjectId
    from datetime import datetime
    
    try:
        requisition = await db_manager.find_one(
            "job_requisitions",
            {"_id": ObjectId(requisition_id)}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid requisition ID")
    
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")
    
    if requisition.get("status") == "posted":
        raise HTTPException(status_code=400, detail="Cannot update a posted job requisition")
    
    data = await request.json()
    
    # Build update dict with allowed fields
    allowed_fields = [
        "linkedin_job_title_id", "linkedin_job_title_text",
        "linkedin_location_id", "linkedin_location_text",
        "workplace_type", "employment_type"
    ]
    
    update_dict = {k: v for k, v in data.items() if k in allowed_fields}
    update_dict["updated_at"] = datetime.utcnow()
    
    # Check if ready to post (all required fields filled)
    updated_req = {**requisition, **update_dict}
    if (updated_req.get("linkedin_job_title_id") and 
        updated_req.get("linkedin_location_id")):
        update_dict["status"] = "ready"
    
    await db_manager.update_one(
        "job_requisitions",
        {"_id": ObjectId(requisition_id)},
        update_dict
    )
    
    return JSONResponse(content={
        "message": "Requisition updated successfully",
        "requisition_id": requisition_id,
        "status": update_dict.get("status", requisition.get("status"))
    })


@app.post("/api/jobs/requisitions/{requisition_id}/post")
async def post_job_to_linkedin(requisition_id: str):
    """
    Post a job requisition to LinkedIn via Unipile.
    
    Requisition must be in "ready" status with all LinkedIn fields filled.
    """
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    from bson import ObjectId
    from datetime import datetime
    from linkedin_service import get_unipile_client, WorkplaceType, EmploymentType
    
    try:
        requisition = await db_manager.find_one(
            "job_requisitions",
            {"_id": ObjectId(requisition_id)}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid requisition ID")
    
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")
    
    if requisition.get("status") == "posted":
        raise HTTPException(status_code=400, detail="Job already posted")
    
    # Validate required fields
    if not requisition.get("linkedin_job_title_id"):
        raise HTTPException(
            status_code=400,
            detail="Missing linkedin_job_title_id. Use /api/linkedin/search?type=JOB_TITLE to find one."
        )
    
    if not requisition.get("linkedin_location_id"):
        raise HTTPException(
            status_code=400,
            detail="Missing linkedin_location_id. Use /api/linkedin/search?type=LOCATION to find one."
        )
    
    try:
        client = get_unipile_client()
        
        # Map workplace and employment types
        workplace = WorkplaceType(requisition.get("workplace_type", "ON_SITE"))
        employment = EmploymentType(requisition.get("employment_type", "FULL_TIME"))
        
        # Create job posting
        result = await client.create_job_posting(
            job_title_id=requisition["linkedin_job_title_id"],
            location_id=requisition["linkedin_location_id"],
            description=requisition.get("description", ""),
            workplace_type=workplace,
            employment_type=employment
        )
        
        # Update requisition with job ID and posted status
        await db_manager.update_one(
            "job_requisitions",
            {"_id": ObjectId(requisition_id)},
            {
                "status": "posted",
                "linkedin_job_id": result.job_id,
                "updated_at": datetime.utcnow()
            }
        )
        
        return JSONResponse(content={
            "message": "Job posted to LinkedIn successfully",
            "requisition_id": requisition_id,
            "linkedin_job_id": result.job_id,
            "status": "posted"
        })
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error posting job to LinkedIn: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# === AI-POWERED ISSUE AND COMMIT ENDPOINTS ===

@app.post("/api/issues")
async def create_issue_with_ai(request: Request):
    """
    POST /issues - AI-Powered Issue Processing
    
    Handles intelligent issue creation with:
    - Duplicate detection via vector similarity
    - LLM-powered reasoning for existing vs new issues
    - Automatic skill extraction and developer matching
    - Job posting trigger for unmatched skills
    
    Body:
    {
        "title": "Issue title",
        "description": "Detailed issue description",
        "priority": "high|medium|low",
        "project_id": "optional_project_id",
        "source": "api|jira|github",
        "external_id": "optional_external_reference"
    }
    """
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        from ai_utils import (
            generate_embedding,
            extract_skills_from_task,
            check_issue_duplicate_with_llm
        )
        from vector_search import (
            search_similar_issues,
            find_matching_users_by_skills,
            create_issue_document,
            update_issue
        )
        from datetime import datetime
        
        data = await request.json()
        
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        
        if not title or not description:
            raise HTTPException(
                status_code=400,
                detail="Title and description are required"
            )
        
        print(f"\n{'='*60}")
        print(f"📥 Processing New Issue: {title}")
        print(f"{'='*60}")
        
        # Step 1: Generate embedding for the issue
        print("🔄 Step 1: Generating embeddings...")
        combined_text = f"{title} {description}"
        issue_embedding = generate_embedding(combined_text)
        
        # Step 2: Search for similar existing issues
        print("🔍 Step 2: Searching for similar issues...")
        similar_issues = await search_similar_issues(
            db_manager,
            issue_embedding,
            top_k=5,
            min_similarity=0.7
        )
        
        print(f"   Found {len(similar_issues)} similar issues")
        
        # Step 3: Use LLM to determine if duplicate
        print("🤖 Step 3: LLM analysis for duplicate detection...")
        llm_analysis = await check_issue_duplicate_with_llm(
            title,
            description,
            similar_issues
        )
        
        print(f"   Is Duplicate: {llm_analysis['is_duplicate']}")
        print(f"   Confidence: {llm_analysis['confidence']:.2%}")
        print(f"   Reasoning: {llm_analysis['reasoning']}")
        
        response_data = {
            "analysis": llm_analysis,
            "similar_issues_found": len(similar_issues)
        }
        
        # Scenario A: Duplicate/Existing Issue
        if llm_analysis["is_duplicate"] and llm_analysis["parent_task_id"]:
            print("📌 Scenario A: Duplicate Issue Detected")
            
            parent_task_id = llm_analysis["parent_task_id"]
            
            # Update activity log
            activity_entry = f"[{datetime.utcnow().isoformat()}] Related issue reported: {title}"
            
            update_data = {
                "updated_at": datetime.utcnow()
            }
            
            # Check if priority changed
            if llm_analysis.get("priority_change"):
                new_priority = data.get("priority", "medium")
                update_data["priority"] = new_priority
                activity_entry += f" | Priority updated to: {new_priority}"
                print(f"   ⚠️  Priority changed: {llm_analysis['priority_change']}")
            
            # Check if new skills required
            if llm_analysis.get("new_skills_required"):
                new_skills = llm_analysis["new_skills_required"]
                print(f"   🎯 New skills required: {new_skills}")
                
                # Generate new skill embedding
                skills_text = ", ".join(new_skills)
                new_skill_embedding = generate_embedding(skills_text)
                update_data["required_skills"] = new_skills
                update_data["skill_embeddings"] = new_skill_embedding
                
                # Re-embed description if needed
                update_data["description_embedding"] = issue_embedding
                
                activity_entry += f" | New skills added: {', '.join(new_skills)}"
            
            # Update the parent issue
            await db_manager.update_one_raw(
                "issues",
                {"_id": ObjectId(parent_task_id)},
                {
                    "$set": update_data,
                    "$push": {"activity_log": activity_entry}
                }
            )
            
            response_data["action"] = "updated_existing"
            response_data["parent_task_id"] = parent_task_id
            response_data["message"] = "Duplicate issue - parent task updated"
            
            print(f"✅ Parent task {parent_task_id} updated")
        
        # Scenario B: New Issue
        else:
            print("🆕 Scenario B: New Issue")
            
            # Extract required skills
            print("🎯 Step 4: Extracting required skills...")
            required_skills = extract_skills_from_task(
                title,
                description,
                "Project"
            )
            print(f"   Skills: {required_skills}")
            
            # Generate skill embeddings
            skills_text = ", ".join(required_skills)
            skill_embedding = generate_embedding(skills_text)
            
            # Create new issue document
            issue_doc = {
                "title": title,
                "description": description,
                "description_embedding": issue_embedding,
                "required_skills": required_skills,
                "skill_embeddings": skill_embedding,
                "priority": data.get("priority", "medium"),
                "is_duplicate": False,
                "parent_task_id": None,
                "assigned_user_id": None,
                "assignment_status": "pending",
                "activity_log": [f"[{datetime.utcnow().isoformat()}] Issue created"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "source": data.get("source", "api"),
                "external_id": data.get("external_id"),
                "project_id": data.get("project_id")
            }
            
            issue_id = await create_issue_document(db_manager, issue_doc)
            
            print(f"✅ Issue created: {issue_id}")
            
            # Step 5: Match skills against developers
            print("👥 Step 5: Matching with developers...")
            matching_users = await find_matching_users_by_skills(
                db_manager,
                required_skills,
                skill_embedding,
                top_k=5,
                min_similarity=0.5
            )
            
            print(f"   Found {len(matching_users)} matching developers")
            
            # Assign or trigger job posting
            if matching_users and len(matching_users) > 0:
                best_match = matching_users[0]
                user_id = str(best_match["_id"])
                match_score = best_match["match_score"]
                
                print(f"   ✅ Best match: {best_match['name']} (score: {match_score:.2%})")
                
                # Assign the task
                await update_issue(
                    db_manager,
                    issue_id,
                    {
                        "assigned_user_id": user_id,
                        "assignment_status": "assigned"
                    }
                )
                
                response_data["action"] = "created_and_assigned"
                response_data["assigned_to"] = {
                    "user_id": user_id,
                    "name": best_match["name"],
                    "match_score": match_score
                }
                response_data["matching_candidates"] = [
                    {
                        "user_id": str(u["_id"]),
                        "name": u["name"],
                        "match_score": u["match_score"],
                        "skills": u["skills"]
                    }
                    for u in matching_users[:3]
                ]
            else:
                print("   ⚠️  No matching developers found")
                
                # Trigger job posting placeholder
                job_posting_result = trigger_job_posting(
                    required_skills,
                    title,
                    description
                )
                
                await update_issue(
                    db_manager,
                    issue_id,
                    {
                        "assignment_status": "posting_required"
                    }
                )
                
                response_data["action"] = "created_requires_posting"
                response_data["job_posting"] = job_posting_result
            
            response_data["issue_id"] = issue_id
            response_data["required_skills"] = required_skills
        
        print(f"{'='*60}\n")
        
        return JSONResponse(
            status_code=201,
            content=response_data
        )
        
    except Exception as e:
        print(f"❌ Error processing issue: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/commits")
async def process_commit_with_ai(request: Request):
    """
    POST /commits - AI-Powered Commit Analysis
    
    Handles intelligent commit processing with:
    - LLM-based diff analysis and skill extraction
    - Task linking via vector similarity search
    - Developer profile evolution tracking
    - Automatic profile updates based on new skills
    
    Body:
    {
        "commit_hash": "abc123",
        "commit_message": "Implemented user authentication",
        "diff": "git diff content...",
        "author_email": "dev@example.com",
        "author_name": "Developer Name",
        "repository": "my-repo",
        "branch": "main",
        "files_changed": 5,
        "lines_added": 120,
        "lines_deleted": 30
    }
    """
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        from ai_utils import (
            generate_embedding,
            extract_skills_from_commit_diff,
            check_profile_update_needed
        )
        from vector_search import (
            search_similar_tasks_for_commit,
            find_user_by_email,
            create_commit_document,
            update_user_profile
        )
        from datetime import datetime
        
        data = await request.json()
        
        commit_hash = data.get("commit_hash", "").strip()
        commit_message = data.get("commit_message", "").strip()
        diff_content = data.get("diff", "").strip()
        author_email = data.get("author_email", "").strip()
        
        if not commit_hash or not author_email:
            raise HTTPException(
                status_code=400,
                detail="commit_hash and author_email are required"
            )
        
        print(f"\n{'='*60}")
        print(f"📥 Processing Commit: {commit_hash[:8]}")
        print(f"   Author: {author_email}")
        print(f"{'='*60}")
        
        # Step 1: LLM extracts summary and skills
        print("🤖 Step 1: Analyzing commit with LLM...")
        llm_extraction = await extract_skills_from_commit_diff(
            commit_message,
            diff_content,
            data.get("repository", "unknown")
        )
        
        summary = llm_extraction["summary"]
        extracted_skills = llm_extraction["skills_used"]
        impact = llm_extraction["impact_assessment"]
        
        print(f"   Summary: {summary}")
        print(f"   Skills: {extracted_skills}")
        print(f"   Impact: {impact}")
        
        # Step 2: Generate embedding for summary
        print("🔄 Step 2: Generating embeddings...")
        summary_embedding = generate_embedding(summary)
        
        # Step 3: Search for matching tasks
        print("🔍 Step 3: Searching for related tasks...")
        matching_tasks = await search_similar_tasks_for_commit(
            db_manager,
            summary_embedding,
            top_k=3,
            min_similarity=0.6
        )
        
        print(f"   Found {len(matching_tasks)} similar tasks")
        
        # Determine task linking
        linked_task_id = None
        is_jira_tracked = False
        
        if matching_tasks and len(matching_tasks) > 0:
            best_match = matching_tasks[0]
            similarity = best_match.get("similarity_score", 0)
            
            # Link if similarity is high enough
            if similarity >= 0.7:
                linked_task_id = str(best_match["_id"])
                is_jira_tracked = True
                print(f"   ✅ Linked to task: {best_match.get('external_id', linked_task_id)} (similarity: {similarity:.2%})")
            else:
                print(f"   ℹ️  Best match similarity too low: {similarity:.2%}")
        
        if not is_jira_tracked:
            print("   📌 Logged as Non-Jira Tracked Activity")
        
        # Step 4: Find user and check profile evolution
        print("👤 Step 4: Checking user profile...")
        user = await find_user_by_email(db_manager, author_email)
        
        profile_update_result = None
        triggered_profile_update = False
        
        if user:
            user_id = str(user["_id"])
            user_name = user.get("name", "Unknown")
            current_skills = user.get("skills", [])
            current_profile = user.get("profile_text", "")
            
            print(f"   Found user: {user_name}")
            print(f"   Current skills: {current_skills}")
            
            # Check if profile needs updating
            print("🔄 Step 5: Checking if profile update needed...")
            profile_analysis = await check_profile_update_needed(
                current_profile,
                current_skills,
                extracted_skills,
                summary
            )
            
            print(f"   Needs Update: {profile_analysis['needs_update']}")
            print(f"   Reasoning: {profile_analysis['reasoning']}")
            
            if profile_analysis["needs_update"]:
                new_skills_to_add = profile_analysis.get("new_skills_to_add", [])
                updated_profile_text = profile_analysis.get("updated_profile_text")
                
                # Merge skills (avoid duplicates)
                updated_skills = list(set(current_skills + new_skills_to_add))
                
                # Generate new profile embedding
                skills_text = ", ".join(updated_skills)
                new_profile_embedding = generate_embedding(skills_text)
                
                # Update user profile
                success = await update_user_profile(
                    db_manager,
                    user_id,
                    updated_skills,
                    new_profile_embedding,
                    updated_profile_text
                )
                
                if success:
                    triggered_profile_update = True
                    print(f"   ✅ Profile updated with new skills: {new_skills_to_add}")
                    
                    profile_update_result = {
                        "updated": True,
                        "new_skills_added": new_skills_to_add,
                        "total_skills": len(updated_skills)
                    }
                else:
                    print("   ⚠️  Profile update failed")
            else:
                print("   ℹ️  No profile update needed")
                profile_update_result = {
                    "updated": False,
                    "reasoning": profile_analysis["reasoning"]
                }
        else:
            user_id = None
            print(f"   ⚠️  User not found for email: {author_email}")
        
        # Step 6: Create commit document
        print("💾 Step 6: Saving commit record...")
        commit_doc = {
            "commit_hash": commit_hash,
            "commit_message": commit_message,
            "diff_content": diff_content,
            "summary": summary,
            "extracted_skills": extracted_skills,
            "summary_embedding": summary_embedding,
            "linked_task_id": linked_task_id,
            "is_jira_tracked": is_jira_tracked,
            "author_email": author_email,
            "author_name": data.get("author_name", ""),
            "user_id": user_id,
            "repository": data.get("repository", ""),
            "branch": data.get("branch", ""),
            "timestamp": datetime.utcnow(),
            "files_changed": data.get("files_changed", 0),
            "lines_added": data.get("lines_added", 0),
            "lines_deleted": data.get("lines_deleted", 0),
            "triggered_profile_update": triggered_profile_update,
            "created_at": datetime.utcnow()
        }
        
        commit_id = await create_commit_document(db_manager, commit_doc)
        
        print(f"✅ Commit record created: {commit_id}")
        print(f"{'='*60}\n")
        
        # Build response
        response_data = {
            "commit_id": commit_id,
            "commit_hash": commit_hash,
            "analysis": {
                "summary": summary,
                "skills_extracted": extracted_skills,
                "impact_assessment": impact
            },
            "task_linking": {
                "linked_task_id": linked_task_id,
                "is_jira_tracked": is_jira_tracked,
                "matching_tasks_found": len(matching_tasks)
            },
            "profile_evolution": profile_update_result
        }
        
        if matching_tasks:
            response_data["task_linking"]["similar_tasks"] = [
                {
                    "task_id": str(t["_id"]),
                    "external_id": t.get("external_id"),
                    "title": t.get("title"),
                    "similarity_score": t.get("similarity_score", 0)
                }
                for t in matching_tasks[:3]
            ]
        
        return JSONResponse(
            status_code=201,
            content=response_data
        )
        
    except Exception as e:
        print(f"❌ Error processing commit: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def trigger_job_posting(required_skills: List[str], title: str, description: str) -> Dict:
    """
    Placeholder function for triggering job posting
    
    In production, this would:
    - Create a job posting in an ATS system
    - Post to job boards
    - Trigger recruiter notifications
    - etc.
    """
    print(f"\n🚨 JOB POSTING TRIGGERED 🚨")
    print(f"   Position: {title}")
    print(f"   Required Skills: {', '.join(required_skills)}")
    print(f"   Description: {description[:100]}...")
    
    return {
        "triggered": True,
        "job_title": title,
        "required_skills": required_skills,
        "status": "pending_recruiter_review",
        "message": "Job posting will be created by recruiter"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

