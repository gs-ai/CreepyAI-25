#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Plugin Compatibility Layer for CreepyAI
This module helps plugins adapt to different versions of the core application
and ensures backward compatibility with legacy plugins.
"""

import os
import sys
import logging
import importlib
import inspect
from typing import Dict, Any, Optional, List, Tuple, Type, Callable
import traceback

logger = logging.getLogger(__name__)

class PluginAdapter:
    """
    Adapter class for ensuring plugin compatibility with different versions
    of the CreepyAI application.
    """
    
    def __init__(self):
        self.legacy_plugin_classes = {}
        self.compatibility_handlers = {}
        self.register_default_handlers()
        
    def register_default_handlers(self):
        """Register built-in compatibility handlers"""
        # Convert between location formats
        self.register_handler(
            'location_format', 
            lambda data: self._convert_location_format(data)
        )
        
        # Convert between target formats
        self.register_handler(
            'target_format',
            lambda data: self._convert_target_format(data)
        )
        
        # Convert between configuration formats
        self.register_handler(
            'config_format',
            lambda data: self._convert_config_format(data)
        )
    
    def register_handler(self, name: str, handler: Callable):
        """Register a compatibility handler function"""
        self.compatibility_handlers[name] = handler
        logger.debug(f"Registered compatibility handler: {name}")
        
    def register_legacy_plugin_class(self, class_name: str, class_type: Type):
        """Register a legacy plugin class for automatic adaptation"""
        self.legacy_plugin_classes[class_name] = class_type
        logger.debug(f"Registered legacy plugin class: {class_name}")
        
    def wrap_legacy_plugin(self, plugin_instance) -> Any:
        """
        Wrap a legacy plugin instance to make it compatible with current system
        
        Returns:
            Wrapped plugin instance compatible with current system
        """
        class_name = plugin_instance.__class__.__name__
        
        if class_name in self.legacy_plugin_classes:
            # Use specific adapter for this legacy plugin class
            adapter_class = self.legacy_plugin_classes[class_name]
            return adapter_class(plugin_instance)
        else:
            # Use generic adapter
            return LegacyPluginAdapter(plugin_instance)
            
    def _convert_location_format(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert between different location data formats
        
        Args:
            location_data: Location data in any recognized format
            
        Returns:
            Location data in standardized format
        """
        standardized = {}
        
        # Handle various formats
        if isinstance(location_data, dict):
            # Extract latitude
            if 'lat' in location_data:
                standardized['lat'] = float(location_data['lat'])
            elif 'latitude' in location_data:
                standardized['lat'] = float(location_data['latitude'])
                
            # Extract longitude
            if 'lon' in location_data:
                standardized['lon'] = float(location_data['lon'])
            elif 'lng' in location_data:
                standardized['lon'] = float(location_data['lng'])
            elif 'longitude' in location_data:
                standardized['lon'] = float(location_data['longitude'])
                
            # Extract date/timestamp
            if 'date' in location_data:
                standardized['date'] = location_data['date']
            elif 'timestamp' in location_data:
                standardized['date'] = location_data['timestamp']
                
            # Extract source
            if 'plugin' in location_data:
                standardized['plugin'] = location_data['plugin']
            elif 'source' in location_data:
                standardized['plugin'] = location_data['source']
                
            # Extract context
            if 'context' in location_data:
                standardized['context'] = location_data['context']
            elif 'shortName' in location_data:
                standardized['context'] = location_data['shortName']
                
            # Copy additional fields as needed
            for field in ['infowindow', 'accuracy', 'shortName']:
                if field in location_data:
                    standardized[field] = location_data[field]
        
        return standardized
    
    def _convert_target_format(self, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert between different target data formats
        
        Args:
            target_data: Target data in any recognized format
            
        Returns:
            Target data in standardized format
        """
        standardized = {}
        
        # Handle various formats
        if isinstance(target_data, dict):
            # Extract target ID
            if 'targetId' in target_data:
                standardized['targetId'] = target_data['targetId']
            elif 'id' in target_data:
                standardized['targetId'] = target_data['id']
                
            # Extract target name
            if 'targetName' in target_data:
                standardized['targetName'] = target_data['targetName']
            elif 'name' in target_data:
                standardized['targetName'] = target_data['name']
                
            # Extract plugin/source
            if 'pluginName' in target_data:
                standardized['pluginName'] = target_data['pluginName']
            elif 'plugin' in target_data:
                standardized['pluginName'] = target_data['plugin']
            elif 'source' in target_data:
                standardized['pluginName'] = target_data['source']
                
            # Extract additional fields
            for field in ['targetUser', 'icon', 'username', 'email', 'type']:
                if field in target_data:
                    standardized[field] = target_data[field]
        
        return standardized
    
    def _convert_config_format(self, config_data: Any) -> Dict[str, Any]:
        """
        Convert between different configuration formats
        
        Args:
            config_data: Configuration data in any recognized format
            
        Returns:
            Configuration data in standardized format
        """
        standardized = {}
        
        # Handle different configuration formats
        if isinstance(config_data, dict):
            # Direct dictionary format
            standardized = config_data.copy()
        elif hasattr(config_data, 'sections') and callable(getattr(config_data, 'sections')):
            # ConfigParser format
            for section in config_data.sections():
                standardized[section] = {}
                for key, value in config_data.items(section):
                    standardized[section][key] = value
        
        return standardized


class LegacyPluginAdapter:
    """Generic adapter for legacy plugins to work with current system"""
    
    def __init__(self, legacy_plugin):
        self.legacy_plugin = legacy_plugin
        self.name = getattr(legacy_plugin, 'name', legacy_plugin.__class__.__name__)
        self.description = getattr(legacy_plugin, 'description', "Legacy plugin")
        
    def __getattr__(self, name):
        """Forward attribute access to the wrapped legacy plugin"""
        return getattr(self.legacy_plugin, name)
        
    def collect_locations(self, target, date_from=None, date_to=None):
        """Adapt to legacy location collection methods"""
        try:
            # Try standard method first
            if hasattr(self.legacy_plugin, 'collect_locations'):
                return self.legacy_plugin.collect_locations(target, date_from, date_to)
                
            # Try returnLocations (old API)
            if hasattr(self.legacy_plugin, 'returnLocations'):
                search_params = {}
                if date_from:
                    search_params['dateFrom'] = date_from
                if date_to:
                    search_params['dateTo'] = date_to
                    
                # Convert target string to dict if needed
                target_obj = target
                if isinstance(target, str):
                    target_obj = {
                        'targetId': target,
                        'targetName': target,
                        'targetUser': target,
                        'pluginName': self.name
                    }
                    
                locations = self.legacy_plugin.returnLocations(target_obj, search_params)
                
                # Convert to standard format
                from plugins.base_plugin import LocationPoint
                
                result = []
                for loc in locations:
                    result.append(LocationPoint.from_dict(loc))
                return result
                
            # No suitable method found
            logger.error(f"No compatible location collection method found in {self.name}")
            return []
            
        except Exception as e:
            logger.error(f"Error adapting legacy plugin {self.name}: {str(e)}")
            logger.debug(traceback.format_exc())
            return []
            
    def search_for_targets(self, search_term):
        """Adapt to legacy target search methods"""
        try:
            # Try standard method first
            if hasattr(self.legacy_plugin, 'search_for_targets'):
                return self.legacy_plugin.search_for_targets(search_term)
                
            # Try searchForTargets (old API)
            if hasattr(self.legacy_plugin, 'searchForTargets'):
                return self.legacy_plugin.searchForTargets(search_term)
                
            # Use default implementation
            return [{
                'pluginName': self.name,
                'targetName': search_term,
                'targetUser': search_term,
                'targetId': f"{self.name}_{search_term}"
            }]
            
        except Exception as e:
            logger.error(f"Error adapting legacy plugin {self.name}: {str(e)}")
            logger.debug(traceback.format_exc())
            return []
            
    def is_configured(self):
        """Adapt to legacy configuration check methods"""
        try:
            # Try standard method first
            if hasattr(self.legacy_plugin, 'is_configured'):
                return self.legacy_plugin.is_configured()
                
            # Try isConfigured (old API)
            if hasattr(self.legacy_plugin, 'isConfigured'):
                return self.legacy_plugin.isConfigured()
                
            # Default to configured
            return True, f"{self.name} is assumed to be configured"
            
        except Exception as e:
            logger.error(f"Error checking if legacy plugin {self.name} is configured: {str(e)}")
            logger.debug(traceback.format_exc())
            return False, f"Error: {str(e)}"
