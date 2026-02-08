"""
CoreSight AI Package

This package contains AI-powered utilities for:
- Embedding generation
- Skill extraction
- Task matching
- Issue analysis
- Profile evolution
"""

from .client import client, EMBEDDING_MODEL, LLM_MODEL
from .embeddings import generate_embedding, calculate_cosine_similarity
from .skills import extract_skills_from_task, extract_skills_fallback
from .matching import find_best_matching_users
from .validation import validate_user_assignment_with_llm, evaluate_candidates_batch
from .reports import generate_no_match_report, generate_fallback_job_description
from .analysis import (
    check_issue_duplicate_with_llm,
    extract_skills_from_commit_diff,
    check_profile_update_needed,
)

__all__ = [
    # Client
    "client",
    "EMBEDDING_MODEL",
    "LLM_MODEL",
    # Embeddings
    "generate_embedding",
    "calculate_cosine_similarity",
    # Skills
    "extract_skills_from_task",
    "extract_skills_fallback",
    # Matching
    "find_best_matching_users",
    # Validation
    "validate_user_assignment_with_llm",
    "evaluate_candidates_batch",
    # Reports
    "generate_no_match_report",
    "generate_fallback_job_description",
    # Analysis
    "check_issue_duplicate_with_llm",
    "extract_skills_from_commit_diff",
    "check_profile_update_needed",
]
