#!/usr/bin/env python3
"""
Fix for the PersonProjectWizard NoneType error.
This script patches the PersonProjectWizard.py file to handle cases where plugins is None.
"""

import os
import re
import logging
import shutil
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("WizardFix")

def fix_person_project_wizard():
    """Fix the NoneType error in PersonProjectWizard.py."""
    
    # Path to the PersonProjectWizard.py file
    wizard_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PersonProjectWizard.py")
    
    if not os.path.exists(wizard_file):
        logger.error(f"PersonProjectWizard.py not found at {wizard_file}")
        return False
    
    # Create backup
    backup_file = wizard_file + '.bak'
    shutil.copy2(wizard_file, backup_file)
    logger.info(f"Created backup at {backup_file}")
    
    try:
        with open(wizard_file, 'r') as f:
            content = f.read()
        
        # Find the problematic line
        pattern = r'(\s*)for plugin in plugins:'
        if pattern in content:
            # Add a check to ensure plugins is not None
            replacement = r'\1if plugins is None:\n\1    plugins = []\n\1for plugin in plugins:'
            modified_content = re.sub(pattern, replacement, content)
            
            with open(wizard_file, 'w') as f:
                f.write(modified_content)
                
            logger.info(f"Successfully patched {wizard_file}")
            return True
        else:
            # Find the line number mentioned in the error (line 390)
            lines = content.split('\n')
            if len(lines) >= 390:
                logger.info(f"Line 390 content: {lines[389]}")
                # Try a more general approach
                line_num = 389  # 0-indexed
                while line_num < min(400, len(lines)):
                    if "for" in lines[line_num] and "plugin" in lines[line_num] and "plugins" in lines[line_num]:
                        indent = len(lines[line_num]) - len(lines[line_num].lstrip())
                        indentation = ' ' * indent
                        lines.insert(line_num, f"{indentation}if plugins is None:")
                        lines.insert(line_num + 1, f"{indentation}    plugins = []")
                        
                        modified_content = '\n'.join(lines)
                        with open(wizard_file, 'w') as f:
                            f.write(modified_content)
                            
                        logger.info(f"Added check at line {line_num+1}")
                        return True
                    line_num += 1
            
            logger.error("Could not find the line with 'for plugin in plugins:'")
            return False
            
    except Exception as e:
        logger.error(f"Error patching file: {e}")
        # Restore backup
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, wizard_file)
            logger.info(f"Restored backup from {backup_file}")
        return False

def main():
    logger.info("Starting PersonProjectWizard fix")
    
    if fix_person_project_wizard():
        logger.info("Successfully applied the PersonProjectWizard fix")
    else:
        logger.error("Failed to apply the PersonProjectWizard fix")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
