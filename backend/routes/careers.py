"""
Public Careers Router for CoreSight

Public-facing API endpoints for job listings.
No authentication required.
"""

from typing import List
from fastapi import APIRouter, HTTPException

from utils import get_db, serialize_doc


router = APIRouter(prefix="/api/public", tags=["Public"])


@router.get("/careers", response_model=List[dict])
async def get_public_careers():
    """
    Get all active job listings for public careers page.
    
    Returns job requisitions where admin_approved is True.
    No authentication required.
    """
    try:
        db = get_db()
        
        # Query for admin-approved job requisitions
        jobs = await db.find_many(
            "job_requisitions",
            {"admin_approved": True}
        )
        
        # Return minimal public-facing data
        public_jobs = []
        for job in jobs:
            public_jobs.append({
                "_id": str(job.get("_id")),
                "title": job.get("suggested_title", ""),
                "description": job.get("description", ""),
                "required_skills": job.get("required_skills", []),
                "location": job.get("location", ""),
                "workplace_type": job.get("workplace_type", "ON_SITE"),
                "employment_type": job.get("employment_type", "FULL_TIME"),
            })
        
        return public_jobs
        
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
