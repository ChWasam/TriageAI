# GitHub Issue Triage Agent

AI-powered automated GitHub issue triage system built for the Red Hat AI Hackathon (January 24, 2026).

## What It Does

Automatically triages GitHub issues by:
- ✅ Validating issue quality (title, description)
- 🔍 Detecting potential duplicates using semantic similarity
- 🏷️ Classifying issues (type, priority, area)
- 👥 Routing to appropriate teams
- 🤖 Applying labels, assignees, and comments automatically

**Problem:** Maintainers waste 10-20 hours/week manually triaging issues (15 min/issue)
**Solution:** Automated triage in 8 seconds per issue (99.1% time reduction)

## Architecture

Built using the **aitemplates.io** framework:

1. **MCP Server** (Port 5001) - FastAPI server with GitHub API tools
2. **Agent** (Port 5002) - LangGraph workflow for orchestration
3. **UI** (Port 5003) - React dashboard for monitoring

```
GitHub Webhook → MCP Server → LangGraph Agent → GitHub API
                                      ↓
                               React Dashboard
```

## Quick Start

### Prerequisites

- Python 3.12.2
- Node.js 18+
- GitHub account with a test repository
- GitHub Personal Access Token
- (Optional) Anthropic API key or Ollama

### 1. Clone and Setup

```bash
cd Triage
cp .env.example .env  # Edit with your tokens
```

### 2. Configure Environment

Edit `.env` file:
```bash
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPO=owner/repo
ANTHROPIC_API_KEY=your_key_here  # or use Ollama
```

### 3. Install Dependencies

**MCP Server:**
```bash
cd template-mcp-server
uv sync
cd ..
```

**Agent:**
```bash
cd template-agent-main
uv sync
cd ..
```

**UI:**
```bash
cd template-ui-main
npm install
cd ..
```

### 4. Start Services

**Terminal 1 - MCP Server:**
```bash
cd template-mcp-server
make local
# Running on http://localhost:5001
```

**Terminal 2 - Agent:**
```bash
cd template-agent-main
make local
# Running on http://localhost:5002
```

**Terminal 3 - UI:**
```bash
cd template-ui-main
npm run dev
# Running on http://localhost:5003
```

### 5. Setup GitHub Webhook

```bash
# In a new terminal
ngrok http 5001
```

Copy the ngrok URL and add webhook in your GitHub repo:
- Settings → Webhooks → Add webhook
- Payload URL: `https://your-ngrok-url.ngrok.io/webhook`
- Content type: `application/json`
- Events: Issues
- Active: ✓

## Project Structure

```
Triage/
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── CLAUDE.md                   # AI assistant context
│
├── template-mcp-server/        # MCP Server
│   ├── template_mcp_server/
│   │   └── src/
│   │       ├── tools/
│   │       │   └── github_tools.py    # 5 GitHub API tools
│   │       ├── mcp.py                 # Tool registration
│   │       └── main.py                # Webhook handler
│   └── pyproject.toml                 # Dependencies
│
├── template-agent-main/        # LangGraph Agent
│   ├── template_agent/
│   │   └── src/
│   │       ├── core/
│   │       │   ├── prompt.py          # System prompt
│   │       │   └── agent.py           # Workflow graph
│   │       └── nodes/                 # Workflow nodes
│   │           ├── assessment_node.py
│   │           ├── duplicate_detection_node.py
│   │           ├── classification_node.py
│   │           ├── assignment_node.py
│   │           └── execute_node.py
│   └── pyproject.toml
│
└── template-ui-main/           # React UI
    ├── src/
    │   ├── App.tsx             # Dashboard
    │   └── components/         # UI components
    └── package.json
```

## GitHub Tools (MCP Server)

5 tools exposed via MCP:

1. **parse_issue** - Fetch issue from GitHub
2. **search_duplicates** - Find similar issues
3. **classify_issue** - Classify type/priority/area
4. **execute_actions** - Apply labels/assignees/comments
5. **get_repo_info** - Fetch repo metadata

## Workflow (LangGraph Agent)

6-node workflow:

```
START
  ↓
assess_quality (validate issue)
  ↓
search_duplicates (find similar issues)
  ↓
classify_issue (determine type/priority/area)
  ↓
assign_team (route to team)
  ↓
execute_actions (apply to GitHub)
  ↓
END
```

## Testing

### Test MCP Tools

```bash
# Test parse_issue tool
curl -X POST "http://localhost:5001/tools/parse_issue?repo=owner/repo&issue_number=1"

# Test classify_issue
curl -X POST "http://localhost:5001/tools/classify_issue" \
  -H "Content-Type: application/json" \
  -d '{"title": "Bug: App crashes", "body": "The app crashes when..."}'
```

### Test Workflow

Create a test issue in your GitHub repo and watch the automation work!

## Dashboard Features

- Real-time event feed
- Last 10 triaged issues
- Statistics (total triaged, duplicates found)
- Issue classification breakdown

## Tech Stack

- **Backend:** FastAPI, PyGithub, LangGraph, LangChain, Pydantic
- **LLM:** Anthropic Claude or Ollama (local)
- **Frontend:** React, TypeScript, Vite, Tailwind CSS
- **Infrastructure:** ngrok (webhooks), GitHub API

## Development

### Adding New Tools

1. Add tool function to `template-mcp-server/template_mcp_server/src/tools/github_tools.py`
2. Register in `template-mcp-server/template_mcp_server/src/mcp.py`
3. Restart MCP server

### Modifying Workflow

1. Update nodes in `template-agent-main/template_agent/src/nodes/`
2. Update graph in `template-agent-main/template_agent/src/core/agent.py`
3. Restart agent

## Troubleshooting

**Tools not found by agent:**
- Check docstrings (must have Args/Returns)
- Verify tool registration in mcp.py
- Restart MCP server

**GitHub API rate limit:**
- Use GITHUB_TOKEN (5000 req/hour vs 60)

**Webhook not firing:**
- Check ngrok is running
- Verify webhook URL in GitHub
- Check webhook delivery logs

## License

MIT License - Built for Red Hat AI Hackathon 2026

## Team

Built by Wasam Chaudhry for the Red Hat AI Hackathon

---

**Goal:** Win 🏆

**Built with:** aitemplates.io framework
