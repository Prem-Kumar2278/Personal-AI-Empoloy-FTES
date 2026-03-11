# AI Employee - Silver Tier (Qwen Code Edition)

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

This is the **Silver Tier** implementation using **Qwen Code** as the reasoning engine instead of Claude Code.

## Quick Start

### Step 1: Install Dependencies

```bash
# Install Gmail API libraries
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Install Playwright for WhatsApp/LinkedIn
pip install playwright
playwright install chromium
```

### Step 2: Set Up Gmail (Already Have credentials.json)

Since you already have `credentials.json`, just run:

```bash
cd D:\GIAIC\Personal-AI-Empoloy-FTES

# First-time authentication (opens browser)
python scripts\gmail_watcher.py --credentials credentials.json

# After authentication, the watcher will run
python scripts\gmail_watcher.py --credentials credentials.json --interval 60
```

### Step 3: Set Up Environment Variables

```bash
# Copy template
copy .env.template .env

# Edit .env and add your Gmail credentials from credentials.json
```

Edit `.env`:
```
# Gmail OAuth (copy from credentials.json)
GMAIL_CLIENT_ID=your_client_id_here
GMAIL_CLIENT_SECRET=your_client_secret_here

# SMTP for sending emails
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Step 4: Start All Watchers

```bash
# Terminal 1: File System Watcher
python scripts\filesystem_watcher.py

# Terminal 2: Gmail Watcher
python scripts\gmail_watcher.py --credentials credentials.json

# Terminal 3: WhatsApp Watcher (optional, first run needs QR scan)
python scripts\whatsapp_watcher.py --no-headless
```

### Step 5: Process with Qwen Code

```bash
# Process all pending items
python scripts\qwen_processor.py --auto

# Or process with custom prompt
python scripts\qwen_processor.py --prompt "Check Needs_Action and process pending emails"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER (Watchers)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ File Watcher │  │ Gmail Watcher│  │WhatsApp Watch│          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼─────────────────┼─────────────────┼──────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OBSIDIAN VAULT                             │
│  Needs_Action/  │  Plans/  │  Pending_Approval/  │  Approved/  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REASONING LAYER                              │
│                   QWEN CODE (The Brain)                         │
│  python scripts\qwen_processor.py --auto                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
┌──────────────────────┐    ┌──────────────────────┐
│  Human-in-the-Loop   │    │   Action Layer       │
│  Pending_Approval/   │    │   LinkedIn Poster    │
│  Approved/           │    │   Email (via MCP)    │
└──────────────────────┘    └──────────────────────┘
```

## Silver Tier Features

### 1. Gmail Watcher ✅

Monitors your Gmail for new unread emails and creates action files.

```bash
# Run Gmail watcher
python scripts\gmail_watcher.py --credentials credentials.json --interval 60
```

**What it does:**
- Checks Gmail every 60 seconds
- Detects new unread emails
- Creates action files in `Needs_Action/`
- Flags urgent emails (keywords: invoice, payment, urgent, etc.)

### 2. LinkedIn Auto-Posting ✅

Create and post LinkedIn content for business growth.

```bash
# Create a business post
python scripts\linkedin_poster.py --topic "Industry Trends"

# Post custom content
python scripts\linkedin_poster.py --content "🚀 Exciting news about our new service!"

# Use Qwen Code to generate content
python scripts\linkedin_poster.py --qwen --topic "AI in Business"
```

### 3. Qwen Code Integration ✅

Process tasks using Qwen Code instead of Claude Code.

```bash
# Process all pending items
python scripts\qwen_processor.py --auto

# Process specific file
python scripts\qwen_processor.py --file EMAIL_invoice_2026-02-26.md

# Custom prompt
python scripts\qwen_processor.py --prompt "Read Company_Handbook.md and process pending emails"
```

### 4. Plan.md Creation ✅

Automatic plan creation for task tracking.

```bash
# Plans are created automatically by qwen_processor.py
# Location: AI_Employee_Vault/Plans/
```

### 5. HITL Approval Workflow ✅

Human-in-the-loop for sensitive actions.

```bash
# Check pending approvals
dir AI_Employee_Vault\Pending_Approval

# Approve an action (move to Approved)
move AI_Employee_Vault\Pending_Approval\PAYMENT_*.md AI_Employee_Vault\Approved\

# Process approved actions
python scripts\approval_manager.py --process
```

### 6. Scheduling ✅

```bash
# Install scheduled tasks (Windows)
python scripts\setup_scheduler.py --install

# Show crontab entries (Linux/Mac)
python scripts\setup_scheduler.py --linux
```

## Folder Structure

```
D:\GIAIC\Personal-AI-Empoloy-FTES\
├── scripts/
│   ├── gmail_watcher.py         # Gmail API watcher
│   ├── whatsapp_watcher.py      # WhatsApp Web watcher
│   ├── filesystem_watcher.py    # File system watcher
│   ├── qwen_processor.py        # Qwen Code integration
│   ├── orchestrator.py          # Main coordinator
│   ├── plan_manager.py          # Plan.md creation
│   ├── approval_manager.py      # HITL workflow
│   ├── audit_logger.py          # Audit logging
│   ├── linkedin_poster.py       # LinkedIn auto-posting
│   └── setup_scheduler.py       # Task Scheduler setup
├── AI_Employee_Vault/
│   ├── Needs_Action/            # Pending items
│   ├── Plans/                   # Qwen Code plans
│   ├── Pending_Approval/        # Awaiting approval
│   ├── Approved/                # Approved actions
│   ├── Done/                    # Completed items
│   ├── Social_Posts/            # LinkedIn posts
│   └── Dashboard.md             # Status dashboard
├── credentials.json             # Gmail OAuth (you have this)
├── .env                         # Environment variables
└── README_SILVER_QWEN.md        # This file
```

## Commands Reference

| Command | Purpose |
|---------|---------|
| `python scripts\gmail_watcher.py --credentials credentials.json` | Start Gmail watcher |
| `python scripts\qwen_processor.py --auto` | Process all pending with Qwen |
| `python scripts\linkedin_poster.py --topic "X"` | Create LinkedIn post |
| `python scripts\approval_manager.py --process` | Process approved actions |
| `python scripts\setup_scheduler.py --install` | Install scheduled tasks |
| `python scripts\verify_silver_tier.py` | Verify Silver Tier |

## Gmail Setup (You Already Have credentials.json)

Since you already have `credentials.json`, follow these steps:

### 1. Verify credentials.json Location

```bash
dir D:\GIAIC\Personal-AI-Empoloy-FTES\credentials.json
```

### 2. First-Time Authentication

```bash
python scripts\gmail_watcher.py --credentials credentials.json
```

This will:
1. Open a browser window
2. Ask you to sign in to Google
3. Request permission to read Gmail
4. Save authentication token to `.gmail_token.json`

### 3. Verify Authentication

After authentication, check:
```bash
dir AI_Employee_Vault\.gmail_token.json
```

### 4. Run Gmail Watcher

```bash
# Check every 60 seconds
python scripts\gmail_watcher.py --credentials credentials.json --interval 60
```

## LinkedIn Setup

### Option 1: Browser Automation (Recommended)

```bash
# Create post (opens browser for posting)
python scripts\linkedin_poster.py --topic "AI in Business" --browser
```

### Option 2: Draft and Manual Post

```bash
# Create draft
python scripts\linkedin_poster.py --topic "AI in Business" --draft

# Review draft
type AI_Employee_Vault\Social_Posts\Drafts\DRAFT_*.md

# Post manually on LinkedIn.com
```

## Qwen Code Setup

### Option 1: Qwen CLI (If Available)

```bash
# Install qwen-code (if available)
pip install qwen-code

# Verify
qwen --version

# Process tasks
python scripts\qwen_processor.py --auto
```

### Option 2: Web Interface

```bash
# Create prompt file
python scripts\qwen_processor.py --auto

# Prompt file created: AI_Employee_Vault\.qwen_prompt_*.txt

# Copy prompt and paste in:
# https://chat.qwen.ai/
```

## End-to-End Example

### 1. Start Watchers

```bash
# Terminal 1: Gmail Watcher
python scripts\gmail_watcher.py --credentials credentials.json
```

### 2. Wait for Email

When a new email arrives, Gmail watcher creates:
```
AI_Employee_Vault\Needs_Action\EMAIL_sender_2026-02-26.md
```

### 3. Process with Qwen Code

```bash
python scripts\qwen_processor.py --auto
```

### 4. Qwen Code Creates Plan

```
AI_Employee_Vault\Plans\PLAN_process_email_20260226_120000.md
```

### 5. Check for Approval

If approval needed:
```
AI_Employee_Vault\Pending_Approval\EMAIL_reply_2026-02-26.md
```

### 6. Approve (if needed)

```bash
move AI_Employee_Vault\Pending_Approval\*.md AI_Employee_Vault\Approved\
python scripts\approval_manager.py --process
```

### 7. Task Complete

```
AI_Employee_Vault\Done\EMAIL_sender_2026-02-26.md
```

## Troubleshooting

### Gmail Watcher Not Working

1. Check credentials.json exists
2. Re-run authentication: delete `.gmail_token.json` and run again
3. Check error logs: `AI_Employee_Vault\Logs\*.log`

### Qwen Code Not Found

Use web interface instead:
1. Run `python scripts\qwen_processor.py --auto`
2. Copy prompt from `.qwen_prompt_*.txt`
3. Paste in https://chat.qwen.ai/

### LinkedIn Poster Not Working

1. Check Playwright installed: `playwright install chromium`
2. Use `--no-headless` for first run
3. Check session folder: `AI_Employee_Vault\.whatsapp_session\`

## Verification

```bash
python scripts\verify_silver_tier.py
```

Expected output:
```
[PASS] All vault folders exist
[PASS] 3 watcher scripts installed
[PASS] linkedin_poster.py exists
[PASS] qwen_processor.py exists
[PASS] All approval folders exist
[SUCCESS] ALL SILVER TIER REQUIREMENTS MET!
```

## Next Steps (Gold Tier)

- [ ] Odoo ERP integration
- [ ] Facebook/Instagram integration
- [ ] Twitter/X integration
- [ ] Weekly CEO Briefing
- [ ] Ralph Wiggum persistence loop

---

*AI Employee Silver Tier - Powered by Qwen Code*
*Built for Personal AI Employee Hackathon 2026*
