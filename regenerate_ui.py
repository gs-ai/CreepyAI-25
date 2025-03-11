#!/usr/bin/env python3
"""
Script to manually regenerate UI file from XML
"""
import os
import subprocess
import sys

def regenerate_ui():
    try:
        ui_file = "app/gui/ui/creepyai_mainwindow.ui"
        py_file = "app/gui/ui/creepyai_mainwindow_ui.py"
        
        if not os.path.exists(ui_file):
            print(f"Error: UI file {ui_file} not found")
            return False
            
        # Run pyuic5 to generate the Python UI file
        result = subprocess.run(['pyuic5', '-o', py_file, ui_file], 
                               check=True, 
                               capture_output=True, 
                               text=True)
        print(f"UI file generated successfully: {py_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating UI file: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == '__main__':
    success = regenerate_ui()
    sys.exit(0 if success else 1)
