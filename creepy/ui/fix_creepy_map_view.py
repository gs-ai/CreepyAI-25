#!/usr/bin/env python3
"""
Direct fix for creepy_map_view.py indentation errors
This script directly modifies the CreepyMapView file to fix indentation issues
"""

import os
import sys
import shutil
import re

def fix_map_view():
    """Fix indentation errors in the creepy_map_view.py file."""
    # Get the path to the file
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "creepy_map_view.py")
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return False
    
    # Create backup
    backup_path = file_path + '.bak'
    shutil.copy2(file_path, backup_path)
    print(f"Created backup at {backup_path}")
    
    try:
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find the class definition
        class_match = re.search(r'class CreepyMapView\([^)]*\):.*?(?=\n\S|\Z)', content, re.DOTALL)
        if not class_match:
            print("Error: Could not find CreepyMapView class definition")
            return False
        
        # Find the __init__ method
        init_match = re.search(r'def __init__\s*\(self,\s*.*?\):.*?(?=\n\s*def|\n\S|\Z)', content, re.DOTALL)
        if not init_match:
            print("Error: Could not find __init__ method")
            return False
        
        # Extract the method body
        init_body = init_match.group(0)
        
        # Determine the correct indentation level
        init_indent_match = re.match(r'^(\s+)def', init_body, re.MULTILINE)
        if not init_indent_match:
            print("Error: Could not determine indentation level")
            return False
        
        method_indent = init_indent_match.group(1)
        body_indent = method_indent + "    "  # Standard 4-space indentation
        
        # Fix the indentation in the __init__ method
        fixed_lines = []
        for line in init_body.split('\n'):
            if line.strip().startswith('self.') and not line.strip().startswith('self.set'):
                # Check if indentation is wrong
                current_indent = len(line) - len(line.lstrip())
                if current_indent != len(body_indent):
                    line = body_indent + line.lstrip()
            
            fixed_lines.append(line)
        
        # Join lines back into a string
        fixed_init = '\n'.join(fixed_lines)
        
        # Replace the __init__ method in the content
        fixed_content = content.replace(init_body, fixed_init)
        
        # Write the fixed content back to the file
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        
        print(f"Successfully fixed indentation in {file_path}")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        # Restore backup
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            print(f"Restored backup from {backup_path}")
        return False

if __name__ == "__main__":
    success = fix_map_view()
    sys.exit(0 if success else 1)
