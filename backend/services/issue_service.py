"""
Issue Service for CoreSight

Handles issue creation with AI-powered duplicate detection,
skill extraction, and user matching.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from bson import ObjectId

from utils.database import DatabaseManager
from ai import (
    generate_embedding,
    extract_skills_from_task,
    find_best_matching_users,
    validate_user_assignment_with_llm,
    evaluate_candidates_batch,
    generate_no_match_report,
    check_issue_duplicate_with_llm,
)
from utils import search_similar_issues
from services.job_service import create_job_requisition_from_report


class IssueService:
    """Service class for issue operations with AI analysis"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    async def create_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new issue with full AI analysis pipeline.
        
        Pipeline:
        1. Generate embeddings for issue description
        2. Search for similar issues (duplicate detection)
        3. Use LLM to confirm if duplicate
        4. Extract required skills
        5. Find matching users
        6. Validate assignment with LLM
        7. Assign to best user or create job requisition
        
        Args:
            issue_data: Issue data with title, description, priority, source
            
        Returns:
            Result with issue_id, status, and AI analysis
        """
        title = issue_data["title"]
        description = issue_data.get("description", "")
        priority = issue_data.get("priority", "medium")
        source = issue_data.get("source", "api")
        external_id = issue_data.get("external_id")
        project_id = issue_data.get("project_id")
        
        now = datetime.utcnow()
        
        # Step 1: Generate embeddings
        issue_text = f"{title}. {description}"
        description_embedding = generate_embedding(issue_text)
        
        # Step 2: Search for similar issues
        similar_issues = await search_similar_issues(
            self.db,
            description_embedding,
            top_k=3,
            min_similarity=0.7
        )
        
        # Step 3: Check for duplicates with LLM
        duplicate_check = await check_issue_duplicate_with_llm(
            title, description, similar_issues
        )
        
        is_duplicate = duplicate_check.get("is_duplicate", False)
        parent_task_id = duplicate_check.get("parent_task_id")
        
        # Step 4: Extract required skills
        required_skills = extract_skills_from_task(title, description, "CoreSight")
        skill_text = ", ".join(required_skills)
        skill_embeddings = generate_embedding(skill_text)
        
        # Create issue document
        issue_doc = {
            "title": title,
            "description": description,
            "description_embedding": description_embedding,
            "parent_task_id": parent_task_id,
            "is_duplicate": is_duplicate,
            "required_skills": required_skills,
            "skill_embeddings": skill_embeddings,
            "priority": priority,
            "assigned_user_id": None,
            "assignment_status": "pending",
            "activity_log": [],
            "created_at": now,
            "updated_at": now,
            "source": source,
            "external_id": external_id,
            "project_id": project_id,
        }
        
        issue_id = await self.db.insert_one("issues", issue_doc)
        issue_doc["_id"] = issue_id
        
        # If duplicate, return early with parent reference
        if is_duplicate and parent_task_id:
            return {
                "issue_id": str(issue_id),
                "status": "duplicate_detected",
                "is_duplicate": True,
                "parent_task_id": parent_task_id,
                "duplicate_analysis": duplicate_check,
                "required_skills": required_skills,
            }
        
        print(f"\n[ASSIGNMENT LOG] Step 4: Extracted Required Skills: {required_skills}")

        # Step 5: Find matching users
        all_users = await self.db.find_many("users", {})
        
        if not all_users:
            print("[ASSIGNMENT LOG] No users found in database. Creating Job Requisition.")
            # No users - create job requisition
            report = await generate_no_match_report(
                title, description, required_skills, 0
            )
            requisition_id = await create_job_requisition_from_report(
                self.db, str(issue_id), report, required_skills
            )
            
            await self.db.update_one(
                "issues",
                {"_id": issue_id},
                {"assignment_status": "posting_required"}
            )
            
            return {
                "issue_id": str(issue_id),
                "status": "no_users_available",
                "report": report,
                "requisition_id": requisition_id,
                "action_required": "fill_job_requisition",
                "required_skills": required_skills,
            }
        
        # Format users for matching
        users_list = [
            {
                "_id": user["_id"],
                "name": user.get("name"),
                "email": user.get("email"),
                "skills": user.get("skills", []),
                "work_profile_embeddings": user.get("work_profile_embeddings", []),
                "hourly_rate": user.get("hourly_rate", 50.0),
            }
            for user in all_users
        ]
        
        matching_users = find_best_matching_users(
            required_skills, description_embedding, users_list, top_n=5
        )
        
        if not matching_users:
            print("[ASSIGNMENT LOG] No matching users found via Vector Search. Creating Job Requisition.")
            # No matching users - create job requisition
            report = await generate_no_match_report(
                title, description, required_skills, len(all_users)
            )
            requisition_id = await create_job_requisition_from_report(
                self.db, str(issue_id), report, required_skills
            )
            
            await self.db.update_one(
                "issues",
                {"_id": issue_id},
                {"assignment_status": "posting_required"}
            )
            
            return {
                "issue_id": str(issue_id),
                "status": "no_match",
                "report": report,
                "requisition_id": requisition_id,
                "action_required": "fill_job_requisition",
                "required_skills": required_skills,
            }

        print(f"[ASSIGNMENT LOG] Step 5: Found {len(matching_users)} potential candidates via Vector Search:")
        for idx, u in enumerate(matching_users):
            print(f"  {idx+1}. {u['name']} (Score: {u['match_score']:.4f}) - Skills: {u['skills']}")
        
        # Step 6: Validate with LLM (Batch Evaluation)
        print("[ASSIGNMENT LOG] Step 6: Sending candidates to LLM for critical evaluation...")
        evaluation = await evaluate_candidates_batch(
            candidates=matching_users,
            task_title=title,
            task_description=description,
            required_skills=required_skills
        )
        
        print(f"[ASSIGNMENT LOG] LLM Evaluation Result:")
        print(f"  Selected User ID: {evaluation.get('selected_user_id')}")
        print(f"  Confidence: {evaluation.get('confidence')}")
        print(f"  Reasoning: {evaluation.get('reasoning')}")
        
        selected_user_id = evaluation.get("selected_user_id")
        
        # Step 7: Assign if a user was selected
        if selected_user_id:
            # Find the full user object
            assigned_user = next((u for u in matching_users if str(u["_id"]) == selected_user_id), None)
            
            if assigned_user:
                print(f"[ASSIGNMENT LOG] Step 7: APPROVED. Assigning task to {assigned_user['name']}.")
                await self.db.update_one(
                    "issues",
                    {"_id": issue_id},
                    {
                        "assigned_user_id": selected_user_id,
                        "assignment_status": "assigned",
                        "updated_at": datetime.utcnow(),
                    }
                )
                
                return {
                    "issue_id": str(issue_id),
                    "status": "assigned",
                    "assigned_to": {
                        "user_id": selected_user_id,
                        "name": assigned_user["name"],
                        "match_score": assigned_user["match_score"],
                    },
                    "validation": evaluation,
                    "required_skills": required_skills,
                }
        
        # If no user was selected by LLM
        print("[ASSIGNMENT LOG] Step 7: REJECTED. No candidate met strict requirements. Creating Job Requisition.")
        # Create job requisition
        report = await generate_no_match_report(
            title, description, required_skills, len(all_users)
        )
        
        # Add LLM reasoning to the report context if available
        if evaluation.get("reasoning"):
            report["llm_evaluation_reasoning"] = evaluation["reasoning"]
            
        requisition_id = await create_job_requisition_from_report(
            self.db, str(issue_id), report, required_skills
        )
        
        await self.db.update_one(
            "issues",
            {"_id": issue_id},
            {"assignment_status": "posting_required"}
        )
        
        return {
            "issue_id": str(issue_id),
            "status": "no_qualified_match",
            "report": report,
            "requisition_id": requisition_id,
            "action_required": "fill_job_requisition",
            "required_skills": required_skills,
            "candidates_evaluated": len(matching_users),
            "llm_reasoning": evaluation.get("reasoning")
        }
    
    async def get_issue(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """Get an issue by ID"""
        try:
            return await self.db.find_one("issues", {"_id": ObjectId(issue_id)})
        except Exception:
            return None
    
    async def list_issues(
        self,
        status: Optional[str] = None,
        is_duplicate: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """List issues with optional filters"""
        filters = {}
        if status:
            filters["assignment_status"] = status
        if is_duplicate is not None:
            filters["is_duplicate"] = is_duplicate
        return await self.db.find_many("issues", filters)
    
    async def update_issue(self, issue_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an issue"""
        update_data["updated_at"] = datetime.utcnow()
        return await self.db.update_one(
            "issues",
            {"_id": ObjectId(issue_id)},
            update_data
        )
