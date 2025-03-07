#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Environment Information Tool
Display information about Python environment and system
"""

import os
import sys
import platform
import subprocess
import pkg_resources

def get_python_info():
    print("\nPython Information:")
    print(f"  Python Version: {platform.python_version()}")
    print(f"  Python Path: {sys.executable}")
    print(f"  Platform: {platform.platform()}")
    print(f"  Working Directory: {os.getcwd()}")

def get_package_versions():
    print("\nInstalled Packages:")
    
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
    print("\nSystem Information:")
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
    print("""
    ╔═══════════════════════════════════════════╗
    ║            CreepyAI Environment           ║
    ╚═══════════════════════════════════════════╝
    """)

def main():
    print_banner()
    get_python_info()
    get_package_versions()
    get_system_info()
    print("")

if __name__ == "__main__":
    main()
