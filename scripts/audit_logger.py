"""
Enhanced Audit Logger - Comprehensive logging for AI Employee actions.

Silver Tier: Required for comprehensive audit logging.

Logs all actions in JSON format with approval status, timestamps,
and actor information.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class AuditLogger:
    """
    Comprehensive audit logging for AI Employee.
    """
    
    # Log retention days
    RETENTION_DAYS = 90
    
    # Required log fields
    REQUIRED_FIELDS = [
        'timestamp',
        'action_type',
        'actor',
        'result'
    ]
    
    def __init__(self, vault_path: str):
        """
        Initialize the audit logger.
        
        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs'
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def log(self, action_type: str, result: str, actor: str = 'system',
            target: str = None, parameters: Dict = None,
            approval_status: str = None, approved_by: str = None,
            extra: Dict = None) -> str:
        """
        Log an action.
        
        Args:
            action_type: Type of action (email_send, payment, etc.)
            result: Result (success, failed, pending)
            actor: Who/what performed the action
            target: Target of the action
            parameters: Action parameters
            approval_status: none, auto_approved, human_approved, rejected
            approved_by: Who approved (if applicable)
            extra: Additional data
            
        Returns:
            Log entry ID
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': actor,
            'target': target,
            'result': result,
            'parameters': parameters or {},
            'approval_status': approval_status or 'none',
            'approved_by': approved_by,
            'extra': extra or {}
        }
        
        # Get today's log file
        log_file = self._get_log_file()
        
        # Load existing logs
        logs = self._load_logs(log_file)
        
        # Add entry
        logs.append(entry)
        
        # Save logs
        self._save_logs(log_file, logs)
        
        return entry['timestamp']
    
    def _get_log_file(self) -> Path:
        """Get today's log file path."""
        return self.logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    
    def _load_logs(self, log_file: Path) -> list:
        """Load logs from file."""
        if not log_file.exists():
            return []
        
        try:
            content = log_file.read_text(encoding='utf-8')
            if content.strip():
                return json.loads(content)
            return []
        except Exception as e:
            print(f"Error loading logs: {e}")
            return []
    
    def _save_logs(self, log_file: Path, logs: list):
        """Save logs to file."""
        try:
            log_file.write_text(json.dumps(logs, indent=2, default=str), encoding='utf-8')
        except Exception as e:
            print(f"Error saving logs: {e}")
    
    def query(self, action_type: str = None, actor: str = None,
              date: str = None, approval_status: str = None) -> list:
        """
        Query logs.
        
        Args:
            action_type: Filter by action type
            actor: Filter by actor
            date: Filter by date (YYYY-MM-DD)
            approval_status: Filter by approval status
            
        Returns:
            List of matching log entries
        """
        if date:
            log_file = self.logs_dir / f"{date}.json"
        else:
            log_file = self._get_log_file()
        
        logs = self._load_logs(log_file)
        
        # Filter
        results = []
        for entry in logs:
            if action_type and entry.get('action_type') != action_type:
                continue
            if actor and entry.get('actor') != actor:
                continue
            if approval_status and entry.get('approval_status') != approval_status:
                continue
            results.append(entry)
        
        return results
    
    def get_summary(self, date: str = None) -> Dict:
        """
        Get summary of logs for a date.
        
        Args:
            date: Date (YYYY-MM-DD), default today
            
        Returns:
            Summary dictionary
        """
        if date:
            log_file = self.logs_dir / f"{date}.json"
        else:
            log_file = self._get_log_file()
        
        logs = self._load_logs(log_file)
        
        summary = {
            'date': date or datetime.now().strftime('%Y-%m-%d'),
            'total_actions': len(logs),
            'by_type': {},
            'by_result': {},
            'by_approval': {},
            'by_actor': {}
        }
        
        for entry in logs:
            # Count by type
            action_type = entry.get('action_type', 'unknown')
            summary['by_type'][action_type] = summary['by_type'].get(action_type, 0) + 1
            
            # Count by result
            result = entry.get('result', 'unknown')
            summary['by_result'][result] = summary['by_result'].get(result, 0) + 1
            
            # Count by approval status
            approval = entry.get('approval_status', 'unknown')
            summary['by_approval'][approval] = summary['by_approval'].get(approval, 0) + 1
            
            # Count by actor
            actor = entry.get('actor', 'unknown')
            summary['by_actor'][actor] = summary['by_actor'].get(actor, 0) + 1
        
        return summary
    
    def cleanup_old_logs(self):
        """Remove logs older than RETENTION_DAYS."""
        cutoff = datetime.now().timestamp() - (self.RETENTION_DAYS * 24 * 60 * 60)
        
        for log_file in self.logs_dir.glob('*.json'):
            try:
                mtime = log_file.stat().st_mtime
                if mtime < cutoff:
                    log_file.unlink()
                    print(f"Removed old log: {log_file.name}")
            except Exception as e:
                print(f"Error processing {log_file}: {e}")
    
    def export_logs(self, output_path: str, start_date: str = None,
                    end_date: str = None):
        """
        Export logs to a file.
        
        Args:
            output_path: Output file path
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        """
        all_logs = []
        
        # Collect logs from date range
        if start_date and end_date:
            from datetime import timedelta
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            current = start
            
            while current <= end:
                log_file = self.logs_dir / f"{current.strftime('%Y-%m-%d')}.json"
                if log_file.exists():
                    all_logs.extend(self._load_logs(log_file))
                current += timedelta(days=1)
        else:
            # Get all logs
            for log_file in self.logs_dir.glob('*.json'):
                all_logs.extend(self._load_logs(log_file))
        
        # Write export
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_logs, f, indent=2, default=str)
        
        print(f"Exported {len(all_logs)} log entries to {output_path}")


def main():
    """Demo/test the audit logger."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Audit Logger for AI Employee')
    parser.add_argument(
        '--vault',
        type=str,
        default=None,
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Create demo log entries'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show today\'s summary'
    )
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up old logs'
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
    
    logger = AuditLogger(str(vault_path))
    
    if args.demo:
        # Create demo log entries
        logger.log(
            action_type='email_send',
            result='success',
            actor='claude_code',
            target='client@example.com',
            parameters={'subject': 'Invoice #123'},
            approval_status='auto_approved'
        )
        
        logger.log(
            action_type='payment',
            result='pending',
            actor='claude_code',
            target='vendor@example.com',
            parameters={'amount': 500},
            approval_status='human_approved',
            approved_by='user'
        )
        
        print("Created demo log entries")
    
    if args.summary:
        summary = logger.get_summary()
        print("\nToday's Log Summary:")
        print(json.dumps(summary, indent=2))
    
    if args.cleanup:
        logger.cleanup_old_logs()


if __name__ == '__main__':
    main()
