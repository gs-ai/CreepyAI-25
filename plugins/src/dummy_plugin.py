"""
Dummy plugin for CreepyAI testing purposes.
This plugin generates random locations for testing.
"""

import random
import datetime
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class DummyPlugin:
    """Simple dummy plugin that generates random locations"""
    
    def __init__(self):
        """Initialize the plugin"""
        self.name = "Dummy Plugin"
        self.description = "Generates random locations for testing"
        self.version = "1.0.0"
        self.author = "CreepyAI"
        
        # Default configuration
        self.config = {
            "location_count": 10,
            "center_lat": 37.7749,
            "center_lng": -122.4194,
            "radius_km": 5.0
        }
    
    def get_version(self):
        """Return plugin version"""
        return self.version
    
    def is_configured(self):
        """Check if plugin is configured correctly"""
        if "location_count" not in self.config:
            return False, "Missing required configuration: location_count"
        return True, "Plugin is configured correctly"
    
    def set_configuration(self, config):
        """Set plugin configuration"""
        self.config.update(config)
        return True
    
    def get_configuration(self):
        """Get plugin configuration"""
        return self.config
    
    def collect_locations(self, target, date_from=None, date_to=None):
        """Collect locations for the target"""
        count = self.config.get('location_count', 10)
        center_lat = self.config.get('center_lat', 37.7749)
        center_lng = self.config.get('center_lng', -122.4194)
        radius_km = self.config.get('radius_km', 5.0)
        
        locations = []
        for i in range(count):
            # Create random location around center point
            lat = center_lat + (random.random() - 0.5) * radius_km * 0.01
            lng = center_lng + (random.random() - 0.5) * radius_km * 0.01
            
            # Random timestamp within last 30 days or between date range
            if date_from and date_to:
                days_range = (date_to - date_from).days
                random_days = random.randint(0, max(days_range, 1))
                random_hours = random.randint(0, 23)
                timestamp = date_from + timedelta(days=random_days, hours=random_hours)
            else:
                random_days = random.randint(0, 30)
                random_hours = random.randint(0, 23)
                timestamp = datetime.now() - timedelta(days=random_days, hours=random_hours)
            
            # Create location object
            location = LocationPoint(
                latitude=lat,
                longitude=lng,
                timestamp=timestamp,
                source="DummyPlugin",
                context=f"Test location {i+1} for {target}"
            )
            locations.append(location)
        
        return locations

class LocationPoint:
    """Location point class representing a single location"""
    
    def __init__(self, latitude, longitude, timestamp, source, context=""):
        """Initialize location point"""
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp
        self.source = source
        self.context = context
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp,
            "source": self.source,
            "context": self.context
        }
    
    def __str__(self):
        """String representation"""
        return f"Location({self.latitude}, {self.longitude}) @ {self.timestamp}"

def get_plugin_class():
    """Return the main plugin class for the plugin manager"""
    return DummyPlugin
