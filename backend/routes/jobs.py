"""
Jobs Router for CoreSight

Handles job requisition management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from utils import get_db, serialize_doc
from services.job_service import JobService


router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


# Request models
class JobRequisitionUpdate(BaseModel):
    linkedin_job_title_id: Optional[str] = None
    linkedin_job_title_text: Optional[str] = None
    linkedin_location_id: Optional[str] = None
    linkedin_location_text: Optional[str] = None
    workplace_type: Optional[str] = None
    employment_type: Optional[str] = None


# Endpoints
@router.get("/requisitions", response_model=List[dict])
async def list_job_requisitions(
    status: Optional[str] = Query(None, description="Filter by status: pending, ready, posted, closed")
):
    """
    List all job requisitions.
    
    Job requisitions are created automatically when no matching developers
    are found for a task.
    """
    try:
        db = get_db()
        service = JobService(db)
        
        requisitions = await service.list_job_requisitions(status)
        
        return [serialize_doc(r) for r in requisitions]
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/requisitions/{requisition_id}", response_model=dict)
async def get_job_requisition(requisition_id: str):
    """
    Get a specific job requisition by ID.
    """
    try:
        db = get_db()
        service = JobService(db)
        
        requisition = await service.get_job_requisition(requisition_id)
        
        if not requisition:
            raise HTTPException(status_code=404, detail="Job requisition not found")
        
        return serialize_doc(requisition)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.patch("/requisitions/{requisition_id}", response_model=dict)
async def update_job_requisition(requisition_id: str, update: JobRequisitionUpdate):
    """
    Update a job requisition with LinkedIn search parameters.
    
    Use /api/linkedin/search/locations and /api/linkedin/search/job-titles
    to find the correct IDs for the LinkedIn fields.
    
    Once both linkedin_job_title_id and linkedin_location_id are set,
    the status will automatically change to 'ready'.
    """
    try:
        db = get_db()
        service = JobService(db)
        
        # Filter out None values
        update_data = {k: v for k, v in update.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        success = await service.update_job_requisition(requisition_id, update_data)
        
        if not success:
            raise HTTPException(status_code=404, detail="Job requisition not found")
        
        # Get updated requisition
        requisition = await service.get_job_requisition(requisition_id)
        
        return {
            "message": "Job requisition updated successfully",
            "requisition": serialize_doc(requisition)
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/requisitions/{requisition_id}/post", response_model=dict)
async def post_job_to_linkedin(requisition_id: str):
    """
    Post a job requisition to LinkedIn.
    
    The requisition must have status 'ready' (both LinkedIn job title
    and location must be set).
    """
    try:
        db = get_db()
        service = JobService(db)
        
        result = await service.post_job_to_linkedin(requisition_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return {
            "message": "Job posted to LinkedIn successfully",
            "job_id": result.get("job_id"),
            "status": result.get("status")
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.delete("/requisitions/{requisition_id}", response_model=dict)
async def delete_job_requisition(requisition_id: str):
    """
    Delete a job requisition.
    """
    try:
        db = get_db()
        service = JobService(db)
        
        success = await service.delete_job_requisition(requisition_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Job requisition not found")
        
        return {"message": "Job requisition deleted successfully"}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
