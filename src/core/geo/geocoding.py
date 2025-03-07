#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Geocoding utilities for CreepyAI.
This module provides functions for converting between addresses and coordinates.
"""

import os
import logging
import json
import requests
import time
from typing import Tuple, Dict, Any, Optional, List
from pathlib import Path
import geopy
from geopy.geocoders import Nominatim, GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

logger = logging.getLogger(__name__)

# Cache directory for geocoding results
CACHE_DIR = os.path.join(Path.home(), '.creepyai', 'geocache')
os.makedirs(CACHE_DIR, exist_ok=True)

class GeocodingHelper:
    """Helper class for geocoding operations"""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = 'nominatim', 
                use_cache: bool = True, cache_dir: Optional[str] = None):
        """
        Initialize the geocoding helper
        
        Args:
            api_key: API key for geocoding service (required for some providers)
            provider: Geocoding provider ('nominatim', 'google', etc.)
            use_cache: Whether to cache results
            cache_dir: Directory to store cache
        """
        self.api_key = api_key
        self.provider = provider
        self.use_cache = use_cache
        self.cache_dir = cache_dir or CACHE_DIR
        
        # Create cache directory
        if self.use_cache and not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create cache directory: {e}")
                self.use_cache = False
        
        # Initialize geocoder
        self.geocoder = self._create_geocoder()
        
        # Rate limiting settings
        self.last_request_time = 0
        self.min_delay = 1.0  # seconds between requests
    
    def _create_geocoder(self):
        """Create geocoder based on provider"""
        try:
            if self.provider == 'google' and self.api_key:
                return GoogleV3(api_key=self.api_key)
            else:
                return Nominatim(user_agent="CreepyAI/1.0")
        except Exception as e:
            logger.error(f"Error creating geocoder: {e}")
            # Fallback to Nominatim
            return Nominatim(user_agent="CreepyAI/1.0")
    
    def _get_cache_file(self, query: str) -> str:
        """Get cache file path for a query"""
        # Create a safe filename from the query
        from hashlib import md5
        safe_filename = md5(query.encode('utf-8')).hexdigest() + '.json'
        return os.path.join(self.cache_dir, safe_filename)
    
    def _get_from_cache(self, query: str) -> Optional[Tuple[float, float]]:
        """Get geocoding results from cache"""
        if not self.use_cache:
            return None
            
        cache_file = self._get_cache_file(query)
        if not os.path.exists(cache_file):
            return None
            
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'lat' in data and 'lon' in data:
                    return float(data['lat']), float(data['lon'])
        except Exception as e:
            logger.debug(f"Error reading from cache: {e}")
            
        return None
    
    def _save_to_cache(self, query: str, lat: float, lon: float) -> None:
        """Save geocoding results to cache"""
        if not self.use_cache:
            return
            
        cache_file = self._get_cache_file(query)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({'lat': lat, 'lon': lon}, f)
        except Exception as e:
            logger.debug(f"Error writing to cache: {e}")
    
    def geocode(self, address: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Convert an address to coordinates
        
        Args:
            address: Address or location name
            
        Returns:
            Tuple of (latitude, longitude) or (None, None) if geocoding fails
        """
        # Check cache first
        cached = self._get_from_cache(address)
        if cached:
            return cached
            
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_delay:
            time.sleep(self.min_delay - time_since_last)
            
        # Geocode
        try:
            location = self.geocoder.geocode(address, timeout=10)
            self.last_request_time = time.time()
            
            if location:
                # Save to cache
                self._save_to_cache(address, location.latitude, location.longitude)
                return location.latitude, location.longitude
                
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            logger.warning(f"Geocoding service unavailable: {e}")
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {e}")
            
        return None, None
    
    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Convert coordinates to an address
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Address string or None if geocoding fails
        """
        query = f"{lat},{lon}"
        
        # Check cache first
        cached = self._get_from_cache(query)
        if cached and isinstance(cached, str):
            return cached
            
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_delay:
            time.sleep(self.min_delay - time_since_last)
            
        # Reverse geocode
        try:
            location = self.geocoder.reverse((lat, lon), timeout=10)
            self.last_request_time = time.time()
            
            if location:
                address = location.address
                # Save to cache
                self._save_to_cache(query, address)
                return address
                
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            logger.warning(f"Geocoding service unavailable: {e}")
        except Exception as e:
            logger.error(f"Error reverse geocoding ({lat}, {lon}): {e}")
            
        return None


class EnhancedGeocodingHelper(GeocodingHelper):
    """
    Enhanced geocoding helper with multiple providers and better error handling
    """
    
    def __init__(self, api_key: Optional[str] = None, provider: str = 'nominatim', 
                use_cache: bool = True, cache_dir: Optional[str] = None,
                fallback_providers: Optional[List[str]] = None):
        """
        Initialize the enhanced geocoding helper
        
        Args:
            api_key: API key for geocoding service (required for some providers)
            provider: Primary geocoding provider
            use_cache: Whether to cache results
            cache_dir: Directory to store cache
            fallback_providers: List of fallback providers to try if primary fails
        """
        super().__init__(api_key, provider, use_cache, cache_dir)
        self.fallback_providers = fallback_providers or ['osm', 'arcgis']
        
        # Initialize fallback geocoders
        self.fallback_geocoders = {}
        for provider in self.fallback_providers:
            try:
                if provider == 'osm':
                    self.fallback_geocoders[provider] = Nominatim(user_agent="CreepyAI/1.0 Fallback")
                elif provider == 'arcgis':
                    from geopy.geocoders import ArcGIS
                    self.fallback_geocoders[provider] = ArcGIS(timeout=10)
                elif provider == 'bing' and self.api_key:
                    from geopy.geocoders import Bing
                    self.fallback_geocoders[provider] = Bing(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize fallback geocoder {provider}: {e}")
    
    def geocode(self, address: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Convert an address to coordinates using primary and fallback providers
        
        Args:
            address: Address or location name
            
        Returns:
            Tuple of (latitude, longitude) or (None, None) if geocoding fails
        """
        # First try with primary geocoder
        result = super().geocode(address)
        if result[0] is not None and result[1] is not None:
            return result
            
        # If primary fails, try fallbacks
        for provider, geocoder in self.fallback_geocoders.items():
            try:
                logger.debug(f"Trying fallback geocoder {provider} for '{address}'")
                
                # Rate limiting
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                if time_since_last < self.min_delay:
                    time.sleep(self.min_delay - time_since_last)
                
                location = geocoder.geocode(address, timeout=10)
                self.last_request_time = time.time()
                
                if location:
                    # Save to cache
                    self._save_to_cache(address, location.latitude, location.longitude)
                    return location.latitude, location.longitude
                    
            except Exception as e:
                logger.debug(f"Fallback geocoder {provider} failed for '{address}': {e}")
                
        return None, None

# Singleton instances for easy import
default_geocoder = GeocodingHelper()
enhanced_geocoder = EnhancedGeocodingHelper()

def geocode(address: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Convert an address to coordinates using the default geocoder
    
    Args:
        address: Address or location name
        
    Returns:
        Tuple of (latitude, longitude) or (None, None) if geocoding fails
    """
    return default_geocoder.geocode(address)

def reverse_geocode(lat: float, lon: float) -> Optional[str]:
    """
    Convert coordinates to an address using the default geocoder
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Address string or None if geocoding fails
    """
    return default_geocoder.reverse_geocode(lat, lon)
