"""
Geocoding utility for CreepyAI.
Provides geocoding and reverse geocoding functionality.
"""
import logging
import json
from typing import Dict, Any, List, Optional, Tuple, Union

logger = logging.getLogger('creepyai.utilities.geocoding')

class GeocodingUtility:
    """Utility for geocoding operations."""
    
    def __init__(self):
        """Initialize geocoding utility."""
        self.initialized = False
        self.available_backends = {}
        
        # Try to import common geocoding libraries
        self._import_backends()
    
    def _import_backends(self) -> None:
        """Import available geocoding backends."""
        backends = {
            "geopy": "geopy",
            "googlemaps": "googlemaps",
            "requests": "requests"
        }
        
        for name, module in backends.items():
            try:
                __import__(module)
                self.available_backends[name] = True
                logger.info(f"Geocoding backend '{name}' is available")
            except ImportError:
                self.available_backends[name] = False
                logger.debug(f"Geocoding backend '{name}' is not available")
        
        self.initialized = True
    
    def geocode(self, address: str, backend: str = "geopy") -> Optional[Tuple[float, float]]:
        """Convert address to coordinates.
        
        Args:
            address: Address to geocode
            backend: Backend to use ('geopy', 'googlemaps', etc.)
            
        Returns:
            Tuple of (latitude, longitude) or None if failed
        """
        if backend == "geopy" and self.available_backends.get("geopy"):
            try:
                from geopy.geocoders import Nominatim
                geolocator = Nominatim(user_agent="creepyai")
                location = geolocator.geocode(address)
                if location:
                    return (location.latitude, location.longitude)
            except Exception as e:
                logger.error(f"Error geocoding with geopy: {e}")
        elif backend == "googlemaps" and self.available_backends.get("googlemaps"):
            # Add Google Maps implementation if API key is available
            logger.warning("Google Maps geocoding not implemented yet")
        else:
            logger.error(f"Backend '{backend}' is not available or not supported")
        
        return None
    
    def reverse_geocode(self, latitude: float, longitude: float, backend: str = "geopy") -> Optional[str]:
        """Convert coordinates to address.
        
        Args:
            latitude: Latitude
            longitude: Longitude
            backend: Backend to use ('geopy', 'googlemaps', etc.)
            
        Returns:
            Address string or None if failed
        """
        if backend == "geopy" and self.available_backends.get("geopy"):
            try:
                from geopy.geocoders import Nominatim
                geolocator = Nominatim(user_agent="creepyai")
                location = geolocator.reverse((latitude, longitude))
                if location:
                    return location.address
            except Exception as e:
                logger.error(f"Error reverse geocoding with geopy: {e}")
        elif backend == "googlemaps" and self.available_backends.get("googlemaps"):
            # Add Google Maps implementation if API key is available
            logger.warning("Google Maps reverse geocoding not implemented yet")
        else:
            logger.error(f"Backend '{backend}' is not available or not supported")
        
        return None
