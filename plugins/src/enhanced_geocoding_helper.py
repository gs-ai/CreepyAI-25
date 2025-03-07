#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Enhanced Geocoding Helper for CreepyAI
Provides geocoding functionality with caching and multiple providers
"""

import os
import json
import logging
import csv
import time
import hashlib
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import urllib.request
import urllib.parse
import threading

logger = logging.getLogger(__name__)

class EnhancedGeocodingHelper:
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
        
        # International cities reference data
        self.international_cities = self._load_international_cities()
        
        # Postal codes data if available
        self.postal_codes_file = os.path.join(self.data_dir, "postal_codes.csv")
        self.postal_codes = {}
        self._load_postal_codes()
        
        # Setup regex patterns
        self.coord_pattern = re.compile(r'([-+]?\d*\.\d+|[-+]?\d+)[,\s]+([-+]?\d*\.\d+|[-+]?\d+)')
        self.city_state_pattern = re.compile(r'([a-z\s]+)[,\s]+([a-z]{2,3})', re.IGNORECASE)
        self.zip_pattern = re.compile(r'\b(\d{5}(?:-\d{4})?)\b')  # US ZIP code pattern
        self.postal_pattern = re.compile(r'\b([A-Z]\d[A-Z] ?\d[A-Z]\d)\b', re.IGNORECASE)  # Canadian postal code
    
    def _load_cache(self) -> Dict[str, Tuple[float, float, datetime]]:
        """Load the geocoding cache from file with timestamps."""
        cache = {}
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    raw_cache = json.load(f)
                    # Convert the stored data including timestamps
                    for location, data in raw_cache.items():
                        if len(data) >= 3:
                            try:
                                timestamp = datetime.fromisoformat(data[2])
                                cache[location] = (data[0], data[1], timestamp)
                            except (ValueError, IndexError):
                                # If timestamp is invalid, use current time
                                cache[location] = (data[0], data[1], datetime.now())
                        else:
                            # Legacy format without timestamp
                            cache[location] = (data[0], data[1], datetime.now())
                            
                logger.info(f"Loaded {len(cache)} cached locations")
        except Exception as e:
            logger.error(f"Error loading geocoding cache: {e}")
        return cache
    
    def _save_cache(self) -> None:
        """Save the geocoding cache to file including timestamps."""
        try:
            # Convert cache to serializable format
            serializable_cache = {}
            for location, data in self.cache.items():
                lat, lon, timestamp = data
                serializable_cache[location] = (lat, lon, timestamp.isoformat())
                
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving geocoding cache: {e}")
    
    def _load_us_cities(self) -> None:
        """Load US cities data if available."""
        try:
            if os.path.exists(self.us_cities_file):
                with open(self.us_cities_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            city = row.get('city', '').lower()
                            state = row.get('state_id', '').lower()
                            
                            if city and state:
                                city_key = f"{city}, {state}"
                                lat = float(row.get('lat', 0))
                                lon = float(row.get('lng', 0))
                                population = int(row.get('population', 0))
                                
                                # Store with population for ranking multiple matches later
                                self.us_cities[city_key] = (lat, lon, population)
                                
                                # Also store by zip code if available
                                zip_code = row.get('zip_code')
                                if zip_code:
                                    self.us_cities[zip_code] = (lat, lon, population)
                        except (ValueError, KeyError, TypeError):
                            continue
                            
                logger.info(f"Loaded {len(self.us_cities)} US cities for offline geocoding")
        except Exception as e:
            logger.error(f"Error loading US cities data: {e}")
    
    def _load_international_cities(self) -> Dict[str, Tuple[float, float]]:
        """Load a hardcoded set of major international cities."""
        return {
            "london": (51.5074, -0.1278),
            "paris": (48.8566, 2.3522),
            "tokyo": (35.6762, 139.6503),
            "new york": (40.7128, -74.0060),
            "los angeles": (34.0522, -118.2437),
            "chicago": (41.8781, -87.6298),
            "sydney": (-33.8688, 151.2093),
            "rome": (41.9028, 12.4964),
            "berlin": (52.5200, 13.4050),
            "beijing": (39.9042, 116.4074),
            "moscow": (55.7558, 37.6173),
            "dubai": (25.2048, 55.2708),
            "toronto": (43.6532, -79.3832),
            "singapore": (1.3521, 103.8198),
            "hong kong": (22.3193, 114.1694),
            "madrid": (40.4168, -3.7038),
            "amsterdam": (52.3676, 4.9041),
            "cairo": (30.0444, 31.2357),
            "mexico city": (19.4326, -99.1332),
            "sao paulo": (-23.5505, -46.6333),
            "mumbai": (19.0760, 72.8777),
            "barcelona": (41.3851, 2.1734),
            "seoul": (37.5665, 126.9780),
            "bangkok": (13.7563, 100.5018),
            "vancouver": (49.2827, -123.1207),
            "buenos aires": (-34.6037, -58.3816),
            "montreal": (45.5017, -73.5673),
            "vienna": (48.2082, 16.3738),
            "san francisco": (37.7749, -122.4194),
            "miami": (25.7617, -80.1918),
            "seattle": (47.6062, -122.3321)
        }
    
    def _load_postal_codes(self) -> None:
        """Load postal code data if available."""
        try:
            if os.path.exists(self.postal_codes_file):
                with open(self.postal_codes_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            postal_code = row.get('postal_code', '').strip()
                            lat = float(row.get('latitude', 0))
                            lon = float(row.get('longitude', 0))
                            
                            if postal_code:
                                self.postal_codes[postal_code] = (lat, lon)
                        except (ValueError, KeyError):
                            continue
                            
                logger.info(f"Loaded {len(self.postal_codes)} postal codes for geocoding")
        except Exception as e:
            logger.error(f"Error loading postal codes data: {e}")
    
    def geocode(self, location_text: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Convert textual location to coordinates.
        Returns (latitude, longitude) tuple or (None, None) if geocoding failed.
        
        This method tries multiple strategies:
        1. Check cache first
        2. Parse direct coordinates
        3. Try to match city, state pattern
        4. Look for postal codes
        5. Check common international cities
        """
        if not location_text:
            return None, None
        
        try:
            # Clean up the location text
            location_text = location_text.strip().lower()
            
            # Generate a normalized key for cache lookup
            cache_key = self._normalize_location_text(location_text)
            
            # Check cache first
            if cache_key in self.cache:
                lat, lon, timestamp = self.cache[cache_key]
                # Check if cache entry is still valid (less than 30 days old)
                if datetime.now() - timestamp < timedelta(days=30):
                    return lat, lon
            
            # Extract coordinates if explicitly provided
            coords = self._extract_coordinates(location_text)
            if coords:
                self._update_cache(cache_key, coords[0], coords[1])
                return coords
                
            # Try city and state matching
            city_state_coords = self._match_city_state(location_text)
            if city_state_coords:
                self._update_cache(cache_key, city_state_coords[0], city_state_coords[1])
                return city_state_coords
                
            # Try postal code matching
            postal_coords = self._match_postal_code(location_text)
            if postal_coords:
                self._update_cache(cache_key, postal_coords[0], postal_coords[1])
                return postal_coords
                
            # Try common international cities
            intl_coords = self._match_international_city(location_text)
            if intl_coords:
                self._update_cache(cache_key, intl_coords[0], intl_coords[1])
                return intl_coords
                
            # If everything fails, return None
            logger.debug(f"Could not geocode location: {location_text}")
            return None, None
            
        except Exception as e:
            logger.error(f"Error in geocoding: {e}")
            return None, None
    
    def _normalize_location_text(self, text: str) -> str:
        """
        Normalize location text for consistent cache keys.
        Remove excess whitespace, lowercase, and standardize punctuation.
        """
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text.lower().strip())
        # Standardize commas with spaces
        text = re.sub(r'\s*,\s*', ', ', text)
        return text
    
    def _update_cache(self, location_key: str, lat: float, lon: float) -> None:
        """Add or update a location in the cache with current timestamp."""
        self.cache[location_key] = (lat, lon, datetime.now())
        # Don't save after every update to reduce disk I/O
        # Instead we'll rely on the app to call save_cache at appropriate times
    
    def _extract_coordinates(self, text: str) -> Optional[Tuple[float, float]]:
        """Extract explicit coordinates from text."""
        # Look for standard coordinate formats
        coord_match = self.coord_pattern.search(text)
        if coord_match:
            try:
                lat = float(coord_match.group(1))
                lon = float(coord_match.group(2))
                
                # Validate coordinates are in reasonable ranges
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return lat, lon
            except (ValueError, IndexError):
                pass
                
        return None
    
    def _match_city_state(self, text: str) -> Optional[Tuple[float, float]]:
        """Try to match city, state pattern."""
        city_state_match = self.city_state_pattern.search(text)
        if city_state_match:
            city = city_state_match.group(1).strip()
            state = city_state_match.group(2).strip()
            city_key = f"{city}, {state}"
            
            if city_key in self.us_cities:
                lat, lon, _ = self.us_cities[city_key]
                return lat, lon
                
        return None
    
    def _match_postal_code(self, text: str) -> Optional[Tuple[float, float]]:
        """Try to match postal codes."""
        # Check for US ZIP codes
        zip_match = self.zip_pattern.search(text)
        if zip_match:
            zip_code = zip_match.group(1)
            if zip_code in self.us_cities:
                lat, lon, _ = self.us_cities[zip_code]
                return lat, lon
            
        # Check for Canadian postal codes
        postal_match = self.postal_pattern.search(text)
        if postal_match:
            postal_code = postal_match.group(1).upper().replace(' ', '')
            if postal_code in self.postal_codes:
                return self.postal_codes[postal_code]
                
        return None
    
    def _match_international_city(self, text: str) -> Optional[Tuple[float, float]]:
        """Try to match common international cities."""
        # Check if the text contains any known city name
        for city, coords in self.international_cities.items():
            if city in text.lower():
                return coords
                
        return None
                
    def save_cache(self) -> None:
        """Manually save the cache to disk."""
        self._save_cache()
        
    def clear_cache(self) -> None:
        """Clear the geocoding cache."""
        self.cache = {}
        self._save_cache()
        
    def get_cache_size(self) -> int:
        """Return the number of cached locations."""
        return len(self.cache)
