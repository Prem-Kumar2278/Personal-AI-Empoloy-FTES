---
name: email-responder
description: Draft and send email replies to pending emails in Needs_Action
version: 1.0
tier: Silver
---

# Email Responder Skill

## Purpose

Process pending email action files, draft appropriate replies, and send them (with approval if required).

## When to Use

- Email action file exists in `Needs_Action/` folder
- Email requires a response
- Sender is known or response is appropriate per Company Handbook

## Input

- Action file path in `Needs_Action/`
- Email content and context
- Company Handbook rules

## Output

- Draft reply (for approval if needed)
- Sent email (if auto-approved)
- Updated action file in `Done/`

## Rules (from Company Handbook)

| Condition | Action |
|-----------|--------|
| Known contact | Auto-approve reply |
| New contact | Require approval |
| Bulk email (10+) | Require approval |
| Sensitive topic | Require approval |

## Steps

1. **Read Action File**
   - Load email from `Needs_Action/`
   - Extract sender, subject, content

2. **Check Handbook Rules**
   - Is sender known?
   - Is this bulk email?
   - Are there sensitive keywords?

3. **Draft Reply**
   - Use appropriate tone (polite, professional)
   - Address sender's concerns
   - Include relevant information

4. **Determine Approval Need**
   - If approval required: Create file in `Pending_Approval/`
   - If auto-approved: Send via Email MCP

5. **Execute**
   - Send email or wait for approval
   - Log action
   - Move to `Done/`

## MCP Tools Used

- `email/send_email` - Send email
- `email/draft_email` - Create draft

## Example Usage

```bash
# Invoke skill
claude "Use email-responder skill for the pending email from Client A"

# With parameters
claude "Use email-responder: file=EMAIL_client_2026-02-25.md, tone=professional"
```

## Example Reply Template

```markdown
Subject: Re: {original_subject}

Dear {sender_name},

Thank you for your email regarding {topic}.

{response_body}

Please let me know if you have any questions.

Best regards,
{your_name}
```

## Error Handling

| Error | Recovery |
|-------|----------|
| SMTP failure | Log error, notify user, retry later |
| Invalid recipient | Flag for human review |
| Content filter | Require approval |

## Logging

All email actions are logged:

```json
{
  "timestamp": "2026-02-25T10:30:00Z",
  "skill": "email-responder",
  "action": "send_email",
  "recipient": "client@example.com",
  "approval_status": "auto_approved",
  "result": "success"
}
```

## Files

- `skills/email-responder/SKILL.md` - This file
- `skills/email-responder/templates/` - Email templates
- `skills/email-responder/handler.py` - Implementation (optional)

---
*Part of AI Employee Silver Tier*
