#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Command-line utility for managing CreepyAI plugins
"""
import os
import sys
import argparse
import logging
import json
import yaml
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class Plugin:
    """Plugin management tool"""
    
    def __init__(self):
        self.name = "Plugin Manager"
        self.description = "Command-line utility for managing plugins"
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
        
    def run(self, args=None):
        """Run the plugin manager with the given arguments"""
        return {"status": "success", "message": "Plugin manager executed successfully"}

# Add the parent directory to the path so we can import the plugins package
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(SCRIPT_DIR))

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def create_arg_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser"""
    parser = argparse.ArgumentParser(
        description="CreepyAI Plugin Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available plugins')
    list_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed information')
    list_parser.add_argument('-t', '--type', help='Filter by plugin type')
    list_parser.add_argument('-c', '--capability', help='Filter by plugin capability')
    list_parser.add_argument('-f', '--format', choices=['text', 'json', 'yaml'], default='text', 
        help='Output format (default: text)')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show detailed information about a plugin')
    info_parser.add_argument('plugin_id', help='ID of the plugin')
    info_parser.add_argument('-f', '--format', choices=['text', 'json', 'yaml'], default='text', 
        help='Output format (default: text)')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a plugin')
    run_parser.add_argument('plugin_id', help='ID of the plugin')
    run_parser.add_argument('-t', '--target', required=True, help='Target for the plugin')
    run_parser.add_argument('-o', '--output', help='Output file for results')
    run_parser.add_argument('-f', '--format', choices=['json', 'yaml', 'csv'], default='json',
        help='Output format (default: json)')
    run_parser.add_argument('-c', '--config', help='Configuration file for the plugin')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test a plugin')
    test_parser.add_argument('plugin_id', help='ID of the plugin')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install a plugin')
    install_parser.add_argument('source', help='Plugin source (file, directory, or URL)')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new plugin')
    create_parser.add_argument('plugin_id', help='ID for the new plugin')
    create_parser.add_argument('-t', '--template', choices=['basic', 'social', 'network', 'file'], 
        default='basic', help='Template to use (default: basic)')
    
    # Configure command
    config_parser = subparsers.add_parser('configure', help='Configure a plugin')
    config_parser.add_argument('plugin_id', help='ID of the plugin')
    config_parser.add_argument('-c', '--config', help='Configuration file (JSON or YAML)')
    config_parser.add_argument('-s', '--set', action='append', metavar='KEY=VALUE', 
        help='Set a configuration option (can be used multiple times)')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Start the plugin dashboard')
    dashboard_parser.add_argument('-p', '--port', type=int, default=8000, help='Port to listen on')
    dashboard_parser.add_argument('-b', '--browser', action='store_true', help='Open in browser')
    
    return parser

def handle_list_command(args):
    """Handle the 'list' command"""
    from app.plugins.plugins_manager import PluginsManager
    
    # Create plugin manager
    plugin_manager = PluginsManager()
    
    # Discover plugins
    plugins = plugin_manager.discover_plugins()
    
    # Filter by type if specified
    if args.type:
        plugins = {pid: info for pid, info in plugins.items() 
            if info.get('type') == args.type}
    
    # Filter by capability if specified
    if args.capability:
        from app.plugins.plugin_registry import registry
        capability_plugins = []
        for cap, info in registry.capabilities.items():
            if cap == args.capability:
                capability_plugins.append(info['plugin'])
        plugins = {pid: info for pid, info in plugins.items() 
            if pid in capability_plugins}
    
    # Prepare output
    if args.format == 'text':
        print(f"Found {len(plugins)} plugins:")
        for plugin_id, info in sorted(plugins.items()):
            print(f"- {plugin_id}: {info.get('name', plugin_id)}")
            
            if args.verbose:
                print(f"  Description: {info.get('description', 'No description')}")
                print(f"  Version: {info.get('version', '1.0')}")
                print(f"  Author: {info.get('author', 'Unknown')}")
                print(f"  Type: {info.get('type', 'plugin')}")
                print(f"  File: {info.get('file', 'Unknown')}")
                print()
    
    elif args.format == 'json':
        print(json.dumps(plugins, indent=2))
        
    elif args.format == 'yaml':
        print(yaml.safe_dump(plugins, default_flow_style=False))

def handle_info_command(args):
    """Handle the 'info' command"""
    from app.plugins.plugins_manager import PluginsManager
    
    # Create plugin manager
    plugin_manager = PluginsManager()
    
    # Discover plugins
    plugins = plugin_manager.discover_plugins()
    
    # Check if the plugin exists
    if args.plugin_id not in plugins:
        print(f"Plugin '{args.plugin_id}' not found.")
        return 1
    
    # Get plugin info
    plugin_info = plugins[args.plugin_id]
    
    # Load the plugin to get more information
    plugin = plugin_manager.load_plugin(args.plugin_id)
    
    # Add extra information from the plugin instance if available
    if plugin:
        if hasattr(plugin, 'get_configuration_options'):
            plugin_info['configuration_options'] = plugin.get_configuration_options()
            
        if hasattr(plugin, 'get_version'):
            plugin_info['version'] = plugin.get_version()
            
        if hasattr(plugin, 'is_configured'):
            configured, message = plugin.is_configured()
            plugin_info['configured'] = configured
            plugin_info['configured_message'] = message
            
        if hasattr(plugin, 'config'):
            # Filter out sensitive information
            filtered_config = {}
            for key, value in plugin.config.items():
                if any(sensitive in key.lower() for sensitive in ['password', 'token', 'secret', 'key']):
                    filtered_config[key] = '********'
                else:
                    filtered_config[key] = value
            plugin_info['current_config'] = filtered_config
    
    # Output the information
    if args.format == 'text':
        print(f"Plugin: {plugin_info.get('name', args.plugin_id)}")
        print(f"ID: {args.plugin_id}")
        print(f"Description: {plugin_info.get('description', 'No description')}")
        print(f"Version: {plugin_info.get('version', '1.0')}")
        print(f"Author: {plugin_info.get('author', 'Unknown')}")
        print(f"Type: {plugin_info.get('type', 'plugin')}")
        print(f"File: {plugin_info.get('file', 'Unknown')}")
        
        if 'configured' in plugin_info:
            status = "Configured" if plugin_info['configured'] else "Not configured"
            print(f"Status: {status}")
            print(f"Status Message: {plugin_info.get('configured_message', '')}")
        
        if 'current_config' in plugin_info:
            print("\nCurrent Configuration:")
            for key, value in plugin_info['current_config'].items():
                print(f"  {key}: {value}")
        
        if 'configuration_options' in plugin_info:
            print("\nConfiguration Options:")
            for option in plugin_info['configuration_options']:
                name = option.get('display_name', option.get('name', 'Unknown'))
                required = " (Required)" if option.get('required', False) else ""
                print(f"  - {name}{required}")
                print(f"    Type: {option.get('type', 'string')}")
                print(f"    Default: {option.get('default', 'None')}")
                print(f"    Description: {option.get('description', 'No description')}")
    
    elif args.format == 'json':
        print(json.dumps(plugin_info, indent=2))
        
    elif args.format == 'yaml':
        print(yaml.safe_dump(plugin_info, default_flow_style=False))

def handle_run_command(args):
    """Handle the 'run' command"""
    from app.plugins.plugins_manager import PluginsManager
    from datetime import datetime
    import csv
    
    # Create plugin manager
    plugin_manager = PluginsManager()
    
    # Load the plugin
    plugin = plugin_manager.load_plugin(args.plugin_id)
    if not plugin:
        print(f"Failed to load plugin '{args.plugin_id}'.")
        return 1
    
    # Apply configuration if provided
    if args.config:
        try:
            # Determine file format
            if args.config.endswith('.json'):
                with open(args.config, 'r') as f:
                    config = json.load(f)
            elif args.config.endswith(('.yaml', '.yml')):
                with open(args.config, 'r') as f:
                    config = yaml.safe_load(f)
            else:
                print(f"Unsupported configuration file format: {args.config}")
                return 1
        except Exception as e:
            print(f"Failed to load configuration file: {e}")
            return 1
        
        # Apply the configuration to the plugin
        plugin.apply_config(config)
    
    # Run the plugin
    try:
        results = plugin.run(args.target)
    except Exception as e:
        print(f"Failed to run plugin: {e}")
        return 1
    
    # Output the results
    if args.output:
        try:
            with open(args.output, 'w') as f:
                if args.format == 'json':
                    json.dump(results, f, indent=2)
                elif args.format == 'yaml':
                    yaml.safe_dump(results, f, default_flow_style=False)
                elif args.format == 'csv':
                    writer = csv.writer(f)
                    writer.writerow(results.keys())
                    writer.writerow(results.values())
        except Exception as e:
            print(f"Failed to write output file: {e}")
            return 1
    else:
        if args.format == 'json':
            print(json.dumps(results, indent=2))
        elif args.format == 'yaml':
            print(yaml.safe_dump(results, default_flow_style=False))
        elif args.format == 'csv':
            writer = csv.writer(sys.stdout)
            writer.writerow(results.keys())
            writer.writerow(results.values())
    
    return 0

def main():
    setup_logging()
    parser = create_arg_parser()
    args = parser.parse_args()
    
    if args.command == 'list':
        handle_list_command(args)
    elif args.command == 'info':
        handle_info_command(args)
    elif args.command == 'run':
        handle_run_command(args)
    elif args.command == 'test':
        handle_test_command(args)
    elif args.command == 'install':
        handle_install_command(args)
    elif args.command == 'create':
        handle_create_command(args)
    elif args.command == 'configure':
        handle_configure_command(args)
    elif args.command == 'dashboard':
        handle_dashboard_command(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()