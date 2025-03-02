#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CreepyAI - OSINT Intelligence Gathering Tool

This is the main entry point for the CreepyAI application.
It handles command-line arguments and launches the appropriate interface.
"""

import os
import sys
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='creepyai.log'
)
logger = logging.getLogger('CreepyAI')

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='CreepyAI - OSINT Intelligence Gathering Tool',
        epilog='For more information, visit: https://github.com/gs-ai/CreepyAI-25'
    )
    
    # Add arguments
    parser.add_argument('-g', '--gui', action='store_true', help='Launch the graphical user interface')
    parser.add_argument('-c', '--cli', action='store_true', help='Use command line interface')
    parser.add_argument('-t', '--target', help='Target for intelligence gathering')
    parser.add_argument('-o', '--output', help='Output directory for results')
    parser.add_argument('-p', '--profile', choices=['basic', 'full', 'social', 'professional', 'custom'], 
                      help='Profile type to use for gathering intelligence')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    return parser.parse_args()

def launch_gui():
    """Launch the graphical user interface"""
    try:
        import tkinter as tk
        from creepyai_gui import CreepyAIGUI
        
        root = tk.Tk()
        app = CreepyAIGUI(root)
        root.mainloop()
    except ImportError as e:
        logger.error(f"Failed to import GUI dependencies: {e}")
        print("Error: Could not load GUI dependencies. Make sure tkinter is installed.")
        print("Try: pip install tk")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error launching GUI: {e}")
        print(f"Error: {e}")
        sys.exit(1)

def launch_cli(args):
    """Launch command line interface with the given arguments"""
    try:
        print("CreepyAI CLI mode")
        print("=================")
        
        if not args.target:
            print("Error: Target is required in CLI mode")
            print("Use --target to specify a target")
            sys.exit(1)
            
        print(f"Target: {args.target}")
        print(f"Profile: {args.profile or 'basic'}")
        print(f"Output directory: {args.output or 'default'}")
        
        # TODO: Implement CLI intelligence gathering
        print("CLI mode is not fully implemented yet")
        
    except Exception as e:
        logger.error(f"Error in CLI mode: {e}")
        print(f"Error: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")
    
    # Determine which interface to launch
    if args.cli:
        launch_cli(args)
    else:
        # Default to GUI if no interface is specified
        launch_gui()

if __name__ == "__main__":
    main()
