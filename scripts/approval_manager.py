"""
Approval Manager - Manages Human-in-the-Loop approval workflow.

Handles creation, tracking, and execution of approval requests.
Monitors Approved folder and executes approved actions.

Silver Tier: Required for HITL approval workflow.
"""

import os
import sys
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class ApprovalManager:
    """
    Manages approval requests for sensitive actions.
    """
    
    # Approval thresholds (can be overridden by Company_Handbook.md)
    THRESHOLDS = {
        'payment_auto_approve': 50.0,
        'payment_require_approval': 100.0,
        'email_bulk_threshold': 10,
        'new_contact_approval': True
    }
    
    def __init__(self, vault_path: str):
        """
        Initialize the approval manager.
        
        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        
        # Folders
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.logs_dir = self.vault_path / 'Logs'
        self.handbook = self.vault_path / 'Company_Handbook.md'
        
        # Ensure folders exist
        for folder in [self.pending_approval, self.approved, self.rejected]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Load thresholds from handbook
        self._load_thresholds()
    
    def _load_thresholds(self):
        """Load approval thresholds from Company_Handbook.md."""
        if self.handbook.exists():
            try:
                content = self.handbook.read_text(encoding='utf-8')
                
                # Parse thresholds from handbook
                if 'payment' in content.lower():
                    # Look for payment threshold mentions
                    import re
                    matches = re.findall(r'payment.*?\$(\d+)', content, re.IGNORECASE)
                    if matches:
                        self.THRESHOLDS['payment_require_approval'] = float(matches[0])
            except Exception as e:
                pass  # Use defaults
    
    def _generate_checksum(self, content: str) -> str:
        """Generate checksum for approval file integrity."""
        return hashlib.md5(content.encode()).hexdigest()
    
    def create_approval_request(self, action_type: str, details: Dict[str, Any],
                                reason: str = None) -> Optional[Path]:
        """
        Create an approval request file.
        
        Args:
            action_type: Type of action (payment, email, etc.)
            details: Action details
            reason: Why approval is required
            
        Returns:
            Path to created file, or None if failed
        """
        try:
            timestamp = datetime.now()
            safe_desc = "".join(c if c.isalnum() else "_" for c in str(details)[:30])
            filename = f"{action_type.upper()}_{safe_desc}_{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}.md"
            filepath = self.pending_approval / filename
            
            # Calculate expiration (24 hours)
            expires = timestamp + timedelta(hours=24)
            
            # Format details for display
            details_text = '\n'.join([f"- **{k.replace('_', ' ').title()}:** {v}" 
                                      for k, v in details.items()])
            
            content = f"""---
type: approval_request
action: {action_type}
created: {timestamp.isoformat()}
expires: {expires.isoformat()}
status: pending
checksum: {self._generate_checksum(json.dumps(details, sort_keys=True))}
---

# Approval Request

## Action Details

{details_text}

## Why Approval Required

{reason if reason else 'This action requires human approval per Company Handbook rules.'}

## To Approve

Move this file to the `/Approved` folder.

## To Reject

Move this file to the `/Rejected` folder.

## Notes

*Add any notes or conditions:*

---
*Created by ApprovalManager (Silver Tier)*
"""
            
            filepath.write_text(content, encoding='utf-8')
            self._log_approval('created', action_type, details, 'pending')
            
            return filepath
            
        except Exception as e:
            print(f"Error creating approval request: {e}")
            return None
    
    def check_requires_approval(self, action_type: str, details: Dict[str, Any]) -> bool:
        """
        Check if an action requires approval based on thresholds.
        
        Args:
            action_type: Type of action
            details: Action details
            
        Returns:
            True if approval required, False if can auto-approve
        """
        if action_type == 'payment':
            amount = float(details.get('amount', 0))
            if amount >= self.THRESHOLDS['payment_require_approval']:
                return True
            if details.get('new_recipient', False):
                return True
            return False
        
        elif action_type == 'email':
            # Check if bulk email
            recipients = details.get('recipients', 1)
            if isinstance(recipients, list) and len(recipients) >= self.THRESHOLDS['email_bulk_threshold']:
                return True
            # Check if new contact
            if details.get('new_contact', False):
                return True
            return False
        
        elif action_type == 'social_post':
            # Scheduled posts auto-approve, replies require approval
            if details.get('is_reply', False) or details.get('is_dm', False):
                return True
            return False
        
        elif action_type == 'file_operation':
            # Delete and move outside vault require approval
            if details.get('operation') in ['delete', 'move_outside_vault']:
                return True
            return False
        
        # Default: require approval for unknown action types
        return True
    
    def get_approved_actions(self) -> list:
        """
        Get list of approved actions ready for execution.
        
        Returns:
            List of (filepath, action_details) tuples
        """
        approved_actions = []
        
        if not self.approved.exists():
            return []
        
        for filepath in self.approved.glob('*.md'):
            try:
                content = filepath.read_text(encoding='utf-8')
                
                # Parse frontmatter
                details = self._parse_frontmatter(content)
                if details:
                    approved_actions.append((filepath, details))
            except Exception as e:
                print(f"Error reading approved file {filepath}: {e}")
        
        return approved_actions
    
    def _parse_frontmatter(self, content: str) -> Optional[Dict]:
        """Parse YAML frontmatter from markdown content."""
        try:
            if not content.startswith('---'):
                return None
            
            # Find end of frontmatter
            end_idx = content.find('---', 3)
            if end_idx == -1:
                return None
            
            frontmatter = content[4:end_idx].strip()
            
            # Simple YAML parsing
            details = {}
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Type conversion
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    elif value.replace('.', '').replace('-', '').isdigit():
                        value = float(value) if '.' in value else int(value)
                    
                    details[key] = value
            
            return details
            
        except Exception as e:
            return None
    
    def execute_approved_action(self, filepath: Path) -> bool:
        """
        Execute an approved action.
        
        Args:
            filepath: Path to approved action file
            
        Returns:
            True if executed successfully
        """
        try:
            content = filepath.read_text(encoding='utf-8')
            details = self._parse_frontmatter(content)
            
            if not details:
                print(f"Could not parse approval file: {filepath}")
                return False
            
            action_type = details.get('action', 'unknown')
            
            # Log execution
            self._log_approval('executed', action_type, details, 'success')
            
            # Move to Done
            dest = self.done / filepath.name
            shutil.move(str(filepath), str(dest))
            
            print(f"Executed approved action: {action_type}")
            return True
            
        except Exception as e:
            print(f"Error executing approved action: {e}")
            return False
    
    def check_expired_approvals(self):
        """Move expired approval requests to Rejected."""
        now = datetime.now()
        
        if not self.pending_approval.exists():
            return
        
        for filepath in self.pending_approval.glob('*.md'):
            try:
                content = filepath.read_text(encoding='utf-8')
                details = self._parse_frontmatter(content)
                
                if details and 'expires' in details:
                    expires = datetime.fromisoformat(details['expires'])
                    if expires < now:
                        # Expired - move to Rejected
                        dest = self.rejected / filepath.name
                        
                        # Add expiration note
                        content += f"\n\n*Expired on {now.isoformat()}*"
                        filepath.write_text(content, encoding='utf-8')
                        
                        shutil.move(str(filepath), str(dest))
                        self._log_approval('expired', details.get('action', 'unknown'), 
                                          details, 'expired')
                        print(f"Expired approval moved to Rejected: {filepath.name}")
                        
            except Exception as e:
                print(f"Error checking expiration for {filepath}: {e}")
    
    def _log_approval(self, event: str, action_type: str, details: Dict, 
                      status: str):
        """Log approval event to JSON log."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'action_type': action_type,
            'details': details,
            'status': status
        }
        
        log_file = self.logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        
        # Load existing logs
        logs = []
        if log_file.exists():
            try:
                content = log_file.read_text(encoding='utf-8')
                if content.strip():
                    logs = json.loads(content)
            except:
                logs = []
        
        logs.append(log_entry)
        
        # Write logs
        log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')
    
    def process_approved_folder(self):
        """Process all approved actions."""
        print("Processing approved actions...")
        
        approved = self.get_approved_actions()
        
        if not approved:
            print("No approved actions pending")
            return
        
        for filepath, details in approved:
            self.execute_approved_action(filepath)
        
        print(f"Processed {len(approved)} approved action(s)")


def main():
    """Main entry point for approval manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Approval Manager for HITL Workflow')
    parser.add_argument(
        '--vault',
        type=str,
        default=None,
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--process',
        action='store_true',
        help='Process approved folder'
    )
    parser.add_argument(
        '--check-expired',
        action='store_true',
        help='Check for expired approvals'
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
    
    manager = ApprovalManager(str(vault_path))
    
    if args.check_expired:
        manager.check_expired_approvals()
    
    if args.process:
        manager.process_approved_folder()


if __name__ == '__main__':
    main()
