"""
Analytics Service for CoreSight

Provides advanced analytics and insights including:
- Code Impact Analysis (Maker vs. Mender Score)
- True Task Costing
- Context Switching (Burnout Detection)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from bson import ObjectId

from utils.database import DatabaseManager


class AnalyticsService:
    """Service class for analytics operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    # ============================================================================
    # CODE IMPACT ANALYSIS - "Maker vs. Mender" Score
    # ============================================================================
    
    async def get_user_impact_breakdown(self, user_id: str) -> Dict[str, Any]:
        """
        Analyze commit data for a user to calculate their "Maker vs. Mender" score.
        
        Categorizes commits as:
        - New Feature (mostly additions)
        - Refactoring (mostly modifications)
        - Cleanup (mostly deletions)
        
        Args:
            user_id: User ID to analyze
            
        Returns:
            Dict containing impact metrics and categorization
        """
        # Fetch all commits for this user
        commits = await self.db.find_many("commits", {"user_id": ObjectId(user_id)})
        
        if not commits:
            return {
                "user_id": user_id,
                "total_commits": 0,
                "message": "No commits found for this user"
            }
        
        # Initialize counters
        total_commits = len(commits)
        total_lines_added = 0
        total_lines_deleted = 0
        total_lines_modified = 0
        
        category_counts = {
            "new_feature": 0,
            "refactoring": 0,
            "cleanup": 0
        }
        
        commit_details = []
        
        for commit in commits:
            lines_added = commit.get("lines_added", 0)
            lines_deleted = commit.get("lines_deleted", 0)
            
            # Approximate modifications (lines that changed but weren't pure add/delete)
            # Using a heuristic: modifications = min(added, deleted) / 2
            lines_modified = min(lines_added, lines_deleted) // 2
            
            total_lines_added += lines_added
            total_lines_deleted += lines_deleted
            total_lines_modified += lines_modified
            
            # Calculate refactor ratio for this commit
            total_lines = lines_added + lines_deleted + lines_modified
            if total_lines == 0:
                refactor_ratio = 0
                category = "cleanup"  # Empty commit
            else:
                refactor_ratio = (lines_deleted + lines_modified) / total_lines
                
                # Categorize based on refactor ratio
                if refactor_ratio < 0.3:
                    category = "new_feature"  # Mostly additions
                elif refactor_ratio < 0.6:
                    category = "refactoring"  # Balanced changes
                else:
                    category = "cleanup"  # Mostly deletions
            
            category_counts[category] += 1
            
            commit_details.append({
                "commit_hash": commit.get("commit_hash", "unknown"),
                "commit_message": commit.get("commit_message", "")[:100],
                "lines_added": lines_added,
                "lines_deleted": lines_deleted,
                "lines_modified": lines_modified,
                "refactor_ratio": round(refactor_ratio, 3),
                "category": category,
                "timestamp": commit.get("timestamp")
            })
        
        # Calculate overall refactor ratio
        total_lines = total_lines_added + total_lines_deleted + total_lines_modified
        overall_refactor_ratio = 0 if total_lines == 0 else (total_lines_deleted + total_lines_modified) / total_lines
        
        # Determine overall user profile
        new_feature_pct = (category_counts["new_feature"] / total_commits) * 100
        refactoring_pct = (category_counts["refactoring"] / total_commits) * 100
        cleanup_pct = (category_counts["cleanup"] / total_commits) * 100
        
        if new_feature_pct >= 50:
            profile = "maker"  # Builder/Creator
        elif refactoring_pct >= 40:
            profile = "mender"  # Maintainer/Refactorer
        elif cleanup_pct >= 40:
            profile = "cleaner"  # Tech debt resolver
        else:
            profile = "balanced"  # Mix of all
        
        return {
            "user_id": user_id,
            "total_commits": total_commits,
            "total_lines_added": total_lines_added,
            "total_lines_deleted": total_lines_deleted,
            "total_lines_modified": total_lines_modified,
            "overall_refactor_ratio": round(overall_refactor_ratio, 3),
            "profile": profile,
            "category_breakdown": {
                "new_feature": {
                    "count": category_counts["new_feature"],
                    "percentage": round(new_feature_pct, 1)
                },
                "refactoring": {
                    "count": category_counts["refactoring"],
                    "percentage": round(refactoring_pct, 1)
                },
                "cleanup": {
                    "count": category_counts["cleanup"],
                    "percentage": round(cleanup_pct, 1)
                }
            },
            "recent_commits": commit_details[-10:]  # Last 10 commits
        }
    
    # ============================================================================
    # TRUE TASK COSTING
    # ============================================================================
    
    async def get_task_cost_analysis(self, task_id: str) -> Dict[str, Any]:
        """
        Calculate the true cost of a task by aggregating all work sessions
        and comparing against project budget.
        
        Args:
            task_id: Task ID to analyze
            
        Returns:
            Dict containing cost breakdown and budget comparison
        """
        # Fetch the task
        task = await self.db.find_one("tasks", {"_id": ObjectId(task_id)})
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Fetch all work sessions for this task
        work_sessions = await self.db.find_many("worksessions", {"task_id": ObjectId(task_id)})
        
        if not work_sessions:
            return {
                "task_id": task_id,
                "task_title": task.get("title", "Unknown"),
                "total_cost": 0.0,
                "total_hours": 0.0,
                "message": "No work sessions found for this task"
            }
        
        # Calculate cost per user
        user_costs = {}
        total_cost = 0.0
        total_hours = 0.0
        
        for session in work_sessions:
            user_id = str(session.get("user_id"))
            duration_minutes = session.get("duration_minutes", 0)
            duration_hours = duration_minutes / 60.0
            
            # Fetch user to get hourly rate
            user = await self.db.find_one("users", {"_id": ObjectId(user_id)})
            if not user:
                continue
                
            hourly_rate = user.get("hourly_rate", 50.0)
            session_cost = duration_hours * hourly_rate
            
            # Aggregate by user
            if user_id not in user_costs:
                user_costs[user_id] = {
                    "user_name": user.get("name", "Unknown"),
                    "hourly_rate": hourly_rate,
                    "hours_worked": 0.0,
                    "total_cost": 0.0,
                    "session_count": 0
                }
            
            user_costs[user_id]["hours_worked"] += duration_hours
            user_costs[user_id]["total_cost"] += session_cost
            user_costs[user_id]["session_count"] += 1
            
            total_cost += session_cost
            total_hours += duration_hours
        
        # Fetch project to compare against budget
        project_id = task.get("project_id")
        project = await self.db.find_one("projects", {"_id": ObjectId(project_id)}) if project_id else None
        
        budget_analysis = {}
        if project:
            total_budget = project.get("total_budget", 0.0)
            
            # Get all tasks in this project to calculate pro-rated budget
            project_tasks = await self.db.find_many("tasks", {"project_id": ObjectId(project_id)})
            task_count = len(project_tasks)
            
            # Simple pro-rating: budget / number of tasks
            # In reality, this could be weighted by task priority or estimated effort
            prorated_budget = total_budget / task_count if task_count > 0 else 0.0
            
            budget_variance = total_cost - prorated_budget
            budget_variance_pct = (budget_variance / prorated_budget * 100) if prorated_budget > 0 else 0
            
            budget_analysis = {
                "project_name": project.get("name", "Unknown"),
                "project_total_budget": total_budget,
                "task_count_in_project": task_count,
                "prorated_task_budget": round(prorated_budget, 2),
                "budget_variance": round(budget_variance, 2),
                "budget_variance_percentage": round(budget_variance_pct, 1),
                "status": "over_budget" if budget_variance > 0 else "within_budget"
            }
        
        return {
            "task_id": task_id,
            "task_title": task.get("title", "Unknown"),
            "task_type": task.get("type", "unknown"),
            "task_status": task.get("status", "unknown"),
            "total_cost": round(total_cost, 2),
            "total_hours": round(total_hours, 2),
            "average_hourly_rate": round(total_cost / total_hours, 2) if total_hours > 0 else 0,
            "user_breakdown": [
                {
                    "user_id": uid,
                    **{k: round(v, 2) if isinstance(v, float) else v for k, v in data.items()}
                }
                for uid, data in user_costs.items()
            ],
            "budget_analysis": budget_analysis
        }
    
    # ============================================================================
    # CONTEXT SWITCHING - BURNOUT DETECTION
    # ============================================================================
    
    async def get_team_focus_health(self, days: int = 7, threshold: int = 4) -> Dict[str, Any]:
        """
        Analyze context switching patterns across the team to detect burnout risk.
        
        Flags users with >4 context switches per day as "High Risk".
        
        Args:
            days: Number of days to analyze (default: 7)
            threshold: Number of task switches per day to flag as high risk (default: 4)
            
        Returns:
            Dict containing team focus health metrics
        """
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Fetch all work sessions in the date range
        work_sessions = await self.db.find_many(
            "worksessions",
            {
                "start_time": {"$gte": start_date, "$lte": end_date}
            }
        )
        
        if not work_sessions:
            return {
                "analysis_period_days": days,
                "message": "No work sessions found in the analysis period"
            }
        
        # Group sessions by user and day
        user_daily_tasks = {}
        
        for session in work_sessions:
            user_id = str(session.get("user_id"))
            task_id = str(session.get("task_id"))
            start_time = session.get("start_time")
            
            if not start_time:
                continue
            
            # Get the date (without time)
            date_key = start_time.strftime("%Y-%m-%d")
            
            # Initialize nested dict structure
            if user_id not in user_daily_tasks:
                user_daily_tasks[user_id] = {}
            
            if date_key not in user_daily_tasks[user_id]:
                user_daily_tasks[user_id][date_key] = set()
            
            # Add task to the set (automatically handles duplicates)
            user_daily_tasks[user_id][date_key].add(task_id)
        
        # Analyze context switching for each user
        user_analysis = []
        high_risk_users = []
        total_context_switches = 0
        
        for user_id, daily_tasks in user_daily_tasks.items():
            # Fetch user details
            user = await self.db.find_one("users", {"_id": ObjectId(user_id)})
            user_name = user.get("name", "Unknown") if user else "Unknown"
            
            # Calculate context switches per day
            daily_switches = []
            max_switches = 0
            total_switches = 0
            high_risk_days = 0
            
            for date, tasks in daily_tasks.items():
                task_count = len(tasks)
                context_switches = task_count - 1  # Switches = tasks - 1
                
                daily_switches.append({
                    "date": date,
                    "unique_tasks": task_count,
                    "context_switches": context_switches,
                    "risk_level": "high" if context_switches >= threshold else "normal"
                })
                
                if context_switches > max_switches:
                    max_switches = context_switches
                
                total_switches += context_switches
                
                if context_switches >= threshold:
                    high_risk_days += 1
            
            avg_switches = total_switches / len(daily_tasks) if daily_tasks else 0
            total_context_switches += total_switches
            
            # Determine overall risk level
            if avg_switches >= threshold or high_risk_days >= (days * 0.4):
                risk_level = "high"
                high_risk_users.append(user_name)
            elif avg_switches >= (threshold * 0.7):
                risk_level = "medium"
            else:
                risk_level = "low"
            
            user_analysis.append({
                "user_id": user_id,
                "user_name": user_name,
                "total_context_switches": total_switches,
                "average_switches_per_day": round(avg_switches, 2),
                "max_switches_in_day": max_switches,
                "high_risk_days": high_risk_days,
                "days_analyzed": len(daily_tasks),
                "risk_level": risk_level,
                "daily_breakdown": sorted(daily_switches, key=lambda x: x["date"], reverse=True)
            })
        
        # Sort by risk level (high first) and then by average switches
        risk_order = {"high": 0, "medium": 1, "low": 2}
        user_analysis.sort(key=lambda x: (risk_order[x["risk_level"]], -x["average_switches_per_day"]))
        
        # Calculate team statistics
        total_users_analyzed = len(user_analysis)
        high_risk_count = sum(1 for u in user_analysis if u["risk_level"] == "high")
        medium_risk_count = sum(1 for u in user_analysis if u["risk_level"] == "medium")
        low_risk_count = sum(1 for u in user_analysis if u["risk_level"] == "low")
        
        return {
            "analysis_period": {
                "days": days,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            },
            "team_summary": {
                "total_users_analyzed": total_users_analyzed,
                "high_risk_users": high_risk_count,
                "medium_risk_users": medium_risk_count,
                "low_risk_users": low_risk_count,
                "total_context_switches": total_context_switches,
                "average_switches_per_user": round(total_context_switches / total_users_analyzed, 2) if total_users_analyzed > 0 else 0
            },
            "alert": {
                "high_risk_threshold": threshold,
                "users_flagged": high_risk_users,
                "message": f"{high_risk_count} user(s) showing signs of context switching overload" if high_risk_count > 0 else "Team focus health is good"
            },
            "user_details": user_analysis
        }
