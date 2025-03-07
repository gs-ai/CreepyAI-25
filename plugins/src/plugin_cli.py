#!/usr/bin/python
# -*- coding: utf-8 -*-

""""
Command-line interface for CreepyAI plugins
Provides a way to interact with plugins from the command line
""""

import os
import sys
import argparse
import logging
import json
import datetime
from typing import List, Dict, Any, Optional
import textwrap
import traceback

from plugins.base_plugin import BasePlugin
from plugins.plugins_manager import PluginsManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PluginCLI:
    """Command-line interface for interacting with CreepyAI plugins"""
    
    def __init__(self):
        """Initialize the CLI with plugin manager and parser"""
        self.plugins_manager = PluginsManager()
        self.parser = self._create_arg_parser()
    
    def _create_arg_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser for the CLI"""
        parser = argparse.ArgumentParser(
            description="CreepyAI Plugin CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent(""""
                Examples:
                  List all available plugins:
                    python plugin_cli.py list
                    
                  Get details about a specific plugin:
                    python plugin_cli.py info -p facebook_plugin
                    
                  Run a plugin to collect location data:
                    python plugin_cli.py run -p instagram_plugin -t "johnsmith" -o results.json
                    
                  Configure a plugin:
                    python plugin_cli.py configure -p twitter_plugin -c '{"api_key": "your_key", "api_secret": "your_secret"}'
            """)"
        )
        
        # Create subparsers for different commands
        subparsers = parser.add_subparsers(dest='command', help='Command to run')
        
        # List plugins command
        list_parser = subparsers.add_parser('list', help='List available plugins')
        list_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed plugin information')
        
        # Plugin info command
        info_parser = subparsers.add_parser('info', help='Show information about a specific plugin')
        info_parser.add_argument('-p', '--plugin', required=True, help='Plugin ID or name')
        
        # Run plugin command
        run_parser = subparsers.add_parser('run', help='Run a plugin to collect location data')
        run_parser.add_argument('-p', '--plugin', required=True, help='Plugin ID or name')
        run_parser.add_argument('-t', '--target', required=True, help='Target to collect data for')
        run_parser.add_argument('-f', '--from-date', help='Start date (YYYY-MM-DD)')
        run_parser.add_argument('-u', '--until-date', help='End date (YYYY-MM-DD)')
        run_parser.add_argument('-o', '--output', help='Output file path')
        run_parser.add_argument('-c', '--config', help='Plugin configuration in JSON format')
        
        # Configure plugin command
        config_parser = subparsers.add_parser('configure', help='Configure a plugin')
        config_parser.add_argument('-p', '--plugin', required=True, help='Plugin ID or name')
        config_parser.add_argument('-c', '--config', required=True, help='Configuration in JSON format')
        
        # Test plugin command
        test_parser = subparsers.add_parser('test', help='Test a plugin')
        test_parser.add_argument('-p', '--plugin', required=True, help='Plugin ID or name')
        test_parser.add_argument('-c', '--config', help='Temporary configuration in JSON format')
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """"
        Run the CLI with the given arguments
        
        Args:
            args: Command-line arguments (defaults to sys.argv[1:])
            
        Returns:
            Exit code (0 for success, non-zero for errors)
        """"
        try:
            # Parse arguments
            parsed_args = self.parser.parse_args(args)
            
            if not parsed_args.command:
                self.parser.print_help()
                return 1
            
            # Discover plugins
            self.plugins_manager.discover_plugins()
            
            # Execute the appropriate command
            if parsed_args.command == 'list':
                return self._handle_list_command(parsed_args)
            elif parsed_args.command == 'info':
                return self._handle_info_command(parsed_args)
            elif parsed_args.command == 'run':
                return self._handle_run_command(parsed_args)
            elif parsed_args.command == 'configure':
                return self._handle_configure_command(parsed_args)
            elif parsed_args.command == 'test':
                return self._handle_test_command(parsed_args)
            else:
                print(f"Unknown command: {parsed_args.command}")
                return 1
                
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            return 1
    
    def _handle_list_command(self, args) -> int:
        """Handle the 'list' command"""
        plugins = self.plugins_manager.discover_plugins()
        
        if not plugins:
            print("No plugins found.")
            return 0
        
        print(f"Found {len(plugins)} plugins:")
        
        for plugin_id, plugin_info in sorted(plugins.items()):
            # Load the plugin to get more info
            plugin = self.plugins_manager.load_plugin(plugin_id) if args.verbose else None
            configured_status = ""
            
            if plugin and hasattr(plugin, 'is_configured'):
                configured, message = plugin.is_configured()
                configured_status = " [Configured]" if configured else " [Not Configured]"
            
            plugin_type = plugin_info.get('type', 'unknown')
            print(f"- {plugin_id}: {plugin_info.get('name', plugin_id)} ({plugin_type}){configured_status}")
            
            if args.verbose:
                print(f"  Description: {plugin_info.get('description', 'No description')}")
                if plugin and hasattr(plugin, 'get_version'):
                    print(f"  Version: {plugin.get_version()}")
                print(f"  File: {plugin_info.get('file', 'Unknown')}")
                print()
        
        return 0
    
    def _handle_info_command(self, args) -> int:
        """Handle the 'info' command"""
        plugin_id = args.plugin
        
        # Find the plugin
        plugins = self.plugins_manager.plugins
        if plugin_id not in plugins:
            # Try to match by name
            for pid, info in plugins.items():
                if info.get('name', '').lower() == plugin_id.lower():
                    plugin_id = pid
                    break
            
            if plugin_id not in plugins:
                print(f"Plugin '{plugin_id}' not found.")
                return 1
        
        # Get plugin info
        plugin_info = plugins[plugin_id]
        plugin = self.plugins_manager.load_plugin(plugin_id)
        
        if not plugin:
            print(f"Failed to load plugin '{plugin_id}'.")
            return 1
        
        # Display plugin information
        print(f"Plugin: {plugin_info.get('name', plugin_id)}")
        print(f"ID: {plugin_id}")
        print(f"Type: {plugin_info.get('type', 'unknown')}")
        print(f"Description: {plugin_info.get('description', 'No description')}")
        
        if hasattr(plugin, 'get_version'):
            print(f"Version: {plugin.get_version()}")
            
        # Check configuration status
        if hasattr(plugin, 'is_configured'):
            configured, message = plugin.is_configured()
            status = "Configured" if configured else "Not configured"
            print(f"Status: {status}")
            print(f"Status message: {message}")
        
        # Show configuration options
        if hasattr(plugin, 'get_configuration_options'):
            config_options = plugin.get_configuration_options()
            if config_options:
                print("\nConfiguration options:")
                for option in config_options:
                    required = " (Required)" if option.get('required', False) else ""
                    default = option.get('default', 'None')
                    print(f"  - {option.get('display_name', option.get('name', 'Unknown'))}{required}")
                    print(f"    Type: {option.get('type', 'string')}, Default: {default}")
                    print(f"    Description: {option.get('description', 'No description')}")
        
        # Show current configuration
        if hasattr(plugin, 'config'):
            print("\nCurrent configuration:")
            for key, value in plugin.config.items():
                # Mask sensitive values
                if 'key' in key.lower() or 'secret' in key.lower() or 'password' in key.lower() or 'token' in key.lower():
                    value = '********'
                print(f"  {key}: {value}")
        
        return 0
    
    def _handle_run_command(self, args) -> int:
        """Handle the 'run' command"""
        plugin_id = args.plugin
        target = args.target
        
        # Find the plugin
        plugins = self.plugins_manager.plugins
        if plugin_id not in plugins:
            # Try to match by name
            for pid, info in plugins.items():
                if info.get('name', '').lower() == plugin_id.lower():
                    plugin_id = pid
                    break
            
            if plugin_id not in plugins:
                print(f"Plugin '{plugin_id}' not found.")
                return 1
        
        # Load the plugin
        plugin = self.plugins_manager.load_plugin(plugin_id)
        
        if not plugin:
            print(f"Failed to load plugin '{plugin_id}'.")
            return 1
        
        # Apply temporary configuration if provided
        original_config = None
        if args.config:
            try:
                original_config = plugin.config.copy() if hasattr(plugin, 'config') else {}
                config = json.loads(args.config)
                plugin.configure(config)
                print(f"Applied temporary configuration")
            except json.JSONDecodeError:
                print(f"Invalid JSON configuration: {args.config}")
                return 1
        
        # Check if the plugin is configured
        if hasattr(plugin, 'is_configured'):
            configured, message = plugin.is_configured()
            if not configured:
                print(f"Plugin is not configured properly: {message}")
                return 1
        
        # Parse date filters
        date_from = None
        date_to = None
        
        if args.from_date:
            try:
                date_from = datetime.datetime.strptime(args.from_date, '%Y-%m-%d')
            except ValueError:
                print(f"Invalid from-date format. Use YYYY-MM-DD.")
                return 1
                
        if args.until_date:
            try:
                date_to = datetime.datetime.strptime(args.until_date, '%Y-%m-%d')
                # Set to end of day
                date_to = date_to.replace(hour=23, minute=59, second=59)
            except ValueError:
                print(f"Invalid until-date format. Use YYYY-MM-DD.")
                return 1
        
        # Run the plugin
        print(f"Running plugin '{plugin_id}' for target '{target}'...")
        try:
            locations = plugin.collect_locations(target, date_from=date_from, date_to=date_to)
            
            # Convert locations to dictionaries for serialization
            location_dicts = [loc.to_dict() for loc in locations]
            
            # Print summary
            print(f"Found {len(locations)} locations.")
            
            # Output to file if specified
            if args.output:
                try:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(location_dicts, f, indent=2)
                    print(f"Saved {len(locations)} locations to {args.output}")
                except Exception as e:
                    print(f"Error saving output file: {e}")
                    return 1
            else:
                # Print the first few locations to console
                max_display = 5
                for i, loc in enumerate(locations[:max_display]):
                    print(f"\nLocation {i+1}:")
                    print(f"  Coordinates: {loc.latitude}, {loc.longitude}")
                    print(f"  Timestamp: {loc.timestamp}")
                    print(f"  Source: {loc.source}")
                    print(f"  Context: {loc.context}")
                
                if len(locations):
