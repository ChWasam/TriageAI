"""
Assessment Node - Validates issue quality.

Checks if the issue has sufficient information for triage.
"""

from typing import TypedDict
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


async def assess_quality(state: TriageState) -> dict:
    """
    Assess the quality of the issue.

    Validates that the issue has:
    - A non-empty title
    - A body with sufficient description (>20 characters)
    - Not already triaged (no triage labels)

    Args:
        state: Current workflow state with issue_data

    Returns:
        Updated state with is_valid and validation_message fields
    """
    issue_data = state.get("issue_data", {})
    title = issue_data.get("title", "")
    body = issue_data.get("body", "")
    labels = issue_data.get("labels", [])

    validation_message = ""
    is_valid = True

    # Check title
    if not title or len(title.strip()) < 5:
        is_valid = False
        validation_message = "Issue title is too short or missing"
        logger.warning("Invalid issue: title too short", issue=issue_data.get("number"))

    # Check body
    elif not body or len(body.strip()) < 20:
        is_valid = False
        validation_message = "Issue description is too short or missing"
        logger.warning("Invalid issue: body too short", issue=issue_data.get("number"))

    # Check if already triaged (has type labels)
    elif any(label in labels for label in ["bug", "feature", "docs", "question"]):
        is_valid = False
        validation_message = "Issue already triaged (has type labels)"
        logger.info("Issue already triaged", issue=issue_data.get("number"))

    else:
        validation_message = "Issue passed quality checks"
        logger.info("Issue validation passed", issue=issue_data.get("number"))

    return {
        **state,
        "is_valid": is_valid,
        "validation_message": validation_message
    }
