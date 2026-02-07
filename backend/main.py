"""
CoreSight API
AI-Driven Enterprise Delivery & Workforce Intelligence System

Version: 1.0.0 - Intelligence Engine
Hackathon: DataZen - Somaiya Vidyavihar University
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("CoreSight Intelligence Engine starting...")
    # Initialize database on startup
    try:
        from models.database import init_db
        init_db()
        print("Database initialized")
    except Exception as e:
        print(f"Database init skipped: {e}")
    yield
    print("CoreSight shutting down")


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
    print("Jira webhook received")
    print(await request.body())
    return JSONResponse(status_code=200, content={"message": "Jira webhook received successfully"})    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        port=8000,
        reload=True
    )
