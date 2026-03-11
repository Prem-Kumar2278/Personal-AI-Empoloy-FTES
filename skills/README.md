# AI Employee Skills

This folder contains Agent Skills for Claude Code. Skills package reusable capabilities that the AI Employee can invoke.

## What are Agent Skills?

[Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) are reusable, composable units of functionality that extend Claude Code's capabilities. Each skill:

- Has a clear purpose and interface
- Can be invoked via prompt
- Follows consistent patterns
- Is documented for reuse

## Available Skills (Silver Tier)

| Skill | Description | Usage |
|-------|-------------|-------|
| `email-responder` | Draft and send email replies | "Use email-responder skill to reply to client" |
| `invoice-generator` | Generate invoices from requests | "Generate invoice for Client A, $1500" |
| `social-poster` | Create and schedule social posts | "Post about our new feature on LinkedIn" |
| `ceo-briefing` | Generate weekly business briefings | "Generate CEO briefing for this week" |
| `approval-request` | Create approval requests | "Request approval for $500 payment" |
| `task-processor` | Process items from Needs_Action | "Process all pending tasks" |

## Skill Structure

Each skill has this structure:

```
skills/
├── email-responder/
│   ├── SKILL.md           # Skill definition and instructions
│   ├── handler.py         # Python implementation (optional)
│   └── examples.md        # Usage examples
├── invoice-generator/
│   ├── SKILL.md
│   └── templates/
│       └── invoice.md
...
```

## SKILL.md Template

```markdown
---
name: skill-name
description: What this skill does
version: 1.0
---

# Skill Name

## Purpose

What this skill is for.

## When to Use

Conditions for using this skill.

## Input

Required information.

## Output

What the skill produces.

## Steps

1. Step one
2. Step two
3. Step three

## Examples

Example usage.
```

## Invoking Skills

### Method 1: Direct Prompt

```bash
claude "Use the email-responder skill to reply to the pending email"
```

### Method 2: With Parameters

```bash
claude "Use invoice-generator skill: client=ABC Corp, amount=1500, service=Consulting"
```

### Method 3: From Orchestrator

The orchestrator automatically invokes skills based on task type.

## Creating New Skills

1. Create folder: `skills/your-skill/`
2. Create `SKILL.md` with definition
3. Implement handler if needed (Python/Node.js)
4. Test with Claude Code
5. Document in this README

## Skill Development Best Practices

1. **Single Responsibility**: Each skill does one thing well
2. **Clear Interface**: Document inputs and outputs
3. **Error Handling**: Handle failures gracefully
4. **Logging**: Log all skill executions
5. **Testing**: Test with various inputs

## Silver Tier Skills Checklist

- [x] Email Responder
- [x] Invoice Generator  
- [ ] Social Poster (LinkedIn)
- [ ] CEO Briefing
- [ ] Approval Request
- [x] Task Processor (Orchestrator)

## Gold Tier Skills (Future)

- [ ] Facebook Poster
- [ ] Instagram Poster
- [ ] Twitter/X Poster
- [ ] Odoo Integration
- [ ] Bank Reconciliation
- [ ] Subscription Auditor
