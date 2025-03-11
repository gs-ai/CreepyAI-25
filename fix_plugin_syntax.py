#!/usr/bin/env python3
"""
Script to fix common syntax errors in plugin files
"""
import os
import re
import sys
import logging
from typing import List, Dict, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PluginSyntaxFixer:
    """Fixes common syntax errors in plugin files"""
    
    def __init__(self, base_dir: str):
        """Initialize with base directory"""
        self.base_dir = base_dir
        self.plugins_dir = os.path.join(base_dir, 'app', 'plugins')
        
    def find_plugin_files(self) -> List[str]:
        """Find all plugin files in the plugins directory"""
        plugin_files = []
        
        for root, dirs, files in os.walk(self.plugins_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    plugin_files.append(os.path.join(root, file))
                    
        return plugin_files
    
    def fix_docstring_issues(self, content: str) -> str:
        """Fix docstring syntax issues"""
        # Fix multiple quotes in a row
        content = re.sub(r'"""""""+"', '"""', content)
        content = re.sub(r"'''''''+", "'''", content)
        
        # Fix unclosed docstrings
        lines = content.split('\n')
        docstring_start = False
        for i, line in enumerate(lines):
            if '"""' in line or "'''" in line:
                # Count occurrences
                triple_double_quotes = line.count('"""')
                triple_single_quotes = line.count("'''")
                
                # If there's an odd number of triple quotes, it's likely unclosed
                if triple_double_quotes % 2 == 1 or triple_single_quotes % 2 == 1:
                    # Check if this is the start of a docstring
                    if not docstring_start:
                        docstring_start = True
                        # Ensure it starts correctly
                        if '"""' in line:
                            quote_type = '"""'
                        else:
                            quote_type = "'''"
                        
                        # If there's code after the opening quote, fix it
                        if line.strip().startswith(quote_type) and len(line.strip()) > 3:
                            parts = line.split(quote_type, 1)
                            lines[i] = parts[0] + quote_type
                    else:
                        # This is the end of a docstring
                        docstring_start = False
                        
        content = '\n'.join(lines)
        
        return content
    
    def fix_indentation_issues(self, content: str) -> str:
        """Fix indentation issues in the code"""
        # Convert tabs to spaces
        content = content.replace('\t', '    ')
        
        # Fix inconsistent indentation patterns
        lines = content.split('\n')
        current_block_indent = 0
        in_class_or_function = False
        
        for i in range(len(lines)):
            line = lines[i]
            
            # Skip empty lines
            if not line.strip():
                continue
                
            # Determine indentation level
            indent_level = len(line) - len(line.lstrip())
            
            # Check for class or function definitions
            if re.match(r'\s*(class|def)\s+\w+', line):
                in_class_or_function = True
                current_block_indent = indent_level
                
            # Check for block endings
            elif in_class_or_function and line.strip() and indent_level <= current_block_indent:
                in_class_or_function = False
                
            # Fix obvious indentation issues
            if in_class_or_function and line.strip() and indent_level > 0:
                if indent_level != current_block_indent and indent_level != current_block_indent + 4:
                    # Adjust indentation to be consistent with the block
                    lines[i] = ' ' * (current_block_indent + 4) + line.lstrip()
        
        return '\n'.join(lines)
    
    def fix_file_syntax(self, file_path: str) -> bool:
        """
        Fix common syntax errors in a file
        
        Returns:
            True if changes were made, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Store original content
            original_content = content
            
            # Apply fixes
            content = self.fix_docstring_issues(content)
            content = self.fix_indentation_issues(content)
            
            # Check if content changed
            if content != original_content:
                # Backup original file
                backup_path = file_path + '.bak'
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                # Write fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                logger.info(f"Fixed syntax issues in {os.path.basename(file_path)}")
                return True
            else:
                logger.info(f"No syntax issues found in {os.path.basename(file_path)}")
                return False
                
        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")
            return False
    
    def fix_all_plugins(self) -> Tuple[int, int]:
        """
        Fix syntax issues in all plugin files
        
        Returns:
            Tuple of (total_files, fixed_files)
        """
        plugin_files = self.find_plugin_files()
        fixed_files = 0
        
        for file_path in plugin_files:
            if self.fix_file_syntax(file_path):
                fixed_files += 1
                
        return len(plugin_files), fixed_files

def main():
    """Main function"""
    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create fixer
    fixer = PluginSyntaxFixer(base_dir)
    
    # Fix all plugins
    total_files, fixed_files = fixer.fix_all_plugins()
    
    print(f"\nProcessed {total_files} plugin files, fixed {fixed_files} files with syntax issues.")
    
    if fixed_files > 0:
        print("\nBackups of original files were created with '.bak' extension.")

if __name__ == "__main__":
    main()
