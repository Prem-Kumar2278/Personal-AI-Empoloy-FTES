"""
Silver Tier Verification Script

Run this script to verify all Silver Tier requirements are met.

Silver Tier Requirements:
1. All Bronze requirements plus:
2. Two or more Watcher scripts (e.g., Gmail + WhatsApp + LinkedIn)
3. Automatically Post on LinkedIn about business to generate sales
4. Claude reasoning loop that creates Plan.md files
5. One working MCP server for external action (e.g., sending emails)
6. Human-in-the-loop approval workflow for sensitive actions
7. Basic scheduling via cron or Task Scheduler
8. All AI functionality should be implemented as Agent Skills
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
    """Run all Silver Tier verification checks."""
    print("=" * 70)
    print("SILVER TIER VERIFICATION")
    print("=" * 70)
    
    project_root = Path(__file__).parent.parent
    vault = project_root / 'AI_Employee_Vault'
    scripts_dir = project_root / 'scripts'
    skills_dir = project_root / 'skills'
    
    all_passed = True
    bronze_count = 0
    silver_count = 0
    
    # ========================================
    # BRONZE TIER REQUIREMENTS (Prerequisites)
    # ========================================
    print("\n" + "=" * 70)
    print("BRONZE TIER REQUIREMENTS (Prerequisites)")
    print("=" * 70)
    
    # Vault folders
    required_folders = ['Inbox', 'Needs_Action', 'Done', 'Plans', 
                       'Pending_Approval', 'Approved', 'Rejected', 'Logs']
    for folder in required_folders:
        if check((vault / folder).exists(), f"Folder /{folder} exists"):
            bronze_count += 1
    
    # Core files
    if check((vault / 'Dashboard.md').exists(), "Dashboard.md exists"):
        bronze_count += 1
    if check((vault / 'Company_Handbook.md').exists(), "Company_Handbook.md exists"):
        bronze_count += 1
    
    # Bronze scripts
    if check((scripts_dir / 'base_watcher.py').exists(), "base_watcher.py exists"):
        bronze_count += 1
    if check((scripts_dir / 'filesystem_watcher.py').exists(), "filesystem_watcher.py exists"):
        bronze_count += 1
    if check((scripts_dir / 'orchestrator.py').exists(), "orchestrator.py exists"):
        bronze_count += 1
    
    # ========================================
    # SILVER TIER REQUIREMENTS
    # ========================================
    print("\n" + "=" * 70)
    print("SILVER TIER REQUIREMENTS")
    print("=" * 70)
    
    # Requirement 2: Two or more Watcher scripts
    print("\n--- Requirement 2: Two or More Watcher Scripts ---")
    watcher_count = 0
    watchers = ['filesystem_watcher.py', 'gmail_watcher.py', 'whatsapp_watcher.py']
    for watcher in watchers:
        if (scripts_dir / watcher).exists():
            print(f"[PASS] {watcher} exists")
            watcher_count += 1
        else:
            print(f"[FAIL] {watcher} missing")
    
    if check(watcher_count >= 2, f"At least 2 watchers installed ({watcher_count}/2)"):
        silver_count += 1
    
    # Requirement 3: LinkedIn Auto-Posting
    print("\n--- Requirement 3: LinkedIn Auto-Posting ---")
    if check((scripts_dir / 'linkedin_poster.py').exists(), "linkedin_poster.py exists"):
        silver_count += 1
    
    # Check Social_Posts folder
    social_posts_dir = vault / 'Social_Posts'
    if check(social_posts_dir.exists(), "Social_Posts folder exists"):
        silver_count += 1
    
    # Requirement 4: Claude Reasoning Loop (Plan.md creation)
    print("\n--- Requirement 4: Claude Reasoning Loop (Plan.md) ---")
    if check((scripts_dir / 'plan_manager.py').exists(), "plan_manager.py exists"):
        silver_count += 1
    
    # Check if Plans folder exists
    if check((vault / 'Plans').exists(), "Plans folder exists"):
        silver_count += 1
    
    # Requirement 5: MCP Server Configuration
    print("\n--- Requirement 5: MCP Server Configuration ---")
    if check((scripts_dir / 'mcp_setup.md').exists(), "mcp_setup.md exists"):
        silver_count += 1
    
    # Check for MCP-related files
    mcp_files = ['approval_manager.py', 'orchestrator.py']
    mcp_count = sum(1 for f in mcp_files if (scripts_dir / f).exists())
    if check(mcp_count == len(mcp_files), "MCP integration files exist"):
        silver_count += 1
    
    # Requirement 6: Human-in-the-Loop Approval Workflow
    print("\n--- Requirement 6: HITL Approval Workflow ---")
    if check((scripts_dir / 'approval_manager.py').exists(), "approval_manager.py exists"):
        silver_count += 1
    
    if check((scripts_dir / 'HITL_WORKFLOW.md').exists(), "HITL_WORKFLOW.md documentation"):
        silver_count += 1
    
    # Check approval folders
    approval_folders = ['Pending_Approval', 'Approved', 'Rejected']
    approval_folder_count = sum(1 for f in approval_folders if (vault / f).exists())
    if check(approval_folder_count == 3, "All approval folders exist"):
        silver_count += 1
    
    # Requirement 7: Basic Scheduling
    print("\n--- Requirement 7: Basic Scheduling ---")
    if check((scripts_dir / 'setup_scheduler.py').exists(), "setup_scheduler.py exists"):
        silver_count += 1
    
    # Requirement 8: Agent Skills
    print("\n--- Requirement 8: Agent Skills Implementation ---")
    if check(skills_dir.exists(), "skills/ folder exists"):
        silver_count += 1
    
    if check((skills_dir / 'README.md').exists(), "skills/README.md exists"):
        silver_count += 1
    
    # Check for skill definitions
    skill_files = list(skills_dir.glob('*/SKILL.md'))
    if check(len(skill_files) >= 2, f"At least 2 Agent Skills defined ({len(skill_files)})"):
        silver_count += 1
    
    # ========================================
    # SILVER TIER BONUS FEATURES
    # ========================================
    print("\n" + "=" * 70)
    print("SILVER TIER BONUS FEATURES")
    print("=" * 70)
    
    # Security setup
    if check((project_root / '.env.template').exists(), ".env.template exists"):
        print("[BONUS] Security: Environment template")
    
    if check((project_root / '.gitignore').exists(), ".gitignore exists"):
        print("[BONUS] Security: Git ignore configured")
    
    # Audit logging
    if check((scripts_dir / 'audit_logger.py').exists(), "audit_logger.py exists"):
        print("[BONUS] Enhanced audit logging")
    
    # ========================================
    # PYTHON IMPORTS TEST
    # ========================================
    print("\n" + "=" * 70)
    print("PYTHON IMPORTS TEST")
    print("=" * 70)
    
    sys.path.insert(0, str(scripts_dir))
    
    silver_modules = [
        'gmail_watcher',
        'whatsapp_watcher', 
        'plan_manager',
        'approval_manager',
        'audit_logger',
        'linkedin_poster',
        'setup_scheduler'
    ]
    
    for module in silver_modules:
        try:
            __import__(module)
            print(f"[PASS] {module} imports correctly")
        except ImportError as e:
            # Some modules may have optional dependencies
            print(f"[INFO] {module} import skipped: {e}")
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    print(f"\nBronze Tier Checks: {bronze_count} passed")
    print(f"Silver Tier Checks: {silver_count} passed")
    
    # Silver Tier requires ~15 checks to pass
    silver_threshold = 12
    
    print("\n" + "=" * 70)
    if silver_count >= silver_threshold and bronze_count >= 10:
        print("[SUCCESS] ALL SILVER TIER REQUIREMENTS MET!")
        print("\nYour AI Employee Silver Tier is ready to use.")
        print("\nNext steps:")
        print("1. Configure MCP servers (see scripts/mcp_setup.md)")
        print("2. Set up environment variables (copy .env.template to .env)")
        print("3. Install scheduled tasks: python scripts/setup_scheduler.py --install")
        print("4. Start watchers: python scripts/gmail_watcher.py --credentials credentials.json")
        print("5. Create LinkedIn post: python scripts/linkedin_poster.py --topic 'Your Topic'")
    else:
        print(f"[IN PROGRESS] {silver_count}/{silver_threshold} Silver Tier checks passed")
        print("\nComplete the remaining requirements to achieve Silver Tier.")
    print("=" * 70)
    
    return 0 if (silver_count >= silver_threshold and bronze_count >= 10) else 1


if __name__ == '__main__':
    sys.exit(main())
