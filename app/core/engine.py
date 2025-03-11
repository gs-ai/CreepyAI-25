"""
Main application engine for CreepyAI.
"""
import os
import sys
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger('engine')

class Engine:
    """Main application engine for CreepyAI."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Engine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.logger = logging.getLogger('engine')
        self.logger.setLevel(logging.INFO)
        self.logger.info("Logger engine initialized with level INFO")
        self._initialized = True
        self.config = {}
        self.plugin_manager = None
        self.root_path = ""
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the engine with configuration.
        
        Args:
            config: Application configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.config = config
            from app.core.path_utils import get_app_root
            self.root_path = get_app_root()
            self.logger.info(f"CreepyAI Engine initialized with root: {self.root_path}")
            
            # Initialize plugin manager if enabled
            if config.get("plugins", {}).get("enabled", True):
                self._initialize_plugins()
                
            return True
            
        except Exception as e:
            self.logger.error(f"Engine initialization failed: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return False
            
    def _initialize_plugins(self) -> bool:
        """Initialize and load plugins.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from app.plugins.plugin_manager import PluginManager
            self.plugin_manager = PluginManager()
            self.plugin_manager.initialize()
            plugins = self.plugin_manager.load_plugins()
            return True
            
        except ImportError:
            self.logger.error("Could not import PluginManager class")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to load plugins: {e}")
            return False
            
    def run_plugin(self, plugin_name: str, *args, **kwargs) -> Any:
        """Run a plugin by name.
        
        Args:
            plugin_name: Name of plugin to run
            *args: Arguments to pass to the plugin
            **kwargs: Keyword arguments to pass to the plugin
            
        Returns:
            Plugin execution result
        """
        if not self.plugin_manager:
            self.logger.error("Plugin manager not initialized")
            return None
            
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if not plugin:
            self.logger.error(f"Plugin not found: {plugin_name}")
            return None
            
        try:
            return plugin.execute(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error executing plugin {plugin_name}: {e}")
            return None

# For backward compatibility - provide CreepyAIEngine as an alias for Engine
CreepyAIEngine = Engine
