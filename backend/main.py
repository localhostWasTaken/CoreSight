"""
CoreSight API
AI-Driven Enterprise Delivery & Workforce Intelligence System

Version: 1.0.0 - Intelligence Engine
Hackathon: DataZen - Somaiya Vidyavihar University
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from utils.database import DatabaseManager
import utils

# Import routers from routes package
from routes import users, tasks, projects, linkedin, jobs, webhooks, issues, commits, analytics, auth

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
        
        # Set db_manager in utils for dependency injection
        utils.set_db_manager(db_manager)
        
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

# Include routers
app.include_router(auth.router)  # Auth first (no protection needed)
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(projects.router)
app.include_router(linkedin.router)
app.include_router(jobs.router)
app.include_router(webhooks.router)
app.include_router(issues.router)
app.include_router(commits.router)
app.include_router(analytics.router)


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


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
