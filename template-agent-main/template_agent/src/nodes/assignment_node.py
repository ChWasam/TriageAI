"""
Assignment Node - Routes issue to appropriate team.

Maps the issue to the right team member or label based on classification.
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


# Team mapping configuration
TEAM_ASSIGNMENTS = {
    "frontend": {
        "labels": ["frontend", "ui"],
        "assignee": None  # Set based on your team
    },
    "backend": {
        "labels": ["backend", "api"],
        "assignee": None
    },
    "infra": {
        "labels": ["infrastructure", "devops"],
        "assignee": None
    },
    "testing": {
        "labels": ["testing", "qa"],
        "assignee": None
    },
    "general": {
        "labels": ["triage"],
        "assignee": None
    }
}


async def assign_team(state: TriageState) -> dict:
    """
    Assign the issue to appropriate team.

    Maps classification to team labels and assignees.

    Args:
        state: Current workflow state with classification

    Returns:
        Updated state with team_assignment dict containing labels and assignee
    """
    classification = state.get("classification", {})

    # Skip if issue is invalid or not classified
    if not state.get("is_valid", True) or not classification:
        logger.info("Skipping team assignment for invalid/unclassified issue")
        return {
            **state,
            "team_assignment": {
                "labels": [],
                "assignee": None,
                "comment": None
            }
        }

    try:
        issue_type = classification.get("issue_type", "question")
        priority = classification.get("priority", "medium")
        area = classification.get("area", "general")

        # Get team assignment based on area
        team_info = TEAM_ASSIGNMENTS.get(area, TEAM_ASSIGNMENTS["general"])

        # Build label list
        labels = []
        labels.append(issue_type)  # Add type label (bug/feature/docs/question)
        labels.append(f"priority:{priority}")  # Add priority label
        labels.extend(team_info["labels"])  # Add area labels

        # Get assignee
        assignee = team_info["assignee"]

        # Build triage comment
        comment = f"""🤖 **Automated Triage**

**Type:** {issue_type}
**Priority:** {priority}
**Area:** {area}

This issue has been automatically triaged. A team member will review it shortly.
"""

        team_assignment = {
            "labels": labels,
            "assignee": assignee,
            "comment": comment
        }

        logger.info(
            "Team assigned",
            issue=state.get("issue_number"),
            assignment=team_assignment
        )

        return {
            **state,
            "team_assignment": team_assignment
        }

    except Exception as e:
        logger.error("Team assignment failed", error=str(e))
        return {
            **state,
            "team_assignment": {
                "labels": [],
                "assignee": None,
                "comment": None
            }
        }
