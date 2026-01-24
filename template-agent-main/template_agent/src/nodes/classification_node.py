"""
Classification Node - Classifies issue type, priority, and area.

Uses MCP tool to classify the issue using LLM or heuristics.
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


async def classify_issue(state: TriageState) -> dict:
    """
    Classify the issue.

    Determines issue type (bug/feature/docs/question),
    priority (critical/high/medium/low),
    and area (frontend/backend/infra/etc).

    Args:
        state: Current workflow state with issue_data

    Returns:
        Updated state with classification dict
    """
    issue_data = state.get("issue_data", {})
    title = issue_data.get("title", "")
    body = issue_data.get("body", "")

    # Skip if issue is invalid
    if not state.get("is_valid", True):
        logger.info("Skipping classification for invalid issue")
        return {
            **state,
            "classification": {}
        }

    try:
        # In production, this would call the MCP classify_issue tool
        # For now, using simple heuristics
        text = (title + " " + body).lower()

        # Classify type
        issue_type = "question"
        if any(word in text for word in ["bug", "error", "fail", "crash", "broken"]):
            issue_type = "bug"
        elif any(word in text for word in ["feature", "add", "implement", "enhance"]):
            issue_type = "feature"
        elif any(word in text for word in ["doc", "documentation", "readme", "guide"]):
            issue_type = "docs"

        # Classify priority
        priority = "medium"
        if any(word in text for word in ["critical", "urgent", "asap", "production down"]):
            priority = "critical"
        elif any(word in text for word in ["important", "blocker", "high priority"]):
            priority = "high"
        elif any(word in text for word in ["minor", "low priority", "nice to have"]):
            priority = "low"

        # Classify area
        area = "general"
        if any(word in text for word in ["ui", "frontend", "react", "css"]):
            area = "frontend"
        elif any(word in text for word in ["api", "backend", "server", "database"]):
            area = "backend"
        elif any(word in text for word in ["deploy", "ci/cd", "docker", "kubernetes"]):
            area = "infra"
        elif any(word in text for word in ["test", "testing", "spec"]):
            area = "testing"

        classification = {
            "issue_type": issue_type,
            "priority": priority,
            "area": area
        }

        logger.info(
            "Issue classified",
            issue=issue_data.get("number"),
            classification=classification
        )

        return {
            **state,
            "classification": classification
        }

    except Exception as e:
        logger.error("Classification failed", error=str(e))
        return {
            **state,
            "classification": {}
        }
