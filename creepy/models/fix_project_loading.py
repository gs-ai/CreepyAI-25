#!/usr/bin/env python3
"""
Fix for the Project loading error: 'os' not defined.
This script patches the Project.py file to ensure 'os' is properly imported.
"""

import os
import re
import logging
import shutil
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ProjectLoadFix")

def fix_project_loading():
    """Fix the 'os' not defined error in Project.py."""
    
    # Path to the Project.py file
    project_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Project.py")
    
    if not os.path.exists(project_file):
        logger.error(f"Project.py not found at {project_file}")
        return False
    
    # Create backup
    backup_file = project_file + '.bak'
    shutil.copy2(project_file, backup_file)
    logger.info(f"Created backup at {backup_file}")
    
    try:
        with open(project_file, 'r') as f:
            content = f.read()
        
        # Check if 'os' is imported
        if not re.search(r'import\s+os', content) and not re.search(r'from\s+os\s+import', content):
            # Add import statement at the top of the file, after any other imports
            import_match = re.search(r'^(import.*?\n|from.*?\n)+', content, re.MULTILINE)
            if import_match:
                pos = import_match.end()
                modified_content = content[:pos] + 'import os\n' + content[pos:]
            else:
                # No imports found, add at top
                modified_content = 'import os\n' + content
                
            with open(project_file, 'w') as f:
                f.write(modified_content)
                
            logger.info(f"Successfully patched {project_file} - added 'import os'")
            return True
        else:
            logger.info("'os' module is already imported in Project.py")
            return True
            
    except Exception as e:
        logger.error(f"Error patching file: {e}")
        # Restore backup
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, project_file)
            logger.info(f"Restored backup from {backup_file}")
        return False

def main():
    logger.info("Starting Project loading fix")
    
    if fix_project_loading():
        logger.info("Successfully applied the Project loading fix")
    else:
        logger.error("Failed to apply the Project loading fix")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
