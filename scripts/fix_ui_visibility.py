#!/usr/bin/env python3
"""
UI Visibility Fix Script for CreepyAI
This script attempts to reset UI configuration to make buttons and controls visible.
"""

import os
import sys
import configparser
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("UIFix")

def fix_ui_config():
    """Reset UI configuration to default settings with all elements visible."""
    
    # Determine config directory
    home_dir = os.path.expanduser("~")
    config_dir = os.path.join(home_dir, ".creepyai", "config")
    ui_config_path = os.path.join(config_dir, "ui_config.ini")
    
    # Ensure config directory exists
    os.makedirs(config_dir, exist_ok=True)
    
    # Create or modify config file
    config = configparser.ConfigParser()
    
    # Read existing config if it exists
    if os.path.exists(ui_config_path):
        try:
            config.read(ui_config_path)
            logger.info(f"Loaded existing configuration from {ui_config_path}")
        except Exception as e:
            logger.error(f"Error reading existing config: {e}")
    
    # Ensure UI section exists
    if "UI" not in config:
        config["UI"] = {}
    
    # Set visibility options
    config["UI"]["show_toolbar"] = "True"
    config["UI"]["show_statusbar"] = "True"
    config["UI"]["show_project_panel"] = "True"
    config["UI"]["show_buttons"] = "True"
    config["UI"]["toolbar_style"] = "2"  # Show text and icons
    
    # Save the updated config
    try:
        with open(ui_config_path, "w") as f:
            config.write(f)
        logger.info(f"UI configuration updated successfully at {ui_config_path}")
    except Exception as e:
        logger.error(f"Failed to write config file: {e}")
        return False
    
    return True

def main():
    logger.info("Starting UI visibility fix")
    
    if fix_ui_config():
        logger.info("UI configuration has been reset to improve visibility")
        logger.info("Please restart CreepyAI for changes to take effect")
    else:
        logger.error("Failed to update UI configuration")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
