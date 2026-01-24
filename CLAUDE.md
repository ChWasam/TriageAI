# GitHub Issue Triage Agent - AI Assistant Context

## Project Overview

**What It Does:**
AI-powered automated GitHub issue triage system that:
- Validates issue quality
- Detects duplicates using semantic similarity
- Classifies type (bug/feature/docs), priority, and area
- Routes to appropriate team
- Applies labels, assignees, and comments automatically

**Problem:** Open source maintainers waste 10-20 hours/week manually triaging issues (15 min per issue)
**Solution:** Automated triage in 8 seconds per issue (99.1% time reduction)

**Hackathon:** Red Hat AI Hackathon - January 24, 2026 (TODAY!)
**Framework:** aitemplates.io (MCP Server + Agent + UI)
**Build Time:** 5-6 hours
**Demo Focus:** Working end-to-end automation with real-time visibility

---

## Critical Goals & Constraints

### MUST Have
- Use all 3 templates: MCP Server + LangGraph Agent + React UI
- Working demo (code without demo = failure)
- Process issues in < 15 seconds
- In-memory storage only (no complex DB)
- Speed over perfection

### Success Metrics
- [ ] Issue created → Webhook → Agent → GitHub updated (< 15 seconds)
- [ ] 5 MCP tools functional
- [ ] 6-node LangGraph workflow complete
- [ ] Dashboard shows real-time events
- [ ] Live demo under 4 minutes

---

## Tech Stack

**Backend:** FastAPI, PyGithub, LangGraph, LangChain, Pydantic
**LLM:** Ollama (local) or Claude API
**Frontend:** React, TypeScript, Vite, Tailwind CSS
**Infrastructure:** ngrok (webhooks), GitHub API

---

## Directory Structure

```
/Users/wasamchaudhry/Study/Open Accelerator Hackathon RedHat/Triage/
├── template-mcp-server/        # MCP Server (port 5001) ✓ Running
│   ├── src/
│   │   ├── tools/             # ADD: github_tools.py (5 tools)
│   │   ├── mcp.py             # EDIT: Register GitHub tools
│   │   └── main.py            # EDIT: Add webhook handler
│   └── pyproject.toml         # ADD: PyGithub dependency
│
├── template-agent/             # Agent (port 5002) ✓ Running
│   ├── src/
│   │   ├── agent/
│   │   │   ├── prompts.py     # EDIT: Triage system prompt
│   │   │   ├── config.py      # EDIT: MCP server URL
│   │   │   └── graph.py       # BUILD: 6-node workflow
│   │   └── nodes/             # ADD: 5 node files
│   └── pyproject.toml
│
├── template-ui/                # UI (port 5003) ✓ Running
│   ├── frontend/src/
│   │   ├── App.tsx            # EDIT: GitHub Triage Dashboard
│   │   └── components/        # ADD: Event feed, stats
│   └── backend/src/api.py     # ADD: /events/recent endpoint
│
└── .env                        # ADD: GITHUB_TOKEN, GITHUB_REPO
```

---

## Coding Conventions

### Simple Code Philosophy (CRITICAL)
- **ALWAYS write the simplest possible code** - No complex abstractions
- **Small incremental steps** - Build piece by piece
- **ALWAYS get approval before implementing** - Show plan, get confirmation
- **Working code > Perfect code** - Prioritize functionality over elegance

### Python
- Type hints required: `def parse_issue(repo: str, num: int) -> IssueData:`
- Async/await for all I/O
- Pydantic models for data validation
- Use logging, not print
- Clear docstrings (agent reads these to discover tools!)

### TypeScript/React
- Functional components only
- TypeScript interfaces for all data
- Tailwind CSS for styling
- Clear component names (PascalCase)

### LangGraph
- State as TypedDict (not classes)
- Nodes as async functions that return updated state
- **NEVER mutate state in-place** - Return new state: `return {**state, 'field': value}`

---

## Customizing Templates

### Current Status
- **MCP Server**: Running on port 5001 ✓
- **Agent**: Running on port 5002 ✓
- **UI**: Running on port 5003 ✓
- **Tools Available**: 3 example tools (multiply_numbers, etc.)

### Step 1: MCP Server - Add GitHub Tools

**Create `src/tools/github_tools.py` with 5 tools:**

1. `parse_issue(repo_name: str, issue_number: int)` - Fetch issue from GitHub
2. `search_duplicates(title: str, body: str)` - Semantic duplicate search
3. `classify_issue(title: str, body: str)` - LLM classification
4. `execute_actions(issue_number: int, labels: list, assignee: str)` - Apply to GitHub
5. `get_repo_info(repo_name: str)` - Fetch repo metadata

**Example tool:**
```python
from github import Github
import os

def parse_issue(repo_name: str, issue_number: int):
    """
    Retrieve issue details from GitHub repository.

    Args:
        repo_name: Repository in format 'owner/repo'
        issue_number: Issue number to fetch

    Returns:
        Dictionary with issue title, body, labels, author
    """
    g = Github(os.getenv("GITHUB_TOKEN"))
    issue = g.get_repo(repo_name).get_issue(issue_number)
    return {
        "number": issue.number,
        "title": issue.title,
        "body": issue.body,
        "labels": [label.name for label in issue.labels],
        "author": issue.user.login
    }
```

**Register in `src/mcp.py`:**
```python
from template_mcp_server.src.tools.github_tools import parse_issue

def _register_mcp_tools(self) -> None:
    self.mcp.tool()(parse_issue)  # Add all 5 tools
```

**Add to `pyproject.toml`:**
```toml
dependencies = ["PyGithub>=2.1.1", ...]
```

**Install & restart:**
```bash
cd template-mcp-server
uv sync
make local
```

### Step 2: Agent - Build Triage Workflow

**Update `src/agent/prompts.py`:**
```python
SYSTEM_PROMPT = """
You are a GitHub issue triage assistant. Your job is to:
1. Validate issue quality (has description, steps)
2. Search for duplicates using semantic similarity
3. Classify issues (bug/feature/docs, priority, area)
4. Route to appropriate team
5. Execute actions (labels, assignees, comments)
Be consistent, fast, and accurate.
"""
```

**Build 6-node workflow in `src/agent/graph.py`:**
```
START → assess_quality → search_duplicates → classify_issue → assign_team → execute_actions → END
```

**Create 5 node files in `src/nodes/`:**
- `assessment_node.py` - Validate issue quality
- `duplicate_detection_node.py` - Search for duplicates
- `classification_node.py` - Classify type/priority/area
- `assignment_node.py` - Map to team
- `execute_node.py` - Execute GitHub actions

### Step 3: UI - GitHub Triage Dashboard

**Update `frontend/src/App.tsx`:**
- Change title to "GitHub Issue Triage Agent"
- Add real-time event feed
- Show last 10 triaged issues
- Display stats (total triaged, duplicates found)

**Add to `backend/src/api.py`:**
```python
@app.get("/events/recent")
async def get_recent_events():
    return triage_events[-50:]  # Last 50 events
```

---

## Key Commands

### Current Setup (Templates Running)
```bash
# MCP Server: http://localhost:5001 ✓
# Agent: http://localhost:5002 ✓
# UI: http://localhost:5003 ✓
```

### Test Tool
```bash
# After adding parse_issue tool
curl -X POST "http://localhost:5001/tools/parse_issue?repo=owner/repo&issue_number=1"
```

### Restart After Changes
```bash
# MCP Server
cd template-mcp-server
uv sync  # If added dependencies
make local

# Agent
cd template-agent
make local

# UI
cd template-ui
npm run dev
```

### Webhook Setup
```bash
ngrok http 5001  # Tunnel MCP server
# Add webhook in GitHub repo settings
```

---

## Environment Variables

**Create `.env` file:**
```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx  # REQUIRED
GITHUB_REPO=owner/repo          # REQUIRED
JINA_API_KEY=jina_xxxx         # For semantic search
LLM_PROVIDER=ollama            # or anthropic
OLLAMA_MODEL=llama3.2
```

**NEVER commit .env to Git!**

---

## The Magic of Docstrings

**CRITICAL:** The agent auto-discovers tools by reading docstrings. Write clear docstrings with:
- What the tool does (first line)
- `Args:` section with parameter descriptions
- `Returns:` section with output description

This is how you "teach" the agent without manual configuration!

---

## Building Your Prototype (6 Steps)

**Step 1: MCP Server**
- Add `parse_issue` tool → test with curl
- Add `classify_issue` tool → test with curl
- Add `execute_actions` tool → test with curl

**Step 2: Agent Workflow**
- Build 3-node graph: parse → classify → execute
- Test with hardcoded issue number
- Verify labels appear on GitHub

**Step 3: Webhook Handler**
- Add `/webhook` POST endpoint to MCP server
- Validate GitHub webhook signature
- Trigger agent on new issue events

**Step 4: Dashboard**
- Show real-time events
- Display last 10 triaged issues
- Add simple statistics

**Step 5: Add Duplicate Detection**
- Implement semantic search
- Add duplicate detection node to workflow

**Step 6: Test & Demo**
- Create test issues in GitHub
- Watch automation work
- Record backup demo video

---

## Hackathon Strategy

**If running out of time, prioritize:**
1. 3 MCP tools (parse, classify, execute) - Skip search initially
2. 3-node workflow (parse → classify → execute) - Skip duplicate detection
3. Basic dashboard - Skip fancy stats

**Speed Tips:**
- Use Claude API instead of Ollama (faster, better quality)
- Skip semantic search, use simple keyword matching
- Hard-code team assignments instead of LLM routing

---

## Common Issues & Quick Fixes

**Tool not found by agent:**
- Check docstring format (must have Args/Returns)
- Verify tool is registered in mcp.py
- Restart MCP server

**LangGraph state error:**
- Don't mutate state: Use `return {**state, 'key': value}`
- Ensure all nodes return updated state dict

**GitHub API rate limit:**
- Use GITHUB_TOKEN (5000 req/hour vs 60 without)

**Webhook not firing:**
- Check ngrok is running
- Verify webhook URL in GitHub settings
- Check webhook delivery logs in GitHub

---

## Next Steps (Immediate)

1. **Add first GitHub tool** (`parse_issue`) to MCP server
2. **Test tool** via curl
3. **Build simple 3-node agent** workflow
4. **Test end-to-end** with hardcoded issue
5. **Add webhook handler**
6. **Add UI event feed**

---

**Last Updated:** January 24, 2026
**Status:** Templates running (ports 5001, 5002, 5003) - Ready for customization
**Goal:** WIN 🏆

**Remember:**
- Simple code > Complex code
- Working demo > Perfect architecture
- Speed > Perfection
- Get approval before implementing
