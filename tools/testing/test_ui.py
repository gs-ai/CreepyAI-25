#!/usr/bin/env python
"""
UI Tester for CreepyAI

Tests both PyQt5 and Tkinter UIs to ensure they work properly.
"""
import os
import sys
import importlib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ui_test.log'
)
logger = logging.getLogger('UI Tester')

# Add project directories to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'core'))

def test_pyqt():
    """Test PyQt5 UI"""
    print("Testing PyQt5 UI...")
    
    try:
        # Check if PyQt5 is installed
        import PyQt5
        print(f"PyQt5 version: {PyQt5.QtCore.QT_VERSION_STR}")
        
        # Try to create a basic window
        from PyQt5.QtWidgets import QApplication, QLabel
        app = QApplication([])
        label = QLabel("PyQt5 is working!")
        label.show()
        
        print("✅ PyQt5 UI test passed! Close the window to continue.")
        app.exec_()
        return True
    except ImportError as e:
        print(f"❌ PyQt5 is not installed: {e}")
        print("   Run 'tools/install_macos_deps.sh' to install PyQt5")
        return False
    except Exception as e:
        print(f"❌ Error testing PyQt5: {e}")
        return False

def test_tkinter():
    """Test Tkinter UI"""
    print("\nTesting Tkinter UI...")
    
    try:
        # Check if Tkinter is installed
        import tkinter as tk
        
        # Try to create a basic window
        root = tk.Tk()
        root.title("Tkinter Test")
        label = tk.Label(root, text="Tkinter is working!")
        label.pack(padx=20, pady=20)
        
        print("✅ Tkinter UI test passed! Close the window to continue.")
        root.mainloop()
        return True
    except ImportError as e:
        print(f"❌ Tkinter is not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing Tkinter: {e}")
        return False

def test_ui_bridge():
    """Test UI Bridge"""
    print("\nTesting UI Bridge...")
    
    try:
        from core.ui_bridge import UIBridge
        bridge = UIBridge()
        print(f"✅ UI Bridge is working | Detected UI: {bridge.ui_type}")
        return True
    except ImportError as e:
        print(f"❌ UI Bridge module not found: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing UI Bridge: {e}")
        return False

if __name__ == "__main__":
    print("CreepyAI UI Tester")
