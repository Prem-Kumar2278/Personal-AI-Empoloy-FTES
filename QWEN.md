# Personal AI Employee (Digital FTE) - Project Context

## Project Overview

This project builds a **Digital Full-Time Equivalent (FTE)** - an autonomous AI employee that works 24/7 to manage personal and business affairs. The system uses **Claude Code** as the reasoning engine and **Obsidian** as the local-first knowledge base/dashboard.

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

### Core Value Proposition

| Feature | Human FTE | Digital FTE |
|---------|-----------|-------------|
| Availability | 40 hours/week | 168 hours/week (24/7) |
| Monthly Cost | $4,000-$8,000+ | $500-$2,000 |
| Ramp-up Time | 3-6 months | Instant |
| Annual Hours | ~2,000 hours | ~8,760 hours |
| Cost per Task | ~$5.00 | ~$0.50 |

**The "Aha!" Moment:** 85-90% cost savings with 4x more availability.

## Architecture: Perception → Reasoning → Action

### 1. The Foundational Layer (Local Engine)

- **The Nerve Center (Obsidian):** GUI and Long-Term Memory
  - `Dashboard.md`: Real-time summary of bank balance, pending messages, active projects
  - `Company_Handbook.md`: Rules of Engagement (e.g., "Flag any payment over $500")
- **The Muscle (Claude Code):** Runs in terminal, uses File System tools to read tasks and write reports

### 2. Perception (The "Watchers")

Lightweight Python Sentinel Scripts running in background:
- **Comms Watcher:** Monitors Gmail and WhatsApp, saves urgent messages to `/Needs_Action`
- **Finance Watcher:** Downloads bank CSVs, logs transactions to `/Accounting/Current_Month.md`
- **File System Watcher:** Monitors drop folders for new files to process

### 3. Reasoning (Claude Code)

When Watcher detects change, it triggers Claude:
1. **Read:** Check `/Needs_Action` and `/Accounting`
2. **Think:** Analyze messages and transactions
3. **Plan:** Create `Plan.md` with checkboxes for next steps

### 4. Action (The "Hands" - MCP Servers)

Model Context Protocol servers handle external actions:
- **Email MCP:** Send emails, draft replies
- **Browser MCP:** Navigate websites, fill forms, click buttons (Playwright)
- **Payment MCP:** Log into payment portals, draft payments
- **Calendar MCP:** Create/update events

### 5. Human-in-the-Loop (HITL)

For sensitive actions:
1. Claude writes `APPROVAL_REQUIRED_Payment_Client_A.md`
2. User moves file to `/Approved` folder
3. Orchestrator executes the action via MCP

## Folder Structure

```
AI_Employee_Vault/
├── Inbox/                    # Raw incoming items
├── Needs_Action/             # Items requiring processing
├── In_Progress/              # Items being worked on (claim-by-move rule)
├── Pending_Approval/         # Actions awaiting human approval
├── Approved/                 # Approved actions ready to execute
├── Rejected/                 # Rejected actions
├── Done/                     # Completed items
├── Plans/                    # Claude-generated plans
├── Logs/                     # Audit logs (YYYY-MM-DD.json)
├── Accounting/               # Bank transactions, invoices
├── Briefings/                # CEO Briefings (weekly reports)
├── Dashboard.md              # Real-time status dashboard
├── Company_Handbook.md       # Rules of Engagement
└── Business_Goals.md         # Q1/Q2 objectives and metrics
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Reasoning Engine | Claude Code | Primary AI agent |
| Knowledge Base | Obsidian | Local Markdown dashboard |
| Browser Automation | Playwright MCP | Web interaction |
| Orchestration | Python | Watcher scripts, process management |
| External Integrations | MCP Servers | Email, banking, social media |
| Process Management | PM2/supervisord | Keep watchers running 24/7 |

## Key Concepts

### Ralph Wiggum Loop (Persistence Pattern)

A Stop hook that keeps Claude iterating until multi-step tasks are complete:
1. Orchestrator creates state file with prompt
2. Claude works on task
3. Claude tries to exit
4. Stop hook checks: Is task file in `/Done`?
5. If NO → Block exit, re-inject prompt (loop continues)
6. If YES → Allow exit (complete)

### Claim-by-Move Rule

Prevents double-work in multi-agent scenarios:
- First agent to move item from `/Needs_Action` to `/In_Progress/<agent>/` owns it
- Other agents must ignore it

### Watcher Architecture Pattern

All Watchers follow this base structure:

```python
class BaseWatcher:
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
    
    def run(self):
        while True:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
            time.sleep(check_interval)
```

## Security & Privacy

### Credential Management
- Never store credentials in plain text or vault
- Use environment variables for API keys
- Use secrets manager for banking credentials (Keychain, 1Password CLI)
- Create `.env` file (add to `.gitignore`)

### Permission Boundaries

| Action Category | Auto-Approve | Requires Approval |
|-----------------|--------------|-------------------|
| Email replies | Known contacts | New contacts, bulk |
| Payments | < $50 recurring | New payees, > $100 |
| Social media | Scheduled posts | Replies, DMs |
| File operations | Create, read | Delete, move outside vault |

### Audit Logging

Every action must be logged:
```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "action_type": "email_send",
  "actor": "claude_code",
  "target": "client@example.com",
  "approval_status": "approved",
  "approved_by": "human",
  "result": "success"
}
```

## Error Recovery

### Retry Logic
- Transient errors (network timeout, rate limit): Exponential backoff
- Authentication errors: Alert human, pause operations
- Logic errors: Human review queue

### Graceful Degradation
- Gmail API down: Queue emails locally, process when restored
- Banking API timeout: Never retry payments automatically
- Claude Code unavailable: Watchers continue, queue grows

## Hackathon Tiers

### Bronze Tier (8-12 hours) - Foundation
- [x] Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- [x] One working Watcher script (Gmail OR file system)
- [x] Claude Code reading/writing to vault
- [x] Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- [x] AI functionality as Agent Skills

### Silver Tier (20-30 hours)
- All Bronze + 2+ watchers, MCP server, HITL workflow, scheduling

### Gold Tier (40+ hours)
- All Silver + Odoo integration, CEO Briefing, Ralph loop, audit logging

### Platinum Tier (60+ hours)
- All Gold + Cloud deployment, domain specialization, 24/7 operation

## Example Flow: Invoice Request

1. **Detection:** WhatsApp Watcher detects "invoice" keyword
2. **File Created:** `/Needs_Action/WHATSAPP_client_a_2026-01-07.md`
3. **Reasoning:** Claude reads, creates `/Plans/PLAN_invoice_client_a.md`
4. **Approval:** Claude writes `/Pending_Approval/EMAIL_invoice_client_a.md`
5. **Human Review:** User moves to `/Approved`
6. **Action:** Orchestrator calls Email MCP to send invoice
7. **Completion:** Files moved to `/Done`, Dashboard updated

## Weekly Research Meetings

- **When:** Wednesdays 10:00 PM
- **Zoom:** https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- **YouTube:** https://www.youtube.com/@panaversity

## Learning Resources

- **Claude Code Fundamentals:** https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows
- **Obsidian:** help.obsidian.md/Getting+started
- **MCP Introduction:** modelcontextprotocol.io/introduction
- **Agent Skills:** platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- **Playwright:** playwright.dev/python/docs/intro
