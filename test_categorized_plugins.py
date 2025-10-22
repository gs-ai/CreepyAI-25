#!/usr/bin/env python3
"""
Test the categorized plugin system
"""
import os
import sys
import logging
from app.core.plugins import PluginManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_plugin_categories():
    """Test that plugins are correctly categorized"""
    plugin_manager = PluginManager()
    plugin_manager.discover_plugins()
    
    print(f"\nDiscovered {len(plugin_manager.plugins)} plugins")
    
    # Show plugins by category
    categories = plugin_manager.get_categories()
    for category in sorted(categories):
        plugins = plugin_manager.get_plugins_by_category(category)
        print(f"\nCategory: {category.upper()} ({len(plugins)} plugins)")
        
        for name, plugin in sorted(plugins.items()):
            info = plugin.get_info() if hasattr(plugin, 'get_info') else {'name': name}
            display_name = info.get('name', name)
            display_version = info.get('version', 'unknown')
            print(f"  - {display_name} (v{display_version})")
    
    assert categories, "No plugin categories were discovered"

    print("\nNo errors found in plugin categorization.")

if __name__ == "__main__":
    try:
        test_plugin_categories()
    except Exception as e:
        logger.error(f"Error testing plugin categories: {e}", exc_info=True)
        sys.exit(1)
