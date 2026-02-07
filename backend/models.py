from enum import Enum
from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, BeforeValidator, ConfigDict
from typing_extensions import Annotated

# --- 1. THE UNIVERSAL ID FIX ---
# Handles MongoDB ObjectId <-> String conversion automatically
PyObjectId = Annotated[str, BeforeValidator(str)]

# --- 2. ENUMS ---
class Role(str, Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"

class TaskType(str, Enum):
    FEATURE = "feature"       # CapEx (Innovation)
    BUG = "bug"               # OpEx (Maintenance)
    DEBT = "tech_debt"        # Risk
    DOCUMENTATION = "docs"

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"         
    DONE = "done"

class ActivityType(str, Enum):
    COMMIT = "commit"
    PR_OPEN = "pr_open"
    PR_REVIEW = "pr_review"
    SPRINT_UPDATE = "sprint_update"
    DEPLOYMENT = "deployment" 
    ASSIGNMENT_CHANGE = "assignment_change" # Tracking adds/removes

# --- 3. BASE MODEL ---
class BaseModelId(BaseModel):
    """Base class for all models to handle _id mapping"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

# --- 4. CORE MODELS ---

class User(BaseModelId):
    name: str
    email: str
    role: Role
    hourly_rate: float = 50.0
    skills: List[str]
    work_profile_embeddings: List[float]
    
    # Maps Project ID -> Cumulative Hours Spent (The "Familiarity" Score)
    project_metrics: Dict[str, float] = Field(default_factory=dict)
    
    github_username: Optional[str] = None
    jira_account_id: Optional[str] = None

class Project(BaseModelId):
    name: str
    repo_url: Optional[str] = None
    total_budget: float = 0.0

class Sprint(BaseModelId):
    project_id: PyObjectId
    name: str
    start_date: datetime
    end_date: datetime
    goal: str
    is_active: bool = True

class WorkSession(BaseModelId):
    """
    THE TIME TRACKER.
    One task can have MANY work sessions by MANY users.
    """
    task_id: PyObjectId
    user_id: PyObjectId
    
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None  # None means "Currently Working"
    
    duration_minutes: float = 0.0 # Calculated when end_time is set
    
    # Audit trail: Who added them? (e.g., "Manager Bob assigned Alice")
    assigned_by_user_id: Optional[PyObjectId] = None 

class Task(BaseModelId):
    """The Work Item"""
    external_id: str        # "PROJ-123"
    title: str
    description: str
    description_embeddings: List[float] # Task semantic vector
    
    type: TaskType
    status: TaskStatus
    priority: str
    
    # Ownership
    project_id: PyObjectId
    sprint_id: Optional[PyObjectId] = None
    
    # --- MULTI-USER ASSIGNMENT ---
    # List of users CURRENTLY working on this.
    # History is tracked in the 'WorkSession' table.
    current_assignee_ids: List[PyObjectId] = Field(default_factory=list)
    
    # Sprint History (To track rollovers)
    sprint_history: List[PyObjectId] = Field(default_factory=list)
    rollover_count: int = 0
    
    # Aggregated Metrics (Sum of all WorkSessions)
    total_time_spent_minutes: int = 0
    total_cost: float = 0.0 # (User A Time * Rate A) + (User B Time * Rate B)
    
    created_at: datetime
    updated_at: datetime

class ActivityLog(BaseModelId):
    """The Event Stream"""
    user_id: PyObjectId
    task_id: Optional[PyObjectId] = None
    project_id: PyObjectId

    work_session_id: Optional[PyObjectId] = None # if none then can be used for anayltics ki pp are owrking on unassigned tasks or general project activity

    activity_type: ActivityType
    content: str 
    timestamp: datetime

    # Semantic Search for "Activity Relevance"
    # Matches Activity Content to Task Description
    embedding: List[float] = Field(default_factory=list)

    # Impact Metrics
    files_touched: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    
    # Metadata for raw webhook JSON (e.g., { "pr_link": "...", "reviewer": "Bob" })
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Issue(BaseModelId):
    """
    Issue/Task representation with embeddings for similarity search
    """
    title: str
    description: str
    description_embedding: List[float] = Field(default_factory=list)
    
    # If this is identified as duplicate
    parent_task_id: Optional[PyObjectId] = None
    is_duplicate: bool = False
    
    # Extracted metadata
    required_skills: List[str] = Field(default_factory=list)
    skill_embeddings: List[float] = Field(default_factory=list)
    priority: str = "medium"
    
    # Assignment info
    assigned_user_id: Optional[PyObjectId] = None
    assignment_status: str = "pending"  # pending, assigned, posting_required
    
    # Activity tracking
    activity_log: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Source info
    source: str = "api"  # api, jira, github, etc
    external_id: Optional[str] = None
    project_id: Optional[PyObjectId] = None


class Commit(BaseModelId):
    """
    Git commit with analysis and skill extraction
    """
    commit_hash: str
    commit_message: str
    diff_content: str  # The actual diff
    
    # LLM Analysis
    summary: str  # Problem solved or feature built
    extracted_skills: List[str] = Field(default_factory=list)
    summary_embedding: List[float] = Field(default_factory=list)
    
    # Task linking
    linked_task_id: Optional[PyObjectId] = None
    is_jira_tracked: bool = False
    
    # Author info
    author_email: str
    author_name: str
    user_id: Optional[PyObjectId] = None  # Linked to our User model
    
    # Metadata
    repository: str
    branch: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Impact metrics
    files_changed: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    
    # Profile evolution tracking
    triggered_profile_update: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)