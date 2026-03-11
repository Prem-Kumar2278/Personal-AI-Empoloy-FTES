# Qwen Code Setup Guide for AI Employee

## Using Qwen Code as the Brain (Instead of Claude Code)

This project uses **Qwen Code** as the reasoning engine instead of Claude Code. Qwen Code provides similar capabilities for file-based reasoning and task processing.

## Setup Qwen Code

### 1. Install Qwen Code

```bash
# Install via pip
pip install qwen-code

# Or use the web interface at https://chat.qwen.ai/
```

### 2. Verify Installation

```bash
qwen --version
```

### 3. Configure for AI Employee

Qwen Code reads from the vault folder and processes tasks similar to Claude Code.

## Running Qwen Code with AI Employee

### Process Pending Tasks

```bash
# Basic task processing
qwen "Check the Needs_Action folder and process any pending items. Follow the Company_Handbook.md rules."

# With specific task
qwen "Read the action file in Needs_Action folder and create a plan in Plans folder"
```

### Using Qwen Code API

```python
from qwen import Qwen

client = Qwen(api_key="your-api-key")

response = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {"role": "system", "content": "You are an AI Employee assistant."},
        {"role": "user", "content": "Process the pending tasks in the vault"}
    ]
)
```

## Qwen Code vs Claude Code

| Feature | Claude Code | Qwen Code |
|---------|-------------|-----------|
| Reasoning | ✅ | ✅ |
| File Reading | ✅ | ✅ |
| Plan Creation | ✅ | ✅ |
| MCP Integration | ✅ | ⚠️ Limited |
| Agent Skills | ✅ | ✅ |

## Integration Points

### 1. Orchestrator Integration

The orchestrator creates prompt files that Qwen Code can process:

```bash
# Orchestrator creates: .qwen_prompt_TASK.txt
# Qwen Code reads and processes the prompt
qwen < .qwen_prompt_TASK.txt
```

### 2. Plan Creation

Qwen Code creates Plan.md files in the Plans folder:

```markdown
---
created: 2026-02-26T00:00:00Z
status: in_progress
objective: Process email task
processed_by: qwen_code
---
```

### 3. Approval Workflow

Qwen Code follows the same HITL workflow:
- Creates approval requests in `Pending_Approval/`
- Waits for human approval
- Executes approved actions

## Example Workflow

```bash
# 1. Watcher creates action file
python scripts/filesystem_watcher.py

# 2. Orchestrator prepares task
python scripts/orchestrator.py

# 3. Qwen Code processes task
qwen "Read .claude_prompt_FILE_test.txt and process the task. Create a plan in Plans folder."

# 4. Move completed task to Done
move AI_Employee_Vault\Needs_Action\*.md AI_Employee_Vault\Done\
```

## Environment Variables for Qwen

```bash
# .env file
QWEN_API_KEY=your_qwen_api_key
QWEN_MODEL=qwen-plus
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

## Troubleshooting

### Qwen Code Not Processing Files

1. Check file encoding (UTF-8)
2. Verify file paths are absolute
3. Ensure prompt files are created correctly

### API Errors

1. Check API key is valid
2. Verify network connection
3. Check rate limits

---

*AI Employee Silver Tier - Qwen Code Integration*
