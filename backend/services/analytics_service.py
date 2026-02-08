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
    
    # ============================================================================
    # OVERVIEW STATS - DASHBOARD SUMMARY
    # ============================================================================
    
    async def get_overview_stats(self) -> Dict[str, Any]:
        """
        Get high-level overview statistics with Jira task type breakdown.
        """
        # Get all data
        commits = await self.db.find_many("commits", {})
        projects = await self.db.find_many("projects", {})
        users = await self.db.find_many("users", {})
        tasks = await self.db.find_many("tasks", {})
        
        # Aggregate commit stats
        total_commits = len(commits)
        total_lines_added = sum(c.get("lines_added", 0) or 0 for c in commits)
        total_lines_deleted = sum(c.get("lines_deleted", 0) or 0 for c in commits)
        
        # Count unique contributors from commits
        contributor_ids = set()
        for c in commits:
            if c.get("user_id"):
                contributor_ids.add(str(c.get("user_id")))
            if c.get("author_email"):
                contributor_ids.add(c.get("author_email"))
        
        # Task type breakdown (from Jira)
        task_types = {}
        for task in tasks:
            t_type = task.get("type", "unknown")
            if t_type not in task_types:
                task_types[t_type] = 0
            task_types[t_type] += 1
        
        # Map task types to work categories
        work_breakdown = {
            "new_feature": task_types.get("feature", 0) + task_types.get("story", 0) + task_types.get("epic", 0),
            "refactor": task_types.get("bug", 0) + task_types.get("improvement", 0),
            "maintenance": task_types.get("task", 0) + task_types.get("subtask", 0),
            "other": sum(v for k, v in task_types.items() if k not in ["feature", "story", "epic", "bug", "improvement", "task", "subtask"])
        }
        
        return {
            "total_commits": total_commits,
            "total_projects": len(projects),
            "total_users": len(users),
            "active_contributors": len(contributor_ids),
            "total_lines_added": total_lines_added,
            "total_lines_deleted": total_lines_deleted,
            "net_lines": total_lines_added - total_lines_deleted,
            "total_tasks": len(tasks),
            "task_types": task_types,
            "work_breakdown": work_breakdown
        }
    
    # ============================================================================
    # PROJECT-WISE ANALYTICS
    # ============================================================================
    
    async def get_project_analytics(self, project_id: str = None) -> Dict[str, Any]:
        """
        Get analytics grouped by project with task type breakdown.
        """
        if project_id:
            projects = [await self.db.find_one("projects", {"_id": ObjectId(project_id)})]
            projects = [p for p in projects if p]
        else:
            projects = await self.db.find_many("projects", {})
        
        # Get all commits once
        all_commits = await self.db.find_many("commits", {})
        all_tasks = await self.db.find_many("tasks", {})
        
        project_stats = []
        
        for project in projects:
            pid = str(project.get("_id"))
            project_name = project.get("name", "Unknown")
            
            # Find commits by multiple matching strategies
            project_commits = []
            for c in all_commits:
                # Match by project_id
                if str(c.get("project_id", "")) == pid:
                    project_commits.append(c)
                    continue
                # Match by repository name (partial match)
                repo = c.get("repository", "")
                if repo and (project_name.lower() in repo.lower() or repo.lower() in project_name.lower()):
                    project_commits.append(c)
                    continue
            
            total_commits = len(project_commits)
            lines_added = sum(c.get("lines_added", 0) or 0 for c in project_commits)
            lines_deleted = sum(c.get("lines_deleted", 0) or 0 for c in project_commits)
            
            # Get unique contributors
            contributor_set = set()
            for c in project_commits:
                if c.get("user_id"):
                    contributor_set.add(str(c.get("user_id")))
                elif c.get("author_name"):
                    contributor_set.add(c.get("author_name"))
            
            # Get tasks for this project and categorize
            project_tasks = [t for t in all_tasks if str(t.get("project_id", "")) == pid]
            task_breakdown = {
                "features": len([t for t in project_tasks if t.get("type") in ["feature", "story", "epic"]]),
                "bugs": len([t for t in project_tasks if t.get("type") == "bug"]),
                "tasks": len([t for t in project_tasks if t.get("type") in ["task", "subtask"]]),
            }
            
            project_stats.append({
                "project_id": pid,
                "project_name": project_name,
                "repo_url": project.get("repo_url", ""),
                "total_commits": total_commits,
                "lines_added": lines_added,
                "lines_deleted": lines_deleted,
                "net_lines": lines_added - lines_deleted,
                "contributor_count": len(contributor_set),
                "contributors": list(contributor_set)[:5],
                "task_breakdown": task_breakdown,
                "total_tasks": len(project_tasks)
            })
        
        # Sort by commits descending
        project_stats.sort(key=lambda x: x["total_commits"], reverse=True)
        
        return {
            "projects": project_stats,
            "total_projects": len(project_stats)
        }
    
    # ============================================================================
    # COMMIT ACTIVITY TIMELINE (PROJECT-WISE)
    # ============================================================================
    
    async def get_commit_activity(self, days: int = 30, project_id: str = None, user_id: str = None) -> Dict[str, Any]:
        """
        Get commit activity over time, optionally filtered by project or user.
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Build query
        query = {}
        if project_id:
            query["project_id"] = project_id
        if user_id:
            query["user_id"] = ObjectId(user_id)
            
        # Get all commits and projects
        # Note: If filtering by user, we still want project breakdown
        all_commits = await self.db.find_many("commits", query)
        projects = await self.db.find_many("projects", {})
        
        # Build project name lookup
        project_names = {str(p.get("_id")): p.get("name", "Unknown") for p in projects}
        
        # Initialize daily counts
        daily_counts = {}
        for i in range(days + 1):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            daily_counts[date] = {
                "date": date, 
                "commits": 0, 
                "lines_added": 0, 
                "lines_deleted": 0,
                "by_project": {}
            }
        
        # Collect project activity
        project_activity = {}
        
        for commit in all_commits:
            committed_at = commit.get("committed_at") or commit.get("created_at")
            if not committed_at:
                continue
                
            # Parse date
            if isinstance(committed_at, str):
                try:
                    committed_at = datetime.fromisoformat(committed_at.replace("Z", "+00:00"))
                except:
                    continue
            
            date_str = committed_at.strftime("%Y-%m-%d")
            
            # Determine project
            commit_project = commit.get("repository", "Unknown")
            for pid, pname in project_names.items():
                if pname.lower() in commit_project.lower() or commit_project.lower() in pname.lower():
                    commit_project = pname
                    break
            
            # Track project activity
            if commit_project not in project_activity:
                project_activity[commit_project] = 0
            project_activity[commit_project] += 1
            
            # Add to daily counts
            if date_str in daily_counts:
                daily_counts[date_str]["commits"] += 1
                daily_counts[date_str]["lines_added"] += commit.get("lines_added", 0) or 0
                daily_counts[date_str]["lines_deleted"] += commit.get("lines_deleted", 0) or 0
                
                # Track by project
                if commit_project not in daily_counts[date_str]["by_project"]:
                    daily_counts[date_str]["by_project"][commit_project] = 0
                daily_counts[date_str]["by_project"][commit_project] += 1
        
        # Convert to sorted list
        activity = sorted(daily_counts.values(), key=lambda x: x["date"])
        
        # Sort project activity
        sorted_projects = sorted(project_activity.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "days": days,
            "activity": activity,
            "total_commits": sum(d["commits"] for d in activity),
            "by_project": dict(sorted_projects)
        }
    
    # ============================================================================
    # WORK TYPE BREAKDOWN (FROM JIRA)
    # ============================================================================
    
    async def get_work_type_breakdown(self) -> Dict[str, Any]:
        """
        Get work categorization based on Jira issue types.
        Bug = Refactor/Maintenance
        Feature/Story = New Development
        """
        tasks = await self.db.find_many("tasks", {})
        
        # Categorize by type
        categories = {
            "new_development": [],  # Features, Stories, Epics
            "bug_fixes": [],        # Bugs
            "maintenance": [],      # Tasks, Subtasks, Improvements
            "other": []
        }
        
        for task in tasks:
            task_type = task.get("type", "").lower()
            task_info = {
                "id": str(task.get("_id")),
                "title": task.get("title", ""),
                "jira_key": task.get("jira_key", ""),
                "status": task.get("status", ""),
                "type": task_type
            }
            
            if task_type in ["feature", "story", "epic"]:
                categories["new_development"].append(task_info)
            elif task_type == "bug":
                categories["bug_fixes"].append(task_info)
            elif task_type in ["task", "subtask", "improvement"]:
                categories["maintenance"].append(task_info)
            else:
                categories["other"].append(task_info)
        
        return {
            "summary": {
                "new_development": len(categories["new_development"]),
                "bug_fixes": len(categories["bug_fixes"]),
                "maintenance": len(categories["maintenance"]),
                "other": len(categories["other"]),
                "total": len(tasks)
            },
            "details": categories
        }


    # ============================================================================
    # TOP CONTRIBUTORS
    # ============================================================================
    
    async def get_top_contributors(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get top contributors based on commit activity and impact.
        """
        # Aggregate commits by user_id
        pipeline = [
            {
                "$group": {
                    "_id": "$user_id",
                    "total_commits": {"$sum": 1},
                    "total_lines_added": {"$sum": "$lines_added"},
                    "total_lines_deleted": {"$sum": "$lines_deleted"},
                    "last_active": {"$max": "$created_at"}
                }
            },
            {
                "$sort": {"total_commits": -1}
            },
            {
                "$limit": limit
            }
        ]
        
        agg_results = await self.db.aggregate("commits", pipeline)
        
        contributors = []
        for res in agg_results:
            user_id = res.get("_id")
            if not user_id:
                continue
                
            # Fetch user details
            user = await self.db.find_one("users", {"_id": ObjectId(user_id)}) if isinstance(user_id, ObjectId) else None
            
            if not user:
                # Try to map string ID if ObjectId failed or wasn't ObjectId
                try:
                    user = await self.db.find_one("users", {"_id": ObjectId(str(user_id))})
                except:
                    pass
            
            name = user.get("name", "Unknown User") if user else "Unknown User"
            
            contributors.append({
                "user_id": str(user_id),
                "name": name,
                "commit_count": res.get("total_commits", 0),
                "lines_added": res.get("total_lines_added", 0),
                "lines_deleted": res.get("total_lines_deleted", 0),
                "last_active": res.get("last_active")
            })
            
        return contributors
