# Gmail Watcher Setup Guide

Complete guide for setting up Gmail API integration with the AI Employee.

## Prerequisites

- Python 3.13+
- Google Account with Gmail
- Gmail API enabled

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project" or select existing project
3. Name: "AI Employee Gmail"
4. Click "Create"

## Step 2: Enable Gmail API

1. In your project, go to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure "OAuth consent screen":
   - User Type: External
   - App name: AI Employee
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue"
   - Scopes: Skip for now
   - Test users: Add your Gmail address
   - Click "Save and Continue"

4. Create OAuth Client ID:
   - Application type: Desktop app
   - Name: AI Employee Gmail
   - Click "Create"

5. Download credentials:
   - Click "Download JSON"
   - Save as `credentials.json` in project root: `D:\GIAIC\Personal-AI-Empoloy-FTES\credentials.json`

## Step 4: Install Gmail API Libraries

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Step 5: First-Time Authentication

Run the Gmail watcher for the first time:

```bash
cd D:\GIAIC\Personal-AI-Empoloy-FTES
python scripts\gmail_watcher.py --credentials credentials.json
```

This will:
1. Open a browser window
2. Ask you to sign in to Google
3. Request permission to read Gmail
4. Save authentication token to `.gmail_token.json`

**Important:** The `.gmail_token.json` file is created automatically and should be kept secure.

## Step 6: Configure Gmail Watcher

Edit `.env` file with Gmail settings:

```bash
# Gmail OAuth
GMAIL_CLIENT_ID=your_client_id_from_credentials.json
GMAIL_CLIENT_SECRET=your_client_secret_from_credentials.json
GMAIL_REDIRECT_URI=http://localhost:8080
```

## Step 7: Run Gmail Watcher

```bash
# Basic usage
python scripts\gmail_watcher.py --credentials credentials.json

# With custom interval (check every 60 seconds)
python scripts\gmail_watcher.py --credentials credentials.json --interval 60

# With custom vault path
python scripts\gmail_watcher.py --credentials credentials.json --vault AI_Employee_Vault
```

## How It Works

1. **Watcher polls Gmail** every 120 seconds (default)
2. **Detects new unread emails**
3. **Creates action files** in `Needs_Action/` folder
4. **Orchestrator processes** action files
5. **Qwen Code creates plans** and responses
6. **Approval workflow** for sensitive actions

## Action File Format

When Gmail watcher detects an email, it creates:

```markdown
---
type: email
from: sender@example.com
subject: Invoice Request
received: 2026-02-26T00:00:00
priority: high
status: pending
gmail_id: abc123
---

# Email Received

## Header Information
- **From:** sender@example.com
- **Subject:** Invoice Request

## Email Content
[Email body here]

## Suggested Actions
- [ ] Read full email
- [ ] Draft reply
- [ ] Check if approval required
```

## Troubleshooting

### Error: credentials.json not found

**Solution:** Ensure `credentials.json` is in the project root:
```
D:\GIAIC\Personal-AI-Empoloy-FTES\credentials.json
```

### Error: Gmail API not enabled

**Solution:** 
1. Go to Google Cloud Console
2. Enable Gmail API for your project

### Error: OAuth consent screen not configured

**Solution:**
1. Complete OAuth consent screen setup
2. Add your email as a test user

### Watcher not detecting emails

**Solutions:**
1. Check token file exists: `.gmail_token.json`
2. Delete token and re-authenticate
3. Check Gmail API quota

### Rate Limit Errors

**Solution:** Increase check interval:
```bash
python scripts\gmail_watcher.py --credentials credentials.json --interval 300
```

## Security Notes

1. **Never commit** `credentials.json` to Git
2. **Never commit** `.gmail_token.json` to Git
3. **Rotate credentials** monthly
4. **Use test user mode** during development
5. **Review Gmail API permissions** regularly

## Advanced Configuration

### Filter Specific Emails

Edit `scripts/gmail_watcher.py` to customize the query:

```python
# Only important unread emails
results = self.service.users().messages().list(
    userId='me',
    q='is:unread is:important'
).execute()

# Only from specific sender
results = self.service.users().messages().list(
    userId='me',
    q='is:unread from:client@example.com'
).execute()

# Only with specific subject
results = self.service.users().messages().list(
    userId='me',
    q='is:unread subject:invoice'
).execute()
```

### Add Custom Keywords

Edit `URGENT_KEYWORDS` in `gmail_watcher.py`:

```python
URGENT_KEYWORDS = [
    'urgent', 'asap', 'invoice', 'payment', 'help',
    'deadline', 'emergency', 'important', 'your_custom_keyword'
]
```

## Integration with AI Employee

The Gmail watcher integrates with:

1. **Orchestrator:** Processes action files
2. **Plan Manager:** Creates plans for emails
3. **Approval Manager:** Handles approval requests
4. **Audit Logger:** Logs all email actions

## Next Steps

After Gmail is working:

1. Set up LinkedIn poster
2. Configure scheduled tasks
3. Test end-to-end workflow

---

*AI Employee Silver Tier - Gmail Integration*
