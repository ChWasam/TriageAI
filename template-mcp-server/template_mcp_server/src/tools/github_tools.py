"""
GitHub Issue Triage Tools

Tools for interacting with GitHub API for issue triage automation.
"""

import os
from typing import Dict, List, Any
from github import Github, GithubException
import structlog

logger = structlog.get_logger(__name__)


def parse_issue(repo_name: str, issue_number: int) -> Dict[str, Any]:
    """
    Retrieve issue details from GitHub repository.

    Fetches complete issue information including title, body, labels,
    author, creation date, and current state.

    Args:
        repo_name: Repository in format 'owner/repo'
        issue_number: Issue number to fetch

    Returns:
        Dictionary with issue details: number, title, body, labels, author,
        created_at, state, comments_count

    Raises:
        ValueError: If GITHUB_TOKEN is not set
        GithubException: If issue or repo not found
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is required")

    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        issue = repo.get_issue(issue_number)

        return {
            "number": issue.number,
            "title": issue.title,
            "body": issue.body or "",
            "labels": [label.name for label in issue.labels],
            "author": issue.user.login,
            "created_at": issue.created_at.isoformat(),
            "state": issue.state,
            "comments_count": issue.comments,
            "url": issue.html_url
        }
    except GithubException as e:
        logger.error("Failed to fetch issue", repo=repo_name, issue=issue_number, error=str(e))
        raise


def search_duplicates(
    repo_name: str,
    title: str,
    body: str,
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for potential duplicate issues using keyword matching.

    Performs keyword-based search in the repository to find similar issues.
    For production, this should use semantic similarity (e.g., Jina embeddings).

    Args:
        repo_name: Repository in format 'owner/repo'
        title: Issue title to search for
        body: Issue body to search for
        max_results: Maximum number of similar issues to return (default: 5)

    Returns:
        List of similar issues with number, title, state, similarity score

    Raises:
        ValueError: If GITHUB_TOKEN is not set
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is required")

    try:
        g = Github(token)
        repo = g.get_repo(repo_name)

        # Extract keywords from title (simple approach for hackathon)
        keywords = " ".join(title.split()[:5])  # Use first 5 words

        # Search open and closed issues
        query = f"repo:{repo_name} is:issue {keywords}"
        issues = g.search_issues(query=query, sort="created", order="desc")

        results = []
        for issue in issues[:max_results]:
            results.append({
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "url": issue.html_url,
                "similarity_score": 0.5  # Placeholder for semantic similarity
            })

        logger.info("Duplicate search completed", results_count=len(results))
        return results

    except GithubException as e:
        logger.error("Failed to search duplicates", repo=repo_name, error=str(e))
        return []


def classify_issue(title: str, body: str) -> Dict[str, Any]:
    """
    Classify issue type, priority, and area using simple heuristics.

    Uses keyword matching to determine issue classification.
    In production, this should use LLM-based classification.

    Args:
        title: Issue title
        body: Issue description

    Returns:
        Dictionary with issue_type (bug/feature/docs/question),
        priority (critical/high/medium/low), and area (frontend/backend/infra/etc)
    """
    text = (title + " " + body).lower()

    # Simple keyword-based classification
    issue_type = "question"
    if any(word in text for word in ["bug", "error", "fail", "crash", "broken"]):
        issue_type = "bug"
    elif any(word in text for word in ["feature", "add", "implement", "enhance"]):
        issue_type = "feature"
    elif any(word in text for word in ["doc", "documentation", "readme", "guide"]):
        issue_type = "docs"

    # Priority detection
    priority = "medium"
    if any(word in text for word in ["critical", "urgent", "asap", "production down"]):
        priority = "critical"
    elif any(word in text for word in ["important", "blocker", "high priority"]):
        priority = "high"
    elif any(word in text for word in ["minor", "low priority", "nice to have"]):
        priority = "low"

    # Area detection
    area = "general"
    if any(word in text for word in ["ui", "frontend", "react", "css"]):
        area = "frontend"
    elif any(word in text for word in ["api", "backend", "server", "database"]):
        area = "backend"
    elif any(word in text for word in ["deploy", "ci/cd", "docker", "kubernetes"]):
        area = "infra"
    elif any(word in text for word in ["test", "testing", "spec"]):
        area = "testing"

    logger.info("Issue classified", type=issue_type, priority=priority, area=area)

    return {
        "issue_type": issue_type,
        "priority": priority,
        "area": area
    }


def execute_actions(
    repo_name: str,
    issue_number: int,
    labels: List[str] = None,
    assignee: str = None,
    comment: str = None
) -> Dict[str, str]:
    """
    Execute triage actions on a GitHub issue.

    Applies labels, assigns team members, and posts comments to the issue.

    Args:
        repo_name: Repository in format 'owner/repo'
        issue_number: Issue number to update
        labels: List of label names to add (optional)
        assignee: GitHub username to assign (optional)
        comment: Comment text to post (optional)

    Returns:
        Dictionary with status and message

    Raises:
        ValueError: If GITHUB_TOKEN is not set
        GithubException: If update fails
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is required")

    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        issue = repo.get_issue(issue_number)

        actions_taken = []

        # Add labels
        if labels:
            issue.add_to_labels(*labels)
            actions_taken.append(f"Added labels: {', '.join(labels)}")

        # Assign user
        if assignee:
            issue.add_to_assignees(assignee)
            actions_taken.append(f"Assigned to: {assignee}")

        # Post comment
        if comment:
            issue.create_comment(comment)
            actions_taken.append("Posted triage comment")

        logger.info("Actions executed", issue=issue_number, actions=actions_taken)

        return {
            "status": "success",
            "message": "; ".join(actions_taken),
            "issue_url": issue.html_url
        }

    except GithubException as e:
        logger.error("Failed to execute actions", issue=issue_number, error=str(e))
        raise


def get_repo_info(repo_name: str) -> Dict[str, Any]:
    """
    Fetch repository metadata and configuration.

    Retrieves repository information including available labels,
    collaborators, and repository statistics.

    Args:
        repo_name: Repository in format 'owner/repo'

    Returns:
        Dictionary with repo name, labels, collaborators, open_issues_count

    Raises:
        ValueError: If GITHUB_TOKEN is not set
        GithubException: If repo not found
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is required")

    try:
        g = Github(token)
        repo = g.get_repo(repo_name)

        # Get available labels
        labels = [label.name for label in repo.get_labels()]

        # Get collaborators (limited for rate limiting)
        collaborators = [c.login for c in list(repo.get_collaborators())[:10]]

        return {
            "name": repo.full_name,
            "labels": labels,
            "collaborators": collaborators,
            "open_issues_count": repo.open_issues_count,
            "default_branch": repo.default_branch,
            "description": repo.description
        }

    except GithubException as e:
        logger.error("Failed to fetch repo info", repo=repo_name, error=str(e))
        raise
