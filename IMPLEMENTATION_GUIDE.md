# GitHub Issue Triage Agent - Implementation Guide

**Simple step-by-step guide to customize the templates**

Templates are already running:
- MCP Server: `http://localhost:5001`
- Agent: `http://localhost:5002`
- UI: `http://localhost:5003`

---

## 1. SETUP ENVIRONMENT VARIABLES (5 minutes)

**Create `.env` file in the Triage directory:**

```bash
cd /Users/wasamchaudhry/Study/Open\ Accelerator\ Hackathon\ RedHat/Triage

cat > .env << EOF
# GitHub Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=yourusername/repo-name

# LLM (choose one)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
# Or use Claude:
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=your_key_here

# Server Ports
MCP_SERVER_PORT=5001
AGENT_SERVER_PORT=5002
UI_PORT=5003
EOF
```

**Get GitHub Token:**
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `write:org`
4. Copy token and paste in `.env`

**Create test repo:**
1. Go to github.com → New repository
2. Name: `triage-agent-demo`
3. Public, initialize with README
4. Copy repo name to `.env` (format: `username/triage-agent-demo`)

---

## 2. ADD GITHUB TOOLS TO MCP SERVER (45 minutes)

### Step 2.1: Install Dependencies

```bash
cd template-mcp-server

# Add PyGithub to pyproject.toml
cat >> pyproject.toml << EOF
PyGithub = "^2.1.1"
EOF

# Install
uv sync
```

### Step 2.2: Create GitHub Tools File

**Create file: `template_mcp_server/src/tools/github_tools.py`**

```python
"""GitHub tools for issue triage."""

import os
from typing import Any, Dict, List
from github import Github
from template_mcp_server.utils.pylogger import get_python_logger

logger = get_python_logger()

# Initialize GitHub client
g = Github(os.getenv("GITHUB_TOKEN"))


def parse_issue(repo_name: str, issue_number: int) -> Dict[str, Any]:
    """Fetch issue details from GitHub.

    TOOL_NAME=parse_issue
    DISPLAY_NAME=Parse GitHub Issue
    USECASE=Retrieve issue details from a GitHub repository

    Args:
        repo_name: Repository name (format: owner/repo)
        issue_number: Issue number to fetch

    Returns:
        Dictionary with issue details (title, body, labels, etc.)
    """
    try:
        repo = g.get_repo(repo_name)
        issue = repo.get_issue(issue_number)

        return {
            "status": "success",
            "number": issue.number,
            "title": issue.title,
            "body": issue.body or "",
            "author": issue.user.login,
            "labels": [label.name for label in issue.labels],
            "state": issue.state,
            "created_at": str(issue.created_at)
        }
    except Exception as e:
        logger.error(f"Error parsing issue: {e}")
        return {"status": "error", "error": str(e)}


def classify_issue(title: str, body: str) -> Dict[str, Any]:
    """Classify issue type, priority, and area using simple heuristics.

    TOOL_NAME=classify_issue
    DISPLAY_NAME=Classify GitHub Issue
    USECASE=Determine issue type (bug/feature), priority, and component area

    Args:
        title: Issue title
        body: Issue body/description

    Returns:
        Dictionary with classification (type, priority, area)
    """
    try:
        text = f"{title} {body}".lower()

        # Determine type
        if any(word in text for word in ["bug", "error", "crash", "broken", "issue"]):
            issue_type = "bug"
        elif any(word in text for word in ["feature", "add", "implement", "enhancement"]):
            issue_type = "feature"
        elif any(word in text for word in ["docs", "documentation", "readme"]):
            issue_type = "docs"
        else:
            issue_type = "question"

        # Determine priority
        if any(word in text for word in ["critical", "urgent", "crash", "broken"]):
            priority = "high"
        elif any(word in text for word in ["minor", "typo", "small"]):
            priority = "low"
        else:
            priority = "medium"

        # Determine area
        if any(word in text for word in ["auth", "login", "signup", "password"]):
            area = "auth"
        elif any(word in text for word in ["ui", "button", "design", "css", "frontend"]):
            area = "ui"
        elif any(word in text for word in ["api", "endpoint", "backend", "server"]):
            area = "api"
        elif any(word in text for word in ["database", "db", "sql"]):
            area = "database"
        else:
            area = "general"

        return {
            "status": "success",
            "type": issue_type,
            "priority": priority,
            "area": area,
            "confidence": 0.8
        }
    except Exception as e:
        logger.error(f"Error classifying issue: {e}")
        return {"status": "error", "error": str(e)}


def execute_actions(
    repo_name: str,
    issue_number: int,
    labels: List[str],
    assignees: List[str],
    comment: str
) -> Dict[str, Any]:
    """Apply labels, assignees, and comment to GitHub issue.

    TOOL_NAME=execute_actions
    DISPLAY_NAME=Execute GitHub Actions
    USECASE=Apply triage actions (labels, assignees, comments) to an issue

    Args:
        repo_name: Repository name
        issue_number: Issue number
        labels: Labels to add
        assignees: Users to assign
        comment: Comment to post

    Returns:
        Dictionary with actions taken
    """
    try:
        repo = g.get_repo(repo_name)
        issue = repo.get_issue(issue_number)

        actions_taken = []

        # Add labels
        if labels:
            issue.add_to_labels(*labels)
            actions_taken.append(f"Added labels: {', '.join(labels)}")

        # Assign users (skip if user doesn't exist)
        if assignees:
            try:
                issue.add_to_assignees(*assignees)
                actions_taken.append(f"Assigned to: {', '.join(assignees)}")
            except:
                logger.warning(f"Could not assign users: {assignees}")

        # Post comment
        if comment:
            issue.create_comment(comment)
            actions_taken.append("Posted comment")

        return {
            "status": "success",
            "actions_taken": actions_taken,
            "message": "Actions completed successfully"
        }
    except Exception as e:
        logger.error(f"Error executing actions: {e}")
        return {"status": "error", "error": str(e)}
```

### Step 2.3: Register Tools

**Edit file: `template_mcp_server/template_mcp_server/src/mcp.py`**

Find the `_register_mcp_tools` method and add:

```python
def _register_mcp_tools(self) -> None:
    """Register all MCP tools."""
    # Import GitHub tools
    from template_mcp_server.src.tools.github_tools import (
        parse_issue,
        classify_issue,
        execute_actions
    )

    # Register tools
    self.mcp.tool()(parse_issue)
    self.mcp.tool()(classify_issue)
    self.mcp.tool()(execute_actions)

    # Keep existing tools
    from template_mcp_server.src.tools.multiply_tool import multiply_numbers
    self.mcp.tool()(multiply_numbers)
```

### Step 2.4: Test Tools

```bash
# Restart MCP server
cd template-mcp-server
make local

# Test in another terminal
curl -X POST "http://localhost:5001/tools/parse_issue?repo_name=yourusername/triage-agent-demo&issue_number=1"
```

---

## 3. CUSTOMIZE AGENT WORKFLOW (60 minutes)

### Step 3.1: Update System Prompt

**Edit: `template-agent-main/template_agent/src/core/prompt.py`**

Replace the `get_system_prompt()` function:

```python
def get_system_prompt() -> str:
    """Get the main system prompt for the triage agent."""
    current_date = get_current_date()

    return (
        f"You are GitHub Triage Agent, an intelligent assistant that automatically triages GitHub issues.\n\n"
        f"Today's date is {current_date}.\n\n"
        "Your workflow:\n"
        "1. **Parse the issue** using parse_issue tool\n"
        "2. **Classify the issue** using classify_issue tool to determine type, priority, and area\n"
        "3. **Execute triage actions** using execute_actions tool to apply labels and post a comment\n\n"
        "Available tools:\n"
        "- parse_issue: Fetch issue details from GitHub\n"
        "- classify_issue: Determine issue type, priority, and component area\n"
        "- execute_actions: Apply labels, assignees, and post comments\n\n"
        "Always follow this workflow in order. Be thorough and professional in your comments.\n\n"
        "Format responses in HTML with Tailwind CSS for the dashboard."
    )
```

### Step 3.2: Update Agent Config

**Edit: `template-agent-main/template_agent/src/settings.py`**

Find the MCP server configuration and update:

```python
# Ensure this points to your MCP server
MCP_SERVER_URL = "http://localhost:5001"
```

### Step 3.3: Test Agent

```bash
# Restart agent
cd template-agent-main
make local

# Test via UI at http://localhost:5003
# Message: "Triage issue #1 from repo yourusername/triage-agent-demo"
```

---

## 4. UPDATE UI DASHBOARD (30 minutes)

### Step 4.1: Update App Title

**Edit: `template-ui-main/frontend/src/App.tsx`**

Find the header and update:

```typescript
<header className="mb-8">
  <h1 className="text-4xl font-bold">
    GitHub Issue Triage Agent
  </h1>
  <p className="text-gray-600 mt-2">
    Automated issue triage powered by AI
  </p>
</header>
```

### Step 4.2: Test UI

```bash
# Restart UI (if needed)
cd template-ui-main
npm run dev

# Open http://localhost:5003
```

---

## 5. TEST END-TO-END (30 minutes)

### Step 5.1: Create Test Issue

1. Go to your GitHub repo
2. Create a new issue:
   - Title: "App crashes when uploading large files"
   - Body: "Steps to reproduce: 1. Open app 2. Upload file > 10MB 3. App crashes. Error: MemoryException"
3. Note the issue number

### Step 5.2: Test via UI

1. Open UI: http://localhost:5003
2. In the chat, type: `Triage issue #1 from repo yourusername/triage-agent-demo`
3. Watch the agent:
   - Parse the issue
   - Classify it (should detect: bug, high priority, general area)
   - Apply labels and post comment
4. Refresh GitHub issue to see labels and comment

### Step 5.3: Verify Results

Check on GitHub:
- Labels should be added: `bug`, `priority:high`, `area:general`
- Comment should be posted by your app
- Issue should still be open

---

## 6. QUICK TROUBLESHOOTING

**Problem: "parse_issue tool not found"**
```bash
# Check tool is registered in mcp.py
# Restart MCP server
cd template-mcp-server
make local
```

**Problem: "GitHub API authentication failed"**
```bash
# Check .env has correct GITHUB_TOKEN
# Test token: curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

**Problem: "Agent doesn't use tools"**
```bash
# Check MCP_SERVER_URL in template-agent-main/template_agent/src/settings.py
# Should be: http://localhost:5001
```

**Problem: "Classification is incorrect"**
```bash
# The classify_issue tool uses simple keyword matching
# You can improve it by:
# 1. Using an LLM (Ollama/Claude) instead of keywords
# 2. Adding more keywords to the logic
```

---

## NEXT STEPS

### Option A: Add Webhook Automation (Advanced)

Make the agent trigger automatically when issues are created:

1. Install ngrok: `brew install ngrok`
2. Expose MCP server: `ngrok http 5001`
3. Add webhook to GitHub repo settings
4. Implement webhook endpoint in MCP server

### Option B: Improve Classification

Replace keyword-based classification with LLM:

```python
def classify_issue(title: str, body: str) -> Dict[str, Any]:
    """Classify using LLM instead of keywords."""
    from langchain_community.llms import Ollama

    llm = Ollama(model="llama3.2")
    prompt = f"""Classify this GitHub issue:
    Title: {title}
    Body: {body}

    Respond with JSON:
    {{"type": "bug|feature|docs|question", "priority": "high|medium|low", "area": "auth|ui|api|database|general"}}
    """

    response = llm.invoke(prompt)
    # Parse JSON from response
    # Return classification
```

### Option C: Add Duplicate Detection

Implement semantic search to find similar issues:

1. Use Jina embeddings API
2. Compare issue similarity
3. Close duplicates automatically

---

## SUCCESS CHECKLIST

- [ ] GitHub token configured in `.env`
- [ ] MCP server has 3 GitHub tools registered
- [ ] Agent uses tools in correct order
- [ ] UI chat triggers full workflow
- [ ] Labels appear on GitHub issue
- [ ] Comment is posted on GitHub issue

---

**You're ready to demo! 🚀**

**Demo script:**
1. Show GitHub repo with unlabeled issue
2. Open UI, send triage command
3. Watch agent work in real-time
4. Refresh GitHub to show labels applied
5. Explain: "Manual triage: 15 min → Automated: 8 seconds"
