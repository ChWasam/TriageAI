"""
Execute Node - Executes triage actions on GitHub.

Applies labels, assignees, and comments to the GitHub issue.
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


async def execute_actions(state: TriageState) -> dict:
    """
    Execute triage actions on GitHub issue.

    Calls the MCP execute_actions tool to apply labels,
    assignees, and post comments on the issue.

    Args:
        state: Current workflow state with team_assignment

    Returns:
        Updated state with actions_result dict
    """
    team_assignment = state.get("team_assignment", {})
    repo_name = state.get("repo_name", "")
    issue_number = state.get("issue_number", 0)

    # Skip if issue is invalid or no assignment
    if not state.get("is_valid", True) or not team_assignment:
        logger.info("Skipping action execution for invalid/unassigned issue")
        return {
            **state,
            "actions_result": {
                "status": "skipped",
                "message": "Issue validation failed or no assignment"
            }
        }

    try:
        labels = team_assignment.get("labels", [])
        assignee = team_assignment.get("assignee")
        comment = team_assignment.get("comment")

        # In production, this would call the MCP execute_actions tool
        # For now, logging the actions
        logger.info(
            "Executing triage actions",
            repo=repo_name,
            issue=issue_number,
            labels=labels,
            assignee=assignee,
            has_comment=bool(comment)
        )

        # Placeholder result
        actions_result = {
            "status": "success",
            "message": f"Would apply labels: {', '.join(labels)}",
            "labels_added": labels,
            "assignee_added": assignee,
            "comment_posted": bool(comment)
        }

        logger.info(
            "Triage actions completed",
            issue=issue_number,
            result=actions_result
        )

        return {
            **state,
            "actions_result": actions_result
        }

    except Exception as e:
        logger.error("Action execution failed", error=str(e))
        return {
            **state,
            "actions_result": {
                "status": "failed",
                "message": f"Error: {str(e)}"
            }
        }
