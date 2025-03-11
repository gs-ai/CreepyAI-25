#!/usr/bin/env python3
"""
Fix import paths for GUI components.
"""
import os
import sys
import shutil
import importlib

def create_ui_symlink():
    """Create a symlink to make ui module available."""
    src_dir = os.path.dirname(os.path.abspath(__file__))
    ui_dir = os.path.join(src_dir, 'ui')
    
    # For Python packages that might import 'ui' directly
    sys.path.insert(0, os.path.dirname(src_dir))
    
    # Create symlink for easier imports
    if not os.path.exists('ui') and os.path.exists(ui_dir):
        try:
            # On Unix-like systems, create a symbolic link
            if os.name == 'posix':
                target_path = os.path.join(os.getcwd(), 'ui')
                if not os.path.exists(target_path):
                    os.symlink(ui_dir, target_path)
                    print(f"Created symlink: {target_path} -> {ui_dir}")
            # On Windows, either copy or use directory junction
            else:
                if not os.path.exists('ui'):
                    shutil.copytree(ui_dir, 'ui')
                    print(f"Copied UI directory to {os.path.join(os.getcwd(), 'ui')}")
                    
            print("UI module is now accessible")
            return True
        except Exception as e:
            print(f"Error setting up UI symlink: {e}")
            return False
    return True

if __name__ == "__main__":
    create_ui_symlink()
