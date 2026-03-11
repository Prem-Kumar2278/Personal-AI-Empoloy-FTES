---
name: invoice-generator
description: Generate invoices from client requests
version: 1.0
tier: Silver
---

# Invoice Generator Skill

## Purpose

Create professional invoices from client requests and send them (with approval if amount exceeds threshold).

## When to Use

- Client requests an invoice via email/WhatsApp
- Service completed, payment due
- Monthly billing cycle

## Input

- Client name and details
- Service description
- Amount
- Due date (default: 30 days)

## Output

- Invoice PDF or markdown
- Email to client
- Transaction logged in Accounting

## Rules (from Company Handbook)

| Condition | Action |
|-----------|--------|
| Amount < $100 | Auto-send |
| Amount >= $100 | Require approval |
| New client | Require approval |

## Steps

1. **Extract Invoice Details**
   - Client name
   - Service provided
   - Amount
   - Reference number

2. **Generate Invoice**
   - Use invoice template
   - Include all required fields
   - Save to Invoices folder

3. **Check Approval Threshold**
   - If >= $100 or new client: Create approval request
   - If < $100 and known client: Auto-send

4. **Send Invoice**
   - Attach invoice to email
   - Send to client
   - Log transaction

5. **Update Records**
   - Add to Accounting
   - Update Dashboard
   - Move task to Done

## Invoice Template

```markdown
# INVOICE

**Invoice #:** INV-2026-001
**Date:** 2026-02-25
**Due Date:** 2026-03-27

---

**From:**
Your Company Name
Your Address
your@email.com

**To:**
Client Name
Client Address
client@email.com

---

| Description | Amount |
|-------------|--------|
| Service provided | $1,500.00 |

---

**Total Due:** $1,500.00

**Payment Instructions:**
Bank Transfer: XXXX-1234
Reference: INV-2026-001
```

## Example Usage

```bash
# Generate invoice
claude "Use invoice-generator skill: client=ABC Corp, amount=1500, service=Consulting"

# With custom due date
claude "Use invoice-generator: client=XYZ Inc, amount=2000, due_date=2026-03-15"
```

## Files

- `skills/invoice-generator/SKILL.md` - This file
- `skills/invoice-generator/templates/` - Invoice templates
- `AI_Employee_Vault/Invoices/` - Generated invoices

---
*Part of AI Employee Silver Tier*
