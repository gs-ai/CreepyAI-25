#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Command line utility to run CreepyAI plugins.
This script provides a simple interface to interact with plugins.
"""

import os
import sys
import argparse
import logging
import json
import importlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set

# Initialize logger at module level, but don't configure it yet
logger = logging.getLogger(__name__)

# Try to import colorama for colored terminal output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOR_SUPPORT = True
except ImportError:
    # Create dummy color constants if colorama is not available
    COLOR_SUPPORT = False
    class DummyColor:
        def __getattr__(self, name):
            return ""
    Fore = Style = DummyColor()

def configure_logging(debug: bool = False) -> None:
    """
    Configure logging based on debug flag.
    
    Args:
        debug: If True, set log level to DEBUG, otherwise INFO
    """
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True  # Overwrite any existing configuration
    )
    logger.debug("Debug logging enabled")

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        Parsed argument namespace
    """
    parser = argparse.ArgumentParser(description="CreepyAI Plugin CLI")
    
    # Main command options
    parser.add_argument('-l', '--list', action='store_true', 
                      help='List all available plugins')
    parser.add_argument('-p', '--plugin', 
                      help='Plugin to run')
    parser.add_argument('-t', '--target', 
                      help='Target for the plugin to work with')
    parser.add_argument('-o', '--output', 
                      help='Output file for results (JSON)')
    parser.add_argument('-d', '--debug', action='store_true', 
                      help='Enable debug logging')
    
    # Date filters
    parser.add_argument('--from-date', 
                      help='Start date filter (YYYY-MM-DD)')
    parser.add_argument('--to-date', 
                      help='End date filter (YYYY-MM-DD)')
    
    # Extra arguments that can be passed to plugins
    parser.add_argument('--args', nargs='+',
                      help='Additional arguments passed to the plugin as key=value pairs')
    
    return parser.parse_args()

def parse_plugin_args(args_list: Optional[List[str]]) -> Dict[str, Any]:
    """
    Parse additional plugin arguments from key=value pairs.
    
    Args:
        args_list: List of strings in format "key=value"
        
    Returns:
        Dictionary of parsed arguments
    """
    if not args_list:
        return {}
        
    result = {}
    for arg in args_list:
        if '=' not in arg:
            logger.warning(f"Ignoring malformed argument: {arg}")
            continue
            
        key, value = arg.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        # Try to convert value to appropriate type
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
            value = float(value)
            
        result[key] = value
        
    return result

def parse_date(date_str: str, is_end_date: bool = False) -> Optional[datetime]:
    """
    Parse date string in YYYY-MM-DD format.
    
    Args:
        date_str: String date in YYYY-MM-DD format
        is_end_date: If True, set time to end of day (23:59:59)
        
    Returns:
        Parsed datetime object
        
    Raises:
        ValueError: If date format is invalid
    """
    date = datetime.strptime(date_str, '%Y-%m-%d')
    if is_end_date:
        date = date.replace(hour=23, minute=59, second=59)
    return date

def get_date_filters(from_date: Optional[str], to_date: Optional[str]) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Parse and validate date filters.
    
    Args:
        from_date: Start date string (YYYY-MM-DD)
        to_date: End date string (YYYY-MM-DD)
        
    Returns:
        Tuple of (from_date, to_date) as datetime objects
        
    Raises:
        ValueError: If date format is invalid
    """
    date_from = None
    date_to = None
    
    if from_date:
        try:
            date_from = parse_date(from_date)
            print_info(f"Filtering from: {date_from.strftime('%Y-%m-%d')}")
        except ValueError:
            raise ValueError(f"Invalid from-date format: {from_date}. Use YYYY-MM-DD.")
    
    if to_date:
        try:
            date_to = parse_date(to_date, is_end_date=True)
            print_info(f"Filtering to: {date_to.strftime('%Y-%m-%d %H:%M:%S')}")
        except ValueError:
            raise ValueError(f"Invalid to-date format: {to_date}. Use YYYY-MM-DD.")
    
    # Validate that from_date <= to_date if both are provided
    if date_from and date_to and date_from > date_to:
        raise ValueError("From-date must be before or equal to to-date")
    
    return date_from, date_to

def save_locations_to_file(locations: List[Any], output_path: str) -> bool:
    """
    Save locations to JSON file.
    
    Args:
        locations: List of location objects
        output_path: Path to save JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert locations to dictionaries
        locations_dicts = [loc.to_dict() for loc in locations]
        
        # Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(locations_dicts, f, indent=2, default=str)
            
        logger.info(f"Saved {len(locations)} locations to {output_path}")
        print_success(f"Saved {len(locations)} locations to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving output file: {e}")
        print_error(f"Error saving output file: {e}")
        return False

def print_info(message: str) -> None:
    """Print info messages with optional color."""
    if COLOR_SUPPORT:
        print(f"{Fore.CYAN}{message}")
    else:
        print(f"INFO: {message}")

def print_success(message: str) -> None:
    """Print success messages with optional color."""
    if COLOR_SUPPORT:
        print(f"{Fore.GREEN}{message}")
    else:
        print(f"SUCCESS: {message}")

def print_error(message: str) -> None:
    """Print error messages with optional color."""
    if COLOR_SUPPORT:
        print(f"{Fore.RED}{Style.BRIGHT}Error: {message}")
    else:
        print(f"ERROR: {message}")

def print_warning(message: str) -> None:
    """Print warning messages with optional color."""
    if COLOR_SUPPORT:
        print(f"{Fore.YELLOW}Warning: {message}")
    else:
        print(f"WARNING: {message}")

def validate_plugin_id(plugin_id: str) -> None:
    """
    Validate plugin ID for security.
    
    Args:
        plugin_id: Plugin ID to validate
        
    Raises:
        ValueError: If plugin ID contains suspicious characters
    """
    # List of suspicious patterns that might indicate an injection attempt
    suspicious_patterns = [';', '|', '&', '>', '<', '$', '`', '\\', '/', '*']
    
    for pattern in suspicious_patterns:
        if pattern in plugin_id:
            raise ValueError(f"Invalid plugin ID: contains suspicious character '{pattern}'")
    
    # Ensure plugin ID is alphanumeric plus dots and underscores
    if not all(c.isalnum() or c in '._' for c in plugin_id):
        invalid_chars = [c for c in plugin_id if not (c.isalnum() or c in '._')]
        raise ValueError(f"Invalid plugin ID: contains invalid characters {', '.join(repr(c) for c in invalid_chars)}")

def display_plugin_info(plugin_id: str, plugin_info: Dict[str, Any]) -> None:
    """
    Display formatted plugin information.
    
    Args:
        plugin_id: Plugin identifier
        plugin_info: Dictionary with plugin metadata
    """
    if COLOR_SUPPORT:
        print(f"{Fore.GREEN}- {Style.BRIGHT}{plugin_id}{Style.RESET_ALL}: {plugin_info.get('name', plugin_id)}")
        if 'version' in plugin_info:
            print(f"  {Fore.CYAN}Version: {plugin_info['version']}")
        print(f"  {plugin_info.get('description', '')}")
    else:
        print(f"- {plugin_id}: {plugin_info.get('name', plugin_id)}")
        if 'version' in plugin_info:
            print(f"  Version: {plugin_info['version']}")
        print(f"  {plugin_info.get('description', '')}")
    print()

def display_location_samples(locations: List[Any], max_display: int = 5) -> None:
    """
    Display sample locations from the results.
    
    Args:
        locations: List of location objects
        max_display: Maximum number of samples to display
    """
    if not locations:
        return
        
    max_display = min(max_display, len(locations))
    if max_display <= 0:
        return
        
    if COLOR_SUPPORT:
        print(f"\n{Style.BRIGHT}{Fore.CYAN}Sample locations:")
    else:
        print("\nSample locations:")
        
    for i, location in enumerate(locations[:max_display]):
        if COLOR_SUPPORT:
            print(f"  {Fore.GREEN}{i+1}. {Style.BRIGHT}{location.latitude}, {location.longitude}")
            print(f"     {Fore.YELLOW}Timestamp: {Style.RESET_ALL}{location.timestamp}")
            print(f"     {Fore.YELLOW}Source: {Style.RESET_ALL}{location.source}")
            print(f"     {Fore.YELLOW}Context: {Style.RESET_ALL}{location.context}")
        else:
            print(f"  {i+1}. {location.latitude}, {location.longitude}")
            print(f"     Timestamp: {location.timestamp}")
            print(f"     Source: {location.source}")
            print(f"     Context: {location.context}")
        print()
        
    # If there are more locations, indicate that
    if len(locations) > max_display:
        remaining = len(locations) - max_display
        if COLOR_SUPPORT:
            print(f"{Fore.CYAN}... and {Style.BRIGHT}{remaining}{Style.RESET_ALL}{Fore.CYAN} more locations")
        else:
            print(f"... and {remaining} more locations")

def load_and_run_plugin(plugin_manager, plugin_id: str, target: str, 
                       date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
                       extra_args: Optional[Dict[str, Any]] = None) -> List[Any]:
    """
    Load and run a plugin with given parameters.
    
    Args:
        plugin_manager: Instance of PluginsManager
        plugin_id: ID of the plugin to run
        target: Target for the plugin to process
        date_from: Optional start date filter
        date_to: Optional end date filter
        extra_args: Optional dictionary of additional arguments for the plugin
        
    Returns:
        List of location results
        
    Raises:
        ValueError: If plugin can't be loaded or run
    """
    # Validate plugin ID for security
    validate_plugin_id(plugin_id)
    
    # Skip if it's a dummy plugin
    if 'dummy' in plugin_id.lower():
        raise ValueError("Cannot run dummy test plugins")
    
    # Load the plugin
    plugin = plugin_manager.load_plugin(plugin_id)
    if not plugin:
        raise ValueError(f"Plugin '{plugin_id}' could not be loaded")
    
    logger.info(f"Running plugin: {plugin.name} v{plugin.get_version()}")
    print_info(f"Running plugin: {plugin.name} v{plugin.get_version()}")
    
    # Check if the plugin is configured
    configured, message = plugin.is_configured()
    if not configured:
        raise ValueError(f"Plugin is not configured: {message}")
    
    # Check if plugin supports extra arguments
    if extra_args and hasattr(plugin, 'supports_args'):
        supported_args = plugin.supports_args()
        unsupported_args = set(extra_args.keys()) - set(supported_args)
        
        if unsupported_args:
            print_warning(f"Plugin doesn't support these arguments: {', '.join(unsupported_args)}")
            # Remove unsupported args
            for arg in unsupported_args:
                del extra_args[arg]
                
    # Run the plugin
    logger.info(f"Collecting locations for target: {target}")
    print_info(f"Collecting locations for target: {target}")
    
    start_time = datetime.now()
    
    # Call with or without extra arguments
    if extra_args:
        logger.debug(f"Passing extra arguments to plugin: {extra_args}")
        locations = plugin.collect_locations(target, date_from=date_from, date_to=date_to, **extra_args)
    else:
        locations = plugin.collect_locations(target, date_from=date_from, date_to=date_to)
        
    execution_time = (datetime.now() - start_time).total_seconds()
    
    logger.info(f"Found {len(locations)} locations in {execution_time:.2f} seconds")
    print_success(f"Found {len(locations)} locations in {execution_time:.2f} seconds")
    
    return locations

def list_available_plugins(plugin_manager) -> int:
    """
    List all available plugins.
    
    Args:
        plugin_manager: Instance of PluginsManager
        
    Returns:
        Exit code (0 for success)
    """
    try:
        plugins = plugin_manager.discover_plugins()
        
        if COLOR_SUPPORT:
            print(f"\n{Style.BRIGHT}{Fore.CYAN}Available plugins ({len(plugins)}):")
            print(f"{Fore.CYAN}{'=' * 40}")
        else:
            print(f"\nAvailable plugins ({len(plugins)}):")
            print("=" * 40)
        
        # Display non-dummy plugins
        for plugin_id, plugin_info in sorted(plugins.items()):
            if 'dummy' not in plugin_id.lower():
                display_plugin_info(plugin_id, plugin_info)
                
        return 0
    except Exception as e:
        logger.error(f"Error listing plugins: {e}")
        print_error(f"Could not list plugins: {e}")
        return 1

def run_specific_plugin(plugin_manager, args) -> int:
    """
    Run a specific plugin with arguments.
    
    Args:
        plugin_manager: Instance of PluginsManager
        args: Command line arguments
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if not args.target:
        print_error("--target is required when using --plugin")
        return 1
    
    try:
        # Parse extra plugin arguments
        extra_args = parse_plugin_args(args.args)
        
        # Parse date filters
        date_from, date_to = get_date_filters(args.from_date, args.to_date)
        
        # Run the plugin
        locations = load_and_run_plugin(
            plugin_manager,
            args.plugin,
            args.target,
            date_from,
            date_to,
            extra_args
        )
        
        # Display sample locations
        display_location_samples(locations)
        
        # Save to output file if requested
        if args.output and locations:
            if not save_locations_to_file(locations, args.output):
                return 1
        
        return 0
        
    except ValueError as e:
        logger.error(f"Value error: {e}")
        print_error(f"{e}")
        return 1
    except Exception as e:
        logger.error(f"Error running plugin: {e}")
        print_error(f"Unexpected error: {e}")
        return 1

def main():
    """Main function for the plugin CLI"""
    args = parse_arguments()
    
    # Configure logging based on debug flag
    configure_logging(args.debug)
    
    try:
        # Import plugin modules
        from app.plugins.plugins_manager import PluginsManager
        
        # Create plugin manager
        plugin_manager = PluginsManager()
        
        # List plugins if requested
        if args.list:
            return list_available_plugins(plugin_manager)
        
        # Run a specific plugin if requested
        if args.plugin:
            return run_specific_plugin(plugin_manager, args)
        
        # If no action specified, show help
        print_info("No action specified. Use --list to see available plugins or --plugin to run a plugin.")
        print_info("For help, run: python run_plugin_cli.py --help")
        return 0
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print_error(f"Could not import required modules: {e}")
        print_info("Make sure you have installed all dependencies and are running from the correct directory.")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        print_error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user.")
        sys.exit(130)
