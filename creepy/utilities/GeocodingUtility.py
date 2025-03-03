import logging
import os
import json
import re
import sqlite3
import urllib.request
import urllib.parse
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class GeocodingUtility:
    """
    Utility for geocoding location names into coordinates without using APIs.
    Uses a local database of coordinates and simple lookup instead of external APIs.
    """
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        
        # Create path for the geocoding database
        geocode_dir = os.path.join(os.path.expanduser("~"), ".creepyai", "geocode")
        os.makedirs(geocode_dir, exist_ok=True)
        
        self.db_path = os.path.join(geocode_dir, "geocode.db")
        self.cache_limit = 10000
        self.conn = None
        self.setup_db()
        
        # Load city data if available
        self.cities_file = os.path.join(geocode_dir, "worldcities.json")
        self.cities_data = self._load_cities_data()
    
    def setup_db(self):
        """Set up the geocoding database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Create geocode cache table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS geocode_cache (
                query TEXT PRIMARY KEY,
                latitude REAL,
                longitude REAL,
                display_name TEXT,
                timestamp INTEGER
            )
            ''')
            
            self.conn.commit()
            logger.info("Geocoding database set up successfully")
        except Exception as e:
            logger.error(f"Error setting up geocoding database: {str(e)}")
    
    def _load_cities_data(self):
        """Load city data from file or create if not exists."""
        if os.path.exists(self.cities_file):
            try:
                with open(self.cities_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cities data: {str(e)}")
                return {}
        else:
            # Create a basic cities database with common cities
            basic_cities = {
                "new york": {"lat": 40.7128, "lng": -74.0060, "name": "New York, USA"},
                "los angeles": {"lat": 34.0522, "lng": -118.2437, "name": "Los Angeles, USA"},
                "london": {"lat": 51.5074, "lng": -0.1278, "name": "London, UK"},
                "paris": {"lat": 48.8566, "lng": 2.3522, "name": "Paris, France"},
                "tokyo": {"lat": 35.6762, "lng": 139.6503, "name": "Tokyo, Japan"},
                "sydney": {"lat": -33.8688, "lng": 151.2093, "name": "Sydney, Australia"},
                "beijing": {"lat": 39.9042, "lng": 116.4074, "name": "Beijing, China"},
                "moscow": {"lat": 55.7558, "lng": 37.6173, "name": "Moscow, Russia"},
                "berlin": {"lat": 52.5200, "lng": 13.4050, "name": "Berlin, Germany"},
                "rome": {"lat": 41.9028, "lng": 12.4964, "name": "Rome, Italy"},
                "madrid": {"lat": 40.4168, "lng": -3.7038, "name": "Madrid, Spain"},
                "cairo": {"lat": 30.0444, "lng": 31.2357, "name": "Cairo, Egypt"},
                "toronto": {"lat": 43.6532, "lng": -79.3832, "name": "Toronto, Canada"},
                "sao paulo": {"lat": -23.5505, "lng": -46.6333, "name": "São Paulo, Brazil"},
                "dubai": {"lat": 25.2048, "lng": 55.2708, "name": "Dubai, UAE"}
            }
            
            try:
                with open(self.cities_file, 'w', encoding='utf-8') as f:
                    json.dump(basic_cities, f, indent=2)
                
                logger.info("Created basic cities database")
                return basic_cities
            except Exception as e:
                logger.error(f"Error creating cities data: {str(e)}")
                return {}
    
    def geocode(self, location_name):
        """
        Convert a location name to coordinates.
        
        Args:
            location_name (str): Location name to geocode
            
        Returns:
            dict: Location information with coordinates or None if not found
        """
        if not location_name or not isinstance(location_name, str):
            logger.warning("Invalid location name provided")
            return None
            
        # Clean up the location name
        clean_name = self._clean_location_name(location_name)
        if not clean_name:
            return None
            
        # Try to get from cache first
        cached = self._get_from_cache(clean_name)
        if cached:
            return {
                'latitude': cached[0],
                'longitude': cached[1],
                'name': cached[2],
                'source': 'cache'
            }
            
        # Try to find in cities data
        city_match = self._find_in_cities(clean_name)
        if city_match:
            # Add to cache
            self._add_to_cache(clean_name, city_match['lat'], city_match['lng'], city_match['name'])
            
            return {
                'latitude': city_match['lat'],
                'longitude': city_match['lng'],
                'name': city_match['name'],
                'source': 'cities'
            }
            
        # No match found
        logger.info(f"No coordinates found for location: {location_name}")
        return None
    
    def _clean_location_name(self, location_name):
        """Clean up a location name for searching."""
        if not location_name:
            return ""
            
        # Remove common terms that might confuse the geocoding
        noise_words = ['location', 'located', 'in', 'at', 'near', 'around', 'vicinity']
        
        clean = location_name.lower().strip()
        for word in noise_words:
            clean = re.sub(r'\b' + word + r'\b', '', clean)
            
        # Remove extra whitespace and punctuation
        clean = re.sub(r'[^\w\s]', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean
    
    def _get_from_cache(self, query):
        """Get geocoding result from cache."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT latitude, longitude, display_name FROM geocode_cache WHERE query = ?",
                (query,)
            )
            result = cursor.fetchone()
            
            if result:
                # Update timestamp to indicate recent use
                cursor.execute(
                    "UPDATE geocode_cache SET timestamp = ? WHERE query = ?",
                    (int(time.time()), query)
                )
                self.conn.commit()
                
                return result
            
            return None
        except Exception as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
            return None
    
    def _add_to_cache(self, query, latitude, longitude, display_name):
        """Add geocoding result to cache."""
        try:
            cursor = self.conn.cursor()
            
            # Check cache size
            cursor.execute("SELECT COUNT(*) FROM geocode_cache")
            count = cursor.fetchone()[0]
            
            # If cache is full, remove oldest entries
            if count >= self.cache_limit:
                # Delete oldest entries (10% of cache_limit)
                cursor.execute(
                    "DELETE FROM geocode_cache WHERE rowid IN "
                    "(SELECT rowid FROM geocode_cache ORDER BY timestamp ASC LIMIT ?)",
                    (self.cache_limit // 10,)
                )
            
            # Add new entry
            cursor.execute(
                "INSERT OR REPLACE INTO geocode_cache (query, latitude, longitude, display_name, timestamp) "
                "VALUES (?, ?, ?, ?, ?)",
                (query, latitude, longitude, display_name, int(time.time()))
            )
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding to cache: {str(e)}")
            return False
    
    def _find_in_cities(self, query):
        """Find location in the cities database."""
        # Direct match
        if query in self.cities_data:
            return self.cities_data[query]
            
        # Partial match
        for city, data in self.cities_data.items():
            if query in city or city in query:
                return data
                
        return None
    
    def batch_geocode(self, location_names):
        """
        Geocode multiple location names.
        
        Args:
            location_names (list): List of location names
            
        Returns:
            dict: Dictionary mapping location names to coordinates
        """
        results = {}
        
        for name in location_names:
            result = self.geocode(name)
            if result:
                results[name] = result
                
        return results
    
    def close(self):
        """Close database connections."""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Clean up resources."""
        self.close()
