"""
Analytics Router for CoreSight

Provides advanced analytics and insights endpoints:
- Code Impact Analysis (Maker vs. Mender Score)
- True Task Costing
- Context Switching (Burnout Detection)
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from utils import get_db
from services.analytics_service import AnalyticsService


router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


# Response models
class ImpactBreakdownResponse(BaseModel):
    """Response model for code impact analysis"""
    user_id: str
    total_commits: int
    total_lines_added: int
    total_lines_deleted: int
    total_lines_modified: int
    overall_refactor_ratio: float
    profile: str  # maker, mender, cleaner, balanced


class TaskCostResponse(BaseModel):
    """Response model for task cost analysis"""
    task_id: str
    task_title: str
    total_cost: float
    total_hours: float
    average_hourly_rate: float


class FocusHealthResponse(BaseModel):
    """Response model for team focus health"""
    analysis_period: dict
    team_summary: dict
    alert: dict


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get(
    "/user/{user_id}/impact_breakdown",
    response_model=dict,
    summary="Get User Code Impact Breakdown",
    description="""
    Analyze a user's commit history to calculate their "Maker vs. Mender" score.
    
    **Categories:**
    - **New Feature**: Mostly code additions (refactor_ratio < 0.3)
    - **Refactoring**: Balanced changes (refactor_ratio 0.3 - 0.6)
    - **Cleanup**: Mostly deletions (refactor_ratio > 0.6)
    
    **Profiles:**
    - **Maker**: 50%+ new features (builders/creators)
    - **Mender**: 40%+ refactoring (maintainers)
    - **Cleaner**: 40%+ cleanup (tech debt resolvers)
    - **Balanced**: Mix of all categories
    
    **Refactor Ratio** = (lines_deleted + lines_modified) / (lines_added + lines_deleted + lines_modified)
    """
)
async def get_user_impact_breakdown(user_id: str):
    """
    Get code impact analysis for a specific user.
    
    Analyzes commit patterns to categorize the user's work style and
    calculate their refactor ratio (maintenance vs. new development).
    """
    try:
        db = get_db()
        service = AnalyticsService(db)
        result = await service.get_user_impact_breakdown(user_id)
        
        return {
            "success": True,
            "data": result
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze user impact: {str(e)}"
        )


@router.get(
    "/task/{task_id}/cost",
    response_model=dict,
    summary="Get True Task Cost Analysis",
    description="""
    Calculate the true cost of a task by aggregating all work sessions.
    
    **Cost Calculation:**
    - Sums all work sessions for the task
    - Calculates: session.duration_hours × user.hourly_rate
    - Breaks down cost by user
    
    **Budget Analysis:**
    - Compares against pro-rated project budget
    - Pro-rated budget = project.total_budget / task_count
    - Shows variance and over/under budget status
    """
)
async def get_task_cost_analysis(task_id: str):
    """
    Get comprehensive cost analysis for a specific task.
    
    Includes:
    - Total cost and hours spent
    - Per-user breakdown with hourly rates
    - Budget variance analysis
    - Project budget comparison
    """
    try:
        db = get_db()
        service = AnalyticsService(db)
        result = await service.get_task_cost_analysis(task_id)
        
        return {
            "success": True,
            "data": result
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze task cost: {str(e)}"
        )


@router.get(
    "/team/focus_health",
    response_model=dict,
    summary="Get Team Focus Health (Burnout Detection)",
    description="""
    Analyze context switching patterns across the team to detect burnout risk.
    
    **Context Switches** = Number of distinct tasks worked on in a single day - 1
    
    **Risk Levels:**
    - **High Risk**: Average ≥ 4 switches/day OR 40%+ days above threshold
    - **Medium Risk**: Average ≥ 2.8 switches/day (70% of threshold)
    - **Low Risk**: Below medium risk threshold
    
    **Why This Matters:**
    - Frequent task switching reduces productivity
    - High context switching correlates with burnout
    - Indicates possible resource allocation issues
    
    **Recommendations:**
    - High Risk: Reduce task assignments, allow focus time
    - Consider batching similar tasks
    - Review sprint planning and workload distribution
    """
)
async def get_team_focus_health(
    days: int = Query(
        default=7,
        ge=1,
        le=30,
        description="Number of days to analyze (1-30)"
    ),
    threshold: int = Query(
        default=4,
        ge=2,
        le=10,
        description="Context switches per day to flag as high risk (2-10)"
    )
):
    """
    Analyze team focus health and detect context switching patterns.
    
    Flags users with excessive task switching as potential burnout risks.
    Provides daily breakdown and team-wide statistics.
    """
    try:
        db = get_db()
        service = AnalyticsService(db)
        result = await service.get_team_focus_health(days=days, threshold=threshold)
        
        return {
            "success": True,
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze team focus health: {str(e)}"
        )


# ============================================================================
# ADDITIONAL UTILITY ENDPOINTS
# ============================================================================

@router.get(
    "/health",
    summary="Analytics Service Health Check",
    description="Check if the analytics service is operational"
)
async def analytics_health():
    """Health check endpoint for analytics service"""
    return {
        "status": "healthy",
        "service": "analytics",
        "available_endpoints": [
            "GET /api/analytics/user/{user_id}/impact_breakdown",
            "GET /api/analytics/task/{task_id}/cost",
            "GET /api/analytics/team/focus_health"
        ]
    }


@router.get(
    "/summary",
    summary="Get Analytics Summary",
    description="Get a high-level summary of all analytics capabilities"
)
async def get_analytics_summary():
    """
    Get an overview of all analytics capabilities and metrics.
    """
    return {
        "success": True,
        "analytics_modules": {
            "code_impact_analysis": {
                "description": "Maker vs. Mender Score - categorizes developers by their commit patterns",
                "endpoint": "/api/analytics/user/{user_id}/impact_breakdown",
                "metrics": ["refactor_ratio", "profile", "category_breakdown"],
                "use_cases": [
                    "Identify team skill distribution",
                    "Balance feature development vs. maintenance work",
                    "Track tech debt resolution efforts"
                ]
            },
            "task_costing": {
                "description": "True Task Cost - aggregates all work sessions to calculate actual task costs",
                "endpoint": "/api/analytics/task/{task_id}/cost",
                "metrics": ["total_cost", "total_hours", "budget_variance"],
                "use_cases": [
                    "Project budget tracking",
                    "Estimate future task costs",
                    "Identify resource-intensive tasks"
                ]
            },
            "burnout_detection": {
                "description": "Context Switching Analysis - detects excessive task switching patterns",
                "endpoint": "/api/analytics/team/focus_health",
                "metrics": ["context_switches", "risk_level", "focus_health_score"],
                "use_cases": [
                    "Prevent developer burnout",
                    "Optimize task assignments",
                    "Improve team focus and productivity"
                ]
            }
        },
        "recommended_usage": {
            "weekly_review": [
                "Run team/focus_health to identify at-risk developers",
                "Review user/impact_breakdown for skill balance"
            ],
            "project_planning": [
                "Use task cost data for estimation",
                "Review budget variance trends"
            ],
            "sprint_retrospective": [
                "Analyze context switching patterns",
                "Review code impact distribution"
            ]
        }
    }
