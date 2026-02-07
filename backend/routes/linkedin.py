"""
LinkedIn Router for CoreSight

Handles LinkedIn search parameter endpoints using Unipile API.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from services.linkedin_service import (
    LinkedinSearchType,
    search_locations,
    search_job_titles,
    get_unipile_client,
)


router = APIRouter(prefix="/api/linkedin", tags=["LinkedIn"])


@router.get("/search/locations")
async def search_linkedin_locations(
    query: str = Query(..., description="Location search query"),
    limit: int = Query(10, ge=1, le=50, description="Max results to return")
):
    """
    Search for LinkedIn locations for job posting.
    
    Returns a list of location IDs and names that can be used
    when creating a job posting.
    """
    try:
        result = await search_locations(query, limit)
        return {
            "results": [r.model_dump() for r in result.results],
            "total_count": result.total_count
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LinkedIn API error: {str(e)}")


@router.get("/search/job-titles")
async def search_linkedin_job_titles(
    query: str = Query(..., description="Job title search query"),
    limit: int = Query(10, ge=1, le=50, description="Max results to return")
):
    """
    Search for LinkedIn job titles for job posting.
    
    Returns a list of job title IDs and names that can be used
    when creating a job posting.
    """
    try:
        result = await search_job_titles(query, limit)
        return {
            "results": [r.model_dump() for r in result.results],
            "total_count": result.total_count
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LinkedIn API error: {str(e)}")


@router.get("/search")
async def search_linkedin(
    category: str = Query("people", description="Search category: 'people' or 'companies'"),
    keywords: Optional[str] = Query(None, description="Search keywords"),
    location: Optional[str] = Query(None, description="Location filter"),
    limit: int = Query(10, ge=1, le=50, description="Max results to return")
):
    """
    Perform a LinkedIn search for people or companies.
    
    This is a general search endpoint for finding profiles or companies.
    """
    try:
        client = get_unipile_client()
        result = await client.search_linkedin(
            category=category,
            keywords=keywords,
            location=location,
            limit=limit
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LinkedIn API error: {str(e)}")
