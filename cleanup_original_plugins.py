#!/usr/bin/env python3
"""
Clean up original plugin files after successful categorization
"""
import os
import sys
import logging
import shutil
from typing import List, Dict
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def verify_categorized_plugins():
    """Verify that all plugins have been properly categorized"""
    plugins_dir = os.path.join("app", "plugins")
    orig_files = []
    categorized_files = []
    
    # Get original plugin files
    for item in os.listdir(plugins_dir):
        if item.endswith('.py') and not item.startswith('__'):
            orig_files.append(item)
    
    # Get categorized plugin files
    for category in ['social_media', 'location_services', 'data_extraction', 'tools', 'other']:
        category_dir = os.path.join(plugins_dir, category)
        if os.path.exists(category_dir) and os.path.isdir(category_dir):
            for item in os.listdir(category_dir):
                if item.endswith('.py') and not item.startswith('__'):
                    categorized_files.append(item)
    
    # Check for missing files
    missing_files = set(orig_files) - set(categorized_files)
    if missing_files:
        logger.error(f"Some plugins were not categorized: {missing_files}")
        return False
    
    return True

def cleanup_original_plugins(confirm=True):
    """Remove original plugin files after verification"""
    plugins_dir = os.path.join("app", "plugins")
    orig_files = []
    
    # Get list of original plugin files
    for item in os.listdir(plugins_dir):
        if item.endswith('.py') and not item.startswith('__'):
            orig_files.append(item)
    
    if not orig_files:
        print("No original plugin files found to clean up.")
        return True
    
    # Ask for confirmation
    if confirm:
        print(f"This will delete {len(orig_files)} original plugin files:")
        for file in sorted(orig_files):
            print(f"  - {file}")
        
        response = input("\nAre you sure you want to proceed? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Operation cancelled.")
            return False
    
    # Delete the files
    for file in orig_files:
        file_path = os.path.join(plugins_dir, file)
        try:
            os.remove(file_path)
            print(f"Removed: {file}")
        except Exception as e:
            logger.error(f"Error removing {file}: {e}")
    
    print("\nOriginal plugin files have been removed.")
    return True

if __name__ == "__main__":
    try:
        # Check if plugins were properly categorized
        if verify_categorized_plugins():
            # Remove the original files
            cleanup_original_plugins()
        else:
            print("Verification failed. Please ensure all plugins are properly categorized first.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error during cleanup: {e}", exc_info=True)
        sys.exit(1)
