"""
OpenStreetMap Search Plugin for CreepyAI
"""
import json
import logging
import urllib.request
import urllib.parse

logger = logging.getLogger(__name__)

class Plugin:
    """OpenStreetMap search plugin"""
    
    def __init__(self):
        self.name = "OSM Search"
        self.description = "Search for locations using OpenStreetMap Nominatim API"
        self.version = "1.0.0"
        self.author = "CreepyAI Team"
        
    def get_info(self):
        """Return plugin information"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author
        }
        
    def run(self, query, limit=10):
        """
        Search for locations matching the query
        
        Args:
            query (str): Search query (e.g., "Paris, France")
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of location dictionaries with name, lat, lon, etc.
        """
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json&limit={limit}"
            
            # Add User-Agent as per Nominatim usage policy
            headers = {
                "User-Agent": f"CreepyAI/1.0 (https://github.com/youruser/CreepyAI)"
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = response.read().decode('utf-8')
                results = json.loads(data)
                
                locations = []
                for result in results:
                    location = {
                        "name": result.get("display_name", ""),
                        "lat": float(result.get("lat", 0)),
                        "lon": float(result.get("lon", 0)),
                        "type": result.get("type", ""),
                        "importance": result.get("importance", 0),
                        "osm_id": result.get("osm_id", ""),
                        "raw_data": result
                    }
                    locations.append(location)
                
                return locations
        except Exception as e:
            logger.error(f"Error searching OpenStreetMap: {e}", exc_info=True)
            return []
    
    def configure(self):
        """Configure plugin settings"""
        # This plugin doesn't have settings to configure
        return True
