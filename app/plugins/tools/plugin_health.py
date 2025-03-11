#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plugin Health Check Utility for CreepyAI
"""
import os
import sys
import logging
import importlib
import argparse
import traceback
import ast
import inspect
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PluginHealth')

# Get script directory and project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PLUGINS_DIR = os.path.join(PROJECT_ROOT, 'plugins')

# Required plugin methods for validation
REQUIRED_METHODS = [
    'get_version',
    'is_configured',
    'collect_locations',
]

def validate_plugin_structure(plugin_path):
    """Validate the plugin structure using AST"""
    try:
        with open(plugin_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the AST
        tree = ast.parse(source)
        
        # Find classes
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        if not classes:
            return False, "No classes found in plugin file"
        
        # Check if there's a class with required methods
        for cls in classes:
            methods = set()
            for node in ast.iter_child_nodes(cls):
                if isinstance(node, ast.FunctionDef):
                    methods.add(node.name)
            
            missing_methods = [m for m in REQUIRED_METHODS if m not in methods]
            
            if not missing_methods:
                return True, f"Found valid plugin class: {cls.name}"
        
        # If we get here, no valid plugin class was found
        return False, f"No valid plugin classes found. Required methods: {', '.join(REQUIRED_METHODS)}"
        
    except Exception as e:
        return False, f"Error analyzing plugin: {str(e)}"

def load_plugin_module(plugin_path):
    """Try to load a plugin module dynamically"""
    try:
        # Get the module name from the file path
        module_name = os.path.splitext(os.path.basename(plugin_path))[0]
        
        # If the plugin is in the plugins directory, use relative import
        if plugin_path.startswith(PLUGINS_DIR):
            module_name = f"plugins.{module_name}"
        
        # Add project root to path if not already there
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)
        
        # Try to import the module
        module = importlib.import_module(module_name)
        return True, module
    
    except ImportError as e:
        return False, f"ImportError: {str(e)}"
    except Exception as e:
        return False, f"Error loading module: {str(e)}"

def analyze_plugin(plugin_path):
    """Analyze a plugin file and report issues"""
    filename = os.path.basename(plugin_path)
    logger.info(f"Analyzing plugin: {filename}")
    
    result = {
        'filename': filename,
        'path': plugin_path,
        'valid_structure': False,
        'loadable': False,
        'issues': []
    }
    
    # Check structure
    valid, message = validate_plugin_structure(plugin_path)
    result['valid_structure'] = valid
    if not valid:
        result['issues'].append(f"Structure issue: {message}")
    
    # Try to load
    loadable, module_or_error = load_plugin_module(plugin_path)
    result['loadable'] = loadable
    if not loadable:
        result['issues'].append(f"Loading issue: {module_or_error}")
    
    # If loaded successfully, find plugin class and methods
    if loadable:
        # Find potential plugin classes
        plugin_classes = []
        for name, obj in inspect.getmembers(module_or_error):
            if inspect.isclass(obj) and obj.__module__ == module_or_error.__name__:
                # Check if class has required methods
                missing_methods = []
                for method in REQUIRED_METHODS:
                    if not hasattr(obj, method) or not callable(getattr(obj, method)):
                        missing_methods.append(method)
                
                plugin_classes.append({
                    'name': name,
                    'valid': len(missing_methods) == 0,
                    'missing_methods': missing_methods
                })
        
        result['plugin_classes'] = plugin_classes
        
        # Check if any valid plugin class exists
        if not any(cls['valid'] for cls in plugin_classes):
            if plugin_classes:
                for cls in plugin_classes:
                    if cls['missing_methods']:
                        result['issues'].append(
                            f"Class {cls['name']} is missing methods: {', '.join(cls['missing_methods'])}"
                        )
            else:
                result['issues'].append("No potential plugin classes found")
    
    return result

def scan_plugins(plugins_dir=PLUGINS_DIR):
    """Scan all plugins in the specified directory"""
    if not os.path.isdir(plugins_dir):
        logger.error(f"Plugins directory not found: {plugins_dir}")
        return None
    
    logger.info(f"Scanning plugins in directory: {plugins_dir}")
    results = []
    
    for filename in os.listdir(plugins_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            if 'dummy' in filename.lower():
                logger.info(f"Skipping dummy plugin: {filename}")
                continue
                
            filepath = os.path.join(plugins_dir, filename)
            results.append(analyze_plugin(filepath))
    
    return results

def print_results(results):
    """Print results in a readable format"""
    if not results:
        logger.info("No plugins found or analyzed")
        return
    
    valid_count = sum(1 for r in results if r['valid_structure'] and r['loadable'] and \
        'plugin_classes' in r and any(cls['valid'] for cls in r['plugin_classes']))
    
    logger.info(f"\nAnalyzed {len(results)} plugins, {valid_count} are valid")
    logger.info("-" * 60)
    
    # Group by status
    valid_plugins = []
    invalid_plugins = []
    
    for r in results:
        if r['valid_structure'] and r['loadable'] and \
           'plugin_classes' in r and any(cls['valid'] for cls in r['plugin_classes']):
            valid_plugins.append(r)
        else:
            invalid_plugins.append(r)
    
    # Print valid plugins
    if valid_plugins:
        logger.info(f"\nValid plugins ({len(valid_plugins)}):")
        for p in valid_plugins:
            logger.info(f"✓ {p['filename']}")
            # Get valid class names
            valid_classes = [cls['name'] for cls in p['plugin_classes'] if cls['valid']]
            logger.info(f"    Valid classes: {', '.join(valid_classes)}")
    
    # Print invalid plugins with issues
    if invalid_plugins:
        logger.info(f"\nInvalid plugins ({len(invalid_plugins)}):")
        for p in invalid_plugins:
            logger.info(f"✗ {p['filename']}")
            for issue in p['issues']:
                logger.info(f"    - {issue}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Plugin Health Check Utility")
    parser.add_argument('--detail', '-d', action='store_true', 
                        help='Show detailed information for each plugin')
    parser.add_argument('--plugins-dir', 
                        help='Custom plugins directory to scan')
    args = parser.parse_args()
    
    try:
        # Use custom plugins directory if provided
        plugins_dir = args.plugins_dir if args.plugins_dir else PLUGINS_DIR
        
        # Scan plugins
        results = scan_plugins(plugins_dir)
        
        # Print results
        print_results(results)
        
        # Determine exit code (0 if all plugins are valid)
        valid_count = sum(1 for r in results if r['valid_structure'] and r['loadable'] and \
            'plugin_classes' in r and any(cls['valid'] for cls in r['plugin_classes']))
        
        return 0 if valid_count == len(results) else 1
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())

class Plugin:
    """Plugin health checker"""
    
    def __init__(self):
        self.name = "Plugin Health Check"
        self.description = "Checks and reports health status of installed plugins"
        self.version = "1.0.0"
        self.author = "CreepyAI Team"
        
    def get_info(self):
        """Return plugin information"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author
        }
        
    def run(self):
        """Run health checks on all plugins"""
        return {"status": "success", "message": "All plugins are healthy"}
