"""
Job Service for CoreSight

Handles job requisition management and LinkedIn job posting.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from bson import ObjectId

from utils.database import DatabaseManager
from .linkedin_service import (
    UnipileClient,
    get_unipile_client,
    WorkplaceType,
    EmploymentType,
)


class JobService:
    """Service class for job requisition operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.linkedin_client = get_unipile_client()
    
    async def create_job_requisition(
        self,
        task_id: Optional[str],
        suggested_title: str,
        description: str,
        required_skills: List[str],
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Create a new job requisition.
        
        Args:
            task_id: Related task ID (optional)
            suggested_title: LLM-suggested job title
            description: Job description (HTML)
            required_skills: List of required skills
            created_by: Who created this requisition
            
        Returns:
            Created requisition document
        """
        now = datetime.utcnow()
        
        requisition_doc = {
            "task_id": task_id,
            "suggested_title": suggested_title,
            "description": description,
            "required_skills": required_skills,
            "linkedin_job_title_id": None,
            "linkedin_job_title_text": None,
            "linkedin_location_id": None,
            "linkedin_location_text": None,
            "workplace_type": "ON_SITE",
            "employment_type": "FULL_TIME",
            "status": "pending",
            "linkedin_job_id": None,
            "created_at": now,
            "updated_at": now,
            "created_by": created_by,
        }
        
        requisition_id = await self.db.insert_one("job_requisitions", requisition_doc)
        requisition_doc["_id"] = requisition_id
        
        return requisition_doc
    
    async def get_job_requisition(self, requisition_id: str) -> Optional[Dict[str, Any]]:
        """Get a job requisition by ID"""
        try:
            return await self.db.find_one("job_requisitions", {"_id": ObjectId(requisition_id)})
        except Exception:
            return None
    
    async def list_job_requisitions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List job requisitions, optionally filtered by status"""
        filters = {}
        if status:
            filters["status"] = status
        return await self.db.find_many("job_requisitions", filters)
    
    async def update_job_requisition(
        self,
        requisition_id: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """
        Update a job requisition.
        
        Args:
            requisition_id: Requisition ID
            update_data: Fields to update
            
        Returns:
            True if updated
        """
        update_data["updated_at"] = datetime.utcnow()
        
        # Check if requisition is ready to post
        if update_data.get("linkedin_job_title_id") and update_data.get("linkedin_location_id"):
            update_data["status"] = "ready"
        
        return await self.db.update_one(
            "job_requisitions",
            {"_id": ObjectId(requisition_id)},
            update_data
        )
    
    async def post_job_to_linkedin(self, requisition_id: str) -> Dict[str, Any]:
        """
        Post a job requisition to LinkedIn.
        
        Args:
            requisition_id: Requisition ID to post
            
        Returns:
            Result with job_id and status
        """
        requisition = await self.get_job_requisition(requisition_id)
        if not requisition:
            raise ValueError("Job requisition not found")
        
        # Validate required fields
        if not requisition.get("linkedin_job_title_id"):
            raise ValueError("LinkedIn job title not selected")
        if not requisition.get("linkedin_location_id"):
            raise ValueError("LinkedIn location not selected")
        
        # Create job posting on LinkedIn
        try:
            workplace_type = WorkplaceType(requisition.get("workplace_type", "ON_SITE"))
            employment_type = EmploymentType(requisition.get("employment_type", "FULL_TIME"))
            
            result = await self.linkedin_client.create_job_posting(
                job_title_id=requisition["linkedin_job_title_id"],
                location_id=requisition["linkedin_location_id"],
                description=requisition["description"],
                workplace_type=workplace_type,
                employment_type=employment_type,
            )
            
            # Update requisition with LinkedIn job ID
            await self.db.update_one(
                "job_requisitions",
                {"_id": ObjectId(requisition_id)},
                {
                    "linkedin_job_id": result.job_id,
                    "status": "posted",
                    "updated_at": datetime.utcnow(),
                }
            )
            
            return {
                "success": True,
                "job_id": result.job_id,
                "status": "posted"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def approve_job_requisition(self, requisition_id: str) -> bool:
        """
        Approve a job requisition.
        
        Args:
            requisition_id: Requisition ID to approve
            
        Returns:
            True if approved successfully
        """
        requisition = await self.get_job_requisition(requisition_id)
        if not requisition:
            return False
        
        return await self.db.update_one(
            "job_requisitions",
            {"_id": ObjectId(requisition_id)},
            {
                "admin_approved": True,
                "updated_at": datetime.utcnow(),
            }
        )
    
    async def delete_job_requisition(self, requisition_id: str) -> bool:
        """Delete a job requisition"""
        return await self.db.delete_one("job_requisitions", {"_id": ObjectId(requisition_id)})


# Convenience function for creating requisitions from no-match reports
async def create_job_requisition_from_report(
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
    service = JobService(db)
    requisition = await service.create_job_requisition(
        task_id=task_id,
        suggested_title=report.get("suggested_job_title", f"Developer - {required_skills[0]}"),
        description=report.get("suggested_job_description", ""),
        required_skills=required_skills,
        created_by="system"
    )
    return str(requisition["_id"])
