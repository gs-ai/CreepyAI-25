#!/usr/bin/env python3
"""
Fix for the PluginsConfigDialog missing config_manager argument error.
This script patches the necessary files to ensure the config_manager is properly passed.
"""

import os
import re
import logging
import shutil
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PluginDialogFix")

def find_file_with_dialog_init(base_dir):
    """Search for the file that initializes the PluginsConfigDialog."""
    for root, _, files in os.walk(base_dir):
        for filename in files:
            if not filename.endswith('.py'):
                continue
                
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    if 'PluginsConfigDialog(' in content and 'config_manager' not in content:
                        return filepath
            except Exception as e:
                logger.error(f"Error reading {filepath}: {e}")
    
    return None

def patch_file(filepath):
    """Patch the file to add the config_manager argument to PluginsConfigDialog initialization."""
    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return False
        
    # Create backup
    backup_path = filepath + '.bak'
    shutil.copy2(filepath, backup_path)
    logger.info(f"Created backup at {backup_path}")
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Find the line that creates the PluginsConfigDialog
        pattern = r'(\w+\s*=\s*)?PluginsConfigDialog\s*\('
        match = re.search(pattern, content)
        if not match:
            logger.error("Could not find PluginsConfigDialog initialization")
            return False
            
        # Determine if we need to add self.config_manager or just config_manager
        if "self.config_manager" in content:
            modified_content = re.sub(
                pattern, 
                r'\1PluginsConfigDialog(self.config_manager, ', 
                content
            )
        else:
            # Add import for config_manager if needed
            if "from creepy.core.config_manager import ConfigManager" not in content:
                import_line = "from creepy.core.config_manager import ConfigManager\n"
                if "import" in content:
                    # Add after the last import
                    last_import = re.search(r'^.*import.*$', content, re.MULTILINE | re.DOTALL)
                    if last_import:
                        pos = last_import.end()
                        modified_content = content[:pos] + "\n" + import_line + content[pos:]
                    else:
                        modified_content = import_line + content
                else:
                    modified_content = import_line + content
                    
                # Add config_manager instantiation
                modified_content = modified_content.replace(
                    pattern, 
                    r'config_manager = ConfigManager()\n\1PluginsConfigDialog(config_manager, ', 
                )
            else:
                # Use existing config_manager
                modified_content = re.sub(
                    pattern, 
                    r'config_manager = ConfigManager()\n\1PluginsConfigDialog(config_manager, ', 
                    content
                )
        
        # Write the modified content
        with open(filepath, 'w') as f:
            f.write(modified_content)
            
        logger.info(f"Successfully patched {filepath}")
        return True
            
    except Exception as e:
        logger.error(f"Error patching file: {e}")
        # Restore backup
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, filepath)
            logger.info(f"Restored backup from {backup_path}")
        return False

def patch_plugin_dialog_class(base_dir):
    """Find and patch the PluginsConfigDialog class to make config_manager optional."""
    for root, _, files in os.walk(base_dir):
        for filename in files:
            if not filename.endswith('.py'):
                continue
                
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    if 'class PluginsConfigDialog' in content:
                        # Create backup
                        backup_path = filepath + '.bak'
                        shutil.copy2(filepath, backup_path)
                        
                        # Make config_manager parameter optional with a default value
                        pattern = r'def __init__\s*\(\s*self,\s*config_manager\s*,'
                        if re.search(pattern, content):
                            
        if config_manager is None:
            from creepy.core.config_manager import ConfigManager
            self.config_manager = ConfigManager()
        else:
            self.config_manager = config_manager
# Already has config_manager, no need to modify
                            return True
                            
                        pattern = r'def __init__\s*\(\s*self\s*,'
                        modified_content = re.sub(
                            pattern, 
                            r'def __init__(self, config_manager=None,  config_manager=None, ', 
                            content
                        )
                        
                        # Add check for config_manager
                        pattern = r'def __init__.*?\):
        if config_manager is None:
            from creepy.core.config_manager import ConfigManager
            self.config_manager = ConfigManager()
        else:
            self.config_manager = config_manager
\s*'
                        add_after = "\n        if config_manager is None:\n            from creepy.core.config_manager import ConfigManager\n            self.config_manager = ConfigManager()\n        else:\n            self.config_manager = config_manager\n"
                        modified_content = re.sub(
                            pattern, 
                            lambda m: m.group(0) + add_after, 
                            modified_content, 
                            flags=re.DOTALL
                        )
                        
                        with open(filepath, 'w') as f:
                            f.write(modified_content)
                            
                        logger.info(f"Modified PluginsConfigDialog class in {filepath}")
                        return True
            except Exception as e:
                logger.error(f"Error processing {filepath}: {e}")
    
    return False

def main():
    logger.info("Starting plugin dialog fix")
    
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    
    # First try to patch the class itself to make config_manager optional
    if patch_plugin_dialog_class(base_dir):
        logger.info("Successfully patched PluginsConfigDialog class")
    else:
        logger.info("Could not find PluginsConfigDialog class or it's already fixed")
    
    # Then try to find and patch files that create the dialog
    file_to_patch = find_file_with_dialog_init(base_dir)
    if file_to_patch:
        if patch_file(file_to_patch):
            logger.info("Successfully applied the plugin dialog fix")
            logger.info("Please restart CreepyAI for changes to take effect")
        else:
            logger.error("Failed to patch file")
            return 1
    else:
        logger.info("Could not find file initializing PluginsConfigDialog without config_manager")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
