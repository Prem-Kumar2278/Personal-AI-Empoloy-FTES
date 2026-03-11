"""
Orchestrator - Main coordinator for AI Employee.

Silver Tier Features:
- Creates Plan.md files for Qwen Code reasoning
- Integrates with Approval Manager for HITL workflow
- Enhanced audit logging
- Processes approved actions

Brain: Qwen Code (instead of Claude Code)

Usage:
    python orchestrator.py --vault /path/to/vault

For Silver Tier: Schedule via Task Scheduler for automatic processing
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List

# Import Silver Tier modules
try:
    from plan_manager import PlanManager
    from approval_manager import ApprovalManager
    from audit_logger import AuditLogger
    SILVER_TIER_AVAILABLE = True
except ImportError:
    SILVER_TIER_AVAILABLE = False
    print("Note: Silver Tier modules not available. Running in Bronze Tier mode.")


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    
    Coordinates between watchers, Claude Code, and the vault.
    """
    
    def __init__(self, vault_path: str, claude_command: str = "claude"):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault
            claude_command: Command to run Claude Code (default: "claude")
        """
        self.vault_path = Path(vault_path)
        self.claude_command = claude_command
        
        # Vault folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.logs_dir = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.handbook = self.vault_path / 'Company_Handbook.md'
        
        # Ensure directories exist
        for folder in [self.needs_action, self.done, self.plans, self.logs_dir]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize Silver Tier managers
        if SILVER_TIER_AVAILABLE:
            self.plan_manager = PlanManager(str(vault_path))
            self.approval_manager = ApprovalManager(str(vault_path))
            self.audit_logger = AuditLogger(str(vault_path))
        else:
            self.plan_manager = None
            self.approval_manager = None
            self.audit_logger = None
        
        # Track processed items
        self.processed_today = 0
    
    def _setup_logging(self):
        """Setup logging."""
        import logging
        log_file = self.logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Orchestrator')
    
    def get_pending_items(self) -> List[Path]:
        """
        Get all pending .md files in Needs_Action folder.
        
        Returns:
            List of Path objects for pending files
        """
        if not self.needs_action.exists():
            return []
        
        pending = []
        for filepath in self.needs_action.iterdir():
            if filepath.is_file() and filepath.suffix == '.md':
                # Check if file has pending status
                content = filepath.read_text(encoding='utf-8')
                if 'status: pending' in content.lower() or 'status: new' in content.lower():
                    pending.append(filepath)
        
        return pending
    
    def process_with_claude(self, item_path: Path) -> bool:
        """
        Process a single item using Claude Code.
        
        Args:
            item_path: Path to the action file
            
        Returns:
            True if processing succeeded, False otherwise
        """
        self.logger.info(f'Processing: {item_path.name}')
        
        # Silver Tier: Create plan for this item
        if self.plan_manager:
            plan_path = self.plan_manager.create_plan_from_action(
                item_path,
                objective=f"Process: {item_path.stem}"
            )
            self.logger.info(f'Created plan: {plan_path.name}')
        
        # Read the action file
        action_content = item_path.read_text(encoding='utf-8')
        
        # Create prompt for Claude
        prompt = f"""You are processing a task from the AI Employee vault.

**Action File:** {item_path.name}

**Content:**
{action_content}

**Your Task:**
1. Read the Company_Handbook.md for rules and guidelines
2. Analyze the action file and determine what needs to be done
3. Create or update a plan file in /Plans/
4. If the task requires human approval, create a file in /Pending_Approval/
5. If the task can be completed autonomously, do so and move to /Done/
6. Update Dashboard.md with the activity

**Important Rules:**
- Follow the Company_Handbook.md rules
- Flag payments over $100 for approval
- Flag unknown contacts for human review
- Log all actions
- Move completed items to /Done folder

Start by reading the Company_Handbook.md, then process this item."""

        try:
            self.logger.info(f'Claude processing: {item_path.name}')
            
            # For Silver Tier: Create a claude prompt file
            prompt_file = self.vault_path / f'.claude_prompt_{item_path.stem}.txt'
            prompt_file.write_text(prompt, encoding='utf-8')
            
            self.logger.info(f'Created Claude prompt file: {prompt_file.name}')
            self.logger.info(f'Run: claude "{prompt[:100]}..."')
            
            # Silver Tier: Log the action
            if self.audit_logger:
                self.audit_logger.log(
                    action_type='orchestrate',
                    result='success',
                    actor='orchestrator',
                    target=item_path.name,
                    approval_status='none'
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f'Error processing with Claude: {e}')
            return False
    
    def update_dashboard(self, action: str, details: str):
        """
        Update the Dashboard.md with recent activity.
        
        Args:
            action: Type of action (e.g., "Processed", "Created", "Moved")
            details: Details of the action
        """
        if not self.dashboard.exists():
            self.logger.warning('Dashboard.md not found')
            return
        
        content = self.dashboard.read_text(encoding='utf-8')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Add to recent activity section
        activity_line = f"- [{timestamp}] {action}: {details}"
        
        # Find the "Recent Activity" section and add the line
        if '## Recent Activity' in content:
            lines = content.split('\n')
            new_lines = []
            for i, line in enumerate(lines):
                new_lines.append(line)
                if line == '## Recent Activity':
                    # Check if next line is empty or start of list
                    if i + 1 < len(lines) and (lines[i + 1].strip() == '' or lines[i + 1].startswith('*No')):
                        new_lines.append('')
                        new_lines.append(activity_line)
                    else:
                        new_lines.insert(i + 1, activity_line)
                        break
            
            content = '\n'.join(new_lines)
        else:
            # Add Recent Activity section if it doesn't exist
            content = content.replace(
                '# AI Employee Dashboard',
                '# AI Employee Dashboard\n\n## Recent Activity\n\n' + activity_line
            )
        
        # Update last_updated timestamp
        content = content.replace(
            'last_updated:',
            f'last_updated: {datetime.now().isoformat()}\n_old_timestamp:'
        )
        content = content.replace('_old_timestamp: ', '_old_timestamp_removed: ')
        
        self.dashboard.write_text(content, encoding='utf-8')
        self.logger.info('Dashboard updated')
    
    def move_to_done(self, item_path: Path):
        """
        Move a completed item to the Done folder.
        
        Args:
            item_path: Path to the item file
        """
        try:
            dest = self.done / item_path.name
            shutil.move(str(item_path), str(dest))
            self.logger.info(f'Moved to Done: {item_path.name}')
            self.processed_today += 1
        except Exception as e:
            self.logger.error(f'Error moving to Done: {e}')
    
    def log_action(self, action_type: str, target: str, result: str, details: dict = None):
        """
        Log an action to the audit log.
        
        Args:
            action_type: Type of action
            target: Target of the action
            result: Result (success/failure)
            details: Additional details
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'orchestrator',
            'target': target,
            'result': result,
            'details': details or {}
        }

        log_file = self.logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        # Load existing logs or create new
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
    
    def run_once(self):
        """
        Run one iteration of processing.
        
        Silver Tier: Also processes approved actions.
        """
        self.logger.info('Starting orchestration run')
        
        # Silver Tier: Process approved actions first
        if self.approval_manager:
            self.logger.info('Processing approved actions...')
            self.approval_manager.process_approved_folder()
            self.approval_manager.check_expired_approvals()
        
        pending = self.get_pending_items()
        
        if not pending:
            self.logger.info('No pending items')
            return
        
        self.logger.info(f'Found {len(pending)} pending item(s)')
        
        for item in pending:
            success = self.process_with_claude(item)
            
            if success:
                self.log_action('process', item.name, 'success')
                self.update_dashboard('Processing', item.name)
            else:
                self.log_action('process', item.name, 'failed')
        
        self.logger.info(f'Orchestration complete. Processed {len(pending)} items.')
    
    def run_continuous(self, interval: int = 60):
        """
        Run continuously, checking for pending items.
        
        Args:
            interval: Seconds between checks
        """
        import time
        
        self.logger.info(f'Starting continuous orchestration (interval: {interval}s)')
        
        try:
            while True:
                self.run_once()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument(
        '--vault',
        type=str,
        default=None,
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--claude',
        type=str,
        default='claude',
        help='Claude command (default: claude)'
    )
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run continuously instead of once'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
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
    
    # Create and run orchestrator
    orchestrator = Orchestrator(str(vault_path), claude_command=args.claude)
    
    if args.continuous:
        orchestrator.run_continuous(interval=args.interval)
    else:
        orchestrator.run_once()


if __name__ == '__main__':
    main()
