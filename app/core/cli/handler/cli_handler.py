"""
Command-line interface handler for CreepyAI
"""

import sys
import argparse
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def parse_arguments(args: List[str]) -> argparse.Namespace:
    """
    Parse command line arguments
    
    Args:
        args: Command line arguments
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="CreepyAI Command Line Interface")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Plugin command
    plugin_parser = subparsers.add_parser('plugin', help='Run a plugin')
    plugin_parser.add_argument('plugin_name', help='Name of the plugin to run')
    plugin_parser.add_argument('--target', '-t', required=True, help='Target for the plugin')
    plugin_parser.add_argument('--output', '-o', help='Output file for results')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), 
                              help='Set a configuration value')
    config_parser.add_argument('--get', metavar='KEY', help='Get a configuration value')
    config_parser.add_argument('--list', action='store_true', help='List all configuration values')
    
    return parser.parse_args(args)

def handle_plugin_command(args: argparse.Namespace, app_config: Dict[str, Any]) -> int:
    """
    Handle the plugin command
    
    Args:
        args: Parsed arguments
        app_config: Application configuration
        
    Returns:
        Exit code
    """
    try:
        # Import and run the plugin cli handler
        from creepy.run_plugin_cli import main as run_plugin
        
        # Build arguments for the plugin CLI
        plugin_args = [
            '--plugin', args.plugin_name,
            '--target', args.target
        ]
        
        if args.output:
            plugin_args.extend(['--output', args.output])
            
        # Set sys.argv and run the plugin CLI
        sys.argv[1:] = plugin_args
        return run_plugin()
        
    except ImportError:
        logger.error("Plugin CLI module not found")
        print("Error: Plugin CLI module not found. Make sure run_plugin_cli.py is available.")
        return 1
    except Exception as e:
        logger.error(f"Error running plugin: {e}", exc_info=True)
        print(f"Error running plugin: {e}")
        return 1

def handle_version_command(app_config: Dict[str, Any]) -> int:
    """
    Handle the version command
    
    Args:
        app_config: Application configuration
        
    Returns:
        Exit code
    """
    app_name = app_config.get('app_name', 'CreepyAI')
    version = app_config.get('version', '1.0.0')
    
    print(f"{app_name} v{version}")
    return 0

def handle_config_command(args: argparse.Namespace, app_config: Dict[str, Any]) -> int:
    """
    Handle the config command
    
    Args:
        args: Parsed arguments
        app_config: Application configuration
        
    Returns:
        Exit code
    """
    from config import save_app_config
    
    if args.set:
        key, value = args.set
        
        # Try to convert string value to appropriate type
        try:
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
                value = float(value)
        except (ValueError, AttributeError):
            pass
            
        # Update config
        app_config[key] = value
        
        # Save config
        if save_app_config(app_config):
            print(f"Configuration updated: {key} = {value}")
        else:
            print("Error saving configuration")
            return 1
            
    elif args.get:
        key = args.get
        if key in app_config:
            print(f"{key} = {app_config[key]}")
        else:
            print(f"Configuration key '{key}' not found")
            return 1
            
    elif args.list:
        print("Current configuration:")
        for key, value in sorted(app_config.items()):
            print(f"{key} = {value}")
            
    return 0

def run(args: List[str], app_config: Dict[str, Any]) -> int:
    """
    Run the CLI interface with the specified arguments
    
    Args:
        args: Command line arguments
        app_config: Application configuration
        
    Returns:
        Exit code
    """
    try:
        # Parse arguments
        parsed_args = parse_arguments(args)
        
        # Handle commands
        if parsed_args.command == 'plugin':
            return handle_plugin_command(parsed_args, app_config)
        elif parsed_args.command == 'version':
            return handle_version_command(app_config)
        elif parsed_args.command == 'config':
            return handle_config_command(parsed_args, app_config)
        else:
            # No command specified or unknown command
            print("Error: No command specified. Use -h for help.")
            return 1
            
    except Exception as e:
        logger.error(f"Error handling CLI command: {e}", exc_info=True)
        print(f"Error: {e}")
        return 1
