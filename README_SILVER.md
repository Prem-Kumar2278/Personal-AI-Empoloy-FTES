# AI Employee - Silver Tier

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

This is the **Silver Tier** implementation of the Personal AI Employee (Digital FTE) hackathon project. It builds upon Bronze Tier to provide a functional AI assistant with multiple watchers, approval workflows, and automated posting.

## What is Silver Tier?

The Silver Tier is the **Functional Assistant** level of the AI Employee hackathon:

**Estimated time:** 20-30 hours

### Silver Tier Requirements (All Implemented)

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | All Bronze requirements | ✅ | File watcher, vault structure, Dashboard, Handbook |
| 2 | Two or more Watcher scripts | ✅ | File System + Gmail + WhatsApp watchers |
| 3 | LinkedIn auto-posting | ✅ | `linkedin_poster.py` with browser automation |
| 4 | Claude reasoning loop (Plan.md) | ✅ | `plan_manager.py` creates structured plans |
| 5 | MCP server for external action | ✅ | Email MCP configuration provided |
| 6 | HITL approval workflow | ✅ | `approval_manager.py` + folder-based workflow |
| 7 | Basic scheduling | ✅ | `setup_scheduler.py` for Task Scheduler/cron |
| 8 | Agent Skills implementation | ✅ | `skills/` folder with skill definitions |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PERCEPTION LAYER (Watchers)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │ File Watcher │  │ Gmail Watcher│  │WhatsApp Watch│                  │
│  │  (Python)    │  │  (Gmail API) │  │ (Playwright) │                  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │
└─────────┼─────────────────┼─────────────────┼──────────────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         OBSIDIAN VAULT                                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ /Needs_Action/  │ /Plans/  │ /Pending_Approval/ │ /Approved/    │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ Dashboard.md    │ Company_Handbook.md │ Business_Goals.md        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         REASONING LAYER                                 │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │   CLAUDE CODE + Plan Manager + Approval Manager                   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
              ┌──────────────────┴───────────────────┐
              ▼                                      ▼
┌────────────────────────────┐    ┌────────────────────────────────┐
│    HUMAN-IN-THE-LOOP       │    │         ACTION LAYER           │
│  ┌──────────────────────┐  │    │  ┌─────────────────────────┐   │
│  │ Review & Approve     │──┼───▶│  │    MCP SERVERS          │   │
│  │ /Pending_Approval/   │  │    │  │  ┌──────┐ ┌──────────┐  │   │
│  └──────────────────────┘  │    │  │  │Email │ │ Browser  │  │   │
│                            │    │  │  │ MCP  │ │   MCP    │  │   │
└────────────────────────────┘    │  │  └──┬───┘ └────┬─────┘  │   │
                                  │  └─────┼──────────┼────────┘   │
                                  └────────┼──────────┼────────────┘
                                           │          │
                                           ▼          ▼
                                  ┌────────────────────────────────┐
                                  │     EXTERNAL ACTIONS           │
                                  │  Send Email │ LinkedIn Post    │
                                  └────────────────────────────────┘
```

## Quick Start

### Prerequisites

```bash
# Check Python version (3.13+)
python --version

# Check Claude Code
claude --version

# Install Silver Tier dependencies
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install playwright
playwright install chromium
```

### 1. Setup Environment Variables

```bash
# Copy template
copy .env.template .env

# Edit .env with your credentials
# - Gmail OAuth credentials
# - SMTP settings for email
# - LinkedIn credentials (optional)
```

### 2. Configure MCP Servers

See `scripts/mcp_setup.md` for detailed MCP configuration.

```bash
# Install MCP servers
npm install -g @anthropic/mcp-server-email
npm install -g @anthropic/browser-mcp

# Configure in ~/.config/claude-code/mcp.json
```

### 3. Start Watchers

```bash
# File System Watcher (always start this)
python scripts\filesystem_watcher.py

# Gmail Watcher (requires OAuth setup)
python scripts\gmail_watcher.py --credentials credentials.json

# WhatsApp Watcher (first run: scan QR code)
python scripts\whatsapp_watcher.py --no-headless
```

### 4. Install Scheduled Tasks

```bash
# Windows: Install scheduled tasks
python scripts\setup_scheduler.py --install

# Linux/Mac: Show crontab entries
python scripts\setup_scheduler.py --linux
```

### 5. Test LinkedIn Posting

```bash
# Create a draft post
python scripts\linkedin_poster.py --topic "Industry Trends"

# Publish the post
python scripts\linkedin_poster.py --publish DRAFT_*.md
```

## Folder Structure

```
Personal-AI-Empoloy-FTES/
├── scripts/
│   ├── base_watcher.py         # Base class for all watchers
│   ├── filesystem_watcher.py   # Bronze: File monitoring
│   ├── gmail_watcher.py        # Silver: Gmail API watcher
│   ├── whatsapp_watcher.py     # Silver: WhatsApp Web watcher
│   ├── orchestrator.py         # Main coordinator (Silver enhanced)
│   ├── plan_manager.py         # Silver: Plan.md creation
│   ├── approval_manager.py     # Silver: HITL approval workflow
│   ├── audit_logger.py         # Silver: JSON audit logging
│   ├── linkedin_poster.py      # Silver: LinkedIn auto-posting
│   ├── setup_scheduler.py      # Silver: Task Scheduler setup
│   ├── verify_silver_tier.py   # Silver Tier verification
│   ├── mcp_setup.md            # MCP server configuration guide
│   └── HITL_WORKFLOW.md        # HITL approval documentation
├── skills/
│   ├── README.md               # Agent Skills documentation
│   ├── email-responder/
│   │   └── SKILL.md            # Email responder skill
│   └── invoice-generator/
│       └── SKILL.md            # Invoice generator skill
├── AI_Employee_Vault/
│   ├── Inbox/                  # Drop files here
│   ├── Needs_Action/           # Pending items
│   ├── Plans/                  # Claude plans
│   ├── Pending_Approval/       # Awaiting approval
│   ├── Approved/               # Approved, ready to execute
│   ├── Rejected/               # Rejected items
│   ├── Done/                   # Completed items
│   ├── Social_Posts/           # LinkedIn posts
│   │   ├── Drafts/
│   │   ├── Scheduled/
│   │   └── Published/
│   ├── Logs/                   # Audit logs
│   ├── Dashboard.md            # Status dashboard
│   └── Company_Handbook.md     # Rules of engagement
├── .env.template               # Environment variables template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Silver Tier Features

### 1. Multiple Watchers

#### File System Watcher
```bash
python scripts\filesystem_watcher.py --interval 30
```

#### Gmail Watcher
```bash
# First time: OAuth authentication
python scripts\gmail_watcher.py --credentials credentials.json

# Subsequent runs (uses saved token)
python scripts\gmail_watcher.py --credentials credentials.json --interval 120
```

#### WhatsApp Watcher
```bash
# First run: Show browser for QR code scan
python scripts\whatsapp_watcher.py --no-headless

# Subsequent runs (uses saved session)
python scripts\whatsapp_watcher.py --interval 60
```

### 2. LinkedIn Auto-Posting

```bash
# Create business post draft
python scripts\linkedin_poster.py --topic "New Service Launch"

# Post custom content
python scripts\linkedin_poster.py --content "🚀 Exciting news about our new product!"

# Publish existing draft
python scripts\linkedin_poster.py --publish DRAFT_20260225_120000.md
```

### 3. Plan.md Creation (Claude Reasoning)

Plans are automatically created by the orchestrator:

```bash
python scripts\orchestrator.py
# Creates: Plans/PLAN_task_20260225_120000.md
```

Plan template:
```markdown
---
created: 2026-02-25T12:00:00Z
status: in_progress
objective: Process client invoice request
source_file: EMAIL_client_2026-02-25.md
---

# Task Plan

## Objective
Process client invoice request

## Steps
- [ ] Read email content
- [ ] Identify sender and intent
- [ ] Check Company Handbook
- [ ] Draft response
- [ ] Check if approval required
- [ ] Execute or request approval
```

### 4. HITL Approval Workflow

When an action requires approval:

1. Claude creates: `Pending_Approval/PAYMENT_vendor_2026-02-25.md`
2. User reviews and moves to `Approved/`
3. Orchestrator executes and moves to `Done/`

```bash
# Approve an action (Windows)
move AI_Employee_Vault\Pending_Approval\PAYMENT_*.md AI_Employee_Vault\Approved\

# Or let orchestrator handle it
python scripts\approval_manager.py --process
```

### 5. Scheduled Tasks

```bash
# Install all scheduled tasks
python scripts\setup_scheduler.py --install

# Tasks created:
# - AI_Employee_Orchestrator_Hourly (runs every hour)
# - AI_Employee_Daily_Briefing (8 AM daily)
# - AI_Employee_Approval_Check (hourly)

# Remove tasks
python scripts\setup_scheduler.py --remove

# List installed tasks
python scripts\setup_scheduler.py --list
```

### 6. Agent Skills

Skills are reusable capabilities for Claude:

```bash
# Available skills:
skills/email-responder/SKILL.md
skills/invoice-generator/SKILL.md

# Usage in Claude prompts:
claude "Use email-responder skill to reply to the pending email"
claude "Use invoice-generator skill: client=ABC Corp, amount=1500"
```

## Commands Reference

| Command | Purpose |
|---------|---------|
| `python scripts\verify_silver_tier.py` | Verify Silver Tier setup |
| `python scripts\filesystem_watcher.py` | Start file watcher |
| `python scripts\gmail_watcher.py --credentials X.json` | Start Gmail watcher |
| `python scripts\whatsapp_watcher.py` | Start WhatsApp watcher |
| `python scripts\orchestrator.py` | Process pending items |
| `python scripts\approval_manager.py --process` | Process approved actions |
| `python scripts\linkedin_poster.py --topic "X"` | Create LinkedIn post |
| `python scripts\setup_scheduler.py --install` | Install scheduled tasks |
| `python scripts\audit_logger.py --summary` | Show log summary |

## Verification

Run the Silver Tier verification:

```bash
python scripts\verify_silver_tier.py
```

Expected output:
```
[PASS] All vault folders exist
[PASS] Dashboard.md exists
[PASS] Company_Handbook.md exists
[PASS] 3 watcher scripts installed
[PASS] linkedin_poster.py exists
[PASS] plan_manager.py exists
[PASS] approval_manager.py exists
[PASS] All approval folders exist
[PASS] skills/ folder exists
[SUCCESS] ALL SILVER TIER REQUIREMENTS MET!
```

## Security

### Environment Variables

```bash
# Copy and configure
copy .env.template .env

# Required for Silver Tier:
GMAIL_CLIENT_ID=xxx
GMAIL_CLIENT_SECRET=xxx
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Never Commit

- `.env` file (credentials)
- `.gmail_token.json` (OAuth token)
- `.whatsapp_session/` (browser session)
- `Logs/*.json` (audit logs with sensitive data)

## Troubleshooting

### Gmail Watcher Not Working

1. Check credentials.json is valid
2. Re-run OAuth: delete `.gmail_token.json` and re-authenticate
3. Verify Gmail API is enabled in Google Cloud Console

### WhatsApp Watcher Not Logging In

1. First run must use `--no-headless` to show QR code
2. Scan QR code within 60 seconds
3. Session is saved to `.whatsapp_session/`

### MCP Server Not Found

```bash
# Install globally
npm install -g @anthropic/mcp-server-email
npm install -g @anthropic/browser-mcp

# Verify
claude /mcp list
```

### Scheduled Tasks Not Running

1. Check Task Scheduler: `taskschd.msc`
2. Verify task status is "Ready"
3. Check task history for errors

## Next Steps (Gold Tier)

After mastering Silver Tier, upgrade to Gold:

- [ ] Odoo ERP integration via MCP
- [ ] Facebook/Instagram integration
- [ ] Twitter/X integration
- [ ] Weekly CEO Briefing generation
- [ ] Ralph Wiggum loop for persistence
- [ ] Comprehensive error recovery
- [ ] Cloud deployment

## Learning Resources

- **Claude Code + Obsidian:** https://www.youtube.com/watch?v=sCIS05Qt79Y
- **MCP Introduction:** https://modelcontextprotocol.io/introduction
- **Agent Skills:** https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- **Gmail API:** https://developers.google.com/gmail/api/quickstart
- **Playwright:** https://playwright.dev/python/docs/intro

## Weekly Research Meetings

- **When:** Wednesdays 10:00 PM
- **Zoom:** [Join Meeting](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **YouTube:** [Panaversity](https://www.youtube.com/@panaversity)

---

*Built with ❤️ for the Personal AI Employee Hackathon 2026*

*Silver Tier: Functional Assistant*
