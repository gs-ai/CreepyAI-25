#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup CreepyAI resources

This script ensures all resource directories and files are properly set up.
"""

import os
import shutil
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def create_directory_structure():
    """Create necessary directories for resources."""
    directories = [
        'resources/icons',
        'resources/styles',
        'resources/ui',
        'resources/templates',
        'resources/data',
        'gui/ui'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    return True

def create_placeholder_files():
    """Create placeholder files where necessary."""
    # Check if we need to create icons
    if not os.path.exists('resources/icons/app_icon.png'):
        try:
            if os.path.exists('create_placeholder_icons.py'):
                subprocess.run(['python', 'create_placeholder_icons.py'], check=True)
                logger.info("Created placeholder icons")
            else:
                logger.warning("create_placeholder_icons.py not found, skipping icon creation")
        except subprocess.CalledProcessError:
            logger.error("Failed to create placeholder icons")
            return False
    
    # Create empty files where needed
    empty_files = [
        'gui/ui/__init__.py'
    ]
    
    for file_path in empty_files:
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write('"""UI module for CreepyAI."""\n')
            logger.info(f"Created file: {file_path}")
    
    return True

def create_resource_file():
    """Create resource QRC file if it doesn't exist."""
    qrc_file = 'resources/creepy_resources.qrc'
    
    if not os.path.exists(qrc_file):
        with open(qrc_file, 'w') as f:
            f.write('''<!DOCTYPE RCC>
<RCC version="1.0">
    <qresource prefix="icons">
        <file alias="app_icon.png">icons/app_icon.png</file>
        <file alias="new.png">icons/new.png</file>
        <file alias="open.png">icons/open.png</file>
        <file alias="save.png">icons/save.png</file>
        <file alias="settings.png">icons/settings.png</file>
    </qresource>
    
    <qresource prefix="styles">
        <file>styles/dark.qss</file>
        <file>styles/light.qss</file>
        <file>styles/base.qss</file>
    </qresource>
    
    <qresource prefix="ui">
        <file>ui/plugin_config_dialog.ui</file>
        <file>ui/settings_dialog.ui</file>
        <file>ui/about_dialog.ui</file>
    </qresource>
</RCC>
''')
        logger.info(f"Created resource file: {qrc_file}")
    
    return True

def create_compile_resources_script():
    """Create a shell script to compile resources."""
    script_file = 'resources/compile_resources.sh'
    
    if not os.path.exists(script_file):
        with open(script_file, 'w') as f:
            f.write('''#!/bin/bash

# Compile resources for CreepyAI
# This script compiles QRC and UI files

echo "======================================"
echo "CreepyAI - Resource Compiler"
echo "======================================"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/.."

# Create placeholder icons if they don't exist
echo "Creating placeholder icons..."
python create_placeholder_icons.py

# Create necessary directories
echo "Creating directory structure..."
mkdir -p resources/templates
mkdir -p resources/data
mkdir -p gui/ui

# Compile QRC file
echo "Compiling Qt resources..."
if command -v pyrcc5 &> /dev/null; then
    pyrcc5 -o resources/creepy_resources_rc.py resources/creepy_resources.qrc
    if [ $? -eq 0 ]; then
        echo "✓ Qt resources compiled successfully"
    else
        echo "✗ Failed to compile Qt resources"
        exit 1
    fi
else
    echo "✗ pyrcc5 command not found. Is PyQt5 installed?"
    exit 1
fi

# Compile UI files
echo "Compiling UI files..."
python compile_ui.py
if [ $? -eq 0 ]; then
    echo "✓ UI files compiled successfully"
else
    echo "✗ Failed to compile UI files"
    exit 1
fi

echo "Resource compilation completed successfully"
''')
        os.chmod(script_file, 0o755)
        logger.info(f"Created script: {script_file}")
    
    return True

def compile_resources():
    """Compile resource files."""
    # First make sure we have the QRC file
    create_resource_file()
    
    # Try to compile Qt resources
    qrc_file = 'resources/creepy_resources.qrc'
    py_file = 'resources/creepy_resources_rc.py'
    
    try:
        logger.info("Compiling Qt resources...")
        result = subprocess.run(['pyrcc5', '-o', py_file, qrc_file], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Qt resources compiled successfully")
        else:
            logger.error(f"Failed to compile Qt resources: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error compiling Qt resources: {e}")
        logger.warning("Skipping Qt resource compilation, you'll need to compile manually")
    
    # Next compile UI files if compile_ui.py exists
    if os.path.exists('compile_ui.py'):
        try:
            logger.info("Compiling UI files...")
            result = subprocess.run(['python', 'compile_ui.py'], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("UI files compiled successfully")
            else:
                logger.error(f"Failed to compile UI files: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error compiling UI files: {e}")
            logger.warning("Skipping UI compilation, you'll need to compile manually")
    else:
        logger.warning("compile_ui.py not found, skipping UI compilation")
    
    return True

def create_default_style_files():
    """Create default style files if they don't exist."""
    # Check if style files exist
    style_files = {
        'resources/styles/dark.qss': """/* Dark theme for CreepyAI */

QMainWindow, QDialog {
    background-color: #2d2d2d;
    color: #f0f0f0;
}

QWidget {
    background-color: #2d2d2d;
    color: #f0f0f0;
}

/* ...other dark theme styles... */
""",
        'resources/styles/light.qss': """/* Light theme for CreepyAI */

QMainWindow, QDialog {
    background-color: #f5f5f5;
    color: #333333;
}

QWidget {
    background-color: #f5f5f5;
    color: #333333;
}

/* ...other light theme styles... */
""",
        'resources/styles/base.qss': """/* Base styles for CreepyAI */

/* Common spacing and sizing */
QWidget {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 12px;
}

/* ...other base styles... */
"""
    }
    
    for file_path, content in style_files.items():
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
            logger.info(f"Created style file: {file_path}")
    
    return True

def create_default_ui_files():
    """Create basic UI files if they don't exist."""
    # Check if UI files exist
    ui_files = {
        'resources/ui/about_dialog.ui': """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>AboutDialog</class>
 <widget class="QDialog" name="AboutDialog">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>400</width>
    <height>300</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>About CreepyAI</string>
  </property>
  <!-- Basic about dialog content -->
 </widget>
</ui>
""",
        'resources/ui/settings_dialog.ui': """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>SettingsDialog</class>
 <widget class="QDialog" name="SettingsDialog">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>500</width>
    <height>400</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Settings</string>
  </property>
  <!-- Basic settings dialog content -->
 </widget>
</ui>
""",
        'resources/ui/plugin_config_dialog.ui': """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>PluginConfigDialog</class>
 <widget class="QDialog" name="PluginConfigDialog">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>500</width>
    <height>400</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Plugin Configuration</string>
  </property>
  <!-- Basic plugin config dialog content -->
 </widget>
</ui>
"""
    }
    
    for file_path, content in ui_files.items():
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
            logger.info(f"Created UI file: {file_path}")
    
    return True

def main():
    """Main function."""
    print("CreepyAI Resource Setup")
    print("=" * 50)
    
    # Create directory structure
    if not create_directory_structure():
        return 1
    
    # Create placeholder files
    if not create_placeholder_files():
        return 1
    
    # Create resource QRC file
    if not create_resource_file():
        return 1
    
    # Create compile resources script
    if not create_compile_resources_script():
        return 1
    
    # Create default style files
    if not create_default_style_files():
        return 1
    
    # Create default UI files
    if not create_default_ui_files():
        return 1
    
    # Compile resources
    if not compile_resources():
        print("Resource setup completed with warnings.")
        print("You may need to manually compile resources.")
        print("Run: chmod +x resources/compile_resources.sh && ./resources/compile_resources.sh")
        return 1
    
    print("Resource setup completed successfully!")
    print("You can now run the application with: ./launch_macos.sh")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
