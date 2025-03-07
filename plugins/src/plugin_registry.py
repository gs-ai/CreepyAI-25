#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Plugin Registry for CreepyAI
Centralized registry for plugin capabilities and integrations
"""

import os
import json
import logging
import threading
from typing import Dict, List, Any, Optional, Set, Callable
import inspect
import time

logger = logging.getLogger(__name__)

class PluginRegistry:
    """
    Central registry for plugin capabilities, allowing plugins to register functions
    and services that other plugins can discover and use.
    """
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PluginRegistry, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        
        # Registry storage
        self.capabilities = {}  # Maps capability names to provider plugins
        self.services = {}      # Maps service names to service functions
        self.hooks = {}         # Maps hook names to handler functions
        self.data_types = {}    # Maps data types to handler plugins
        self.extensions = {}    # Maps file extensions to handler plugins
        self.integrations = {}  # Maps integration names to handler plugins
        
        # Statistics
        self.stats = {
            'service_calls': {},
            'hook_invocations': {},
            'capability_usage': {}
        }
    
    def register_capability(self, plugin_name: str, capability_name: str, 
                          description: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a plugin capability
        
        Args:
            plugin_name: Name of the plugin providing the capability
            capability_name: Name of the capability
            description: Description of the capability
            metadata: Optional metadata about the capability
            
        Returns:
            True if registration was successful
        """
        with self._lock:
            if capability_name in self.capabilities:
                logger.warning(f"Capability '{capability_name}' already registered by {self.capabilities[capability_name]['plugin']}")
                return False
                
            self.capabilities[capability_name] = {
                'plugin': plugin_name,
                'description': description,
                'metadata': metadata or {},
                'registered_at': time.time()
            }
            
            logger.info(f"Plugin '{plugin_name}' registered capability: {capability_name}")
            return True
    
    def has_capability(self, capability_name: str) -> bool:
        """Check if a capability is registered"""
        return capability_name in self.capabilities
    
    def get_capability_provider(self, capability_name: str) -> Optional[str]:
        """Get the name of the plugin providing a capability"""
        capability = self.capabilities.get(capability_name)
        return capability['plugin'] if capability else None
    
    def register_service(self, plugin_name: str, service_name: str, 
                        service_func: Callable, description: str) -> bool:
        """
        Register a service function provided by a plugin
        
        Args:
            plugin_name: Name of the plugin providing the service
            service_name: Name of the service
            service_func: Function that implements the service
            description: Description of the service
            
        Returns:
            True if registration was successful
        """
        with self._lock:
            if service_name in self.services:
                logger.warning(f"Service '{service_name}' already registered by {self.services[service_name]['plugin']}")
                return False
                
            # Check that service_func is callable
            if not callable(service_func):
                logger.error(f"Service function for '{service_name}' is not callable")
                return False
                
            # Get the function signature for documentation
            try:
                sig = inspect.signature(service_func)
                signature_str = str(sig)
            except (ValueError, TypeError):
                signature_str = "(unknown)"
                
            self.services[service_name] = {
                'plugin': plugin_name,
                'function': service_func,
                'description': description,
                'signature': signature_str,
                'registered_at': time.time()
            }
            
            # Initialize statistics
            self.stats['service_calls'][service_name] = 0
            
            logger.info(f"Plugin '{plugin_name}' registered service: {service_name}{signature_str}")
            return True
    
    def call_service(self, service_name: str, *args, **kwargs) -> Any:
        """
        Call a registered service function
        
        Args:
            service_name: Name of the service to call
            *args: Positional arguments to pass to the service
            **kwargs: Keyword arguments to pass to the service
            
        Returns:
            Return value from the service function
            
        Raises:
            KeyError: If the service does not exist
            Exception: Any exception raised by the service function
        """
        with self._lock:
            if service_name not in self.services:
                raise KeyError(f"Service '{service_name}' is not registered")
                
            service = self.services[service_name]
            
            # Update statistics
            self.stats['service_calls'][service_name] += 1
            
            # Call the service function
            return service['function'](*args, **kwargs)
    
    def register_hook(self, plugin_name: str, hook_name: str, 
                     handler_func: Callable) -> bool:
        """
        Register a hook handler function
        
        Args:
            plugin_name: Name of the plugin providing the handler
            hook_name: Name of the hook to handle
            handler_func: Function that handles the hook
            
        Returns:
            True if registration was successful
        """
        with self._lock:
            if hook_name not in self.hooks:
                self.hooks[hook_name] = []
                self.stats['hook_invocations'][hook_name] = 0
                
            # Check if this plugin already registered a handler for this hook
            for handler in self.hooks[hook_name]:
                if handler['plugin'] == plugin_name:
                    logger.warning(f"Plugin '{plugin_name}' already registered a handler for hook '{hook_name}'")
                    # Update the existing handler
                    handler['function'] = handler_func
                    return True
            
            # Add new handler
            self.hooks[hook_name].append({
                'plugin': plugin_name,
                'function': handler_func,
                'registered_at': time.time()
            })
            
            logger.info(f"Plugin '{plugin_name}' registered handler for hook: {hook_name}")
            return True
    
    def invoke_hook(self, hook_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Invoke all registered handlers for a hook
        
        Args:
            hook_name: Name of the hook to invoke
            *args: Positional arguments to pass to handlers
            **kwargs: Keyword arguments to pass to handlers
            
        Returns:
            Dictionary mapping plugin names to handler results
        """
        results = {}
        
        with self._lock:
            if hook_name not in self.hooks:
                return results
                
            handlers = self.hooks[hook_name]
            
            # Update statistics
            self.stats['hook_invocations'][hook_name] += 1
            
            # Invoke all handlers
            for handler in handlers:
                plugin_name = handler['plugin']
                try:
                    result = handler['function'](*args, **kwargs)
                    results[plugin_name] = result
                except Exception as e:
                    logger.error(f"Error invoking hook '{hook_name}' handler from plugin '{plugin_name}': {e}")
                    results[plugin_name] = {'error': str(e)}
            
        return results
    
    def register_data_type_handler(self, plugin_name: str, data_type: str, 
                                 description: str, priority: int = 0) -> bool:
        """
        Register a plugin as handler for a specific data type
        
        Args:
            plugin_name: Name of the plugin that can handle the data type
            data_type: MIME type or data type descriptor
            description: Description of what the plugin can do with this data type
            priority: Priority level (higher number means higher priority)
            
        Returns:
            True if registration was successful
        """
        with self._lock:
            if data_type not in self.data_types:
                self.data_types[data_type] = []
                
            # Check if this plugin is already registered for this data type
            for handler in self.data_types[data_type]:
                if handler['plugin'] == plugin_name:
                    # Update existing registration
                    handler['description'] = description
                    handler['priority'] = priority
                    return True
            
            # Add new handler
            self.data_types[data_type].append({
                'plugin': plugin_name,
                'description': description,
                'priority': priority,
                'registered_at': time.time()
            })
            
            # Sort handlers by priority (highest first)
            self.data_types[data_type].sort(key=lambda h: h['priority'], reverse=True)
            
            logger.info(f"Plugin '{plugin_name}' registered as handler for data type: {data_type}")
            return True
    
    def get_data_type_handlers(self, data_type: str) -> List[Dict[str, Any]]:
        """
        Get all handlers for a specific data type
        
        Args:
            data_type: MIME type or data type descriptor
            
        Returns:
            List of handler dictionaries sorted by priority
        """
        return self.data_types.get(data_type, [])
    
    def register_file_extension_handler(self, plugin_name: str, extension: str, 
                                      description: str, priority: int = 0) -> bool:
        """
        Register a plugin as handler for files with a specific extension
        
        Args:
            plugin_name: Name of the plugin that can handle the file extension
            extension: File extension (e.g. 'jpg', 'pdf')
            description: Description of what the plugin can do with this file type
            priority: Priority level (higher number means higher priority)
            
        Returns:
            True if registration was successful
        """
        with self._lock:
            # Normalize extension (remove leading dot and convert to lowercase)
            extension = extension.lower().lstrip('.')
            
            if extension not in self.extensions:
                self.extensions[extension] = []
                
            # Check if this plugin is already registered for this extension
            for handler in self.extensions[extension]:
                if handler['plugin'] == plugin_name:
                    # Update existing registration
                    handler['description'] = description
                    handler['priority'] = priority
                    return True
            
            # Add new handler
            self.extensions[extension].append({
                'plugin': plugin_name,
                'description': description,
                'priority': priority,
                'registered_at': time.time()
            })
            
            # Sort handlers by priority (highest first)
            self.extensions[extension].sort(key=lambda h: h['priority'], reverse=True)
            
            logger.info(f"Plugin '{plugin_name}' registered as handler for file extension: {extension}")
            return True
    
    def get_file_extension_handlers(self, extension: str) -> List[Dict[str, Any]]:
        """
        Get all handlers for a specific file extension
        
        Args:
            extension: File extension (with or without leading dot)
            
        Returns:
            List of handler dictionaries sorted by priority
        """
        # Normalize extension
        extension = extension.lower().lstrip('.')
        return self.extensions.get(extension, [])
    
    def register_integration(self, plugin_name: str, integration_name: str, 
                           description: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a plugin as providing an integration with an external system
        
        Args:
            plugin_name: Name of the plugin providing the integration
            integration_name: Name of the integration
            description: Description of the integration
            config: Optional configuration information for the integration
            
        Returns:
            True if registration was successful
        """
        with self._lock:
            if integration_name in self.integrations:
                logger.warning(f"Integration '{integration_name}' already registered by {self.integrations[integration_name]['plugin']}")
                return False
                
            self.integrations[integration_name] = {
                'plugin': plugin_name,
                'description': description,
                'config': config or {},
                'registered_at': time.time()
            }
            
            logger.info(f"Plugin '{plugin_name}' registered integration: {integration_name}")
            return True
    
    def get_integration(self, integration_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific integration
        
        Args:
            integration_name: Name of the integration
            
        Returns:
            Dictionary with integration information or None if not found
        """
        return self.integrations.get(integration_name)
    
    def get_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered capabilities"""
        return self.capabilities.copy()
    
    def get_services(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered services"""
        # Filter out the actual function objects to make the result serializable
        services = {}
        for name, info in self.services.items():
            services[name] = {
                'plugin': info['plugin'],
                'description': info['description'],
                'signature': info['signature'],
                'registered_at': info['registered_at']
            }
        return services
    
    def get_hooks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all registered hooks"""
        # Filter out the actual function objects to make the result serializable
        hooks = {}
        for name, handlers in self.hooks.items():
            hooks[name] = [{
                'plugin': handler['plugin'],
                'registered_at': handler['registered_at']
            } for handler in handlers]
        return hooks
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            'capabilities_count': len(self.capabilities),
            'services_count': len(self.services),
            'hooks_count': len(self.hooks),
            'data_types_count': len(self.data_types),
            'extensions_count': len(self.extensions),
            'integrations_count': len(self.integrations),
            'service_calls': self.stats['service_calls'].copy(),
            'hook_invocations': self.stats['hook_invocations'].copy()
        }


# Create a singleton instance
registry = PluginRegistry()

# Decorator for registering services
def service(name: str, description: str):
    """Decorator for registering a function as a service"""
    def decorator(func):
        plugin_name = func.__module__.split('.')[-1]  # Use module name as plugin name
        registry.register_service(plugin_name, name, func, description)
        return func
    return decorator

# Decorator for registering hook handlers
def hook_handler(hook_name: str):
    """Decorator for registering a function as a hook handler"""
    def decorator(func):
        plugin_name = func.__module__.split('.')[-1]  # Use module name as plugin name
        registry.register_hook(plugin_name, hook_name, func)
        return func
    return decorator
