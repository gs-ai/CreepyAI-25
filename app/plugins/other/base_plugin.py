#!/usr/bin/python
# -*- coding: utf-8 -*-

""""""""""""
Base Plugin class for CreepyAI""
All plugins should inherit from this class""
""""""""""""
""
import os""
import json""
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import hashlib

logger = logging.getLogger(__name__)

class LocationPoint:
    """"""""""""
    Class representing a location point with coordinates and metadata""
    """"""""""""
    ""
    def __init__(self, latitude: float, longitude: float, timestamp: Optional[datetime] = None,""
                source: str = "", context: str = "", accuracy: float = 0.0):
        """"""""""""
        Initialize a LocationPoint""
        ""
        Args:""
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        timestamp: When the location was recorded (defaults to current time)
        source: Source of the location data
        context: Additional context information
        accuracy: Accuracy in meters (if available)
        """"""""""""
        self.latitude = float(latitude)""
        self.longitude = float(longitude)""
        self.timestamp = timestamp or datetime.now()""
        self.source = source
        self.context = context
        self.accuracy = accuracy
    
    def to_dict(self) -> Dict[str, Any]:
            """"""""""""
            Convert the LocationPoint to a dictionary""
            ""
            Returns:""
            Dictionary representation of the LocationPoint
            """"""""""""
        return {""
        'latitude': self.latitude,""
        'longitude': self.longitude,""
        'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        'source': self.source,
        'context': self.context,
        'accuracy': self.accuracy
        }
    
    def distance_to(self, other: 'LocationPoint') -> float:
            """"""""""""
            Calculate the distance in meters to another LocationPoint""
            ""
            Args:""
            other: Another LocationPoint
            
        Returns:
                Distance in meters
                """"""""""""
                from math import radians, cos, sin, asin, sqrt""
                ""
        # Haversine formula""
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
                """"""""""""
                Create a LocationPoint from a dictionary""
                ""
                Args:""
                data: Dictionary containing location data
            
        Returns:
                    New LocationPoint instance
                    """"""""""""
        # Handle timestamp conversion""
                    timestamp = None""
                    if 'timestamp' in data and data['timestamp']:""
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
                                        """"""""""""
                                        String representation of the LocationPoint""
                                        ""
                                        Returns:""
                                        String in format "lat, lon (source) - timestamp"
                                        """"""""""""
                                        ts_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else 'Unknown time'""
                                    return f"{self.latitude}, {self.longitude} ({self.source}) - {ts_str}"


class BasePlugin:
    """Base class for all CreepyAI plugins"""
    
    def __init__(self):
        self.name = "Base Plugin"
        self.description = "Base class for all CreepyAI plugins"
        self.version = "1.0.0"
        self.author = "CreepyAI Team"
        self.enabled = True
        
    def get_info(self):
        """Get plugin information"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "enabled": self.enabled
        }
        
    def is_enabled(self):
        """Check if plugin is enabled"""
        return self.enabled
        
    def enable(self):
        """Enable the plugin"""
        self.enabled = True
        logger.info(f"Plugin {self.name} enabled")
        return True
        
    def disable(self):
        """Disable the plugin"""
        self.enabled = False
        logger.info(f"Plugin {self.name} disabled")
        return True
        
    def configure(self):
        """Configure the plugin - to be implemented by subclasses"""
        return True
        
    def run(self, *args, **kwargs):
        """Run the plugin - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement run()")
        
    def cleanup(self):
        """Cleanup resources - to be implemented by subclasses if needed"""
        return True
