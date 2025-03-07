#!/usr/bin/env python
"""
Debug Environment for CreepyAI

Performs a series of checks to verify the environment and diagnose issues.
"""
import os
import sys
import platform
import importlib
import logging
import json
from importlib import import_module

# Add project directories to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'core'))
sys.path.insert(0, os.path.join(BASE_DIR, 'models'))
sys.path.insert(0, os.path.join(BASE_DIR, 'utilities'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(BASE_DIR, 'debug.log')
)
logger = logging.getLogger('CreepyAI Debug')

def check_system_info():
    """Check system information"""
    print("\n=== System Information ===")
    print(f"Python Version: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.architecture()[0]}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Base Directory: {BASE_DIR}")

def check_module(module_name):
    """Check if a module can be imported and get its version if available"""
    try:
        module = import_module(module_name)
        version = getattr(module, '__version__', 'Unknown')
        location = getattr(module, '__file__', 'Unknown')
        return True, version, location
    except ImportError as e:
        return False, str(e), None

def check_dependencies():
    """Check project dependencies"""
    print("\n=== Dependency Check ===")
    
    # Essential modules
    essential_modules = [
        "PyQt5", "PyQt5.QtCore", "PyQt5.QtWidgets", "PyQt5.QtWebEngineWidgets", 
        "tkinter", "json", "logging", "configparser", "datetime", "csv"
    ]
    
    # Optional modules
    optional_modules = [
        "folium", "simplekml", "Pillow", "yapsy", "matplotlib"
    ]
    
    print("\nEssential Modules:")
    for module in essential_modules:
        success, version, location = check_module(module)
        status = "✅ Installed" if success else "❌ Missing"
        print(f"{module}: {status} | {version}")
        if location:
            print(f"    Location: {location}")
    
    print("\nOptional Modules:")
    for module in optional_modules:
        success, version, location = check_module(module)
        status = "✅ Installed" if success else "⚠️ Not installed"
        print(f"{module}: {status} | {version}")
        if location:
            print(f"    Location: {location}")

def check_project_structure():
    """Check if key project files exist"""
    print("\n=== Project Structure ===")
    
    key_files = [
        "launch_creepyai.py",
        "CreepyMain.py",
        "creepyai_gui.py",
        "core/ui_bridge.py",
        "core/config_manager.py",
        "models/PluginManager.py",
        "utilities/ExportUtils.py",
        "plugins/base_plugin.py"
    ]
    
    for file_path in key_files:
        full_path = os.path.join(BASE_DIR, file_path)
        exists = os.path.exists(full_path)
        status = "✅ Found" if exists else "❌ Missing"
        print(f"{file_path}: {status}")

def check_ui_compatibility():
    """Check UI compatibility"""
    print("\n=== UI Compatibility Check ===")
    
    # Check PyQt5
    pyqt_available = check_module("PyQt5.QtWidgets")[0] and check_module("PyQt5.QtWebEngineWidgets")[0]
    print(f"PyQt5 UI: {'✅ Available' if pyqt_available else '❌ Not available'}")
    
    # Check Tkinter
    tkinter_available = check_module("tkinter")[0]
    print(f"Tkinter UI: {'✅ Available' if tkinter_available else '❌ Not available'}")
    
    # Check UI Bridge
    try:
        from core.ui_bridge import UIBridge
        bridge = UIBridge()
        print(f"UI Bridge: ✅ Working | Detected UI: {bridge.ui_type}")
    except Exception as e:
        print(f"UI Bridge: ❌ Error: {str(e)}")

def check_plugin_system():
    """Check if the plugin system is working"""
    print("\n=== Plugin System Check ===")
    
    try:
        # Try to import the plugin manager
        success = False
        
        # Try models.PluginManager first
        try:
            from models.PluginManager import PluginManager
            pm = PluginManager.get_instance()
            pm.set_plugin_paths([os.path.join(BASE_DIR, 'plugins')])
            plugins = pm.discover_plugins()
            success = True
            print(f"Plugin Manager (models): ✅ Working | Found {len(plugins)} plugins")
            print("Plugins found:")
            for plugin_name in pm.get_plugin_names():
                print(f"  - {plugin_name}")
        except ImportError:
            print("Plugin Manager (models): ❌ Import Error")
        
        # Try utilities.PluginManager as fallback
        if not success:
            try:
                from utilities.PluginManager import PluginManager
                pm = PluginManager.get_instance()
                pm.set_plugin_paths([os.path.join(BASE_DIR, 'plugins')])
                plugins = pm.discover_plugins()
                print(f"Plugin Manager (utilities): ✅ Working | Found {len(plugins)} plugins")
                print("Plugins found:")
                for plugin_name in pm.get_plugin_names():
                    print(f"  - {plugin_name}")
            except Exception as e:
                print(f"Plugin Manager (utilities): ❌ Error: {str(e)}")
    
    except Exception as e:
        print(f"Plugin System: ❌ Error: {str(e)}")

def check_configuration():
    """Check if the configuration system is working"""
    print("\n=== Configuration System Check ===")
    
    try:
        # Try to import the config manager
        from core.config_manager import ConfigManager
        config = ConfigManager()
        
        # Get configuration directory
        config_dir = config._get_config_dir()
        config_file = config.config_file
        
        print(f"Config Directory: {config_dir}")
        print(f"Config File: {config_file}")
        print(f"Config File Exists: {'✅ Yes' if os.path.exists(config_file) else '❌ No'}")
        
        # Check if we can read and write config
        try:
            test_key = "test_debug_key"
            test_value = f"test_value_{os.urandom(4).hex()}"
            
            # Set a test value
            config.set(test_key, test_value)
            
            # Read it back
            read_value = config.get(test_key)
            
            if read_value == test_value:
                print("Config Read/Write: ✅ Working")
            else:
                print(f"Config Read/Write: ❌ Error: Value mismatch ({read_value} != {test_value})")
                
            # Clean up test key
            config.config.pop(test_key, None)
            config.save_config()
            
        except Exception as e:
            print(f"Config Read/Write: ❌ Error: {str(e)}")
            
    except Exception as e:
        print(f"Configuration System: ❌ Error: {str(e)}")

def main():
    """Main entry point"""
    print("CreepyAI Environment Debug Tool")
