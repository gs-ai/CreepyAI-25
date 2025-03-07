#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Base Plugin class for CreepyAI
All plugins should inherit from this class
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import hashlib

logger = logging.getLogger(__name__)

class LocationPoint:
    """
    Class representing a location point with coordinates and metadata
    """
    
    def __init__(self, latitude: float, longitude: float, timestamp: Optional[datetime] = None,
                source: str = "", context: str = "", accuracy: float = 0.0):
        """
        Initialize a LocationPoint
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            timestamp: When the location was recorded (defaults to current time)
            source: Source of the location data
            context: Additional context information
            accuracy: Accuracy in meters (if available)
        """
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.timestamp = timestamp or datetime.now()
        self.source = source
        self.context = context
        self.accuracy = accuracy
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the LocationPoint to a dictionary
        
        Returns:
            Dictionary representation of the LocationPoint
        """
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'source': self.source,
            'context': self.context,
            'accuracy': self.accuracy
        }
    
    def distance_to(self, other: 'LocationPoint') -> float:
        """
        Calculate the distance in meters to another LocationPoint
        
        Args:
            other: Another LocationPoint
            
        Returns:
            Distance in meters
        """
        from math import radians, cos, sin, asin, sqrt
        
        # Haversine formula
        lon1, lat1, lon2, lat2 = map(
            radians, [self.longitude, self.latitude, other.longitude, other.latitude]
        )
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000  # Earth radius in meters
        
        return c * r
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LocationPoint':
        """
        Create a LocationPoint from a dictionary
        
        Args:
            data: Dictionary containing location data
            
        Returns:
            New LocationPoint instance
        """
        # Handle timestamp conversion
        timestamp = None
        if 'timestamp' in data and data['timestamp']:
            if isinstance(data['timestamp'], str):
                try:
                    timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                except ValueError:
                    # Try different timestamp formats
                    for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                        try:
                            timestamp = datetime.strptime(data['timestamp'], fmt)
                            break
                        except ValueError:
                            pass
            elif isinstance(data['timestamp'], (int, float)):
                timestamp = datetime.fromtimestamp(data['timestamp'])
        
        return cls(
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            timestamp=timestamp,
            source=data.get('source', ''),
            context=data.get('context', ''),
            accuracy=float(data.get('accuracy', 0.0))
        )
    
    def __str__(self) -> str:
        """
        String representation of the LocationPoint
        
        Returns:
            String in format "lat, lon (source) - timestamp"
        """
        ts_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else 'Unknown time'
        return f"{self.latitude}, {self.longitude} ({self.source}) - {ts_str}"


class BasePlugin:
    """
    Base class for all CreepyAI plugins
    All plugins must inherit from this class
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the plugin
        
        Args:
            name: Human-readable name of the plugin
            description: Description of what the plugin does
        """
        self.name = name
        self.description = description
        self.version = "1.0.0"
        self.author = ""
        
        # Directory for plugin data
        self.data_dir = os.path.join(os.path.expanduser('~'), '.creepyai', 'plugins', self._get_plugin_id())
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Plugin configuration
        self.config = {}
        
        # Load configuration from config.json if it exists
        self._load_config()
    
    def _get_plugin_id(self) -> str:
        """Get the plugin ID (used for directory and config naming)"""
        return self.__class__.__name__
    
    def _get_config_path(self) -> str:
        """Get the path to the plugin's configuration file"""
        return os.path.join(self.data_dir, 'config.json')
    
    def _load_config(self) -> None:
        """Load the plugin configuration from config.json"""
        config_path = self._get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.config.update(json.load(f))
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load plugin configuration: {e}")
    
    def _save_config(self) -> None:
        """Save the plugin configuration to config.json"""
        config_path = self._get_config_path()
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save plugin configuration: {e}")
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the plugin with provided settings
        
        Args:
            config: Dictionary containing configuration settings
        """
        # Update configuration
        self.config.update(config)
        
        # Save configuration
        self._save_config()
    
    def is_configured(self) -> Tuple[bool, str]:
        """
        Check if the plugin is properly configured
        
        Returns:
            Tuple of (is_configured, message)
        """
        return True, f"{self.name} plugin is configured"
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        """
        Get available configuration options for this plugin
        
        Returns:
            List of configuration option dictionaries
        """
        return []
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None,
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
        """
        Collect location data for the given target
        
        Args:
            target: Target to collect data for (e.g. username, ID, etc.)
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            List of LocationPoint objects
        """
        # To be implemented by subclasses
        return []
    
    def search_for_targets(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for targets matching the given search term
        
        Args:
            search_term: Search query
            
        Returns:
            List of target dictionaries containing at least:
            - targetId: Unique identifier for the target
            - targetName: Display name for the target
            - pluginName: Name of this plugin
        """
        # Default implementation - return a single target with the search term
        return [{
            'targetId': search_term,
            'targetName': search_term,
            'pluginName': self.name
        }]
    
    def get_version(self) -> str:
        """
        Get the plugin version
        
        Returns:
            Version string
        """
        return self.version
    
    def get_author(self) -> str:
        """
        Get the plugin author
        
        Returns:
            Author name/email
        """
        return self.author
    
    def cleanup(self) -> None:
        """
        Clean up resources when the plugin is being unloaded
        """
        pass
    
    def get_plugin_status(self) -> Dict[str, Any]:
        """
        Get the current status of the plugin
        
        Returns:
            Dictionary with status information
        """
        configured, message = self.is_configured()
        return {
            'name': self.name,
            'version': self.version,
            'configured': configured,
            'status_message': message,
            'config_count': len(self.config)
        }
