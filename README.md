# AI Employee - Bronze Tier

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

This is the **Bronze Tier** implementation of the Personal AI Employee (Digital FTE) hackathon project. It provides the foundational layer for an autonomous AI employee that works 24/7 using Claude Code and Obsidian.

## What is Bronze Tier?

The Bronze Tier is the **Minimum Viable Deliverable** for the AI Employee hackathon:

- ✅ Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- ✅ One working Watcher script (File System monitoring)
- ✅ Claude Code integration for reading/writing to the vault
- ✅ Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- ✅ AI functionality implemented as Agent Skills

**Estimated Setup Time:** 8-12 hours

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  File System    │────▶│   File Watcher   │────▶│  Needs_Action/  │
│  (Drop Files)   │     │   (Python)       │     │  (Markdown)     │
└─────────────────┘     └──────────────────┘     └─────────┬───────┘
                                                           │
                                                           ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Done/          │◀────│   Claude Code    │◀────│  Orchestrator   │
│  (Completed)    │     │   (Reasoning)    │     │  (Coordinator)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Prerequisites

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| **Claude Code** | Active subscription | Primary reasoning engine |
| **Obsidian** | v1.10.6+ (free) | Knowledge base & dashboard |
| **Python** | 3.13 or higher | Watcher scripts & orchestration |
| **Node.js** | v24+ LTS | Future MCP servers (Silver tier+) |

### Hardware Requirements

- Minimum: 8GB RAM, 4-core CPU, 20GB free disk space
- Recommended: 16GB RAM, 8-core CPU, SSD storage

## Quick Start

### 1. Verify Prerequisites

```bash
# Check Python version
python --version  # Should be 3.13+

# Check Claude Code
claude --version

# If Claude Code not installed:
npm install -g @anthropic/claude-code
```

### 2. Setup the Vault

The vault is already created at `AI_Employee_Vault/`. Open it in Obsidian:

1. Open Obsidian
2. Click "Open folder as vault"
3. Select the `AI_Employee_Vault` folder

### 3. Configure the Watcher

Edit the file system watcher if needed (optional):

```bash
# Default check interval is 30 seconds
# To change, edit scripts/filesystem_watcher.py or pass --interval
```

### 4. Start the File Watcher

```bash
# Navigate to project root
cd D:\GIAIC\Personal-AI-Empoloy-FTES

# Start the watcher (runs continuously)
python scripts/filesystem_watcher.py

# Or specify custom vault path
python scripts/filesystem_watcher.py --vault /path/to/vault

# Or change check interval
python scripts/filesystem_watcher.py --interval 60
```

**Keep this terminal window open** - the watcher runs continuously.

### 5. Test the System

1. **Drop a test file** into `AI_Employee_Vault/Inbox/`:
   ```bash
   echo "Please process this task" > "AI_Employee_Vault/Inbox/test_task.txt"
   ```

2. **Wait 30 seconds** - the watcher will detect it and create an action file

3. **Check `Needs_Action/`** - you should see a new `.md` file

4. **Run the Orchestrator** to process with Claude:
   ```bash
   python scripts/orchestrator.py
   ```

5. **Run Claude Code** manually (Bronze Tier):
   ```bash
   claude "Check the Needs_Action folder and process any pending items. Follow the Company_Handbook.md rules."
   ```

## Folder Structure

```
AI_Employee_Vault/
├── Inbox/              # Drop files here for processing
├── Needs_Action/       # Items awaiting processing
├── Done/               # Completed items
├── Plans/              # Claude-generated plans
├── Pending_Approval/   # Items awaiting human approval
├── Approved/           # Approved items ready to execute
├── Rejected/           # Rejected items
├── Logs/               # Audit logs
├── Accounting/         # Bank transactions, invoices
├── Briefings/          # CEO briefings (weekly reports)
├── Dashboard.md        # Real-time status dashboard
└── Company_Handbook.md # Rules of engagement
```

## Usage Guide

### Dropping Files for Processing

1. Create a text file with your task:
   ```
   AI_Employee_Vault/Inbox/my_task.txt
   ```

2. Content example:
   ```
   Please review this document and summarize the key points.
   Also check if there are any action items I need to complete.
   ```

3. The watcher will automatically create an action file in `Needs_Action/`

### Processing with Claude Code

For Bronze Tier, processing is semi-automated:

```bash
# Option 1: Run orchestrator to prepare items
python scripts/orchestrator.py

# Option 2: Run Claude directly
claude "Check /Needs_Action folder and process pending items"

# Option 3: Interactive mode
claude
> "Read the Dashboard.md and Company_Handbook.md, then check for new tasks"
```

### Moving Items to Done

After Claude processes an item:

1. Review the output
2. Move the action file to `/Done/` folder
3. Dashboard will be updated automatically

## Scripts Reference

### filesystem_watcher.py

Monitors the Inbox folder for new files.

```bash
# Basic usage
python scripts/filesystem_watcher.py

# Custom vault path
python scripts/filesystem_watcher.py --vault /path/to/vault

# Change check interval (default: 30s)
python scripts/filesystem_watcher.py --interval 60
```

### orchestrator.py

Coordinates processing of pending items.

```bash
# Run once (process all pending items)
python scripts/orchestrator.py

# Run continuously
python scripts/orchestrator.py --continuous

# Custom interval (default: 60s)
python scripts/orchestrator.py --continuous --interval 120
```

### base_watcher.py

Base class for creating custom watchers (Gmail, WhatsApp, etc.).

## Configuration

### Company Handbook Rules

Edit `AI_Employee_Vault/Company_Handbook.md` to customize:

- Payment approval thresholds
- Communication rules
- File handling policies
- Business goals and metrics

### Dashboard

The `Dashboard.md` is automatically updated. Key sections:

- **Quick Status:** Pending, in-progress, completed counts
- **Recent Activity:** Timestamped log of actions
- **System Health:** Component status

## Troubleshooting

### Watcher not detecting files

1. Check the watcher is running: `python scripts/filesystem_watcher.py`
2. Verify Inbox folder exists: `AI_Employee_Vault/Inbox/`
3. Check logs: `AI_Employee_Vault/Logs/YYYY-MM-DD.log`

### Claude Code not working

1. Verify installation: `claude --version`
2. Check subscription status
3. Ensure internet connection

### Action files not created

1. Check watcher logs for errors
2. Verify file permissions
3. Ensure `.filesystem_watcher_state` file is writable

## Next Steps (Silver Tier)

After mastering Bronze Tier, upgrade to Silver:

- [ ] Add Gmail Watcher for email monitoring
- [ ] Add WhatsApp Watcher for message monitoring
- [ ] Implement MCP server for sending emails
- [ ] Add Human-in-the-Loop approval workflow
- [ ] Set up scheduled tasks (cron/Task Scheduler)

## Security Notes

⚠️ **Important Security Practices:**

1. **Never commit credentials** - Add `.env` to `.gitignore`
2. **Use environment variables** for API keys
3. **Review before approving** - Always check approval requests
4. **Audit logs regularly** - Check `Logs/` folder weekly

## Learning Resources

- **Claude Code Fundamentals:** https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows
- **Obsidian Guide:** https://help.obsidian.md/Getting+started
- **Agent Skills:** https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- **Hackathon Document:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`

## Weekly Research Meetings

- **When:** Wednesdays 10:00 PM
- **Zoom:** [Join Meeting](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **YouTube:** [Panaversity](https://www.youtube.com/@panaversity)

## License

This is a hackathon project for educational purposes.

---

*Built with ❤️ for the Personal AI Employee Hackathon 2026*
