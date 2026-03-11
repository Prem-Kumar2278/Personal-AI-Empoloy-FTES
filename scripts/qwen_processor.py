"""
Qwen Code Processor - Processes AI Employee tasks using Qwen Code.

This script prepares tasks for Qwen Code and executes Qwen Code to process them.
It's the main integration point between the AI Employee vault and Qwen Code.

Silver Tier: Use this instead of manual Claude Code commands.

Usage:
    python scripts/qwen_processor.py                    # Process all pending
    python scripts/qwen_processor.py --file FILE.md     # Process specific file
    python scripts/qwen_processor.py --prompt "Your prompt"  # Custom prompt
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


class QwenProcessor:
    """
    Processes AI Employee tasks using Qwen Code.
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize the Qwen processor.
        
        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.handbook = self.vault_path / 'Company_Handbook.md'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure plans folder exists
        self.plans.mkdir(parents=True, exist_ok=True)
    
    def get_pending_items(self):
        """Get list of pending action files."""
        if not self.needs_action.exists():
            return []
        
        pending = []
        for filepath in self.needs_action.iterdir():
            if filepath.is_file() and filepath.suffix == '.md':
                content = filepath.read_text(encoding='utf-8')
                if 'status: pending' in content.lower():
                    pending.append(filepath)
        
        return pending
    
    def create_qwen_prompt(self, action_file: Path) -> str:
        """
        Create a prompt for Qwen Code.
        
        Args:
            action_file: Path to action file
            
        Returns:
            Prompt string for Qwen Code
        """
        content = action_file.read_text(encoding='utf-8')
        
        prompt = f"""You are an AI Employee assistant powered by Qwen Code.
Your task is to process items from the AI Employee vault.

**Action File:** {action_file.name}

**Content:**
{content}

**Your Tasks:**
1. Read the Company_Handbook.md for rules and guidelines
2. Analyze the action file and determine what needs to be done
3. Create a plan file in the Plans folder with:
   - Objective
   - Steps (as checkboxes)
   - Status tracking
4. If the task requires human approval:
   - Create a file in Pending_Approval folder
   - Include reason for approval
5. If the task can be completed autonomously:
   - Execute the task
   - Move the action file to Done folder
6. Update Dashboard.md with the activity

**Important Rules from Company Handbook:**
- Flag payments over $100 for approval
- Flag unknown contacts for human review
- Log all actions
- Be polite and professional in all communications

**Output Format:**
1. First, read the Company_Handbook.md
2. Then, create a plan in Plans/
3. Finally, execute the task or request approval

Start processing now."""
        
        return prompt
    
    def process_with_qwen(self, prompt: str, output_file: Path = None):
        """
        Process a prompt using Qwen Code.
        
        Args:
            prompt: Prompt to send to Qwen Code
            output_file: Optional file to save output
        """
        print("=" * 60)
        print("Processing with Qwen Code...")
        print("=" * 60)
        
        # Method 1: Try qwen CLI if available
        try:
            result = subprocess.run(
                ['qwen', prompt],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            output = result.stdout
            if result.stderr:
                print(f"Qwen stderr: {result.stderr}")
            
            if output_file:
                output_file.write_text(output, encoding='utf-8')
            
            print(output)
            return output
            
        except FileNotFoundError:
            print("Qwen CLI not found. Using alternative methods...")
        except subprocess.TimeoutExpired:
            print("Qwen Code timed out (5 minute limit)")
        except Exception as e:
            print(f"Error running Qwen Code: {e}")
        
        # Method 2: Create prompt file for manual processing
        print("\n" + "=" * 60)
        print("Creating prompt file for manual Qwen Code processing...")
        print("=" * 60)
        
        prompt_file = self.vault_path / f'.qwen_prompt_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        prompt_file.write_text(prompt, encoding='utf-8')
        
        print(f"\nPrompt file created: {prompt_file}")
        print(f"\nTo process with Qwen Code, run:")
        print(f"  qwen < {prompt_file}")
        print(f"\nOr copy the prompt and use the Qwen web interface:")
        print(f"  https://chat.qwen.ai/")
        
        return None
    
    def create_plan_template(self, action_file: Path, objective: str) -> Path:
        """
        Create a plan template for Qwen Code to fill in.
        
        Args:
            action_file: Path to action file
            objective: Plan objective
            
        Returns:
            Path to created plan file
        """
        timestamp = datetime.now()
        safe_obj = "".join(c if c.isalnum() else "_" for c in objective[:30])
        filename = f"PLAN_{safe_obj}_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        plan_path = self.plans / filename
        
        content = f"""---
created: {timestamp.isoformat()}
status: in_progress
objective: {objective}
source_file: {action_file.name}
processed_by: qwen_code
---

# Task Plan

## Objective

{objective}

## Steps

*Qwen Code will create steps here*

## Progress

*Steps will be checked off as completed*

## Related Files

- Source: `{action_file.name}`

## Approval Requests

*Approval requests will be linked here if required*

## Notes

*Add notes during execution:*

---
*Created by QwenProcessor (Silver Tier)*
*Brain: Qwen Code*
"""
        
        plan_path.write_text(content, encoding='utf-8')
        return plan_path
    
    def process_all_pending(self):
        """Process all pending action files."""
        print("Getting pending items...")
        pending = self.get_pending_items()
        
        if not pending:
            print("No pending items to process.")
            return
        
        print(f"Found {len(pending)} pending item(s)")
        
        for item in pending:
            print(f"\n{'='*60}")
            print(f"Processing: {item.name}")
            print(f"{'='*60}")
            
            # Create plan template
            plan_path = self.create_plan_template(
                item,
                objective=f"Process: {item.stem}"
            )
            print(f"Created plan: {plan_path.name}")
            
            # Create Qwen prompt
            prompt = self.create_qwen_prompt(item)
            
            # Process with Qwen Code
            self.process_with_qwen(prompt)
    
    def process_custom_prompt(self, prompt: str):
        """Process a custom prompt."""
        self.process_with_qwen(prompt)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Qwen Code Processor for AI Employee')
    parser.add_argument(
        '--vault',
        type=str,
        default=None,
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Process specific action file'
    )
    parser.add_argument(
        '--prompt',
        type=str,
        help='Custom prompt for Qwen Code'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Auto-process all pending items'
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
    
    processor = QwenProcessor(str(vault_path))
    
    if args.prompt:
        processor.process_custom_prompt(args.prompt)
    elif args.file:
        file_path = processor.needs_action / args.file
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            sys.exit(1)
        
        prompt = processor.create_qwen_prompt(file_path)
        processor.process_with_qwen(prompt)
    elif args.auto:
        processor.process_all_pending()
    else:
        # Default: process all pending
        processor.process_all_pending()


if __name__ == '__main__':
    main()
