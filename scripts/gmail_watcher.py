"""
Gmail Watcher - Monitors Gmail for new important/unread emails.

This watcher connects to the Gmail API, checks for new messages,
and creates action files in the Needs_Action folder.

Setup Requirements:
1. Create Google Cloud Project
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Download credentials.json to project root

Usage:
    python scripts/gmail_watcher.py --credentials credentials.json

Silver Tier: This is one of the 2+ required watchers.
Brain: Qwen Code processes the created action files.
"""

import os
import sys
import base64
import argparse
from pathlib import Path
from datetime import datetime
from email import message_from_bytes

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from base_watcher import BaseWatcher

# Try to import Google libraries (may not be installed)
try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import client_config
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new important/unread messages.
    
    Creates action files for emails that need attention.
    """
    
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    # Keywords that indicate urgent emails
    URGENT_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 
                       'deadline', 'emergency', 'important']
    
    def __init__(self, vault_path: str, credentials_path: str, 
                 check_interval: int = 120, max_results: int = 10):
        """
        Initialize the Gmail watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to Gmail OAuth credentials JSON
            check_interval: Seconds between checks (default: 120)
            max_results: Maximum emails to fetch per check (default: 10)
        """
        if not GOOGLE_LIBS_AVAILABLE:
            print("ERROR: Google API libraries not installed.")
            print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            sys.exit(1)
        
        super().__init__(vault_path, check_interval)
        
        self.credentials_path = Path(credentials_path)
        self.token_path = self.vault_path / '.gmail_token.json'
        self.max_results = max_results
        
        # Initialize Gmail service
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API using OAuth 2.0."""
        try:
            creds = None
            
            # Load token from previous session
            if self.token_path.exists():
                try:
                    creds = Credentials.from_authorized_user_file(
                        self.token_path, self.SCOPES
                    )
                except Exception as e:
                    self.logger.warning(f'Could not load token: {e}')
                    self.token_path.unlink()
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except RefreshError as e:
                        self.logger.warning(f'Token refresh failed: {e}')
                        creds = None
                
                if not creds:
                    # Interactive OAuth flow (first time only)
                    self.logger.info('Starting OAuth authentication...')
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0, prompt='consent')
                
                # Save token for future use
                self.token_path.write_text(creds.to_json())
                self.logger.info('Authentication successful')
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info('Gmail service initialized')
            
        except FileNotFoundError:
            self.logger.error(f'Credentials file not found: {self.credentials_path}')
            self.logger.error('Download credentials.json from Google Cloud Console')
            self.logger.error('See GMAIL_SETUP.md for setup instructions')
            raise
        except Exception as e:
            self.logger.error(f'Authentication failed: {e}')
            raise
    
    def _decode_message(self, service, user_id: str, msg_id: str) -> dict:
        """
        Decode a Gmail message.
        
        Args:
            service: Gmail API service
            user_id: User ID (usually 'me')
            msg_id: Message ID
            
        Returns:
            Dictionary with message details
        """
        try:
            message = service.users().messages().get(
                userId=user_id, 
                id=msg_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
            
            # Get body
            body = ''
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            body_data = part['body']['data']
                            body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
            elif 'body' in message['payload']:
                if message['payload']['body'].get('data'):
                    body_data = message['payload']['body']['data']
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
            
            return {
                'id': msg_id,
                'from': headers.get('From', 'Unknown'),
                'to': headers.get('To', ''),
                'subject': headers.get('Subject', 'No Subject'),
                'date': headers.get('Date', ''),
                'snippet': message.get('snippet', ''),
                'body': body[:2000],  # Limit body length
                'thread_id': message.get('threadId', '')
            }
            
        except Exception as e:
            self.logger.error(f'Error decoding message {msg_id}: {e}')
            return None
    
    def _is_urgent(self, email: dict) -> bool:
        """Check if email contains urgent keywords."""
        text = f"{email['subject']} {email['snippet']} {email['body']}".lower()
        return any(keyword in text for keyword in self.URGENT_KEYWORDS)
    
    def _get_priority(self, email: dict) -> str:
        """Determine email priority based on content."""
        if self._is_urgent(email):
            return 'high'
        return 'normal'
    
    def check_for_updates(self) -> list:
        """
        Check Gmail for new unread messages.
        
        Returns:
            List of email dictionaries
        """
        if not self.service:
            self.logger.error('Gmail service not initialized')
            return []
        
        try:
            # Fetch unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=self.max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    email = self._decode_message(self.service, 'me', msg['id'])
                    if email:
                        emails.append(email)
                        self.processed_ids.add(msg['id'])
            
            if emails:
                self.logger.info(f'Found {len(emails)} new email(s)')
            
            return emails
            
        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            # Try to re-authenticate on error
            try:
                self._authenticate()
            except:
                pass
            return []
    
    def create_action_file(self, email: dict) -> Path:
        """
        Create a .md action file for the email.
        
        Args:
            email: Email dictionary
            
        Returns:
            Path to created action file
        """
        try:
            # Generate filename from email ID and subject
            safe_subject = "".join(c if c.isalnum() else "_" for c in email['subject'][:30])
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"EMAIL_{safe_subject}_{timestamp}.md"
            filepath = self.needs_action / filename
            
            # Determine priority
            priority = self._get_priority(email)
            
            # Create action file content
            content = f"""---
type: email
from: {email['from']}
to: {email['to']}
subject: {email['subject']}
received: {datetime.now().isoformat()}
email_date: {email['date']}
priority: {priority}
status: pending
gmail_id: {email['id']}
thread_id: {email['thread_id']}
---

# Email Received

## Header Information

- **From:** {email['from']}
- **To:** {email['to']}
- **Subject:** {email['subject']}
- **Date:** {email['date']}
- **Priority:** {priority.upper()}

## Email Content

```
{email['body'] if email['body'] else email['snippet']}
```

## Quick Preview
{email['snippet']}

## Suggested Actions

- [ ] Read full email
- [ ] Draft reply
- [ ] Forward to relevant party
- [ ] Archive after processing
- [ ] Mark as read in Gmail

## Reply Draft

*Draft your reply below:*

---
*Created by GmailWatcher (Silver Tier)*
"""
            
            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f'Created action file for email from: {email["from"]}')
            
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            raise


def main():
    """Main entry point for the Gmail watcher."""
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee Vault')
    parser.add_argument(
        '--vault',
        type=str,
        default=None,
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--credentials',
        type=str,
        required=True,
        help='Path to Gmail OAuth credentials JSON file'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=120,
        help='Check interval in seconds (default: 120)'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=10,
        help='Maximum emails to fetch per check (default: 10)'
    )
    
    args = parser.parse_args()
    
    # Determine vault path
    if args.vault:
        vault_path = Path(args.vault)
    else:
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
    
    # Validate vault path
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Validate credentials path
    if not Path(args.credentials).exists():
        print(f"Error: Credentials file not found: {args.credentials}")
        print("Download credentials.json from Google Cloud Console")
        sys.exit(1)
    
    # Create and run watcher
    watcher = GmailWatcher(
        str(vault_path),
        args.credentials,
        check_interval=args.interval,
        max_results=args.max_results
    )
    watcher.run()


if __name__ == '__main__':
    main()
