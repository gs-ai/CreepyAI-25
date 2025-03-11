#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Location model for CreepyAI.

This class represents a geolocation point with metadata.
"""
import uuid
import datetime
from typing import Dict, Any, Optional


class Location:
    """
    Represents a geographic location with metadata.
    Used for storing and managing location data within CreepyAI.
    """
    
    def __init__(self, latitude: float = 0.0, longitude: float = 0.0, 
                 timestamp: Optional[datetime.datetime] = None,
                 context: str = "", plugin: str = "",
                 shortName: str = "", infowindow: str = ""):
        """
        Initialize a new Location instance.
        
        Args:
            latitude: The latitude coordinate
            longitude: The longitude coordinate
            timestamp: The datetime when this location was recorded
            context: Additional context about the location
            plugin: Name of the plugin that provided this location
            shortName: A short name/title for this location
            infowindow: HTML content for the map info window
        """
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.datetime = timestamp or datetime.datetime.now()
        self.context = context
        self.plugin = plugin
        self.shortName = shortName
        self.infowindow = infowindow
        self.visible = True
        self.id = str(uuid.uuid4())
        self.accuracy = None  # Accuracy in meters if available
        self.altitude = None  # Altitude if available
        self.source = None    # Source of the location data
        self.metadata = {}    # Additional metadata dictionary
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert location to dictionary representation"""
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'datetime': self.datetime.isoformat() if self.datetime else None,
            'timestamp': self.datetime.isoformat() if self.datetime else None,
            'context': self.context,
            'plugin': self.plugin,
            'name': self.shortName,
            'description': self.infowindow,
            'visible': self.visible,
            'accuracy': self.accuracy,
            'altitude': self.altitude,
            'source': self.source,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        """Create a Location instance from a dictionary"""
        location = cls(
            latitude=data.get('latitude', 0.0),
            longitude=data.get('longitude', 0.0),
            context=data.get('context', ''),
            plugin=data.get('plugin', ''),
            shortName=data.get('name', '') or data.get('shortName', ''),
            infowindow=data.get('description', '') or data.get('infowindow', '')
        )
        
        # Handle timestamp/datetime
        timestamp = data.get('timestamp') or data.get('datetime')
        if timestamp:
            if isinstance(timestamp, str):
                try:
                    location.datetime = datetime.datetime.fromisoformat(timestamp)
                except ValueError:
                    # Try to parse other formats if needed
                    pass
            elif isinstance(timestamp, (int, float)):
                location.datetime = datetime.datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, datetime.datetime):
                location.datetime = timestamp
        
        # Set other attributes
        if 'id' in data:
            location.id = data['id']
        if 'visible' in data:
            location.visible = data['visible']
        if 'accuracy' in data:
            location.accuracy = data['accuracy']
        if 'altitude' in data:
            location.altitude = data['altitude']
        if 'source' in data:
            location.source = data['source']
        if 'metadata' in data and isinstance(data['metadata'], dict):
            location.metadata = data['metadata']
        
        return location
    
    def __str__(self) -> str:
        """Return string representation of the location"""
        return f"Location({self.latitude}, {self.longitude}, {self.datetime})"
    
    def __repr__(self) -> str:
        """Return developer representation of the location"""
        return f"Location(lat={self.latitude}, lng={self.longitude}, id={self.id})"
