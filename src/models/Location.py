#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import json
import hashlib
import math
from functools import cached_property

logger = logging.getLogger(__name__)

class Location:
    """
    Represents a geographical location with metadata.
    This is the core data object for CreepyAI.
    """
    
    # Earth radius in km (for distance calculations)
    EARTH_RADIUS = 6371.0
    
    def __init__(self, latitude=0.0, longitude=0.0, time=None):
        """
        Initialize a location.
        
        Args:
            latitude (float): The latitude in decimal degrees
            longitude (float): The longitude in decimal degrees
            time (datetime): When the location was recorded
        """
        self._latitude = 0.0
        self._longitude = 0.0
        
        # Set attributes with validation
        self.latitude = latitude
        self.longitude = longitude
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
        self._hash = None  # Cache for hash value
        self.visible = True
        self.attributes = {}
    
    @property
    def latitude(self):
        """Get latitude."""
        return self._latitude
    
    @latitude.setter
    def latitude(self, value):
        """Set latitude with validation."""
        if value is None:
            self._latitude = 0.0
            return
            
        try:
            value = float(value)
            if -90 <= value <= 90:
                self._latitude = value
            else:
                logger.warning(f"Invalid latitude value: {value}")
                self._latitude = 0.0
        except (ValueError, TypeError):
            logger.warning(f"Invalid latitude value: {value}")
            self._latitude = 0.0
    
    @property
    def longitude(self):
        """Get longitude."""
        return self._longitude
    
    @longitude.setter
    def longitude(self, value):
        """Set longitude with validation."""
        if value is None:
            self._longitude = 0.0
            return
            
        try:
            value = float(value)
            if -180 <= value <= 180:
                self._longitude = value
            else:
                logger.warning(f"Invalid longitude value: {value}")
                self._longitude = 0.0
        except (ValueError, TypeError):
            logger.warning(f"Invalid longitude value: {value}")
            self._longitude = 0.0
    
    @cached_property
    def is_valid(self):
        """Check if the location has valid coordinates."""
        return (-90 <= self.latitude <= 90 and 
                -180 <= self.longitude <= 180 and 
                self.latitude != 0 and 
                self.longitude != 0)
    
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
        location_dict = {
            'id': self.id,
            'plugin': self.plugin,
            'datetime': self.datetime.isoformat(),
            'shortName': self.shortName,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'altitude': self.altitude,
            'accuracy': self.accuracy,
            'context': self.context,
            'infowindow': self.infowindow,
            'visible': self.visible,
            'attributes': self.attributes
        }
        return json.dumps(location_dict)
    
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
        location.visible = data.get('visible', True)
        location.attributes = data.get('attributes', {})
        
        return location
    
    @classmethod
    def from_json(cls, json_str):
        """Create a Location from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self):
        """String representation of the location."""
        return f"Location({self.latitude:.6f}, {self.longitude:.6f}) @ {self.datetime_friendly}"
    
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
        if self._hash is None:
            # Create a hash based on coordinates, time and source
            hash_str = f"{self.latitude:.6f}:{self.longitude:.6f}:{self.datetime_friendly}:{self.source}"
            self._hash = hash(hash_str)
        return self._hash
    
    def get_distance(self, other):
        """
        Calculate the distance to another location in kilometers using Haversine formula.
        
        Args:
            other (Location): Other location
            
        Returns:
            float: Distance in kilometers
        """
        # Convert coordinates from degrees to radians
        lat1_rad = math.radians(self.latitude)
        lon1_rad = math.radians(self.longitude)
        lat2_rad = math.radians(other.latitude)
        lon2_rad = math.radians(other.longitude)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        # Calculate distance
        distance = self.EARTH_RADIUS * c
        return distance
    
    def updateId(self):
        """Generate a unique ID based on properties."""
        # Generate ID if not already set
        if self.id is None:
            string = self.plugin + str(self.datetime) + str(self.longitude) + str(self.latitude) + self.context
            self.id = hashlib.md5(string.encode('utf-8')).hexdigest()
        return self.id

    def getAttributeKeys(self):
        """Return all the attribute keys for this location."""
        return self.attributes.keys()
        
    def getAttribute(self, key):
        """Get a specific attribute value by key."""
        if key in self.attributes:
            return self.attributes[key]
        return None
        
    def addAttribute(self, key, value):
        """Add a new attribute to this location."""
        self.attributes[key] = value

    def to_database_dict(self):
        """Convert to a dictionary format suitable for database storage"""
        loc_dict = {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'date': self.datetime.isoformat() if hasattr(self.datetime, 'isoformat') else str(self.datetime),
            'source': self.plugin,
            'source_type': getattr(self, 'source_type', 'plugin'),
            'confidence': getattr(self, 'confidence', 0.0),
            'context': self.context
        }
        
        # Add any additional attributes that might exist
        for attr in ['target_id', 'altitude', 'accuracy']:
            if hasattr(self, attr):
                loc_dict[attr] = getattr(self, attr)
                
        return loc_dict

    @classmethod
    def from_database_dict(cls, data):
        """Create a Location from database dictionary format"""
        loc = cls()
        
        loc.latitude = data.get('latitude', 0.0)
        loc.longitude = data.get('longitude', 0.0)
        
        # Parse datetime
        date_str = data.get('date')
        if date_str:
            try:
                from datetime import datetime
                loc.datetime = datetime.fromisoformat(date_str)
            except ValueError:
                loc.datetime = datetime.now()
                
        loc.plugin = data.get('source', '')
        loc.context = data.get('context', {})
        loc.shortName = data.get('short_name', '')
        loc.infowindow = data.get('infowindow', '')
        
        # Add optional fields
        if 'id' in data:
            loc.id = data['id']
        if 'target_id' in data:
            loc.target_id = data['target_id']
        if 'altitude' in data:
            loc.altitude = data['altitude']
        if 'accuracy' in data:
            loc.accuracy = data['accuracy']
        if 'visible' in data:
            loc.visible = data['visible']
            
        return loc
