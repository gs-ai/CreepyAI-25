#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CreepyAI Environment Test Script
================================

This script tests if all required components are installed
and functioning correctly for the CreepyAI application.
"""

import sys
import os
import platform

def check_python():
    """Test Python version"""
    print(f"Python version: {platform.python_version()}")
    return sys.version_info >= (3, 6)

def check_module(module_name):
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def test_pyqt5():
    """Test PyQt5 installation"""
    if check_module('PyQt5'):
        try:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import QT_VERSION_STR
            print(f"PyQt5 version: {QT_VERSION_STR}")
            return True
        except Exception as e:
            print(f"PyQt5 import error: {str(e)}")
            return False
    return False

def test_file_access():
    """Test if we can access and create files"""
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CreepyAI-25', 'creepy')
    
    if not os.path.exists(app_path):
        print(f"Warning: Application path not found at {app_path}")
        return False
        
    # Test if we can create a file
    try:
        test_file = os.path.join(app_path, 'test_file.txt')
        with open(test_file, 'w') as f:
            f.write('Test file')
        
        if os.path.exists(test_file):
            os.remove(test_file)
            return True
        return False
    except Exception as e:
        print(f"File access error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("CreepyAI Environment Test")
    print("========================\n")
    
    tests = [
        ("Python 3.6+", check_python),
        ("PyQt5", test_pyqt5),
        ("yapsy", lambda: check_module('yapsy')),
        ("configobj", lambda: check_module('configobj')),
        ("PIL/Pillow", lambda: check_module('PIL')),
        ("File Access", test_file_access)
    ]
    
    all_passed = True
    
    for name, test_func in tests:
        try:
            result = test_func()
            status = "PASS" if result else "FAIL"
            if not result:
                all_passed = False
        except Exception as e:
            status = "ERROR"
            print(f"  Exception: {str(e)}")
            all_passed = False
            
        print(f"{name:20s}: {status}")
    
    print("\nOverall result:", "PASS" if all_passed else "FAIL")
    
    if not all_passed:
        print("\nSome tests failed. Please ensure all requirements are installed:")
        print("  conda install -c conda-forge pyqt")
        print("  pip install yapsy configobj Pillow")
    else:
        print("\nAll tests passed! You can run CreepyAI with:")
        print("  python launch_creepyai.py")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
