#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import json
import hashlib
from math import sin, cos, sqrt, atan2, radians

logger = logging.getLogger(__name__)

class Location:
    """
    Represents a geographical location with metadata.
    This is the core data object for CreepyAI.
    """
    
    def __init__(self, latitude=0.0, longitude=0.0, time=None):
        """
        Initialize a location.
        
        Args:
            latitude (float): The latitude in decimal degrees
            longitude (float): The longitude in decimal degrees
            time (datetime): When the location was recorded
        """
        self.latitude = float(latitude) if latitude is not None else 0.0
        self.longitude = float(longitude) if longitude is not None else 0.0
        self.datetime = time or datetime.datetime.now()
        self.context = {}
        self.source = ""
        self.accuracy = "unknown"
        self.plugin = ""
        self.confidence = 0.0
        self.icon = ""
        self.altitude = None
        self.shortName = ""
        self.infowindow = ""
        self.id = None
        self.target_id = None
    
    @property
    def is_valid(self):
        """Check if the location has valid coordinates."""
        return -90 <= self.latitude <= 90 and -180 <= self.longitude <= 180 and self.latitude != 0 and self.longitude != 0
    
    @property
    def datetime_friendly(self):
        """Get a human-readable date string."""
        if isinstance(self.datetime, datetime.datetime):
            return self.datetime.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(self.datetime, str):
            return self.datetime
        else:
            return str(self.datetime)
    
    def to_dict(self):
        """Convert the location to a dictionary."""
        loc_dict = {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'datetime': self.datetime_friendly,
            'context': self.context,
            'source': self.source,
            'accuracy': self.accuracy,
            'plugin': self.plugin,
            'confidence': self.confidence
        }
        
        if self.altitude is not None:
            loc_dict['altitude'] = self.altitude
            
        if self.shortName:
            loc_dict['shortName'] = self.shortName
            
        if self.infowindow:
            loc_dict['infowindow'] = self.infowindow
            
        if self.id is not None:
            loc_dict['id'] = self.id
            
        if self.target_id is not None:
            loc_dict['target_id'] = self.target_id
            
        return loc_dict
    
    def to_json(self):
        """Convert the location to JSON."""
        return json.dumps(self.to_dict())
    
    def get_context(self, key, default=""):
        """Get a specific context value."""
        if isinstance(self.context, dict):
            return self.context.get(key, default)
        return default
    
    @classmethod
    def from_dict(cls, data):
        """Create a Location from a dictionary."""
        location = cls()
        
        # Set basic properties
        location.latitude = float(data.get('latitude', 0.0))
        location.longitude = float(data.get('longitude', 0.0))
        
        # Handle time conversion
        time_str = data.get('datetime')
        if time_str:
            try:
                location.datetime = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    # Try ISO format
                    location.datetime = datetime.datetime.fromisoformat(time_str)
                except ValueError:
                    logger.warning(f"Could not parse time: {time_str}")
                    location.datetime = datetime.datetime.now()
        
        # Set other properties
        location.context = data.get('context', {})
        location.source = data.get('source', '')
        location.accuracy = data.get('accuracy', 'unknown')
        location.plugin = data.get('plugin', '')
        location.confidence = float(data.get('confidence', 0.0))
        location.altitude = data.get('altitude')
        location.shortName = data.get('shortName', '')
        location.infowindow = data.get('infowindow', '')
        location.id = data.get('id')
        location.target_id = data.get('target_id')
        
        return location
    
    @classmethod
    def from_json(cls, json_str):
        """Create a Location from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self):
        """String representation of the location."""
        return f"Location({self.latitude}, {self.longitude}) @ {self.datetime_friendly}"
    
    def __eq__(self, other):
        """Check if two locations are equal."""
        if not isinstance(other, Location):
            return False
        
        # Two locations are considered equal if they have the same coordinates
        # at the same time from the same source
        return (abs(self.latitude - other.latitude) < 0.0001 and
                abs(self.longitude - other.longitude) < 0.0001 and
                self.datetime == other.datetime and
                self.source == other.source)
    
    def __hash__(self):
        """Hash function for the location."""
        # Create a hash based on coordinates, time and source
        hash_str = f"{self.latitude:.6f}:{self.longitude:.6f}:{self.datetime_friendly}:{self.source}"
        return hash(hash_str)
    
    def get_distance(self, other):
        """
        Calculate the distance to another location in kilometers.
        Uses the Haversine formula for spherical earth.
        """
        # Approximate radius of earth in km
        R = 6371.0
        
        lat1 = radians(self.latitude)
        lon1 = radians(self.longitude)
        lat2 = radians(other.latitude)
        lon2 = radians(other.longitude)
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        return distance