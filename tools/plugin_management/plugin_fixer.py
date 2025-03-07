#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plugin Fixer Utility for CreepyAI
This tool helps diagnose and fix common issues with plugin files
"""

import os
import sys
import re
import ast
import logging
from pathlib import Path
import shutil
import argparse
import datetime
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PluginFixer')

# Get script directory and project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PLUGINS_DIR = os.path.join(PROJECT_ROOT, 'plugins')

# Common syntax errors to check for
COMMON_SYNTAX_ISSUES = [
    (r'"""[^"]*$', 'Unterminated triple-quote string'),
    (r"'''[^']*$", 'Unterminated triple-quote string'),
    (r'"[^"\n]*$', 'Unterminated string literal'),
    (r"'[^'\n]*$", 'Unterminated string literal'),
    (r'\([^)]*$', 'Unclosed parenthesis'),
    (r'\[[^\]]*$', 'Unclosed bracket'),
    (r'\{[^}]*$', 'Unclosed brace'),
    (r'^\s*for\s+.*\s+in\s+.*\s*:[ \t]*$', 'for loop missing indented block'),
    (r'^\s*if\s+.*\s*:[ \t]*$', 'if statement missing indented block'),
    (r'^\s*def\s+.*\s*\(.*\)\s*:[ \t]*$', 'function missing indented block'),
    (r'^\s*class\s+.*\s*:[ \t]*$', 'class missing indented block'),
]

def check_plugin_syntax(file_path):
    """Check plugin file for syntax errors"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # First try with ast.parse to catch Python syntax errors
        try:
            ast.parse(content)
            return True, "No syntax errors found"
        except SyntaxError as e:
            # Get line and column info from the exception
            line_num = e.lineno
            col_offset = e.offset
            line = content.splitlines()[line_num - 1] if line_num <= len(content.splitlines()) else ""
            
            # Simple visual indicator of error position
            indicator = ' ' * (col_offset - 1) + '^' if col_offset else ''
            
            return False, f"Syntax error at line {line_num}: {e}\n{line}\n{indicator}"
        
    except Exception as e:
        return False, f"Error reading or parsing file: {e}"

def analyze_plugin_file(file_path):
    """Analyze plugin file for common errors and provide detailed report"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            content = ''.join(lines)
            
        issues = []
        
        # Check line by line for common issues
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Check for common patterns that indicate errors
            for pattern, issue_desc in COMMON_SYNTAX_ISSUES:
                if re.search(pattern, line):
                    # Check if this is a true error or just a multi-line statement
                    # For example, a triple quote that's actually closed later
                    if pattern in [r'"""[^"]*$', r"'''[^']*$"] and '"""' in content[content.find(line) + len(line):]:
                        continue
                        
                    issues.append({
                        'line': line_num,
                        'content': line.rstrip(),
                        'description': issue_desc
                    })
                    break
                    
            # Check for specific common issues
            if ':' not in line and re.search(r'^\s*(if|for|def|class|elif|else|try|except|finally)\s', line):
                issues.append({
                    'line': line_num,
                    'content': line.rstrip(),
                    'description': 'Missing colon at end of statement'
                })
        
        return issues
    
    except Exception as e:
        logger.error(f"Error analyzing file {file_path}: {e}")
        return [{
            'line': 0,
            'content': '',
            'description': f"Error analyzing file: {e}"
        }]

def fix_common_issues(file_path, backup=True):
    """Attempt to fix common issues in plugin files"""
    if backup:
        backup_file = f"{file_path}.bak"
        shutil.copy2(file_path, backup_file)
        logger.info(f"Created backup: {backup_file}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        for i, line in enumerate(lines):
            # Fix missing colons
            if re.search(r'^\s*(if|for|def|class|elif|else|try|except|finally)\s', line) and ':' not in line:
                line = line.rstrip() + ':\n'
            
            # Fix unterminated strings
            for pattern in [r'"[^"\n]*$', r"'[^'\n]*$"]:
                if re.search(pattern, line):
                    if '"' in line and line.count('"') % 2 == 1:
                        line = line.rstrip() + '"\n'
                    elif "'" in line and line.count("'") % 2 == 1:
                        line = line.rstrip() + "'\n"
            
            # Add missing indentation for control structures
            if i > 0 and i < len(lines) - 1:
                prev_line = lines[i-1].rstrip()
                next_line = lines[i+1]
                
                if re.search(r':\s*$', prev_line) and not next_line.startswith(' ') and not next_line.startswith('\t'):
                    # This line should be indented based on previous line ending with :
                    indent = re.match(r'^(\s*)', prev_line).group(1) + '    '
                    fixed_lines.append(line)
                    fixed_lines.append(f"{indent}pass  # Auto-added by plugin_fixer.py\n")
                    continue
            
            fixed_lines.append(line)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
            
        logger.info(f"Applied fixes to {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error fixing file {file_path}: {e}")
        return False

def scan_plugins():
    """Scan all plugin files and report issues"""
    if not os.path.isdir(PLUGINS_DIR):
        logger.error(f"Plugins directory not found: {PLUGINS_DIR}")
        return
    
    logger.info(f"Scanning plugins directory: {PLUGINS_DIR}")
    plugins_with_issues = []
    
    for filename in os.listdir(PLUGINS_DIR):
        if filename.endswith('.py') and not filename.startswith('__'):
            file_path = os.path.join(PLUGINS_DIR, filename)
            
            # Skip handling dummy plugin
            if 'dummy' in filename.lower():
                logger.info(f"Skipping dummy plugin: {filename}")
                continue
                
            logger.info(f"Checking plugin: {filename}")
            valid, message = check_plugin_syntax(file_path)
            
            if not valid:
                plugins_with_issues.append({
                    'file': filename,
                    'path': file_path,
                    'message': message,
                    'issues': analyze_plugin_file(file_path)
                })
    
    if plugins_with_issues:
        logger.info(f"\nFound {len(plugins_with_issues)} plugins with issues:")
        for plugin in plugins_with_issues:
            logger.info(f"\n{'-' * 60}")
            logger.info(f"Plugin: {plugin['file']}")
            logger.info(f"Path: {plugin['path']}")
            logger.info(f"Message: {plugin['message']}")
            
            if plugin['issues']:
                logger.info("Specific issues:")
                for issue in plugin['issues']:
                    logger.info(f"  Line {issue['line']}: {issue['description']}")
                    logger.info(f"    {issue['content']}")
    else:
        logger.info("No syntax issues found in plugins!")
        
    return plugins_with_issues

def fix_all_plugins():
    """Fix all plugins with issues"""
    plugins_with_issues = scan_plugins()
    
    if not plugins_with_issues:
        logger.info("No issues to fix!")
        return
    
    logger.info("\nAttempting to fix plugin issues...")
    
    # Create backup directory
    backup_dir = os.path.join(PROJECT_ROOT, "plugins_backup_" + 
                           datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup all plugins first
    for filename in os.listdir(PLUGINS_DIR):
        # Skip handling dummy files
        if 'dummy' in filename.lower():
            continue
            
        if filename.endswith('.py') and not filename.startswith('__'):
            src = os.path.join(PLUGINS_DIR, filename)
            dst = os.path.join(backup_dir, filename)
            shutil.copy2(src, dst)
    
    logger.info(f"Backed up all plugins to: {backup_dir}")
    
    # Now fix plugins with issues
    fixed_count = 0
    for plugin in plugins_with_issues:
        logger.info(f"Fixing: {plugin['file']}")
        if fix_common_issues(plugin['path'], backup=False):
            fixed_count += 1
    
    logger.info(f"\nFixed {fixed_count} out of {len(plugins_with_issues)} plugins with issues")
    logger.info(f"Original versions backed up to: {backup_dir}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Plugin Fixer Utility")
    parser.add_argument('--scan', action='store_true', help='Scan plugins for issues')
    parser.add_argument('--fix', action='store_true', help='Try to fix issues in all plugins')
    args = parser.parse_args()
    
    # Default action if no args given
    if not (args.scan or args.fix):
        args.scan = True
    
    try:
        if args.scan:
            scan_plugins()
            
        if args.fix:
            fix_all_plugins()
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error(traceback.format_exc())
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
