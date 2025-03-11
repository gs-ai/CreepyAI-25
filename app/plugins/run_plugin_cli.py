#!/usr/bin/python
# -*- coding: utf-8 -*-

""""""""""""
Command line utility to run CreepyAI plugins.""
This script provides a simple interface to interact with plugins.""
""""""""""""
""
import os""
import sys""
import argparse
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Set up basic logging
logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def parse_arguments():
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
    
    return parser.parse_args()

def main():
        """Main function for the plugin CLI"""""""""""
        args = parse_arguments()
    
    # Configure logging based on debug flag
    if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Import plugin modules
                from app.plugins.plugins_manager import PluginsManager
        
        # Create plugin manager
                plugin_manager = PluginsManager()
        
        # List plugins if requested
        if args.list:
                    plugins = plugin_manager.discover_plugins()
                    print(f"\nAvailable plugins ({len(plugins)}):")
                    print("=" * 40)
            for plugin_id, plugin_info in sorted(plugins.items()):
                        print(f"- {plugin_id}: {plugin_info.get('name', plugin_id)}")
                        print(f"  {plugin_info.get('description', '')}")
                        print()
                    return 0
        
        # Run a specific plugin if requested
        if args.plugin:
            if not args.target:
                            print("Error: --target is required when using --plugin")
                        return 1
                
            # Load the plugin
                        plugin = plugin_manager.load_plugin(args.plugin)
            if not plugin:
                            print(f"Error: Plugin '{args.plugin}' could not be loaded")
                        return 1
                
                        print(f"Running plugin: {plugin.name} v{plugin.get_version()}")
            
            # Check if the plugin is configured
                        configured, message = plugin.is_configured()
            if not configured:
                            print(f"Plugin is not configured: {message}")
                        return 1
                
            # Parse date filters if provided
                        date_from = None
                        date_to = None
            
            if args.from_date:
                try:
                                date_from = datetime.strptime(args.from_date, '%Y-%m-%d')
                                print(f"Filtering from: {date_from.strftime('%Y-%m-%d')}")
                except ValueError:
                                    print(f"Error: Invalid from-date format: {args.from_date}")
                                return 1
                    
            if args.to_date:
                try:
                                        date_to = datetime.strptime(args.to_date, '%Y-%m-%d')
                    # Set to end of day
                                        date_to = date_to.replace(hour=23, minute=59, second=59)
                                        print(f"Filtering to: {date_to.strftime('%Y-%m-%d')}")
                except ValueError:
                                            print(f"Error: Invalid to-date format: {args.to_date}")
                                        return 1
            
            # Run the plugin
                                        print(f"Collecting locations for target: {args.target}")
                                        start_time = datetime.now()
                                        locations = plugin.collect_locations(args.target, date_from=date_from, date_to=date_to)
                                        execution_time = (datetime.now() - start_time).total_seconds()
            
                                        print(f"Found {len(locations)} locations in {execution_time:.2f} seconds")
            
            # Display first few locations
                                        max_display = min(5, len(locations))
            if max_display > 0:
                                            print("\nSample locations:")
                for i, location in enumerate(locations[:max_display]):
                                                print(f"  {i+1}. {location.latitude}, {location.longitude}")
                                                print(f"     Timestamp: {location.timestamp}")
                                                print(f"     Source: {location.source}")
                                                print(f"     Context: {location.context}")
                                                print()
                    
                # If there are more locations, indicate that
                if len(locations) > max_display:
                                                    print(f"... and {len(locations) - max_display} more locations")
            
            # Save to output file if requested
            if args.output and locations:
                try:
                    # Convert locations to dictionaries
                                                            locations_dicts = [loc.to_dict() for loc in locations]
                    
                    # Create output directory if needed
                                                            output_dir = os.path.dirname(args.output)
                    if output_dir and not os.path.exists(output_dir):
                                                                os.makedirs(output_dir)
                        
                    # Save to file
                    with open(args.output, 'w', encoding='utf-8') as f:
                                                                    json.dump(locations_dicts, f, indent=2, default=str)
                        
                                                                    print(f"Saved {len(locations)} locations to {args.output}")
                    
                except Exception as e:
                                                                        print(f"Error saving output file: {e}")
                                                                    return 1
            
                                                                return 0
        
        # If no action specified, show help
                                                                print("No action specified. Use --list to see available plugins or --plugin to run a plugin.")
                                                            return 0
        
    except Exception as e:
                                                                logger.error(f"Error: {e}")
        if args.debug:
                                                                    import traceback
                                                                    traceback.print_exc()
                                                                return 1

if __name__ == "__main__":
                                                                    sys.exit(main())
