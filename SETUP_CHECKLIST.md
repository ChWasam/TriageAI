# Setup Checklist - GitHub Issue Triage Agent

Quick reference for hackathon day setup.

## Pre-Hackathon Setup

### 1. Environment Variables
- [ ] Copy `.env.example` to `.env`
- [ ] Add GitHub Personal Access Token to `.env`
- [ ] Add target GitHub repo to `.env` (format: `owner/repo`)
- [ ] Add Anthropic API key to `.env` (or configure Ollama)
- [ ] Verify `.env` is in `.gitignore`

### 2. GitHub Setup
- [ ] Create test repository or use existing repo
- [ ] Generate GitHub Personal Access Token with `repo` scope
- [ ] Ensure you have admin access to the repo (for webhooks)

### 3. Dependencies Installation

**MCP Server:**
```bash
cd template-mcp-server
uv sync
```
- [ ] MCP server dependencies installed
- [ ] PyGithub added to pyproject.toml

**Agent:**
```bash
cd template-agent-main
uv sync
```
- [ ] Agent dependencies installed

**UI:**
```bash
cd template-ui-main
npm install
```
- [ ] UI dependencies installed

### 4. Verify Services Start

**Terminal 1 - MCP Server:**
```bash
cd template-mcp-server
make local
```
- [ ] MCP Server running on http://localhost:5001
- [ ] No errors in console

**Terminal 2 - Agent:**
```bash
cd template-agent-main
make local
```
- [ ] Agent running on http://localhost:5002
- [ ] No errors in console

**Terminal 3 - UI:**
```bash
cd template-ui-main
npm run dev
```
- [ ] UI running on http://localhost:5003
- [ ] Dashboard loads in browser

## Hackathon Day - Implementation

### Phase 1: MCP Server Tools (30 min)

- [ ] Verify `github_tools.py` exists in `template-mcp-server/template_mcp_server/src/tools/`
- [ ] Register tools in `mcp.py`
- [ ] Test `parse_issue` tool with curl
- [ ] Test `classify_issue` tool with curl
- [ ] Verify all 5 tools are working

**Test Command:**
```bash
curl -X POST "http://localhost:5001/tools/parse_issue?repo=owner/repo&issue_number=1"
```

### Phase 2: Agent Workflow (60 min)

- [ ] Verify all 5 node files exist in `template-agent-main/template_agent/src/nodes/`
- [ ] Update `prompt.py` with triage system prompt
- [ ] Build LangGraph workflow in `agent.py` or `graph.py`
- [ ] Test workflow with hardcoded issue number
- [ ] Verify workflow completes without errors

**Workflow Nodes:**
1. assess_quality
2. search_duplicates
3. classify_issue
4. assign_team
5. execute_actions

### Phase 3: Webhook Handler (30 min)

- [ ] Install ngrok: `brew install ngrok` (if needed)
- [ ] Start ngrok: `ngrok http 5001`
- [ ] Copy ngrok URL
- [ ] Add webhook to GitHub repo:
  - Settings → Webhooks → Add webhook
  - URL: `https://xxx.ngrok.io/webhook`
  - Content type: `application/json`
  - Events: Issues
  - Active: ✓
- [ ] Add webhook handler to `main.py` in MCP server
- [ ] Test webhook with new issue
- [ ] Verify webhook delivery in GitHub

### Phase 4: UI Dashboard (30 min)

- [ ] Update `App.tsx` title to "GitHub Issue Triage Agent"
- [ ] Add event feed component
- [ ] Add statistics display
- [ ] Test real-time updates
- [ ] Verify UI shows triaged issues

### Phase 5: Integration Testing (30 min)

- [ ] Create test issue in GitHub
- [ ] Verify webhook triggers
- [ ] Check agent processes issue
- [ ] Confirm labels/comments appear on GitHub
- [ ] Check dashboard shows event
- [ ] Test with different issue types (bug, feature, docs)

### Phase 6: Demo Preparation (30 min)

- [ ] Record backup demo video
- [ ] Prepare 3-4 test issues
- [ ] Clean up GitHub issues from testing
- [ ] Test full workflow end-to-end
- [ ] Prepare demo script (2-3 minutes)

## Common Issues & Quick Fixes

**Tool not discovered by agent:**
```bash
# Check tool has proper docstring with Args/Returns
# Verify registration in mcp.py
# Restart MCP server
cd template-mcp-server && make local
```

**GitHub API 401 error:**
```bash
# Verify GITHUB_TOKEN in .env
# Check token has 'repo' scope
# Token format: ghp_xxxxxxxxxxxx
```

**LangGraph state error:**
```python
# Never mutate state in place
# Always return new dict:
return {**state, 'key': value}
```

**Webhook not firing:**
```bash
# Check ngrok is running
# Verify webhook URL in GitHub settings
# Check webhook "Recent Deliveries" in GitHub
```

**Port already in use:**
```bash
# Kill process on port
lsof -ti:5001 | xargs kill -9
lsof -ti:5002 | xargs kill -9
lsof -ti:5003 | xargs kill -9
```

## Time Breakdown (Total: 6 hours)

- Setup & Dependencies: 30 min
- MCP Tools: 30 min
- Agent Workflow: 60 min
- Webhook Integration: 30 min
- UI Dashboard: 30 min
- Integration Testing: 30 min
- Demo Prep: 30 min
- **Buffer:** 2 hours 30 min

## Success Criteria

- [ ] Issue created in GitHub
- [ ] Webhook triggers MCP server
- [ ] Agent processes issue through workflow
- [ ] Labels/comments applied to GitHub issue
- [ ] Dashboard shows real-time event
- [ ] Full cycle < 15 seconds
- [ ] Demo ready

## Emergency Simplifications (If Running Out of Time)

**Option 1: Skip Duplicate Detection**
- Remove `search_duplicates` node from workflow
- Reduces complexity, saves 15 min

**Option 2: Skip Semantic Search**
- Use simple keyword matching instead
- Saves 20 min

**Option 3: Hard-code Team Assignments**
- Remove LLM classification
- Use keyword-based assignment
- Saves 15 min

**Option 4: Skip UI Customization**
- Use default template UI
- Saves 30 min

## Final Checks Before Demo

- [ ] All 3 services running
- [ ] Webhook configured and active
- [ ] Test issues prepared
- [ ] GitHub repo clean
- [ ] Demo script practiced
- [ ] Backup video ready
- [ ] Confident in pitch

---

**Remember:**
- Speed > Perfection
- Working demo is essential
- Test early, test often
- Have fun! 🚀
