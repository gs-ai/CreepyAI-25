#!/usr/bin/python
# -*- coding: utf-8 -*-

""""""""""""
Plugin Validator for CreepyAI""
Validates the structure and functionality of plugins""
""""""""""""
""
import os""
import sys""
import argparse
import inspect
import importlib
import json
import logging
from typing import Dict, List, Any, Optional, Set, Tuple

# Add parent directory to path so we can import plugins
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(SCRIPT_DIR)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import required modules
    from app.plugins.base_plugin import BasePlugin

# Configure logging
    logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("plugin_validator")

class PluginValidator:
        """"""""""""
        Validates CreepyAI plugins for proper structure, implementation, and behavior""
        """"""""""""
        ""
        def __init__(self, plugin_dir: str = None):""
        """"""""""""
        Initialize the validator""
        ""
        Args:""
        plugin_dir: Directory containing plugins (defaults to the plugins directory)
        """"""""""""
        self.plugin_dir = plugin_dir or os.path.join(parent_dir, 'plugins')""
        self.results = {}""
        ""
    def validate_plugin_module(self, module_path: str) -> Dict[str, Any]:
            """"""""""""
            Validate a plugin module file""
            ""
            Args:""
            module_path: Path to the plugin module file
            
        Returns:
                Dictionary with validation results
                """"""""""""
                if not os.path.exists(module_path):""
            return {""
            "valid": False,
            "errors": [f"File not found: {module_path}"]
            }
            
        # Extract module name from path
            module_name = os.path.basename(module_path)
        if module_name.endswith('.py'):
                module_name = module_name[:-3]
        
                result = {
                "name": module_name,
                "path": module_path,
                "valid": False,
                "errors": [],
                "warnings": [],
                "plugin_class": None,
                "implements": {}
                }
        
        try:
            # Import the module
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
            if not spec or not spec.loader:
                        result["errors"].append("Could not create module spec")
                    return result
                
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
            
            # Find plugin classes (those that inherit from BasePlugin)
                    plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj != BasePlugin:
                            plugin_classes.append((name, obj))
            
            if not plugin_classes:
                                result["errors"].append("No plugin classes found (must inherit from BasePlugin)")
                            return result
            
            # Use the first plugin class found
                            class_name, plugin_class = plugin_classes[0]
                            result["plugin_class"] = class_name
            
            # Try to instantiate the plugin
            try:
                                plugin_instance = plugin_class()
                
                # Check required attributes
                for attr in ['name', 'description', 'version']:
                    if not hasattr(plugin_instance, attr):
                                        result["errors"].append(f"Missing required attribute: {attr}")
                    else:
                                            result["implements"][attr] = getattr(plugin_instance, attr)
                
                # Check required methods
                for method_name in ['collect_locations', 'is_configured', 'get_configuration_options']:
                    if not hasattr(plugin_instance, method_name) or not callable(getattr(plugin_instance, method_name)):
                                                    result["errors"].append(f"Missing required method: {method_name}")
                    else:
                                                        result["implements"][method_name] = True
                
                # Check configuration
                                                        config_status, config_message = plugin_instance.is_configured()
                                                        result["configured"] = config_status
                                                        result["config_message"] = config_message
                
                # Check docstrings
                if not plugin_class.__doc__:
                                                            result["warnings"].append("Missing class docstring")
                
                for method_name in ['collect_locations', 'is_configured', 'get_configuration_options']:
                                                                method = getattr(plugin_instance, method_name, None)
                    if method and not method.__doc__:
                                                                    result["warnings"].append(f"Missing docstring for method: {method_name}")
                
            except Exception as e:
                                                                        result["errors"].append(f"Error instantiating plugin class: {str(e)}")
                                                                    return result
            
            # If we got here with no errors, the plugin is valid
            if not result["errors"]:
                                                                        result["valid"] = True
                
                                                                    return result
            
        except Exception as e:
                                                                        result["errors"].append(f"Error validating plugin module: {str(e)}")
                                                                    return result
    
    def validate_all_plugins(self) -> Dict[str, Dict[str, Any]]:
                                                                        """"""""""""
                                                                        Validate all plugins in the plugin directory""
                                                                        ""
                                                                        Returns:""
                                                                        Dictionary mapping plugin names to validation results
                                                                        """"""""""""
                                                                        results = {}""
                                                                        ""
        # Find all Python files in the plugin directory""
        for file_name in os.listdir(self.plugin_dir):
            if file_name.endswith('.py') and not file_name.startswith('__'):
                                                                                file_path = os.path.join(self.plugin_dir, file_name)
                                                                                plugin_name = file_name[:-3]
                                                                                results[plugin_name] = self.validate_plugin_module(file_path)
        
                                                                                self.results = results
                                                                            return results
    
    def print_validation_report(self) -> None:
                                                                                """"""""""""
                                                                                Print a validation report for all plugins""
                                                                                """"""""""""
                                                                                if not self.results:""
                                                                                self.validate_all_plugins()""
                                                                                ""
                                                                                valid_count = sum(1 for result in self.results.values() if result["valid"])
                                                                                total_count = len(self.results)
        
                                                                                print(f"\n===== Plugin Validation Report =====")
                                                                                print(f"Valid plugins: {valid_count}/{total_count}\n")
        
        for plugin_name, result in sorted(self.results.items()):
                                                                                    status = "✅ VALID" if result["valid"] else "❌ INVALID"
                                                                                    print(f"{plugin_name}: {status}")
            
            if result.get("implements", {}).get("name"):
                                                                                        print(f"  Name: {result['implements']['name']}")
                
            if result.get("implements", {}).get("version"):
                                                                                            print(f"  Version: {result['implements']['version']}")
                
            if "configured" in result:
                                                                                                config_status = "Configured" if result["configured"] else "Not configured"
                                                                                                print(f"  Status: {config_status}")
                                                                                                print(f"  Message: {result.get('config_message', '')}")
            
            if result["errors"]:
                                                                                                    print("  Errors:")
                for error in result["errors"]:
                                                                                                        print(f"    - {error}")
            
            if result["warnings"]:
                                                                                                            print("  Warnings:")
                for warning in result["warnings"]:
                                                                                                                print(f"    - {warning}")
                    
                                                                                                                print()
    
    def export_validation_results(self, output_path: str) -> bool:
                                                                                                                    """"""""""""
                                                                                                                    Export validation results to a JSON file""
                                                                                                                    ""
                                                                                                                    Args:""
                                                                                                                    output_path: Path to output file
            
        Returns:
                                                                                                                        True if successful, False otherwise
                                                                                                                        """"""""""""
                                                                                                                        if not self.results:""
                                                                                                                        self.validate_all_plugins()""
                                                                                                                        ""
        try:
            with open(output_path, 'w') as f:
                                                                                                                                json.dump(self.results, f, indent=2)
                                                                                                                            return True
        except Exception as e:
                                                                                                                                logger.error(f"Error exporting validation results: {e}")
                                                                                                                            return False
            
def main():
                                                                                                                                """Main function for running the validator from command line"""""""""""
                                                                                                                                parser = argparse.ArgumentParser(description="Validate CreepyAI plugins")
                                                                                                                                parser.add_argument("-d", "--dir", help="Plugin directory path")
                                                                                                                                parser.add_argument("-o", "--output", help="Output JSON file path")
                                                                                                                                parser.add_argument("-p", "--plugin", help="Validate a specific plugin")
                                                                                                                                args = parser.parse_args()
    
                                                                                                                                validator = PluginValidator(args.dir)
    
    if args.plugin:
        # Validate a specific plugin
                                                                                                                                    plugin_path = args.plugin
        if not os.path.isabs(plugin_path):
                                                                                                                                        plugin_path = os.path.join(validator.plugin_dir, args.plugin)
        if not plugin_path.endswith('.py'):
                                                                                                                                            plugin_path += '.py'
            
                                                                                                                                            result = validator.validate_plugin_module(plugin_path)
                                                                                                                                            validator.results = {args.plugin: result}
    else:
        # Validate all plugins
                                                                                                                                                validator.validate_all_plugins()
    
                                                                                                                                                validator.print_validation_report()
    
    if args.output:
        if validator.export_validation_results(args.output):
                                                                                                                                                        print(f"Exported validation results to {args.output}")
        else:
                                                                                                                                                            print(f"Failed to export validation results to {args.output}")

if __name__ == "__main__":
                                                                                                                                                                main()
