#!/usr/bin/env python3
"""
Script to organize plugins into categories
"""
import os
import shutil
import re
from typing import Dict, List, Set, Tuple

def categorize_plugins() -> Dict[str, List[str]]:
    """
    Categorize plugins based on filename patterns
    
    Returns:
        Dictionary mapping categories to plugin files
    """
    plugins_dir = "app/plugins"
    if not os.path.exists(plugins_dir):
        print(f"Plugins directory not found: {plugins_dir}")
        return {}
        
    # Define categories and their patterns
    categories = {
        "social_media": [r"(facebook|twitter|instagram|linkedin|tiktok|snapchat|pinterest|yelp)", 
                        r"social_media"],
        "location_services": [r"(google_maps|foursquare|location_history|wifi_mapper|wifi_analysis)",
                            r"geo[a-z]*", r"location"],
        "data_extraction": [r"(exif|google_takeout|idcrawl|email)", r"extract"],
        "tools": [r"(dummy|test|example|plugin_)", r"utils", r"tool"],
    }
    
    # Collect all plugin files
    plugin_files = []
    for item in os.listdir(plugins_dir):
        if item.endswith(".py") and not item.startswith("__"):
            plugin_files.append(item)
            
    # Categorize plugin files
    categorized_plugins = {category: [] for category in categories}
    categorized_plugins["other"] = []  # For uncategorized plugins
    
    for plugin_file in plugin_files:
        categorized = False
        for category, patterns in categories.items():
            if any(re.search(pattern, plugin_file, re.IGNORECASE) for pattern in patterns):
                categorized_plugins[category].append(plugin_file)
                categorized = True
                break
                
        if not categorized:
            categorized_plugins["other"].append(plugin_file)
            
    return categorized_plugins

def create_categorized_structure() -> None:
    """Create a categorized directory structure for plugins"""
    plugins_dir = "app/plugins"
    categories = categorize_plugins()
    
    for category, plugins in categories.items():
        if not plugins:
            continue
            
        category_dir = os.path.join(plugins_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # Create an __init__.py for the category
        with open(os.path.join(category_dir, "__init__.py"), "w") as f:
            f.write(f'"""\nCreepyAI {category.replace("_", " ").title()} Plugins\n"""\n')
        
        print(f"Category: {category}")
        for plugin_file in plugins:
            print(f"  - {plugin_file}")
    
    print("\nTo move plugins to their categories, run with --move")

def move_plugins_to_categories() -> None:
    """Move plugin files to their category directories"""
    plugins_dir = "app/plugins"
    categories = categorize_plugins()
    
    for category, plugins in categories.items():
        if not plugins:
            continue
            
        category_dir = os.path.join(plugins_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # Create an __init__.py for the category
        with open(os.path.join(category_dir, "__init__.py"), "w") as f:
            f.write(f'"""\nCreepyAI {category.replace("_", " ").title()} Plugins\n"""\n')
        
        print(f"Moving plugins to category: {category}")
        for plugin_file in plugins:
            src_path = os.path.join(plugins_dir, plugin_file)
            dst_path = os.path.join(category_dir, plugin_file)
            
            print(f"  Moving {plugin_file} to {category}")
            shutil.copy2(src_path, dst_path)
            
    print("\nPlugins have been copied to category directories.")
    print("Original files remain in the main plugins directory.")
    print("Once you verify everything works, you can delete the originals.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--move":
        move_plugins_to_categories()
    else:
        create_categorized_structure()
        print("\nRun with --move to actually move the files")
