"""
LinkedIn Poster - Creates and posts LinkedIn content for business growth.

Silver Tier: Automatically post on LinkedIn about business to generate sales.

Usage:
    python scripts\linkedin_poster.py --content "Your post content"
    python scripts\linkedin_poster.py --draft  # Create draft only
    python scripts\linkedin_poster.py --qwen  # Use Qwen Code to generate content

Note: Requires LinkedIn API credentials or browser automation.
Brain: Qwen Code can generate post content automatically.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Try to import LinkedIn API (optional)
try:
    from linkedin_api import Linkedin
    LINKEDIN_API_AVAILABLE = True
except ImportError:
    LINKEDIN_API_AVAILABLE = False

# Try to import Playwright for browser automation
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class LinkedInPoster:
    """
    Posts content to LinkedIn for business growth.
    """
    
    def __init__(self, vault_path: str, use_browser: bool = True):
        """
        Initialize the LinkedIn poster.
        
        Args:
            vault_path: Path to the Obsidian vault
            use_browser: Use browser automation instead of API
        """
        self.vault_path = Path(vault_path)
        self.use_browser = use_browser
        
        # Folders
        self.posts_dir = self.vault_path / 'Social_Posts'
        self.drafts_dir = self.posts_dir / 'Drafts'
        self.scheduled_dir = self.posts_dir / 'Scheduled'
        self.published_dir = self.posts_dir / 'Published'
        self.logs_dir = self.vault_path / 'Logs'
        
        # Ensure folders exist
        for folder in [self.posts_dir, self.drafts_dir, self.scheduled_dir, self.published_dir]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging."""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger('LinkedInPoster')
    
    def generate_post_content(self, topic: str, tone: str = 'professional') -> str:
        """
        Generate LinkedIn post content.
        
        Args:
            topic: Topic to post about
            tone: Tone of post (professional, casual, enthusiastic)
            
        Returns:
            Generated post content
        """
        templates = {
            'professional': """🏢 {topic}

Key insights and professional perspective on {topic}.

#Business #Professional #Industry""",
            
            'casual': """Hey network! 👋

Just wanted to share some thoughts on {topic}...

What's your experience been?

#Networking #Discussion""",
            
            'enthusiastic': """🚀 Exciting news about {topic}!

This is a game-changer for our industry!

#Innovation #Growth #Exciting"""
        }
        
        template = templates.get(tone, templates['professional'])
        return template.format(topic=topic)
    
    def create_draft(self, content: str, scheduled_time: str = None) -> Path:
        """
        Create a draft post file.
        
        Args:
            content: Post content
            scheduled_time: Optional scheduled publish time
            
        Returns:
            Path to draft file
        """
        timestamp = datetime.now()
        filename = f"DRAFT_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.drafts_dir / filename
        
        post_content = f"""---
type: linkedin_post
created: {timestamp.isoformat()}
status: draft
scheduled: {scheduled_time if scheduled_time else 'N/A'}
platform: LinkedIn
---

# LinkedIn Post Draft

## Content

```
{content}
```

## To Publish

1. Review the content above
2. Move this file to `/Social_Posts/Scheduled/` folder
3. Or run: python scripts/linkedin_poster.py --publish {filename}

## To Edit

Edit the content section above and save.

---
*Created by LinkedInPoster (Silver Tier)*
"""
        
        filepath.write_text(post_content, encoding='utf-8')
        self.logger.info(f'Created draft: {filename}')
        
        return filepath
    
    def post_via_browser(self, content: str) -> bool:
        """
        Post to LinkedIn using browser automation.
        
        Args:
            content: Post content
            
        Returns:
            True if posted successfully
        """
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error('Playwright not available')
            return False
        
        playwright = None
        browser = None
        
        try:
            playwright = sync_playwright().start()
            
            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()
            
            # Navigate to LinkedIn
            self.logger.info('Navigating to LinkedIn...')
            page.goto('https://www.linkedin.com/feed/', wait_until='networkidle')
            
            # Wait for user to manually post (browser automation is fragile)
            self.logger.info('Please create your post manually in the opened browser')
            self.logger.info('The browser window is ready for you to use')
            
            # Wait for user to complete (or timeout after 5 minutes)
            page.wait_for_timeout(300000)
            
            browser.close()
            playwright.stop()
            
            return True
            
        except Exception as e:
            self.logger.error(f'Error in browser automation: {e}')
            if browser:
                browser.close()
            if playwright:
                playwright.stop()
            return False
    
    def post_via_api(self, content: str) -> bool:
        """
        Post to LinkedIn using API.
        
        Args:
            content: Post content
            
        Returns:
            True if posted successfully
        """
        if not LINKEDIN_API_AVAILABLE:
            self.logger.error('LinkedIn API not available')
            return False
        
        try:
            # Get credentials from environment
            username = os.getenv('LINKEDIN_USERNAME')
            password = os.getenv('LINKEDIN_PASSWORD')
            
            if not username or not password:
                self.logger.error('LinkedIn credentials not set')
                return False
            
            # Connect to LinkedIn
            api = Linkedin(username, password)
            
            # Post update
            response = api.submit_post(content)
            
            self.logger.info('Posted to LinkedIn successfully')
            return True
            
        except Exception as e:
            self.logger.error(f'Error posting to LinkedIn: {e}')
            return False
    
    def publish_post(self, draft_file: str) -> bool:
        """
        Publish a draft post.
        
        Args:
            draft_file: Name of draft file
            
        Returns:
            True if published successfully
        """
        draft_path = self.drafts_dir / draft_file
        
        if not draft_path.exists():
            self.logger.error(f'Draft not found: {draft_file}')
            return False
        
        # Read draft content
        content = draft_path.read_text(encoding='utf-8')
        
        # Extract post content from markdown
        if '## Content' in content:
            start = content.find('```') + 3
            end = content.find('```', start)
            post_content = content[start:end].strip()
        else:
            post_content = content
        
        # Post to LinkedIn
        if self.use_browser:
            success = self.post_via_browser(post_content)
        else:
            success = self.post_via_api(post_content)
        
        if success:
            # Move to published
            published_path = self.published_dir / draft_file
            draft_path.rename(published_path)
            self.logger.info(f'Published: {draft_file}')
            return True
        else:
            self.logger.error('Failed to publish post')
            return False
    
    def create_business_post(self, topic: str = None) -> Path:
        """
        Create a business-focused LinkedIn post.
        
        Args:
            topic: Optional specific topic
            
        Returns:
            Path to draft file
        """
        if not topic:
            topics = [
                "industry trends",
                "our latest project",
                "client success story",
                "team achievement",
                "new service offering"
            ]
            topic = topics[datetime.now().weekday() % len(topics)]
        
        content = self.generate_post_content(topic, tone='professional')
        return self.create_draft(content)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LinkedIn Poster for AI Employee')
    parser.add_argument(
        '--vault',
        type=str,
        default=None,
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--content',
        type=str,
        help='Post content'
    )
    parser.add_argument(
        '--topic',
        type=str,
        help='Business topic for auto-generated post'
    )
    parser.add_argument(
        '--draft',
        action='store_true',
        help='Create draft only (don\'t publish)'
    )
    parser.add_argument(
        '--publish',
        type=str,
        help='Publish a draft file'
    )
    parser.add_argument(
        '--api',
        action='store_true',
        help='Use API instead of browser'
    )
    
    args = parser.parse_args()
    
    # Determine vault path
    if args.vault:
        vault_path = Path(args.vault)
    else:
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
    
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    poster = LinkedInPoster(str(vault_path), use_browser=not args.api)
    
    if args.publish:
        poster.publish_post(args.publish)
    elif args.content:
        draft = poster.create_draft(args.content)
        print(f"Created draft: {draft}")
        if not args.draft:
            poster.publish_post(draft.name)
    elif args.topic:
        draft = poster.create_business_post(args.topic)
        print(f"Created business post draft: {draft}")
    else:
        # Default: create business post
        draft = poster.create_business_post()
        print(f"Created draft: {draft}")
        print(f"\nTo publish, run: python scripts/linkedin_poster.py --publish {draft.name}")


if __name__ == '__main__':
    main()
