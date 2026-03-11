"""
WhatsApp Watcher - Monitors WhatsApp Web for new messages.

This watcher uses Playwright to automate WhatsApp Web, checks for
unread messages containing important keywords, and creates action
files in the Needs_Action folder.

Setup Requirements:
1. Install Playwright: pip install playwright
2. Install browsers: playwright install
3. First run will require QR code scan to authenticate

Usage:
    python scripts/whatsapp_watcher.py

Silver Tier: This is one of the 2+ required watchers.

Note: Be aware of WhatsApp's terms of service when using automation.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from base_watcher import BaseWatcher

# Try to import Playwright
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class WhatsAppWatcher(BaseWatcher):
    """
    Watches WhatsApp Web for new messages with important keywords.
    
    Uses Playwright to automate browser interaction with WhatsApp Web.
    """
    
    # Keywords that indicate important messages
    IMPORTANT_KEYWORDS = [
        'urgent', 'asap', 'invoice', 'payment', 'help',
        'deadline', 'emergency', 'important', 'meeting',
        'call', 'price', 'cost', 'order', 'delivery'
    ]
    
    # WhatsApp Web selectors (may change over time)
    SELECTORS = {
        'chat_list': '[data-testid="chat-list"]',
        'chat': 'div[role="row"]',
        'unread_badge': '[aria-label*="unread"]',
        'message_content': 'span[title]',
        'search_box': '[data-testid="search"]',
    }
    
    def __init__(self, vault_path: str, session_path: str = None,
                 check_interval: int = 60, headless: bool = True):
        """
        Initialize the WhatsApp watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            session_path: Path to store browser session data
            check_interval: Seconds between checks (default: 60)
            headless: Run browser in headless mode (default: True)
        """
        if not PLAYWRIGHT_AVAILABLE:
            print("ERROR: Playwright not installed.")
            print("Install with: pip install playwright && playwright install")
            sys.exit(1)
        
        super().__init__(vault_path, check_interval)
        
        # Session path for persistent login
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = self.vault_path / '.whatsapp_session'
        
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.last_check_time = datetime.now()
    
    def _init_browser(self):
        """Initialize Playwright browser with persistent context."""
        playwright = sync_playwright().start()
        
        # Launch browser with persistent context (saves login session)
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.session_path),
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        return playwright, browser
    
    def _is_logged_in(self, page) -> bool:
        """Check if WhatsApp Web is logged in."""
        try:
            # Look for chat list (indicates logged in)
            page.wait_for_selector(self.SELECTORS['chat_list'], timeout=5000)
            return True
        except PlaywrightTimeout:
            return False
    
    def _get_unread_chats(self, page) -> list:
        """Get list of chats with unread messages."""
        try:
            chats = []
            
            # Find all chat elements
            chat_elements = page.query_selector_all(self.SELECTORS['chat'])
            
            for chat in chat_elements:
                try:
                    # Check for unread indicator
                    unread = chat.query_selector('[aria-label*="unread"]')
                    if unread:
                        # Extract chat info
                        name_elem = chat.query_selector('span[title]')
                        if name_elem:
                            name = name_elem.get_attribute('title')
                            
                            # Get last message text
                            msg_elem = chat.query_selector('span[dir="auto"]')
                            last_message = ''
                            if msg_elem:
                                last_message = msg_elem.inner_text()
                            
                            chats.append({
                                'name': name,
                                'last_message': last_message,
                                'element': chat
                            })
                except Exception as e:
                    self.logger.debug(f'Error processing chat: {e}')
                    continue
            
            return chats
            
        except Exception as e:
            self.logger.error(f'Error getting unread chats: {e}')
            return []
    
    def _contains_important_keyword(self, text: str) -> bool:
        """Check if text contains important keywords."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.IMPORTANT_KEYWORDS)
    
    def check_for_updates(self) -> list:
        """
        Check WhatsApp Web for new important messages.
        
        Returns:
            List of message dictionaries
        """
        messages = []
        playwright = None
        browser = None
        
        try:
            # Initialize browser
            playwright, browser = self._init_browser()
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Navigate to WhatsApp Web
            self.logger.info('Navigating to WhatsApp Web...')
            page.goto('https://web.whatsapp.com', wait_until='networkidle')
            
            # Wait for page to load
            try:
                page.wait_for_selector(self.SELECTORS['chat_list'], timeout=30000)
            except PlaywrightTimeout:
                self.logger.warning('WhatsApp Web did not load within 30 seconds')
                self.logger.warning('Please scan QR code if this is first run')
                # Wait additional time for QR scan
                try:
                    page.wait_for_selector(self.SELECTORS['chat_list'], timeout=60000)
                except PlaywrightTimeout:
                    self.logger.error('WhatsApp Web login failed')
                    return []
            
            # Check if logged in
            if not self._is_logged_in(page):
                self.logger.error('Not logged in to WhatsApp Web')
                self.logger.info('Please scan QR code to authenticate')
                return []
            
            self.logger.info('WhatsApp Web loaded successfully')
            
            # Get unread chats
            unread_chats = self._get_unread_chats(page)
            self.logger.info(f'Found {len(unread_chats)} unread chat(s)')
            
            # Filter for important messages
            for chat in unread_chats:
                message_text = chat['last_message']
                
                if self._contains_important_keyword(message_text):
                    messages.append({
                        'from': chat['name'],
                        'message': message_text,
                        'timestamp': datetime.now().isoformat(),
                        'type': 'whatsapp'
                    })
                    self.logger.info(f'Important message from: {chat["name"]}')
            
            # Close browser (keep session for next run)
            browser.close()
            playwright.stop()
            
            return messages
            
        except Exception as e:
            self.logger.error(f'Error checking WhatsApp: {e}')
            if browser:
                try:
                    browser.close()
                except:
                    pass
            if playwright:
                playwright.stop()
            return []
    
    def create_action_file(self, message: dict) -> Path:
        """
        Create a .md action file for the WhatsApp message.
        
        Args:
            message: Message dictionary
            
        Returns:
            Path to created action file
        """
        try:
            # Generate filename
            safe_name = "".join(c if c.isalnum() else "_" for c in message['from'][:20])
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"WHATSAPP_{safe_name}_{timestamp}.md"
            filepath = self.needs_action / filename
            
            # Create action file content
            content = f"""---
type: whatsapp
from: {message['from']}
received: {message['timestamp']}
priority: high
status: pending
keywords_detected: true
---

# WhatsApp Message Received

## Message Details

- **From:** {message['from']}
- **Received:** {datetime.fromisoformat(message['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
- **Priority:** HIGH (important keywords detected)

## Message Content

```
{message['message']}
```

## Why This Was Flagged

This message contains one or more important keywords:
{', '.join([k for k in self.IMPORTANT_KEYWORDS if k in message['message'].lower()])}

## Suggested Actions

- [ ] Read full message in WhatsApp
- [ ] Draft reply
- [ ] Respond via WhatsApp
- [ ] Archive after processing

## Reply Draft

*Draft your reply below:*

---
*Created by WhatsAppWatcher (Silver Tier)*
"""
            
            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f'Created action file for WhatsApp from: {message["from"]}')
            
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            raise


def main():
    """Main entry point for the WhatsApp watcher."""
    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee Vault')
    parser.add_argument(
        '--vault',
        type=str,
        default=None,
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--session',
        type=str,
        default=None,
        help='Path to store browser session data'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser with visible window (for first-time QR scan)'
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
    
    # Create and run watcher
    watcher = WhatsAppWatcher(
        str(vault_path),
        session_path=args.session,
        check_interval=args.interval,
        headless=not args.no_headless
    )
    watcher.run()


if __name__ == '__main__':
    main()
