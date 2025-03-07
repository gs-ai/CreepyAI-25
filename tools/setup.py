#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup script for CreepyAI
"""

import os
import sys
import subprocess
import stat

def check_environment():
    """Check if running in a virtual environment"""
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        print("⚠️ WARNING: You are not running in a virtual environment!")
        response = input("Would you like to continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting. Please create and activate a virtual environment before running setup.")
            sys.exit(1)

def install_requirements():
    """Install requirements from requirements.txt"""
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        print("📦 Installing dependencies from requirements.txt...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_path])
        print("✅ Dependencies installed successfully!")
    else:
        print("❌ requirements.txt not found!")

def main():
    """Main entry point for setup"""
    print("Setting up CreepyAI...")
    
    # Get project root directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to project directory
    os.chdir(project_dir)
    
    # Make sure tools directory exists
    tools_dir = os.path.join(project_dir, 'tools')
    if not os.path.exists(tools_dir):
        os.makedirs(tools_dir)
    
    # Run setup_tools.py if it exists
    setup_tools = os.path.join(tools_dir, 'setup_tools.py')
    if os.path.exists(setup_tools):
        # Make sure it's executable
        current_mode = os.stat(setup_tools).st_mode
        os.chmod(setup_tools, current_mode | stat.S_IXUSR)
        
        # Run the setup script
        subprocess.run([sys.executable, setup_tools])
    else:
        print(f"Setup tools script not found at {setup_tools}")
        print("Please make sure the tools directory is properly set up.")
    
    # Look for requirements.txt and install if found
    req_file = os.path.join(project_dir, 'requirements.txt')
    if os.path.exists(req_file):
        print("Installing requirements...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', req_file])
    
    print("\nSetup complete!")
    print("You can now run: ./creepyai help")

if __name__ == "__main__":
    check_environment()
    install_requirements()
    main()
