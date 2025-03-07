#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup script for CreepyAI tools
This script ensures all required directories and permissions are set correctly
"""

import os
import sys
import shutil
import stat
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ToolsSetup')

# Get script directory and project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def ensure_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Created directory: {path}")
    else:
        logger.info(f"Directory already exists: {path}")

def fix_permissions():
    """Fix permissions for all scripts in tools directory"""
    logger.info("Fixing script permissions...")
    
    # Make all scripts in tools directory executable
    tools_dir = SCRIPT_DIR
    for filename in os.listdir(tools_dir):
        filepath = os.path.join(tools_dir, filename)
        if filename.endswith(('.py', '.sh')) and os.path.isfile(filepath):
            current_mode = os.stat(filepath).st_mode
            os.chmod(filepath, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            logger.info(f"Made executable: {filename}")
    
    # Fix main creepyai script in project root
    creepyai_script = os.path.join(PROJECT_ROOT, 'creepyai')
    if os.path.exists(creepyai_script):
        current_mode = os.stat(creepyai_script).st_mode
        os.chmod(creepyai_script, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        logger.info(f"Made executable: {os.path.basename(creepyai_script)}")

def create_readme():
    """Create README.md for tools directory if it doesn't exist"""
    readme_path = os.path.join(SCRIPT_DIR, 'README.md')
    if not os.path.exists(readme_path):
        with open(readme_path, 'w') as f:
            f.write("""# CreepyAI Tools

This directory contains utility scripts for CreepyAI.

## Available Tools

- `creepyai_cli.py` - Main command line interface
- `plugin_fixer.py` - Tool to scan and fix plugin issues
- `test_qt.py` - Test PyQt5 environment 
- `test_plugins.py` - Test plugin discovery
- `run_creepyai.py` - Python launcher for CreepyAI
- `run_creepyai.sh` - Shell launcher for CreepyAI
- `run_tkinter_ui.sh` - Launcher for Tkinter UI version
- `run_plugin_cli.py` - CLI for plugins
- `setup_tools.py` - This setup script

## Usage

Run tools from the project root directory:

```bash
# Fix permissions first
./tools/setup_tools.py

# Use the CLI
./creepyai help

# Or run individual tools
./tools/test_plugins.py
```
""")
        logger.info(f"Created README.md")

def check_dependencies():
    """Check and install basic dependencies"""
    logger.info("Checking dependencies...")
    
    try:
        import pip
        
        requirements = [
            "PyQt5",
            "yapsy",
        ]
        
        for req in requirements:
            logger.info(f"Checking {req}...")
            try:
                __import__(req.lower())
                logger.info(f"  {req} is installed")
            except ImportError:
                logger.info(f"  Installing {req}...")
                subprocess.run([sys.executable, "-m", "pip", "install", req])
    
    except ImportError:
        logger.warning("pip not available, skipping dependency check")

def create_launcher():
    """Create/update main launcher script"""
    launcher_path = os.path.join(PROJECT_ROOT, 'creepyai')
    with open(launcher_path, 'w') as f:
        f.write("""#!/bin/bash
# Quick launcher script for CreepyAI

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the CLI tool
PYTHON="python3"
if ! command -v $PYTHON &>/dev/null; then
    PYTHON="python"
fi

$PYTHON "$SCRIPT_DIR/tools/creepyai_cli.py" "$@"
""")
    
    # Make executable
    os.chmod(launcher_path, 0o755)
    logger.info(f"Created launcher script: {launcher_path}")

def create_env_info():
    """Create an environment info script"""
    env_path = os.path.join(SCRIPT_DIR, 'env_info.py')
    with open(env_path, 'w') as f:
        f.write("""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Environment Information Tool
Display information about Python environment and system
\"\"\"

import os
import sys
import platform
import subprocess
import pkg_resources

def get_python_info():
    print("\\nPython Information:")
    print(f"  Python Version: {platform.python_version()}")
    print(f"  Python Path: {sys.executable}")
    print(f"  Platform: {platform.platform()}")
    print(f"  Working Directory: {os.getcwd()}")

def get_package_versions():
    print("\\nInstalled Packages:")
    
    packages = [
        "PyQt5", "PyQtWebEngine", "yapsy", "folium", 
        "psutil", "requests", "pyyaml"
    ]
    
    for package in packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"  {package}: {version}")
        except pkg_resources.DistributionNotFound:
            print(f"  {package}: Not installed")

def get_system_info():
    print("\\nSystem Information:")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Machine: {platform.machine()}")
    
    # Check for Qt installation
    try:
        from PyQt5.QtCore import QT_VERSION_STR
        print(f"  Qt Version: {QT_VERSION_STR}")
    except ImportError:
        print("  Qt Version: Not found")
    
    # Check if GUI environment is available
    display = os.environ.get('DISPLAY', 'Not set')
    print(f"  DISPLAY: {display}")

def print_banner():
    print(\"\"\"
    ╔═══════════════════════════════════════════╗
    ║            CreepyAI Environment           ║
    ╚═══════════════════════════════════════════╝
    \"\"\")

def main():
    print_banner()
    get_python_info()
    get_package_versions()
    get_system_info()
    print("")

if __name__ == "__main__":
    main()
""")
    
    # Make executable
    os.chmod(env_path, 0o755)
    logger.info(f"Created environment info script: {env_path}")

def print_help():
    """Print help information"""
    logger.info("\nSetup complete! You can now run:")
    logger.info("  ./creepyai help       - To see available commands")
    logger.info("  ./tools/plugin_fixer.py --scan  - To scan for plugin issues")
    logger.info("  ./tools/plugin_fixer.py --fix   - To try fixing plugin issues")
    logger.info("  ./tools/env_info.py            - To see environment information")

def main():
    """Main entry point"""
    print("Setting up CreepyAI tools...")
    
    # Ensure directories exist
    ensure_directory(SCRIPT_DIR)
    ensure_directory(os.path.join(PROJECT_ROOT, 'plugins'))
    
    # Fix permissions
    fix_permissions()
    
    # Create/update files
    create_readme()
    create_launcher()
    create_env_info()
    
    # Check dependencies
    check_dependencies()
    
    # Print help
    print_help()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
