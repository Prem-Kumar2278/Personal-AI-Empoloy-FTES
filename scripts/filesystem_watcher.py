"""
File System Watcher - Monitors a drop folder for new files.

This is the Bronze Tier watcher - simple, reliable, and doesn't require
external API setup. Users drop files into the Inbox folder and the
watcher creates corresponding action files in Needs_Action.

Usage:
    python filesystem_watcher.py --vault /path/to/vault

Or with default path:
    python filesystem_watcher.py
"""

import os
import sys
import hashlib
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from base_watcher import BaseWatcher


class FileSystemWatcher(BaseWatcher):
    """
    Watches the Inbox folder for new files and creates action files.
    
    Supported file types:
    - Text files (.txt, .md)
    - Documents (.pdf, .docx - metadata only)
    - Any file (creates metadata .md file)
    """
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        self.processed_files = set()
        
        # Load previously processed files from state file
        self._load_state()
    
    def _load_state(self):
        """Load state from file to remember processed files across restarts."""
        state_file = self.vault_path / '.filesystem_watcher_state'
        if state_file.exists():
            try:
                self.processed_files = set(state_file.read_text().splitlines())
                self.logger.info(f'Loaded {len(self.processed_files)} processed file hashes')
            except Exception as e:
                self.logger.warning(f'Could not load state file: {e}')
    
    def _save_state(self):
        """Save current state to file."""
        state_file = self.vault_path / '.filesystem_watcher_state'
        try:
            state_file.write_text('\n'.join(self.processed_files))
        except Exception as e:
            self.logger.warning(f'Could not save state file: {e}')
    
    def _get_file_hash(self, filepath: Path) -> str:
        """
        Generate a unique hash for a file based on path and modification time.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Unique hash string
        """
        try:
            stat = filepath.stat()
            content = f"{filepath.absolute()}:{stat.st_mtime}:{stat.st_size}"
            return hashlib.md5(content.encode()).hexdigest()
        except Exception as e:
            self.logger.error(f'Error hashing file {filepath}: {e}')
            return None
    
    def check_for_updates(self) -> list:
        """
        Check the Inbox folder for new files.
        
        Returns:
            List of Path objects for new files
        """
        new_files = []
        
        if not self.inbox.exists():
            self.logger.warning(f'Inbox folder does not exist: {self.inbox}')
            return []
        
        try:
            # Get all files in inbox (not directories)
            for filepath in self.inbox.iterdir():
                if filepath.is_file() and not filepath.name.startswith('.'):
                    file_hash = self._get_file_hash(filepath)
                    
                    if file_hash and file_hash not in self.processed_files:
                        new_files.append(filepath)
                        self.processed_files.add(file_hash)
            
            # Save state after finding new files
            if new_files:
                self._save_state()
                
        except Exception as e:
            self.logger.error(f'Error checking inbox: {e}')
        
        return new_files
    
    def create_action_file(self, filepath: Path) -> Path:
        """
        Create a .md action file for the dropped file.
        
        Args:
            filepath: Path to the dropped file
            
        Returns:
            Path to created action file
        """
        try:
            stat = filepath.stat()
            file_size = stat.st_size
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            # Try to read content if it's a text file
            content_preview = ""
            is_text_file = filepath.suffix.lower() in ['.txt', '.md', '.log', '.csv']
            
            if is_text_file:
                try:
                    text_content = filepath.read_text(encoding='utf-8', errors='ignore')
                    # Take first 500 chars as preview
                    content_preview = text_content[:500].strip()
                    if len(text_content) > 500:
                        content_preview += "\n\n... (truncated)"
                except Exception as e:
                    content_preview = f"Could not read file content: {e}"
            
            # Generate action file name
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            action_filename = f"FILE_{filepath.stem}_{timestamp}.md"
            action_path = self.needs_action / action_filename
            
            # Create action file content
            action_content = f"""---
type: file_drop
original_name: {filepath.name}
original_path: {filepath.absolute()}
size: {file_size}
received: {datetime.now().isoformat()}
modified: {modified_time.isoformat()}
status: pending
priority: normal
---

# File Dropped for Processing

## File Details

- **Original Name:** {filepath.name}
- **Size:** {self._format_size(file_size)}
- **Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Content Preview

```
{content_preview if content_preview else "(Binary file or could not read)"}
```

## Suggested Actions

- [ ] Review file content
- [ ] Process and take action
- [ ] Move to appropriate folder
- [ ] Archive after processing

## Notes

*Add any notes about processing this file below:*

---
*Created by FileSystemWatcher (Bronze Tier)*
"""
            
            action_path.write_text(action_content, encoding='utf-8')
            self.logger.info(f'Created action file for: {filepath.name}')
            
            return action_path
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            raise
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


def main():
    """Main entry point for the file system watcher."""
    parser = argparse.ArgumentParser(
        description='File System Watcher for AI Employee Vault'
    )
    parser.add_argument(
        '--vault',
        type=str,
        default=None,
        help='Path to the Obsidian vault (default: AI_Employee_Vault in project root)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Check interval in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Determine vault path
    if args.vault:
        vault_path = Path(args.vault)
    else:
        # Default to AI_Employee_Vault in project root
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
    
    # Validate vault path
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        print("Please create the vault or specify --vault path")
        sys.exit(1)
    
    # Create and run watcher
    watcher = FileSystemWatcher(str(vault_path), check_interval=args.interval)
    watcher.run()


if __name__ == '__main__':
    main()
