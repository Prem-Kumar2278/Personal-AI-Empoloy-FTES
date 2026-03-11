# Human-in-the-Loop (HITL) Approval Workflow

## Overview

For sensitive actions (payments, bulk emails, etc.), the AI Employee requires human approval before executing. This is implemented through a file-based approval workflow.

## Workflow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Claude Code    │────▶│  Pending_Approval│────▶│   Human Review  │
│  Creates Request│     │  Folder          │     │   (You)         │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                    ┌─────────────────────────────────────┼─────────────────────────────────────┐
                    │                                     │                                     │
                    ▼                                     ▼                                     ▼
          ┌──────────────────┐                  ┌──────────────────┐                  ┌──────────────────┐
          │   Move to        │                  │   Move to        │                  │   Leave in       │
          │   /Approved/     │                  │   /Rejected/     │                  │   Pending        │
          └────────┬─────────┘                  └────────┬─────────┘                  └──────────────────┘
                   │                                     │
                   ▼                                     ▼
          ┌──────────────────┐                  ┌──────────────────┐
          │  Orchestrator    │                  │  Task Cancelled  │
          │  Executes Action │                  │  & Logged        │
          └──────────────────┘                  └──────────────────┘
```

## Approval Thresholds (from Company_Handbook.md)

| Action Type | Auto-Approve | Requires Approval |
|-------------|--------------|-------------------|
| Email replies | Known contacts | New contacts, bulk sends |
| Payments | < $50 recurring | New payees, > $100 |
| Social media | Scheduled posts | Replies, DMs |
| File operations | Create, read | Delete, move outside vault |

## Approval File Format

When Claude determines an action requires approval, it creates a file:

**Location:** `Pending_Approval/ACTION_description_timestamp.md`

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
reason: Invoice #1234 payment
created: 2026-02-25T10:30:00Z
expires: 2026-02-26T10:30:00Z
status: pending
---

# Approval Request

## Action Details

- **Type:** Payment
- **Amount:** $500.00
- **Recipient:** Client A (Bank: XXXX1234)
- **Reference:** Invoice #1234
- **Reason:** Monthly service payment

## Why Approval Required

This payment exceeds the auto-approve threshold of $100 for new recipients.

## To Approve

Move this file to the `/Approved` folder.

## To Reject

Move this file to the `/Rejected` folder.

## Notes

*Add any notes or conditions:*

---
*Created by AI Employee (Silver Tier)*
```

## Human Actions

### To Approve

1. Review the approval request file
2. Move file from `Pending_Approval/` to `Approved/`
3. Orchestrator will execute the action

```bash
# Example (Windows)
move AI_Employee_Vault\Pending_Approval\PAYMENT_client.md AI_Employee_Vault\Approved\
```

### To Reject

1. Optionally add rejection reason to file
2. Move file from `Pending_Approval/` to `Rejected/`

```bash
# Example (Windows)
move AI_Employee_Vault\Pending_Approval\PAYMENT_client.md AI_Employee_Vault\Rejected\
```

### To Request More Information

1. Edit the file and add questions in the Notes section
2. Leave file in `Pending_Approval/`
3. Claude will see the notes on next run

## Orchestrator Integration

The orchestrator monitors the `Approved/` folder:

```python
# Pseudocode
approved_files = list(Approved_folder.glob('*.md'))
for file in approved_files:
    action = parse_approval_file(file)
    execute_action(action)
    log_action(action, status='executed')
    move_to_done(file)
```

## Expiration

Approval requests older than 24 hours are automatically moved to `Rejected/` with status `expired`.

## Audit Logging

All approval actions are logged:

```json
{
  "timestamp": "2026-02-25T10:35:00Z",
  "action_type": "approval_request",
  "action": "payment",
  "amount": 500.00,
  "status": "approved",
  "approved_by": "human",
  "result": "executed"
}
```

## Implementation Files

- `scripts/approval_manager.py` - Manages approval workflow
- `Pending_Approval/` - Pending requests
- `Approved/` - Approved, ready to execute
- `Rejected/` - Rejected or expired

## Usage Example

### Step 1: Claude Creates Approval Request

```bash
claude "Process the invoice request for Client A ($500)"
# Claude creates: Pending_Approval/PAYMENT_client_a_2026-02-25.md
```

### Step 2: Human Reviews

```bash
# Read the request
type AI_Employee_Vault\Pending_Approval\PAYMENT_client_a_2026-02-25.md

# Approve it
move AI_Employee_Vault\Pending_Approval\PAYMENT_client_a_2026-02-25.md AI_Employee_Vault\Approved\
```

### Step 3: Orchestrator Executes

```bash
python scripts/orchestrator.py
# Detects approved file, executes payment, moves to Done
```

## Security

- Approval files include checksums to prevent tampering
- Sensitive data (account numbers) are masked
- All approvals are logged with timestamps
- Expired approvals require re-submission
