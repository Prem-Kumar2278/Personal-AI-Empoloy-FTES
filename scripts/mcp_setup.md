# MCP Servers Configuration for AI Employee

This folder contains MCP (Model Context Protocol) server configurations.

## Setup Instructions

### 1. Install MCP Servers

```bash
# Email MCP Server (for sending emails)
npm install -g @anthropic/mcp-server-email

# Browser MCP Server (Playwright - for web automation)
npm install -g @anthropic/browser-mcp

# Or use npx directly (no installation needed)
```

### 2. Configure Claude Code

Edit your Claude Code MCP configuration:

**Windows:** `%APPDATA%\Claude\mcp.json`
**Mac/Linux:** `~/.config/claude-code/mcp.json`

```json
{
  "mcpServers": {
    "email": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-email"],
      "env": {
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "your-email@gmail.com",
        "SMTP_PASSWORD": "your-app-password"
      }
    },
    "browser": {
      "command": "npx",
      "args": ["-y", "@anthropic/browser-mcp"],
      "env": {
        "HEADLESS": "true"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-filesystem"],
      "args": ["--allowed-dirs", "D:\\GIAIC\\Personal-AI-Empoloy-FTES\\AI_Employee_Vault"]
    }
  }
}
```

### 3. Gmail App Password Setup

For email MCP to work with Gmail:

1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Generate an App Password: https://myaccount.google.com/apppasswords
4. Use this password in the MCP config (NOT your regular password)

### 4. Verify MCP Servers

After configuration, verify in Claude Code:

```bash
claude
> /mcp list
```

You should see: email, browser, filesystem

## Available MCP Tools

### Email MCP

- `send_email` - Send an email
- `draft_email` - Create email draft
- `search_emails` - Search inbox

### Browser MCP (Playwright)

- `browser_navigate` - Go to URL
- `browser_click` - Click element
- `browser_type` - Type text
- `browser_snapshot` - Get page accessibility snapshot
- `browser_screenshot` - Take screenshot
- `browser_evaluate` - Run JavaScript

### Filesystem MCP

- `read_file` - Read file contents
- `write_file` - Write file
- `list_directory` - List folder contents
- `search_files` - Search for files

## Usage in Claude Prompts

```bash
claude "Use the email MCP to send a reply to the client"
claude "Use browser MCP to navigate to the payment portal"
claude "Use filesystem MCP to read the action file"
```

## Troubleshooting

### MCP Server Not Found

```bash
# Install globally
npm install -g @anthropic/mcp-server-email
npm install -g @anthropic/browser-mcp
```

### Authentication Failed

- Verify SMTP credentials in mcp.json
- Use Gmail App Password, not regular password
- Check 2FA is enabled on Google Account

### Browser MCP Fails

```bash
# Install Playwright browsers
playwright install chromium
```

## Security Notes

- Never commit mcp.json with real credentials
- Use environment variables for sensitive data
- Rotate app passwords regularly
- Review MCP server permissions
