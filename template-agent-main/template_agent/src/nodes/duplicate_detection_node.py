"""
Duplicate Detection Node - Searches for similar issues.

Uses MCP tool to search for potential duplicate issues.
"""

from typing import TypedDict, Any
import structlog

logger = structlog.get_logger(__name__)


class TriageState(TypedDict):
    """State object for triage workflow."""
    repo_name: str
    issue_number: int
    issue_data: dict
    is_valid: bool
    validation_message: str
    duplicates: list
    classification: dict
    team_assignment: dict
    actions_result: dict


async def search_duplicates(state: TriageState) -> dict:
    """
    Search for duplicate issues.

    Calls the MCP search_duplicates tool to find similar issues
    based on title and body content.

    Args:
        state: Current workflow state with issue_data

    Returns:
        Updated state with duplicates list
    """
    issue_data = state.get("issue_data", {})
    repo_name = state.get("repo_name", "")
    title = issue_data.get("title", "")
    body = issue_data.get("body", "")

    # Skip if issue is invalid
    if not state.get("is_valid", True):
        logger.info("Skipping duplicate search for invalid issue")
        return {
            **state,
            "duplicates": []
        }

    try:
        # In production, this would call the MCP tool
        # For now, using placeholder logic
        duplicates = []

        logger.info(
            "Duplicate search completed",
            issue=issue_data.get("number"),
            found=len(duplicates)
        )

        return {
            **state,
            "duplicates": duplicates
        }

    except Exception as e:
        logger.error("Duplicate search failed", error=str(e))
        return {
            **state,
            "duplicates": []
        }
