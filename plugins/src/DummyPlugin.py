#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Dummy Plugin for CreepyAI
Generates simulated location data for testing purposes
"""

import os
import random
import logging
import json
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import configparser

from plugins.base_plugin import BasePlugin, LocationPoint

logger = logging.getLogger(__name__)

class DummyPlugin(BasePlugin):
    """Plugin for generating simulated location data"""
    
    def __init__(self):
        super().__init__(
            name="Dummy Location Generator",
            description="Generates simulated location data for testing"
        )
        self.version = "1.0.0"
        
        # Load config from DummyPlugin.conf if available
        self._load_config_from_conf()
    
    def _load_config_from_conf(self):
        """Load configuration from DummyPlugin.conf if available"""
        config_path = os.path.join(os.path.dirname(__file__), 'DummyPlugin.conf')
        if os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.read(config_path)
            
            # Update self.config with values from the config file
            for section in config.sections():
                for key, value in config.items(section):
                    self.config[key] = value
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        """Return configuration options for this plugin"""
        return [
            {
                "name": "base_latitude",
                "display_name": "Base Latitude",
                "type": "float",
                "default": 37.7749,
                "required": True,
                "description": "Base latitude for generating locations"
            },
            {
                "name": "base_longitude",
                "display_name": "Base Longitude",
                "type": "float",
                "default": -122.4194,
                "required": True,
                "description": "Base longitude for generating locations"
            },
            {
                "name": "location_variance",
                "display_name": "Location Variance (meters)",
                "type": "int",
                "default": 100,
                "required": True,
                "description": "Variance in meters for generating random locations"
            },
            {
                "name": "location_count",
                "display_name": "Number of Locations",
                "type": "int",
                "default": 10,
                "required": True,
                "description": "Number of locations to generate"
            },
            {
                "name": "date_range_days",
                "display_name": "Date Range (days)",
                "type": "int",
                "default": 30,
                "required": True,
                "description": "Date range in days for generating random timestamps"
            }
        ]
    
    def is_configured(self) -> Tuple[bool, str]:
        """Check if the plugin is properly configured"""
        required_keys = ["base_latitude", "base_longitude", "location_variance", "location_count", "date_range_days"]
        for key in required_keys:
            if key not in self.config:
                return False, f"Missing required configuration: {key}"
        return True, "Dummy plugin is configured"
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None,
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
        """
        Generate simulated location data
        
        Args:
            target: Target to collect data for (ignored in this plugin)
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            List of LocationPoint objects
        """
        locations = []
        
        base_lat = float(self.config.get("base_latitude", 37.7749))
        base_lon = float(self.config.get("base_longitude", -122.4194))
        variance = int(self.config.get("location_variance", 100))
        count = int(self.config.get("location_count", 10))
        date_range_days = int(self.config.get("date_range_days", 30))
        
        for _ in range(count):
            lat_offset = random.uniform(-variance, variance) / 111320  # Approx meters to degrees
            lon_offset = random.uniform(-variance, variance) / (111320 * math.cos(math.radians(base_lat)))
            timestamp = datetime.now() - timedelta(days=random.randint(0, date_range_days))
            
            location = LocationPoint(
                latitude=base_lat + lat_offset,
                longitude=base_lon + lon_offset,
                timestamp=timestamp,
                source="DummyPlugin",
                context="Simulated location"
            )
            locations.append(location)
        
        # Apply date filtering
        if date_from or date_to:
            locations = [
                loc for loc in locations 
                if (not date_from or loc.timestamp >= date_from) and
                   (not date_to or loc.timestamp <= date_to)
            ]
        
        return locations
