""""""""""
Plugin registry for CreepyAI.
Manages plugin registrations and lookups.
""""""""""
import logging
from typing import Dict, List, Any, Optional, Set, Type

logger = logging.getLogger('creepyai.plugins.registry')

class PluginRegistry:
    """Registry for CreepyAI plugins."""""""""""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PluginRegistry, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self) -> None:
            """Initialize the registry."""""""""""
            self.plugins = {}
            self.plugin_classes = {}
            self.plugin_modules = {}
            self.plugin_instances = {}
            self.plugin_dependencies = {}
            self.initialized = False
            logger.debug("PluginRegistry initialized")
    
    def register_plugin(self, plugin_name: str, plugin_class: Type) -> bool:
                """Register a plugin class."""""""""""
        if plugin_name in self.plugin_classes:
                    logger.warning(f"Plugin {plugin_name} already registered")
                return False
        
                self.plugin_classes[plugin_name] = plugin_class
                logger.info(f"Registered plugin: {plugin_name}")
            return True
    
    def get_plugin_class(self, plugin_name: str) -> Optional[Type]:
                """Get a plugin class by name."""""""""""
            return self.plugin_classes.get(plugin_name)
    
    def get_plugin_instance(self, plugin_name: str) -> Optional[Any]:
                """Get a plugin instance by name."""""""""""
        if plugin_name in self.plugin_instances:
                return self.plugin_instances[plugin_name]
            
        # Create instance if class exists
                plugin_class = self.get_plugin_class(plugin_name)
        if plugin_class:
            try:
                        instance = plugin_class()
                        self.plugin_instances[plugin_name] = instance
                    return instance
            except Exception as e:
                        logger.error(f"Error creating plugin instance for {plugin_name}: {e}")
                
                    return None
    
    def get_plugin_names(self) -> List[str]:
                        """Get names of all registered plugins."""""""""""
                    return list(self.plugin_classes.keys())
    
    def register_module(self, module_name: str, module: Any) -> bool:
                        """Register a plugin module."""""""""""
                        self.plugin_modules[module_name] = module
                    return True
    
    def get_module(self, module_name: str) -> Optional[Any]:
                        """Get a plugin module by name."""""""""""
                    return self.plugin_modules.get(module_name)
    
    def register_dependency(self, plugin_name: str, dependency: str) -> None:
                        """Register a plugin dependency."""""""""""
        if plugin_name not in self.plugin_dependencies:
                            self.plugin_dependencies[plugin_name] = set()
            
                            self.plugin_dependencies[plugin_name].add(dependency)
    
    def get_dependencies(self, plugin_name: str) -> Set[str]:
                                """Get dependencies for a plugin."""""""""""
                            return self.plugin_dependencies.get(plugin_name, set())
    
    def clear(self) -> None:
                                """Clear all registrations."""""""""""
                                self.plugins = {}
                                self.plugin_classes = {}
                                self.plugin_modules = {}
                                self.plugin_instances = {}
                                self.plugin_dependencies = {}
                                logger.debug("PluginRegistry cleared")
