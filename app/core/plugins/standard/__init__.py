"""
Standard plugins for CreepyAI
"""
import os
import sys
import importlib
import logging

logger = logging.getLogger(__name__)

# Make sure all standard plugins are discovered
def register_standard_plugins():
    """Register all standard plugins"""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get all Python files in this directory 
    for file_name in os.listdir(this_dir):
        if file_name.endswith('.py') and file_name != '__init__.py':
            plugin_name = file_name[:-3]  # Remove .py extension
            try:
                # Import the module
                spec = importlib.util.spec_from_file_location(
                    plugin_name, 
                    os.path.join(this_dir, file_name)
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                logger.info(f"Loaded standard plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Error loading standard plugin {plugin_name}: {e}")

# Register standard plugins when this module is imported
register_standard_plugins()
