"""
Location model for CreepyAI.
"""
import datetime
from typing import Dict, Any, Optional
import json
import uuid

class Location:
    """Represents a geographical location with metadata"""
    
    def __init__(self, lat=0.0, lon=0.0, name="", description="", location_type="", 
                 source="", accuracy=0, timestamp=None, tags=None):
        self.id = str(uuid.uuid4())
        self.lat = float(lat)
        self.lon = float(lon)
        self.name = name
        self.description = description
        self.location_type = location_type
        self.source = source
        self.accuracy = accuracy
        self.timestamp = timestamp or datetime.now()
        self.tags = tags or []
        self.custom_properties = {}
        
    def to_dict(self):
        """Convert location to dictionary for serialization"""
        return {
            "id": self.id,
            "lat": self.lat,
            "lon": self.lon,
            "name": self.name,
            "description": self.description,
            "location_type": self.location_type,
            "source": self.source,
            "accuracy": self.accuracy,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "custom_properties": self.custom_properties
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create location from dictionary (deserialization)"""
        location = cls(
            lat=data.get("lat", 0),
            lon=data.get("lon", 0),
            name=data.get("name", ""),
            description=data.get("description", ""),
            location_type=data.get("location_type", ""),
            source=data.get("source", ""),
            accuracy=data.get("accuracy", 0),
            tags=data.get("tags", [])
        )
        location.id = data.get("id", location.id)
        
        # Parse timestamp
        if "timestamp" in data:
            try:
                location.timestamp = datetime.fromisoformat(data["timestamp"])
            except (ValueError, TypeError):
                location.timestamp = datetime.now()
                
        location.custom_properties = data.get("custom_properties", {})
        return location
