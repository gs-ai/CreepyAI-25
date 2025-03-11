""""""""""
Plugin utilities for CreepyAI
""""""""""
import os
import sys
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

logger = logging.getLogger('creepyai.plugins')

class PluginInfo:
    """Class representing plugin metadata"""""""""""
    
    def __init__(self, name, path, description=None, version="1.0.0", author=None):
        self.name = name
        self.path = path
        self.description = description or f"Plugin: {name}"
        self.version = version
        self.author = author or "Unknown"
        self.enabled = True
    
    def to_dict(self):
            """Convert to dictionary representation"""""""""""
        return {
        "name": self.name,
        "path": str(self.path),
        "description": self.description,
        "version": self.version,
        "author": self.author,
        "enabled": self.enabled
        }

def discover_plugins(plugins_dir):
            """Discover available plugins in the specified directory"""""""""""
            plugins = {}
    
    if not os.path.exists(plugins_dir):
                logger.warning(f"Plugins directory does not exist: {plugins_dir}")
            return plugins
    
    # Search for Python files
    for item in os.scandir(plugins_dir):
        if item.is_file() and item.name.endswith('.py') and not item.name.startswith('__'):
                    plugin_name = os.path.splitext(item.name)[0]
                    plugin_info = PluginInfo(
                    name=plugin_name,
                    path=item.path
                    )
                    plugins[plugin_name] = plugin_info
    
    # Search for plugin directories
    for item in os.scandir(plugins_dir):
        if item.is_dir() and not item.name.startswith('__'):
                            init_file = os.path.join(item.path, '__init__.py')
                            main_file = os.path.join(item.path, 'main.py')
            
            if os.path.exists(init_file) or os.path.exists(main_file):
                                plugin_name = item.name
                                plugin_info = PluginInfo(
                                name=plugin_name,
                                path=item.path
                                )
                                plugins[plugin_name] = plugin_info
    
                            return plugins

def load_plugin(plugin_info):
                                """Load a plugin based on its information"""""""""""
    try:
        if os.path.isfile(plugin_info.path):
            # Direct Python file
                                        module_name = os.path.splitext(os.path.basename(plugin_info.path))[0]
                                        spec = importlib.util.spec_from_file_location(module_name, plugin_info.path)
            if spec is None:
                                            logger.error(f"Could not create spec for {plugin_info.path}")
                                        return None
                
                                        module = importlib.util.module_from_spec(spec)
                                        spec.loader.exec_module(module)
                                    return module
        elif os.path.isdir(plugin_info.path):
            # Plugin directory
                                        init_file = os.path.join(plugin_info.path, '__init__.py')
                                        main_file = os.path.join(plugin_info.path, 'main.py')
            
            if os.path.exists(init_file):
                # Use __init__.py
                                            module_name = os.path.basename(plugin_info.path)
                                            spec = importlib.util.spec_from_file_location(module_name, init_file)
                if spec is None:
                                                logger.error(f"Could not create spec for {init_file}")
                                            return None
                    
                                            module = importlib.util.module_from_spec(spec)
                                            spec.loader.exec_module(module)
                                        return module
            elif os.path.exists(main_file):
                # Use main.py
                                            module_name = os.path.basename(plugin_info.path) + ".main"
                                            spec = importlib.util.spec_from_file_location(module_name, main_file)
                if spec is None:
                                                logger.error(f"Could not create spec for {main_file}")
                                            return None
                    
                                            module = importlib.util.module_from_spec(spec)
                                            spec.loader.exec_module(module)
                                        return module
        
                                        logger.error(f"Could not determine how to load plugin: {plugin_info.name}")
                                    return None
    except Exception as e:
                                        logger.error(f"Error loading plugin {plugin_info.name}: {e}")
                                    return None
