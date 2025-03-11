"""
Enhanced geocoding helper with additional features
"""

from app.plugins.geocoding_helper import GeocodingHelper
from typing import Tuple, Optional, Dict, List, Any
import logging
import os
import json
import csv
import re

logger = logging.getLogger(__name__)

class EnhancedGeocodingHelper(GeocodingHelper):
    """
    Enhanced geocoding helper with offline databases and additional geocoding methods
    """
    
    def __init__(self):
        super().__init__()
        self.us_cities = {}
        self.postal_codes = {}
        
        # Additional cache for specific location types
        self.cache_dir = os.path.join(os.path.expanduser("~"), ".creepyai", "cache", "enhanced_geocoding")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Try to load offline databases
        self._load_offline_databases()
    
    def _load_offline_databases(self):
        """Load offline geocoding databases if available"""
        # Load US cities database
        us_cities_path = os.path.join(self.cache_dir, "us_cities.csv")
        if os.path.exists(us_cities_path):
            try:
                with open(us_cities_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        city_key = f"{row.get('city', '').lower()}, {row.get('state_id', '').lower()}"
                        self.us_cities[city_key] = {
                            'lat': float(row.get('lat', 0)),
                            'lon': float(row.get('lng', 0)),
                            'population': int(row.get('population', 0))
                        }
                logger.info(f"Loaded {len(self.us_cities)} US cities")
            except Exception as e:
                logger.error(f"Error loading US cities database: {e}")
        
        # Load postal codes database
        postal_codes_path = os.path.join(self.cache_dir, "postal_codes.csv")
        if os.path.exists(postal_codes_path):
            try:
                with open(postal_codes_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        postal_code = row.get('postal_code', '')
                        if postal_code:
                            self.postal_codes[postal_code] = {
                                'lat': float(row.get('latitude', 0)),
                                'lon': float(row.get('longitude', 0)),
                                'country': row.get('country_code', '')
                            }
                logger.info(f"Loaded {len(self.postal_codes)} postal codes")
            except Exception as e:
                logger.error(f"Error loading postal codes database: {e}")
    
    def geocode(self, location: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Enhanced geocoding with offline database support and better parsing
        
        Args:
            location: Location string to geocode
            
        Returns:
            Tuple of (latitude, longitude) or (None, None) if geocoding failed
        """
        if not location:
            return None, None
            
        # Normalize location string
        location = location.strip()
        
        # First try standard geocoding (includes cache check)
        lat, lon = super().geocode(location)
        if lat is not None and lon is not None:
            return lat, lon
            
        # Try to extract postal/zip code
        zip_match = re.search(r'\b(\d{5}(-\d{4})?)\b', location)
        if zip_match and zip_match.group(1) in self.postal_codes:
            postal_data = self.postal_codes[zip_match.group(1)]
            return postal_data['lat'], postal_data['lon']
            
        # Try to match US city
        # Look for patterns like "City, ST" or "City, State"
        city_match = re.search(r'([^,]+),\s*([A-Za-z]{2})\b', location)
        if city_match:
            city = city_match.group(1).strip().lower()
            state = city_match.group(2).lower()
            city_key = f"{city}, {state}"
            
            if city_key in self.us_cities:
                city_data = self.us_cities[city_key]
                return city_data['lat'], city_data['lon']
                
        # Fall back to online geocoding
        return super().geocode(location)
