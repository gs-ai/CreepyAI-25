"""
Geocoding helper for CreepyAI plugins
"""

import os
import json
import logging
from typing import Tuple, Optional, Dict, Any
import re
import time
import urllib.request
import urllib.parse

logger = logging.getLogger(__name__)

class GeocodingHelper:
    """Simple geocoding helper to convert text addresses to coordinates"""
    
    def __init__(self):
        """Initialize the geocoding helper"""
        self.cache_dir = os.path.join(os.path.expanduser("~"), ".creepyai", "cache", "geocoding")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_file = os.path.join(self.cache_dir, "geocode_cache.json")
        self.cache = self._load_cache()
        self.rate_limit_sleep = 1.0  # Sleep time between API requests to avoid rate limiting
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load geocoding cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading geocoding cache: {e}")
        
        return {}
    
    def _save_cache(self):
        """Save geocoding cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f)
        except Exception as e:
            logger.error(f"Error saving geocoding cache: {e}")
    
    def geocode(self, location: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Convert a location string to coordinates
        
        Args:
            location: Location string to geocode
            
        Returns:
            Tuple of (latitude, longitude) or (None, None) if geocoding failed
        """
        if not location:
            return None, None
        
        # Normalize location string
        location = location.strip()
        
        # Check for direct coordinates in the string like "40.7128, -74.0060"
        coord_match = re.search(r'(-?\d+\.\d+)[,\s]+(-?\d+\.\d+)', location)
        if coord_match:
            try:
                lat = float(coord_match.group(1))
                lon = float(coord_match.group(2))
                
                # Validate coordinates
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return lat, lon
            except (ValueError, IndexError):
                pass
        
        # Check cache
        cache_key = location.lower()
        if cache_key in self.cache:
            coords = self.cache[cache_key]
            return coords['lat'], coords['lon']
        
        # Use Nominatim (OpenStreetMap) API as a fallback
        try:
            # Be gentle with the API - add a delay
            time.sleep(self.rate_limit_sleep)
            
            encoded_location = urllib.parse.quote(location)
            user_agent = "CreepyAI/1.0"
            url = f"https://nominatim.openstreetmap.org/search?q={encoded_location}&format=json&limit=1"
            
            headers = {'User-Agent': user_agent}
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                if data and len(data) > 0:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    
                    # Cache the result
                    self.cache[cache_key] = {'lat': lat, 'lon': lon}
                    self._save_cache()
                    
                    return lat, lon
        except Exception as e:
            logger.error(f"Error geocoding {location}: {e}")
        
        return None, None
