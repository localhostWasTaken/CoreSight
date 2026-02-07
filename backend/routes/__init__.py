"""
CoreSight API Routes Package

This package contains all API route handlers organized by domain.
Routes are thin HTTP handlers that delegate to services for business logic.
"""

from .users import router as users_router
from .tasks import router as tasks_router
from .projects import router as projects_router
from .linkedin import router as linkedin_router
from .jobs import router as jobs_router
from .webhooks import router as webhooks_router
from .issues import router as issues_router
from .commits import router as commits_router

# Re-export routers with their expected names for main.py compatibility
from . import users, tasks, projects, linkedin, jobs, webhooks, issues, commits

__all__ = [
    "users",
    "tasks", 
    "projects",
    "linkedin",
    "jobs",
    "webhooks",
    "issues",
    "commits",
    "users_router",
    "tasks_router",
    "projects_router",
    "linkedin_router",
    "jobs_router",
    "webhooks_router",
    "issues_router",
    "commits_router",
]
