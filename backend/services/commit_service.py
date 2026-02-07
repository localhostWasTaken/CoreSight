"""
Commit Service for CoreSight

Handles commit processing with AI-powered skill extraction,
task linking, and profile evolution.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from bson import ObjectId

from database import DatabaseManager
from ai import (
    generate_embedding,
    extract_skills_from_commit_diff,
    check_profile_update_needed,
)
from utils import search_similar_tasks_for_commit, find_user_by_email


class CommitService:
    """Service class for commit operations with AI analysis"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    async def process_commit(self, commit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a commit with full AI analysis pipeline.
        
        Pipeline:
        1. Extract skills and summary from commit diff using LLM
        2. Generate embeddings for commit summary
        3. Search for related tasks
        4. Link to task if match found
        5. Find author user
        6. Check if profile needs updating
        7. Update user profile if needed
        
        Args:
            commit_data: Commit data with hash, message, diff, author info
            
        Returns:
            Result with commit_id, analysis, and profile updates
        """
        commit_hash = commit_data["commit_hash"]
        commit_message = commit_data["commit_message"]
        diff_content = commit_data.get("diff", "")
        author_email = commit_data["author_email"]
        author_name = commit_data["author_name"]
        repository = commit_data.get("repository", "unknown")
        branch = commit_data.get("branch", "main")
        
        now = datetime.utcnow()
        
        # Step 1: Extract skills and summary using LLM
        analysis = await extract_skills_from_commit_diff(
            commit_message, diff_content, repository
        )
        
        summary = analysis.get("summary", commit_message)
        skills_used = analysis.get("skills_used", [])
        impact = analysis.get("impact_assessment", "minor")
        
        # Step 2: Generate embeddings
        summary_embedding = generate_embedding(summary)
        
        # Step 3: Search for related tasks
        similar_tasks = await search_similar_tasks_for_commit(
            self.db,
            summary_embedding,
            top_k=1,
            min_similarity=0.6
        )
        
        linked_task_id = None
        is_jira_tracked = False
        
        if similar_tasks:
            best_task = similar_tasks[0]
            linked_task_id = str(best_task.get("_id"))
            is_jira_tracked = bool(best_task.get("external_id"))
        
        # Step 4: Find author user
        user = await find_user_by_email(self.db, author_email)
        user_id = str(user["_id"]) if user else None
        
        # Create commit document
        commit_doc = {
            "commit_hash": commit_hash,
            "commit_message": commit_message,
            "diff_content": diff_content,
            "summary": summary,
            "extracted_skills": skills_used,
            "summary_embedding": summary_embedding,
            "linked_task_id": linked_task_id,
            "is_jira_tracked": is_jira_tracked,
            "author_email": author_email,
            "author_name": author_name,
            "user_id": user_id,
            "repository": repository,
            "branch": branch,
            "timestamp": now,
            "files_changed": commit_data.get("files_changed", 0),
            "lines_added": commit_data.get("lines_added", 0),
            "lines_deleted": commit_data.get("lines_deleted", 0),
            "triggered_profile_update": False,
            "created_at": now,
        }
        
        commit_id = await self.db.insert_one("commits", commit_doc)
        
        # Step 5 & 6: Check if profile needs updating
        profile_update = None
        if user:
            current_skills = user.get("skills", [])
            current_profile = user.get("profile_text", "")
            
            profile_check = await check_profile_update_needed(
                current_profile,
                current_skills,
                skills_used,
                summary
            )
            
            if profile_check.get("needs_update"):
                # Step 7: Update user profile
                new_skills = list(set(current_skills + profile_check.get("new_skills_to_add", [])))
                
                # Generate new embedding for updated skills
                skills_text = ", ".join(new_skills)
                new_embedding = generate_embedding(skills_text)
                
                await self.db.update_one(
                    "users",
                    {"_id": user["_id"]},
                    {
                        "skills": new_skills,
                        "work_profile_embeddings": new_embedding,
                    }
                )
                
                # Mark commit as having triggered profile update
                await self.db.update_one(
                    "commits",
                    {"_id": commit_id},
                    {"triggered_profile_update": True}
                )
                
                profile_update = {
                    "updated": True,
                    "new_skills_added": profile_check.get("new_skills_to_add", []),
                    "reasoning": profile_check.get("reasoning"),
                }
        
        return {
            "commit_id": str(commit_id),
            "commit_hash": commit_hash,
            "analysis": {
                "summary": summary,
                "skills_used": skills_used,
                "impact_assessment": impact,
            },
            "linked_task": {
                "task_id": linked_task_id,
                "is_jira_tracked": is_jira_tracked,
            } if linked_task_id else None,
            "author": {
                "email": author_email,
                "name": author_name,
                "user_id": user_id,
            },
            "profile_update": profile_update,
        }
    
    async def get_commit(self, commit_id: str) -> Optional[Dict[str, Any]]:
        """Get a commit by ID"""
        try:
            return await self.db.find_one("commits", {"_id": ObjectId(commit_id)})
        except Exception:
            return None
    
    async def get_commit_by_hash(self, commit_hash: str) -> Optional[Dict[str, Any]]:
        """Get a commit by git hash"""
        return await self.db.find_one("commits", {"commit_hash": commit_hash})
    
    async def list_commits(
        self,
        user_id: Optional[str] = None,
        repository: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List commits with optional filters"""
        filters = {}
        if user_id:
            filters["user_id"] = user_id
        if repository:
            filters["repository"] = repository
        return await self.db.find_many("commits", filters)
    
    async def get_commits_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all commits by a user"""
        return await self.list_commits(user_id=user_id)
