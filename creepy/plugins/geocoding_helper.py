"""
Geocoding helper module for converting textual locations to coordinates.
Uses offline resources where possible to avoid API dependencies.
"""

import os
import csv
import re
import json
import math
from typing import Tuple, Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class GeocodingHelper:
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the geocoding helper with optional data directory for cached/offline data."""
        if data_dir is None:
            data_dir = os.path.join(os.path.expanduser("~"), ".creepyai", "geocoding")
        
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Cache for previously geocoded locations
        self.cache_file = os.path.join(self.data_dir, "geocoding_cache.json")
        self.cache = self._load_cache()
        
        # US cities data file - can be downloaded from https://simplemaps.com/data/us-cities (free basic version)
        self.us_cities_file = os.path.join(self.data_dir, "uscities.csv")
        self.us_cities = {}
        self._load_us_cities()
    
    def _load_cache(self) -> Dict[str, Tuple[float, float]]:
        """Load the geocoding cache from file."""
        cache = {}
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            except Exception as e:
                logger.error(f"Error loading geocoding cache: {e}")
        return cache
    
    def _save_cache(self) -> None:
        """Save the geocoding cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f)
        except Exception as e:
            logger.error(f"Error saving geocoding cache: {e}")
    
    def _load_us_cities(self) -> None:
        """Load US cities data if available."""
        if os.path.exists(self.us_cities_file):
            try:
                with open(self.us_cities_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        city_key = f"{row.get('city', '').lower()}, {row.get('state_id', '').lower()}"
                        try:
                            self.us_cities[city_key] = (
                                float(row.get('lat', 0.0)), 
                                float(row.get('lng', 0.0))
                            )
                        except (ValueError, TypeError):
                            pass
                logger.info(f"Loaded {len(self.us_cities)} US cities for offline geocoding")
            except Exception as e:
                logger.error(f"Error loading US cities data: {e}")
    
    def geocode(self, location_text: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Convert textual location to coordinates.
        Returns (latitude, longitude) tuple or (None, None) if geocoding failed.
        """
        if not location_text:
            return None, None
        
        # Clean up the location text
        location_text = location_text.strip().lower()
        
        # Check cache first
        if location_text in self.cache:
            return self.cache[location_text]
        
        # Try direct coordinate extraction (e.g., "40.7128, -74.0060")
        coord_match = re.search(r'([-+]?\d*\.\d+|[-+]?\d+)[,\s]+([-+]?\d*\.\d+|[-+]?\d+)', location_text)
        if coord_match:
            try:
                lat = float(coord_match.group(1))
                lon = float(coord_match.group(2))
                # Validate coordinates
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    self.cache[location_text] = (lat, lon)
                    self._save_cache()
                    return lat, lon
            except (ValueError, IndexError):
                pass
        
        # Try US city matching
        # Extract city and state using common patterns
        city_state_match = re.search(r'([a-z\s]+)[,\s]+([a-z]{2})', location_text)
        if city_state_match:
            city = city_state_match.group(1).strip()
            state = city_state_match.group(2).strip()
            city_key = f"{city}, {state}"
            
            if city_key in self.us_cities:
                lat, lon = self.us_cities[city_key]
                self.cache[location_text] = (lat, lon)
                self._save_cache()
                return lat, lon
        
        # For common international cities, we can have a small hardcoded dataset
        common_cities = {
            "london": (51.5074, -0.1278),
            "paris": (48.8566, 2.3522),
            "tokyo": (35.6762, 139.6503),
            "new york": (40.7128, -74.0060),
            "los angeles": (34.0522, -118.2437),
            "chicago": (41.8781, -87.6298),
            "sydney": (-33.8688, 151.2093),
            "rome": (41.9028, 12.4964),
            "berlin": (52.5200, 13.4050)
        }
        
        # Check if the location text contains any common city name
        for city, coords in common_cities.items():
            if city in location_text:
                self.cache[location_text] = coords
                self._save_cache()
                return coords
        
        # If we can't geocode offline, return None
        return None, None
