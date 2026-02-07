"""
CoreSight Utils Package

Contains utility functions and helpers.
"""

from .utils import (
    get_db,
    get_db_manager,
    set_db_manager,
    serialize_doc,
    serialize_docs,
    success_response,
    error_response,
)

from ai.vector_search import (
    search_similar_issues,
    search_similar_tasks_for_commit,
    find_user_by_email,
)

__all__ = [
    "get_db",
    "get_db_manager",
    "set_db_manager",
    "serialize_doc",
    "serialize_docs",
    "success_response",
    "error_response",
    "search_similar_issues",
    "search_similar_tasks_for_commit",
    "find_user_by_email",
]
