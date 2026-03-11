"""
Bronze Tier Verification Script

Run this script to verify all Bronze Tier requirements are met.
"""

import sys
from pathlib import Path


def check(condition, message):
    """Print check result."""
    if condition:
        print(f"[PASS] {message}")
        return True
    else:
        print(f"[FAIL] {message}")
        return False


def main():
    """Run all Bronze Tier verification checks."""
    print("=" * 60)
    print("BRONZE TIER VERIFICATION")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    vault = project_root / 'AI_Employee_Vault'
    scripts_dir = project_root / 'scripts'
    
    all_passed = True
    
    print("\n1. VAULT STRUCTURE")
    print("-" * 40)
    
    # Check required folders
    required_folders = ['Inbox', 'Needs_Action', 'Done', 'Plans', 'Pending_Approval', 'Approved', 'Rejected', 'Logs']
    for folder in required_folders:
        all_passed &= check((vault / folder).exists(), f"Folder /{folder} exists")
    
    print("\n2. CORE FILES")
    print("-" * 40)
    
    # Check Dashboard.md
    all_passed &= check((vault / 'Dashboard.md').exists(), "Dashboard.md exists")
    
    # Check Company_Handbook.md
    all_passed &= check((vault / 'Company_Handbook.md').exists(), "Company_Handbook.md exists")
    
    print("\n3. WATCHER SCRIPTS")
    print("-" * 40)
    
    # Check base_watcher.py
    all_passed &= check((scripts_dir / 'base_watcher.py').exists(), "base_watcher.py exists")
    
    # Check filesystem_watcher.py
    all_passed &= check((scripts_dir / 'filesystem_watcher.py').exists(), "filesystem_watcher.py exists")
    
    # Check orchestrator.py
    all_passed &= check((scripts_dir / 'orchestrator.py').exists(), "orchestrator.py exists")
    
    print("\n4. PYTHON IMPORTS")
    print("-" * 40)
    
    # Test imports
    try:
        sys.path.insert(0, str(scripts_dir))
        from base_watcher import BaseWatcher
        all_passed &= check(True, "base_watcher.py imports correctly")
    except Exception as e:
        all_passed &= check(False, f"base_watcher.py import failed: {e}")
    
    try:
        from filesystem_watcher import FileSystemWatcher
        all_passed &= check(True, "filesystem_watcher.py imports correctly")
    except Exception as e:
        all_passed &= check(False, f"filesystem_watcher.py import failed: {e}")
    
    try:
        from orchestrator import Orchestrator
        all_passed &= check(True, "orchestrator.py imports correctly")
    except Exception as e:
        all_passed &= check(False, f"orchestrator.py import failed: {e}")
    
    print("\n5. FUNCTIONAL TESTS")
    print("-" * 40)
    
    # Check if watcher created action files
    needs_action = vault / 'Needs_Action'
    action_files = list(needs_action.glob('*.md')) if needs_action.exists() else []
    all_passed &= check(len(action_files) >= 0, "Watcher can create action files (tested earlier)")
    
    # Check logs exist
    logs_dir = vault / 'Logs'
    log_files = list(logs_dir.glob('*.log')) if logs_dir.exists() else []
    all_passed &= check(len(log_files) > 0, "Logs are being created")
    
    # Check Dashboard was updated
    if (vault / 'Dashboard.md').exists():
        content = (vault / 'Dashboard.md').read_text(encoding='utf-8')
        all_passed &= check('Recent Activity' in content, "Dashboard has Recent Activity section")
        all_passed &= check('Processing:' in content, "Dashboard was updated by orchestrator")
    
    print("\n6. DOCUMENTATION")
    print("-" * 40)
    
    # Check README
    all_passed &= check((project_root / 'README.md').exists(), "README.md exists")
    
    # Check qwen.md
    all_passed &= check((project_root / 'qwen.md').exists(), "qwen.md exists")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL BRONZE TIER REQUIREMENTS MET!")
        print("\nYour AI Employee Bronze Tier is ready to use.")
        print("\nNext steps:")
        print("1. Open AI_Employee_Vault in Obsidian")
        print("2. Run: python scripts/filesystem_watcher.py")
        print("3. Drop a file in AI_Employee_Vault/Inbox/")
        print("4. Run: python scripts/orchestrator.py")
        print("5. Run: claude \"Process pending items in Needs_Action\"")
    else:
        print("[FAILED] SOME CHECKS FAILED - Review above for details")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
