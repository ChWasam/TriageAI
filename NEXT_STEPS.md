# Next Steps - Complete the Integration

The initial structure is set up. Now you need to integrate everything together.

## What's Been Created

✅ Project structure with all directories
✅ `.env` and `.env.example` files
✅ `.gitignore` file
✅ GitHub tools (`github_tools.py`) with 5 tools
✅ Agent nodes (5 files) for workflow
✅ Documentation (README, SETUP_CHECKLIST)

## What Needs to Be Done

### 1. Update MCP Server (20 min)

**File: `template-mcp-server/pyproject.toml`**
```toml
# Add to dependencies list (around line 15-28):
"PyGithub>=2.1.1",
```

**File: `template-mcp-server/template_mcp_server/src/mcp.py`**
```python
# Add import at top:
from template_mcp_server.src.tools.github_tools import (
    parse_issue,
    search_duplicates,
    classify_issue,
    execute_actions,
    get_repo_info
)

# In _register_mcp_tools method, add:
self.mcp.tool()(parse_issue)
self.mcp.tool()(search_duplicates)
self.mcp.tool()(classify_issue)
self.mcp.tool()(execute_actions)
self.mcp.tool()(get_repo_info)
```

**File: `template-mcp-server/template_mcp_server/src/main.py`**
```python
# Add webhook handler endpoint (around line 50+):
@app.post("/webhook")
async def github_webhook(request: Request):
    """Handle GitHub webhook events."""
    payload = await request.json()

    # Verify it's an issue event
    if payload.get("action") == "opened":
        issue = payload.get("issue", {})
        repo = payload.get("repository", {}).get("full_name")
        issue_number = issue.get("number")

        # TODO: Trigger agent workflow
        logger.info("New issue webhook received", repo=repo, issue=issue_number)

        return {"status": "received"}

    return {"status": "ignored"}
```

**Install and restart:**
```bash
cd template-mcp-server
uv sync
make local
```

**Test:**
```bash
curl -X POST "http://localhost:5001/tools/parse_issue" \
  -H "Content-Type: application/json" \
  -d '{"repo_name": "owner/repo", "issue_number": 1}'
```

### 2. Update Agent Workflow (30 min)

**File: `template-agent-main/template_agent/src/core/prompt.py`**
```python
# Update SYSTEM_PROMPT:
SYSTEM_PROMPT = """
You are a GitHub issue triage assistant. Your job is to:
1. Validate issue quality (has description, steps)
2. Search for duplicates using semantic similarity
3. Classify issues (bug/feature/docs/question, priority, area)
4. Route to appropriate team
5. Execute actions (labels, assignees, comments)

Be consistent, fast, and accurate. Always verify before taking actions.
"""
```

**File: `template-agent-main/template_agent/src/core/agent.py` or `manager.py`**

Find where the LangGraph workflow is defined and update it to use our nodes:

```python
from template_agent.src.nodes import (
    assess_quality,
    search_duplicates,
    classify_issue,
    assign_team,
    execute_actions
)

# Build workflow (syntax depends on template structure):
workflow.add_node("assess_quality", assess_quality)
workflow.add_node("search_duplicates", search_duplicates)
workflow.add_node("classify_issue", classify_issue)
workflow.add_node("assign_team", assign_team)
workflow.add_node("execute_actions", execute_actions)

# Connect nodes:
workflow.set_entry_point("assess_quality")
workflow.add_edge("assess_quality", "search_duplicates")
workflow.add_edge("search_duplicates", "classify_issue")
workflow.add_edge("classify_issue", "assign_team")
workflow.add_edge("assign_team", "execute_actions")
workflow.add_edge("execute_actions", END)
```

**Restart:**
```bash
cd template-agent-main
make local
```

### 3. Update UI Dashboard (20 min)

**File: `template-ui-main/src/App.tsx`**

Update the title and add triage-specific UI elements:

```tsx
<h1>GitHub Issue Triage Agent</h1>
<p>Real-time automated issue triage powered by AI</p>

{/* Add event feed component */}
{/* Add statistics dashboard */}
```

**Restart:**
```bash
cd template-ui-main
npm run dev
```

### 4. Setup Webhook (10 min)

**Install ngrok:**
```bash
brew install ngrok  # Mac
# or download from ngrok.com
```

**Start ngrok:**
```bash
ngrok http 5001
```

**Add webhook to GitHub:**
1. Go to your test repo
2. Settings → Webhooks → Add webhook
3. Payload URL: `https://xxx.ngrok.io/webhook`
4. Content type: `application/json`
5. Events: Select "Issues"
6. Active: ✓
7. Add webhook

### 5. Integration Testing (20 min)

**Test 1: MCP Tools**
```bash
# Test parse_issue
curl -X POST "http://localhost:5001/tools/parse_issue" \
  -H "Content-Type: application/json" \
  -d '{"repo_name": "owner/repo", "issue_number": 1}'

# Test classify_issue
curl -X POST "http://localhost:5001/tools/classify_issue" \
  -H "Content-Type: application/json" \
  -d '{"title": "Bug: App crashes", "body": "The app crashes when I click..."}'
```

**Test 2: Agent Workflow**
```bash
# Call agent with test issue
curl -X POST "http://localhost:5002/stream" \
  -H "Content-Type: application/json" \
  -d '{"repo_name": "owner/repo", "issue_number": 1}'
```

**Test 3: Full Integration**
1. Create a new issue in your GitHub repo
2. Watch the webhook delivery in GitHub
3. Check MCP server logs
4. Check agent logs
5. Verify labels/comments appear on GitHub issue
6. Check dashboard shows the event

### 6. Demo Preparation (15 min)

**Create test issues:**
1. **Bug:** "Bug: Login button doesn't work - Critical issue, app crashes when clicking login"
2. **Feature:** "Add dark mode support - Would be nice to have dark theme option"
3. **Docs:** "Update README with setup instructions - Documentation needs improvement"

**Prepare demo script:**
```
1. Show dashboard (clean state)
2. Create new issue in GitHub
3. Show webhook triggered (ngrok/logs)
4. Show agent processing (logs)
5. Show GitHub issue updated (labels, comment)
6. Show dashboard event (real-time)
7. Explain architecture diagram
8. Highlight time savings (15 min → 8 sec)
```

## Quick Reference Commands

**Start all services:**
```bash
# Terminal 1
cd template-mcp-server && make local

# Terminal 2
cd template-agent-main && make local

# Terminal 3
cd template-ui-main && npm run dev

# Terminal 4
ngrok http 5001
```

**Test MCP tools:**
```bash
curl http://localhost:5001/tools
```

**Check agent status:**
```bash
curl http://localhost:5002/health
```

**View UI:**
```
http://localhost:5003
```

## Files to Edit Summary

| File | Action | Time |
|------|--------|------|
| `template-mcp-server/pyproject.toml` | Add PyGithub dependency | 2 min |
| `template-mcp-server/src/mcp.py` | Register GitHub tools | 5 min |
| `template-mcp-server/src/main.py` | Add webhook handler | 10 min |
| `template-agent-main/src/core/prompt.py` | Update system prompt | 3 min |
| `template-agent-main/src/core/agent.py` | Build workflow graph | 20 min |
| `template-ui-main/src/App.tsx` | Update dashboard | 15 min |

**Total:** ~55 minutes + testing

## Critical Checks

Before demo:
- [ ] All 3 services running (ports 5001, 5002, 5003)
- [ ] ngrok running and webhook configured
- [ ] GITHUB_TOKEN in .env is valid
- [ ] Test issue successfully triaged
- [ ] Dashboard shows events
- [ ] Demo script practiced

## Need Help?

1. Check `SETUP_CHECKLIST.md` for troubleshooting
2. Read `CLAUDE.md` for detailed context
3. Review `README.md` for architecture overview

---

**You're almost there! The foundation is set, now wire it all together! 🚀**
