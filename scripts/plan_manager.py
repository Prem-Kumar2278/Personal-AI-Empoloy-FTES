"""
Plan Manager - Creates and manages Plan.md files for Claude reasoning.

Claude creates structured plans with checkboxes for multi-step tasks.
Plans track progress and link to approval requests when needed.

Silver Tier: Required for Claude reasoning loop.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict


class PlanManager:
    """
    Manages Plan.md files for task tracking.
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize the plan manager.
        
        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.plans_dir = self.vault_path / 'Plans'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.done = self.vault_path / 'Done'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure plans directory exists
        self.plans_dir.mkdir(parents=True, exist_ok=True)
    
    def create_plan(self, objective: str, steps: List[str], 
                    source_file: str = None, metadata: Dict = None) -> Path:
        """
        Create a new Plan.md file.
        
        Args:
            objective: Task objective
            steps: List of step descriptions
            source_file: Source action file name
            metadata: Additional metadata
            
        Returns:
            Path to created plan file
        """
        timestamp = datetime.now()
        
        # Generate filename
        safe_obj = "".join(c if c.isalnum() else "_" for c in objective[:30])
        filename = f"PLAN_{safe_obj}_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.plans_dir / filename
        
        # Format steps as checkboxes
        steps_text = '\n'.join([f"- [ ] {step}" for step in steps])
        
        # Build metadata
        meta_lines = []
        if metadata:
            for key, value in metadata.items():
                meta_lines.append(f"{key}: {value}")
        
        content = f"""---
created: {timestamp.isoformat()}
status: in_progress
objective: {objective}
source_file: {source_file if source_file else 'N/A'}
{chr(10).join(meta_lines)}
---

# Task Plan

## Objective

{objective}

## Steps

{steps_text}

## Progress

*Steps will be checked off as completed*

## Related Files

{f"- Source: `{source_file}`" if source_file else "- No source file"}

## Approval Requests

*Approval requests will be linked here if required*

## Notes

*Add notes during execution:*

---
*Created by PlanManager (Silver Tier)*
"""
        
        filepath.write_text(content, encoding='utf-8')
        return filepath
    
    def update_plan_status(self, plan_path: Path, status: str,
                           completed_steps: List[int] = None) -> bool:
        """
        Update plan status and completed steps.
        
        Args:
            plan_path: Path to plan file
            status: New status (in_progress, completed, blocked)
            completed_steps: List of step indices (0-based) to mark complete
            
        Returns:
            True if updated successfully
        """
        try:
            content = plan_path.read_text(encoding='utf-8')
            
            # Update status in frontmatter
            content = content.replace('status: in_progress', f'status: {status}')
            
            # Update completed steps
            if completed_steps:
                lines = content.split('\n')
                step_idx = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('- [ ]'):
                        if step_idx in completed_steps:
                            lines[i] = line.replace('- [ ]', '- [x]')
                        step_idx += 1
                content = '\n'.join(lines)
            
            plan_path.write_text(content, encoding='utf-8')
            return True
            
        except Exception as e:
            print(f"Error updating plan: {e}")
            return False
    
    def link_approval_request(self, plan_path: Path, approval_file: str) -> bool:
        """
        Link an approval request to a plan.
        
        Args:
            plan_path: Path to plan file
            approval_file: Name of approval request file
            
        Returns:
            True if linked successfully
        """
        try:
            content = plan_path.read_text(encoding='utf-8')
            
            # Find Approval Requests section and add link
            if '## Approval Requests' in content:
                approval_link = f"- [{approval_file}](../Pending_Approval/{approval_file})"
                content = content.replace(
                    '## Approval Requests\n\n*Approval requests will be linked here if required*',
                    f'## Approval Requests\n\n{approval_link}'
                )
            
            plan_path.write_text(content, encoding='utf-8')
            return True
            
        except Exception as e:
            print(f"Error linking approval: {e}")
            return False
    
    def get_plan_for_source(self, source_file: str) -> Optional[Path]:
        """
        Find plan file for a source action file.
        
        Args:
            source_file: Source action file name
            
        Returns:
            Path to plan file or None
        """
        if not self.plans_dir.exists():
            return None
        
        for plan_file in self.plans_dir.glob('*.md'):
            content = plan_file.read_text(encoding='utf-8')
            if f'source_file: {source_file}' in content:
                return plan_file
        
        return None
    
    def get_active_plans(self) -> List[Path]:
        """
        Get all active (in_progress) plans.
        
        Returns:
            List of plan file paths
        """
        active = []
        
        if not self.plans_dir.exists():
            return []
        
        for plan_file in self.plans_dir.glob('*.md'):
            content = plan_file.read_text(encoding='utf-8')
            if 'status: in_progress' in content:
                active.append(plan_file)
        
        return active
    
    def complete_plan(self, plan_path: Path, result: str = None) -> bool:
        """
        Mark a plan as completed.
        
        Args:
            plan_path: Path to plan file
            result: Result summary
            
        Returns:
            True if completed successfully
        """
        try:
            content = plan_path.read_text(encoding='utf-8')
            
            # Update status
            content = content.replace('status: in_progress', 'status: completed')
            
            # Add result if provided
            if result:
                if '## Notes' in content:
                    content = content.replace(
                        '## Notes\n\n*Add notes during execution:*',
                        f'## Notes\n\n**Result:** {result}\n\n*Execution complete*\n'
                    )
            
            # Move to Done folder
            dest = self.done / plan_path.name
            import shutil
            shutil.move(str(plan_path), str(dest))
            
            return True
            
        except Exception as e:
            print(f"Error completing plan: {e}")
            return False
    
    def create_plan_from_action(self, action_path: Path, 
                                objective: str = None) -> Path:
        """
        Create a plan based on an action file.
        
        Args:
            action_path: Path to action file
            objective: Optional objective override
            
        Returns:
            Path to created plan file
        """
        content = action_path.read_text(encoding='utf-8')
        
        # Parse action file
        frontmatter = {}
        if content.startswith('---'):
            end_idx = content.find('---', 3)
            if end_idx != -1:
                fm_content = content[4:end_idx]
                for line in fm_content.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip()
        
        # Determine objective
        if not objective:
            objective = frontmatter.get('type', 'Process task')
            if frontmatter.get('subject'):
                objective = f"Process: {frontmatter['subject']}"
        
        # Generate default steps based on type
        action_type = frontmatter.get('type', 'unknown')
        
        if action_type == 'email':
            steps = [
                "Read email content",
                "Identify sender and intent",
                "Check Company Handbook for rules",
                "Draft response or determine action",
                "Check if approval required",
                "Execute action or request approval",
                "Archive email"
            ]
        elif action_type == 'whatsapp':
            steps = [
                "Read WhatsApp message",
                "Identify sender and keywords",
                "Check Company Handbook for rules",
                "Draft response",
                "Check if approval required",
                "Send response or request approval",
                "Mark as processed"
            ]
        elif action_type == 'file_drop':
            steps = [
                "Read file content",
                "Understand requested task",
                "Check Company Handbook for rules",
                "Create execution plan",
                "Execute or request approval",
                "Move to Done"
            ]
        else:
            steps = [
                "Analyze task requirements",
                "Check Company Handbook for rules",
                "Identify required actions",
                "Check if approval required",
                "Execute actions",
                "Update Dashboard"
            ]
        
        # Create plan
        plan_path = self.create_plan(
            objective=objective,
            steps=steps,
            source_file=action_path.name,
            metadata={
                'action_type': action_type,
                'priority': frontmatter.get('priority', 'normal')
            }
        )
        
        return plan_path


def main():
    """Demo/test the plan manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Plan Manager for Claude Reasoning')
    parser.add_argument(
        '--vault',
        type=str,
        default=None,
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Create demo plan'
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
    
    manager = PlanManager(str(vault_path))
    
    if args.demo:
        # Create demo plan
        plan = manager.create_plan(
            objective="Process client invoice request",
            steps=[
                "Read invoice request details",
                "Verify client information",
                "Calculate invoice amount",
                "Generate invoice PDF",
                "Check if approval required (>$100)",
                "Send invoice or request approval",
                "Log transaction"
            ],
            source_file="demo_test.txt",
            metadata={'demo': True}
        )
        print(f"Created demo plan: {plan}")


if __name__ == '__main__':
    main()
