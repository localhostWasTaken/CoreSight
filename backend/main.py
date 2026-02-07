"""
CoreSight API
AI-Driven Enterprise Delivery & Workforce Intelligence System

Version: 1.0.0 - Intelligence Engine
Hackathon: DataZen - Somaiya Vidyavihar University
"""

import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        port=8080,
        reload=True
    )
