#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Geocoding Helper for CreepyAI
Provides basic geocoding functionality
"""

import os
import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import urllib.request
import urllib.parse

logger = logging.getLogger(__name__)

class GeocodingHelper:
    """
    Helper class for geocoding operations
    """
    
    def __init__(self, cache_file: Optional[str] = None):
        """
        Initialize the geocoding helper with optional cache file
        
        Args:
            cache_file: Path to geocoding cache file
        """
        # Set cache file path
        if cache_file:
            self.cache_file = cache_file
        else:
            cache_dir = os.path.join(os.path.expanduser('~'), '.creepyai', 'cache')
            os.makedirs(cache_dir, exist_ok=True)
            self.cache_file = os.path.join(cache_dir, 'geocoding_cache.json')
        
        # Load cache
        self.cache = self._load_cache()
        
        # Regex patterns for coordinate extraction
        self.coord_patterns = [
            # Standard format: lat: 40.7128, lon: -74.0060
            re.compile(r'lat(?:itude)?[:\s=]+\s*([-+]?\d*\.\d+|[-+]?\d+)[,\s]+lon(?:gitude)?[:\s=]+\s*([-+]?\d*\.\d+|[-+]?\d+)'),
            # Simple format: 40.7128, -74.0060
            re.compile(r'([-+]?\d*\.\d+|[-+]?\d+)[,\s]+([-+]?\d*\.\d+|[-+]?\d+)'),
            # Reversed format: longitude=-74.0060, latitude=40.7128
            re.compile(r'lon(?:gitude)?[:\s=]+\s*([-+]?\d*\.\d+|[-+]?\d+)[,\s]+lat(?:itude)?[:\s=]+\s*([-+]?\d*\.\d+|[-+]?\d+)'),
        ]
    
    def _load_cache(self) -> Dict[str, Tuple[float, float]]:
        """Load the geocoding cache from disk"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading geocoding cache: {e}")
        return {}
    
    def _save_cache(self) -> None:
        """Save the geocoding cache to disk"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving geocoding cache: {e}")
    
    def geocode(self, location_str: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Convert a location string to coordinates
        
        Args:
            location_str: Location string to geocode
            
        Returns:
            Tuple of (latitude, longitude) or (None, None) if geocoding failed
        """
        if not location_str:
            return None, None
            
        # Normalize location string
        location_str = location_str.strip().lower()
        
        # Check cache
        if location_str in self.cache:
            return self.cache[location_str]
            
        # Try to extract coordinates from the string
        coords = self._extract_coordinates(location_str)
        if coords:
            self.cache[location_str] = coords
            self._save_cache()
            return coords
            
        # Try to geocode using an online service
        coords = self._geocode_online(location_str)
        if coords:
            self.cache[location_str] = coords
            self._save_cache()
            return coords
            
        return None, None
    
    def _extract_coordinates(self, text: str) -> Optional[Tuple[float, float]]:
        """Extract coordinates from text using regex patterns"""
        for pattern in self.coord_patterns:
            match = pattern.search(text)
            if match:
                try:
                    # Check if this is a reversed pattern (lon, lat)
                    if pattern == self.coord_patterns[2]:  # Reversed format
                        lon = float(match.group(1))
                        lat = float(match.group(2))
                    else:  # Standard format
                        lat = float(match.group(1))
                        lon = float(match.group(2))
                    
                    # Validate coordinates
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        return lat, lon
                except (ValueError, IndexError):
                    pass
        return None
    
    def _geocode_online(self, location_str: str) -> Optional[Tuple[float, float]]:
        """Geocode using an online service (simple Nominatim implementation)"""
        try:
            # Use OpenStreetMap Nominatim API
            encoded_location = urllib.parse.quote(location_str)
            url = f"https://nominatim.openstreetmap.org/search?q={encoded_location}&format=json&limit=1"
            
            # Add user agent to comply with Nominatim usage policy
            headers = {
                'User-Agent': 'CreepyAI/1.0',
            }
            
            request = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(request, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                if data and len(data) > 0:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    return lat, lon
        except Exception as e:
            logger.debug(f"Error geocoding online: {e}")
        
        return None
    
    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Convert coordinates to a location name
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Location name or None if reverse geocoding failed
        """
        try:
            # Use OpenStreetMap Nominatim API for reverse geocoding
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            
            # Add user agent to comply with Nominatim usage policy
            headers = {
                'User-Agent': 'CreepyAI/1.0',
            }
            
            request = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(request, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                if 'display_name' in data:
                    return data['display_name']
        except Exception as e:
            logger.debug(f"Error reverse geocoding: {e}")
        
        return None
    
    def save_cache(self) -> None:
        """Manually save the geocoding cache"""
        self._save_cache()
    
    def clear_cache(self) -> None:
        """Clear the geocoding cache"""
        self.cache = {}
        self._save_cache()
    
    def get_cache_size(self) -> int:
        """Return the number of cached locations"""
        return len(self.cache)
