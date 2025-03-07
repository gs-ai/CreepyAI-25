#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to merge UI-related folders in CreepyAI project.
This script consolidates files from components/, gui/, and ui/ into a single ui/ folder.
"""

import os
import shutil
import re
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path('/Users/mbaosint/Desktop/Projects/CreepyAI')

# Source directories to merge
SOURCE_DIRS = [
    PROJECT_ROOT / 'components',
    PROJECT_ROOT / 'gui',
    PROJECT_ROOT / 'ui'
]

# Target directory structure
TARGET_DIR = PROJECT_ROOT / 'ui'
TARGET_SUBDIRS = [
    TARGET_DIR / 'dialogs',
    TARGET_DIR / 'wizards',
    TARGET_DIR / 'widgets',
    TARGET_DIR / 'utils',
    TARGET_DIR / 'main',
    TARGET_DIR / 'resources'  # For UI resources like icons
]

# Mapping of file types to target subdirectories
FILE_TYPE_MAPPING = {
    r'.*Dialog\.py$': 'dialogs',
    r'.*Wizard\.py$': 'wizards',
    r'.*Widget\.py$': 'widgets',
    r'creepy.*\.py$': 'main',
    r'.*\.ui$': 'resources'
}

def ensure_target_dirs_exist():
    """Create the target directory structure if it doesn't exist"""
    for dir_path in TARGET_SUBDIRS:
        dir_path.mkdir(parents=True, exist_ok=True)
    print(f"Created target directory structure in {TARGET_DIR}")

def determine_target_subdir(filename):
    """Determine which subdirectory a file belongs in based on its name"""
    for pattern, subdir in FILE_TYPE_MAPPING.items():
        if re.match(pattern, filename):
            return subdir
    return 'main'  # Default location

def process_python_file(source_path, target_path):
    """Process a Python file, updating imports if necessary"""
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update imports from components/, gui/ or ui/ to ui/
    content = re.sub(r'from (components|gui|ui)\.', r'from ui.', content)
    content = re.sub(r'import (components|gui|ui)\.', r'import ui.', content)
    
    # Add note about file relocation
    if not content.startswith('"""'):
        # If no docstring, add a comment
        content = f"# Note: This file was moved from {source_path.relative_to(PROJECT_ROOT)} to ui/\n\n" + content
    
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)

def copy_file(source_path, target_subdir):
    """Copy a file to the appropriate target subdirectory"""
    target_path = TARGET_DIR / target_subdir / source_path.name
    
    # Don't overwrite newer files
    if target_path.exists() and target_path.stat().st_mtime > source_path.stat().st_mtime:
        print(f"Skipping {source_path.name} (target is newer)")
        return
    
    print(f"Copying {source_path} -> {target_path}")
    
    # Process Python files to update imports
    if source_path.suffix == '.py':
        process_python_file(source_path, target_path)
    else:
        shutil.copy2(source_path, target_path)

def create_init_files():
    """Create __init__.py files in all directories"""
    for subdir in TARGET_SUBDIRS:
        init_file = subdir / '__init__.py'
        if not init_file.exists():
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(f'"""\n{subdir.name} module for CreepyAI UI\n"""\n\n')
            print(f"Created {init_file}")
    
    # Create main __init__.py
    main_init = TARGET_DIR / '__init__.py'
    if not main_init.exists():
        with open(main_init, 'w', encoding='utf-8') as f:
            f.write('"""\nCreepyAI UI module\n"""\n\n')
            
            # Import commonly used classes for convenience
            f.write('# Import common classes for convenience\n')
            f.write('from ui.main.creepyai_gui import CreepyAIApp\n\n')
            
            f.write('__all__ = ["CreepyAIApp", "dialogs", "wizards", "widgets", "utils", "main"]\n')
        print(f"Created {main_init}")

def merge_directories():
    """Merge UI-related files from source directories into the unified ui/ directory"""
    ensure_target_dirs_exist()
    
    for source_dir in SOURCE_DIRS:
        if not source_dir.exists():
            print(f"Source directory {source_dir} does not exist, skipping")
            continue
            
        for file_path in source_dir.glob('**/*'):
            # Skip directories, __pycache__, etc.
            if file_path.is_dir() or '__pycache__' in str(file_path):
                continue
                
            # Only copy Python files, UI files, and other UI resources
            if file_path.suffix not in ['.py', '.ui', '.qrc', '.json']:
                continue
                
            # Determine target subdirectory
            target_subdir = determine_target_subdir(file_path.name)
            copy_file(file_path, target_subdir)
    
    create_init_files()
    print("UI folders merge complete!")

def update_project_imports():
    """Update imports in the project to use the new ui module"""
    for py_file in PROJECT_ROOT.glob('**/*.py'):
        # Skip the ui directory itself and any __pycache__
        if 'ui/' in str(py_file) or '__pycache__' in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Skip if file doesn't import from components, gui or ui
            if not re.search(r'(from|import) (components|gui|ui)\.', content):
                continue
                
            # Update imports
            new_content = re.sub(r'from (components|gui)\.', r'from ui.', content)
            new_content = re.sub(r'import (components|gui)\.', r'import ui.', new_content)
            
            if new_content != content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated imports in {py_file}")
                
        except Exception as e:
            print(f"Error processing {py_file}: {e}")

if __name__ == "__main__":
    print("Starting UI folders merge...")
    merge_directories()
    update_project_imports()
    
    # Note: This doesn't delete the original directories
    # That should be done manually after verifying everything works
    print("\nNext steps:")
    print("1. Test the application to make sure everything works properly")
    print("2. When confirmed, manually delete the empty components/ and gui/ directories")
