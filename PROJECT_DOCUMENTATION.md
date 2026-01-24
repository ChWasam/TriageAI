# GitHub Issue Triage Agent - Project Documentation

## THE PROBLEM

**Maintainers waste 10-20 hours/week manually triaging GitHub issues**

Manual workflow per issue (15-20 minutes):
1. Read title and description (2-3 min)
2. Search for duplicates manually (5-7 min)
3. Decide on labels and priority (2 min)
4. Apply labels (1 min)
5. Assign to team (1 min)
6. Write acknowledgment comment (2-3 min)
7. Add to project board (1 min)

**Total:** 15-20 min × 50 issues/week = **12-16 hours/week wasted**

---

## THE SOLUTION

**AI agent that triages issues automatically in 8 seconds**

### What It Does

1. **Validates issue quality** - Checks if issue has enough info
2. **Classifies intelligently** - Determines type (bug/feature), priority, and area
3. **Applies labels & assigns** - Updates GitHub automatically
4. **Posts professional comment** - Acknowledges and explains triage

### Value Proposition

- **Time savings:** 15 min → 8 sec per issue (99% reduction)
- **Scale:** Handle 200+ issues/week automatically
- **Quality:** Consistent labeling, never miss patterns
- **Speed:** Instant first response to reporters

---

## ARCHITECTURE

### Component Overview

```
GitHub Issue Created
       ↓
   [Webhook] (optional - for automation)
       ↓
┌──────────────────────────┐
│   MCP SERVER (Port 5001) │
│   - GitHub Tools         │
│   - parse_issue          │
│   - classify_issue       │
│   - execute_actions      │
└──────────┬───────────────┘
           │ Tools available to agent
           ↓
┌──────────────────────────┐
│   AGENT (Port 5002)      │
│   - LangGraph workflow   │
│   - Calls MCP tools      │
│   - Makes decisions      │
└──────────┬───────────────┘
           │ Results
           ↓
┌──────────────────────────┐
│   UI (Port 5003)         │
│   - Chat interface       │
│   - Real-time feedback   │
│   - HTML/Tailwind UI     │
└──────────────────────────┘
```

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **MCP Server** | FastAPI, PyGithub | Provides GitHub tools to agent |
| **Agent** | LangGraph, LangChain | Orchestrates triage workflow |
| **Classification** | Keywords or LLM | Determines issue type/priority |
| **UI** | React, TypeScript | Chat interface for testing |

---

## WORKFLOW

**Simple 3-Step Process:**

```
1. PARSE
   ↓
   Agent calls: parse_issue(repo, issue_number)
   Returns: {title, body, author, labels, state}

2. CLASSIFY
   ↓
   Agent calls: classify_issue(title, body)
   Returns: {type: "bug", priority: "high", area: "api"}

3. EXECUTE
   ↓
   Agent calls: execute_actions(issue_number, labels, comment)
   GitHub updated with labels and comment
```

---

## DEMO STRATEGY (3 minutes)

### Part 1: Show Problem (30 sec)
- Display GitHub repo with unlabeled issues
- "Maintainers spend 15 min per issue doing this manually"

### Part 2: Live Demo (90 sec)
- Open UI at http://localhost:5003
- Type: "Triage issue #1 from repo username/triage-agent-demo"
- Watch agent:
  - Parse issue ✓
  - Classify (bug, high priority, api area) ✓
  - Apply labels and comment ✓
- Refresh GitHub → labels appear

### Part 3: Impact (60 sec)
- Show before/after comparison
- "15 minutes → 8 seconds = 99% time reduction"
- "For 50 issues/week: saves 12+ hours"
- "Scales to hundreds of issues automatically"

---

## CUSTOMIZATION POINTS

### Easy Wins (5-15 min each)

**1. Improve Classification**
- Replace keyword matching with LLM (Ollama/Claude)
- More accurate type/priority detection

**2. Add More Tools**
- `search_duplicates()` - Find similar issues
- `get_project_info()` - Auto-add to project boards
- `request_info()` - Ask for missing details

**3. Better Comments**
- Template-based responses
- Link to documentation
- Suggest related issues

### Advanced Features (30-60 min each)

**1. Webhook Automation**
- Trigger triage on issue creation (no manual command)
- Use ngrok for local testing

**2. Duplicate Detection**
- Semantic search with Jina embeddings
- Automatically close duplicates

**3. Dashboard**
- Show recent triages
- Statistics (issues/day, time saved)
- Manual override controls

---

## SUCCESS METRICS

### Technical Success
- [ ] All 3 components running (MCP + Agent + UI)
- [ ] GitHub tools working (parse, classify, execute)
- [ ] Agent completes full workflow
- [ ] Labels appear on GitHub issue
- [ ] Comment posted automatically

### Demo Success
- [ ] Live triage in < 15 seconds
- [ ] Clear before/after comparison
- [ ] Value prop communicated (99% time reduction)
- [ ] Professional polish (no errors, smooth flow)

### Judging Criteria
- ✅ Uses all 3 aitemplates.io components
- ✅ Solves real problem (everyone relates to issue triage)
- ✅ Working demo (not slides/mockups)
- ✅ Technical complexity (AI classification, GitHub API)
- ✅ Production potential (actually useful)

---

## TIME BUDGET

**Total: 3 hours to working demo**

| Task | Time |
|------|------|
| Setup .env + GitHub token | 5 min |
| Add GitHub tools to MCP server | 45 min |
| Update agent system prompt | 15 min |
| Update UI title/header | 5 min |
| Create test issue on GitHub | 5 min |
| Test end-to-end workflow | 30 min |
| Fix bugs and polish | 45 min |
| Practice demo 3 times | 30 min |

**Buffer:** 1 hour for unexpected issues

---

## RISKS & MITIGATION

**Risk:** GitHub API rate limits
- **Mitigation:** Use authenticated token (5000 req/hour)

**Risk:** Classification accuracy too low
- **Mitigation:** Start with keywords, upgrade to LLM if needed

**Risk:** Demo fails during presentation
- **Mitigation:** Record backup video, have screenshots ready

**Risk:** Agent doesn't find tools
- **Mitigation:** Check tool registration, verify docstrings format

---

## PITCH POINTS

**Problem:** "Maintainers waste 12-16 hours/week on repetitive issue triage"

**Solution:** "AI agent automates the entire workflow in 8 seconds"

**Tech:** "Uses aitemplates.io MCP server + LangGraph agent + React UI"

**Impact:** "99% time reduction, scales to hundreds of issues"

**Demo:** "Watch it triage a real GitHub issue live"

**Future:** "Add duplicate detection, webhook automation, team routing"

---

## NEXT STEPS

1. ✅ Templates running (done)
2. Create `.env` with GitHub token
3. Add 3 GitHub tools to MCP server
4. Update agent system prompt
5. Create test GitHub issue
6. Test full workflow
7. Practice demo 3 times
8. WIN! 🏆

---

**Good luck! You've got this! 🚀**
