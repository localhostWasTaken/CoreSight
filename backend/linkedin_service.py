"""
LinkedIn/Unipile Service for CoreSight
Handles LinkedIn search parameters and job posting via Unipile API
"""

import os
import httpx
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


# === Configuration ===
UNIPILE_BASE_URL = os.getenv("UNIPILE_BASE_URL", "https://api1.unipile.com:13111")
UNIPILE_API_KEY = os.getenv("UNIPILE_API_KEY", "")
UNIPILE_ACCOUNT_ID = os.getenv("UNIPILE_ACCOUNT_ID", "")
UNIPILE_COMPANY_ID = os.getenv("UNIPILE_COMPANY_ID", "")


# === Enums ===
class LinkedinSearchType(str, Enum):
    """Types of LinkedIn search parameters available"""
    LOCATION = "LOCATION"
    JOB_TITLE = "JOB_TITLE"
    COMPANY = "COMPANY"
    INDUSTRY = "INDUSTRY"
    SKILL = "SKILL"


class WorkplaceType(str, Enum):
    ON_SITE = "ON_SITE"
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"


class EmploymentType(str, Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERNSHIP = "INTERNSHIP"


# === Response Models ===
class SearchResult(BaseModel):
    id: str
    text: str
    type: str


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_count: int


class JobPostingResponse(BaseModel):
    job_id: str
    project_id: Optional[str] = None
    status: str


# === Unipile Client ===
class UnipileClient:
    """
    Async client for Unipile LinkedIn API
    
    Implements:
    - LinkedIn search parameters (for autocomplete)
    - Job posting (create draft, publish)
    """
    
    def __init__(
        self,
        base_url: str = UNIPILE_BASE_URL,
        api_key: str = UNIPILE_API_KEY,
        account_id: str = UNIPILE_ACCOUNT_ID,
        company_id: str = UNIPILE_COMPANY_ID
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.account_id = account_id
        self.company_id = company_id
        
        self._headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-API-KEY": self.api_key
        }
    
    def _check_config(self) -> None:
        """Validate required configuration is present"""
        if not self.api_key:
            raise ValueError("UNIPILE_API_KEY not configured")
        if not self.account_id:
            raise ValueError("UNIPILE_ACCOUNT_ID not configured")
    
    async def search_linkedin_parameters(
        self,
        search_type: LinkedinSearchType,
        query: str,
        limit: int = 10
    ) -> SearchResponse:
        """
        Search LinkedIn for autocomplete parameters
        
        Uses the Unipile search_parameters endpoint to get:
        - Locations (for job location field)
        - Job titles (standard LinkedIn job titles)
        - Companies
        - Industries
        
        Args:
            search_type: Type of parameter to search for
            query: Search query string
            limit: Max results to return
            
        Returns:
            SearchResponse with list of matching items
        """
        self._check_config()
        
        url = f"{self.base_url}/api/v1/linkedin/search_parameters"
        
        params = {
            "account_id": self.account_id,
            "type": search_type.value,
            "query": query,
            "limit": limit
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    url,
                    headers=self._headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                # Parse Unipile response format
                items = data.get("items", [])
                results = []
                
                for item in items:
                    results.append(SearchResult(
                        id=str(item.get("id", item.get("urn", ""))),
                        text=item.get("name", item.get("text", "")),
                        type=search_type.value
                    ))
                
                return SearchResponse(
                    results=results,
                    total_count=len(results)
                )
                
            except httpx.HTTPStatusError as e:
                print(f"Unipile API error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                print(f"Error searching LinkedIn parameters: {e}")
                raise
    
    async def search_linkedin(
        self,
        category: str = "people",
        keywords: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Perform LinkedIn search for people or companies
        
        Args:
            category: "people" or "companies"
            keywords: Search keywords
            location: Location filter
            limit: Max results
            
        Returns:
            Raw search results from Unipile
        """
        self._check_config()
        
        url = f"{self.base_url}/api/v1/linkedin/search"
        
        params = {
            "account_id": self.account_id,
            "limit": limit
        }
        
        body = {
            "api": "classic",
            "category": category
        }
        
        if keywords:
            body["keywords"] = keywords
        if location:
            body["location"] = location
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    url,
                    headers=self._headers,
                    params=params,
                    json=body
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                print(f"Unipile search error: {e.response.status_code} - {e.response.text}")
                raise
    
    async def create_job_posting(
        self,
        job_title_id: str,
        location_id: str,
        description: str,
        workplace_type: WorkplaceType = WorkplaceType.ON_SITE,
        employment_type: EmploymentType = EmploymentType.FULL_TIME,
        screening_questions: Optional[List[Dict]] = None
    ) -> JobPostingResponse:
        """
        Create a new job posting draft on LinkedIn
        
        Args:
            job_title_id: LinkedIn job title ID (from search_parameters)
            location_id: LinkedIn location ID (from search_parameters)
            description: Job description (HTML supported)
            workplace_type: ON_SITE, REMOTE, or HYBRID
            employment_type: FULL_TIME, PART_TIME, CONTRACT, INTERNSHIP
            screening_questions: Optional list of screening questions
            
        Returns:
            JobPostingResponse with job_id for further actions
        """
        self._check_config()
        
        if not self.company_id:
            raise ValueError("UNIPILE_COMPANY_ID not configured")
        
        url = f"{self.base_url}/api/v1/linkedin/jobs"
        
        body = {
            "account_id": self.account_id,
            "job_title": job_title_id,
            "company": self.company_id,
            "location": location_id,
            "workplace": workplace_type.value,
            "employment_status": employment_type.value,
            "description": description,
        }
        
        if screening_questions:
            body["screening_questions"] = screening_questions
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    url,
                    headers=self._headers,
                    json=body
                )
                response.raise_for_status()
                data = response.json()
                
                return JobPostingResponse(
                    job_id=data.get("job_id", ""),
                    project_id=data.get("project_id"),
                    status="draft"
                )
                
            except httpx.HTTPStatusError as e:
                print(f"Unipile job creation error: {e.response.status_code} - {e.response.text}")
                raise
    
    async def publish_job_posting(self, job_id: str) -> JobPostingResponse:
        """
        Publish a draft job posting to LinkedIn
        
        Args:
            job_id: The job ID from create_job_posting
            
        Returns:
            JobPostingResponse with updated status
        """
        self._check_config()
        
        url = f"{self.base_url}/api/v1/linkedin/jobs/{job_id}/publish"
        
        body = {
            "account_id": self.account_id,
            "free": True  # Use free posting slot
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    url,
                    headers=self._headers,
                    json=body
                )
                response.raise_for_status()
                
                return JobPostingResponse(
                    job_id=job_id,
                    status="published"
                )
                
            except httpx.HTTPStatusError as e:
                print(f"Unipile publish error: {e.response.status_code} - {e.response.text}")
                raise


# === Helper Functions ===
def get_unipile_client() -> UnipileClient:
    """Factory function to get configured Unipile client"""
    return UnipileClient()


async def search_locations(query: str, limit: int = 10) -> SearchResponse:
    """Convenience function to search locations"""
    client = get_unipile_client()
    return await client.search_linkedin_parameters(
        LinkedinSearchType.LOCATION,
        query,
        limit
    )


async def search_job_titles(query: str, limit: int = 10) -> SearchResponse:
    """Convenience function to search job titles"""
    client = get_unipile_client()
    return await client.search_linkedin_parameters(
        LinkedinSearchType.JOB_TITLE,
        query,
        limit
    )
