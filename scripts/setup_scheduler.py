"""
Windows Task Scheduler Setup - Creates scheduled tasks for AI Employee.

Silver Tier: Required for basic scheduling via cron or Task Scheduler.

Usage (Run as Administrator):
    python scripts\setup_scheduler.py --install

To remove:
    python scripts\setup_scheduler.py --remove
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


def get_python_exe():
    """Get path to Python executable."""
    return sys.executable


def get_project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


def get_vault_path():
    """Get vault directory."""
    return get_project_root() / 'AI_Employee_Vault'


def create_scheduled_task(task_name: str, script: str, schedule: str,
                          start_time: str = None):
    """
    Create a Windows Scheduled Task.
    
    Args:
        task_name: Name for the task
        script: Script to run
        schedule: Schedule type (hourly, daily, etc.)
        start_time: Start time (HH:MM format)
    """
    project_root = get_project_root()
    python_exe = get_python_exe()
    script_path = project_root / 'scripts' / script
    
    # Build schtasks command
    cmd = ['schtasks', '/create']
    cmd.extend(['/tn', f'AI_Employee_{task_name}'])
    cmd.extend(['/tr', f'"{python_exe}" "{script_path}"'])
    cmd.extend(['/sc', schedule])
    cmd.extend(['/rl', 'HIGHEST'])  # Run with highest privileges
    cmd.extend(['/f'])  # Force create (overwrite if exists)
    
    if start_time:
        cmd.extend(['/st', start_time])
    
    if schedule == 'daily':
        cmd.extend(['/ru', 'SYSTEM'])  # Run as SYSTEM for daily tasks
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ Created scheduled task: AI_Employee_{task_name}")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create task: {task_name}")
        print(e.stderr)
        return False


def remove_scheduled_task(task_name: str):
    """Remove a scheduled task."""
    cmd = ['schtasks', '/delete', '/tn', f'AI_Employee_{task_name}', '/f']
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ Removed scheduled task: AI_Employee_{task_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to remove task: {task_name}")
        print(e.stderr)
        return False


def install_all_tasks():
    """Install all scheduled tasks."""
    print("=" * 60)
    print("Installing AI Employee Scheduled Tasks")
    print("=" * 60)
    
    tasks = [
        {
            'name': 'Orchestrator_Hourly',
            'script': 'orchestrator.py',
            'schedule': 'hourly',
            'description': 'Process pending items every hour'
        },
        {
            'name': 'Daily_Briefing',
            'script': 'daily_briefing.py',
            'schedule': 'daily',
            'start_time': '08:00',
            'description': 'Generate daily briefing at 8 AM'
        },
        {
            'name': 'Approval_Check',
            'script': 'approval_manager.py',
            'schedule': 'hourly',
            'description': 'Check for approved actions every hour'
        }
    ]
    
    success_count = 0
    for task in tasks:
        print(f"\nCreating: {task['name']}")
        print(f"  Description: {task['description']}")
        print(f"  Schedule: {task['schedule']}")
        if task.get('start_time'):
            print(f"  Start Time: {task['start_time']}")
        
        if create_scheduled_task(
            task['name'],
            task['script'],
            task['schedule'],
            task.get('start_time')
        ):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Installed {success_count}/{len(tasks)} scheduled tasks")
    print("=" * 60)
    
    # List installed tasks
    print("\nInstalled Tasks:")
    list_installed_tasks()


def remove_all_tasks():
    """Remove all AI Employee scheduled tasks."""
    print("=" * 60)
    print("Removing AI Employee Scheduled Tasks")
    print("=" * 60)
    
    tasks = ['Orchestrator_Hourly', 'Daily_Briefing', 'Approval_Check']
    
    success_count = 0
    for task_name in tasks:
        if remove_scheduled_task(task_name):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Removed {success_count}/{len(tasks)} scheduled tasks")
    print("=" * 60)


def list_installed_tasks():
    """List all installed AI Employee tasks."""
    cmd = ['schtasks', '/query', '/fo', 'LIST', '/v']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        ai_tasks = [line for line in lines if 'AI_Employee' in line]
        
        if ai_tasks:
            print("\nAI Employee Scheduled Tasks:")
            for task in ai_tasks:
                print(f"  - {task.strip()}")
        else:
            print("\nNo AI Employee scheduled tasks found.")
            
    except Exception as e:
        print(f"Error listing tasks: {e}")


def create_linux_crontab():
    """Generate crontab entries for Linux/Mac."""
    project_root = get_project_root()
    scripts_dir = project_root / 'scripts'
    
    crontab = f"""# AI Employee Scheduled Tasks
# Generated: {datetime.now().isoformat()}
# Install with: crontab -e

# Process pending items every hour
0 * * * * cd {project_root} && python {scripts_dir / 'orchestrator.py'}

# Check for approved actions every hour
30 * * * * cd {project_root} && python {scripts_dir / 'approval_manager.py'} --process

# Generate daily briefing at 8 AM
0 8 * * * cd {project_root} && python {scripts_dir / 'daily_briefing.py'}

# Check for expired approvals daily at 9 AM
0 9 * * * cd {project_root} && python {scripts_dir / 'approval_manager.py'} --check-expired
"""
    
    print("Linux/Mac Crontab Entries:")
    print("=" * 60)
    print(crontab)
    print("=" * 60)
    print("\nTo install, run:")
    print(f"  echo '{crontab.strip()}' | crontab -")
    print("\nOr manually edit crontab:")
    print("  crontab -e")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Windows Task Scheduler Setup for AI Employee'
    )
    parser.add_argument(
        '--install',
        action='store_true',
        help='Install all scheduled tasks'
    )
    parser.add_argument(
        '--remove',
        action='store_true',
        help='Remove all scheduled tasks'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List installed tasks'
    )
    parser.add_argument(
        '--linux',
        action='store_true',
        help='Show Linux/Mac crontab entries'
    )
    
    args = parser.parse_args()
    
    if args.install:
        install_all_tasks()
    elif args.remove:
        remove_all_tasks()
    elif args.list:
        list_installed_tasks()
    elif args.linux:
        create_linux_crontab()
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python setup_scheduler.py --install")
        print("  python setup_scheduler.py --remove")
        print("  python setup_scheduler.py --list")
        print("  python setup_scheduler.py --linux")


if __name__ == '__main__':
    main()
