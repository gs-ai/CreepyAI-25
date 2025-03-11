"""
Standardization helpers for plugin output
"""
import logging
from typing import List, Dict, Any, Union, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LocationStandardizer:
    """
    Helper class to standardize location data from different plugins
    """
    
    @staticmethod
    def standardize_location(location_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert various location data formats to a standard format
        
        Args:
            location_data: Location data in any format
            
        Returns:
            Standardized location data dictionary
        """
        if not isinstance(location_data, dict):
            logger.warning(f"Cannot standardize non-dict location data: {type(location_data)}")
            return {}
            
        standard = {}
        
        # Extract coordinates
        if 'lat' in location_data and 'lon' in location_data:
            standard['lat'] = float(location_data['lat'])
            standard['lon'] = float(location_data['lon'])
        elif 'latitude' in location_data and 'longitude' in location_data:
            standard['lat'] = float(location_data['latitude'])
            standard['lon'] = float(location_data['longitude'])
        elif 'coordinates' in location_data and isinstance(location_data['coordinates'], (list, tuple)) and len(location_data['coordinates']) >= 2:
            # GeoJSON style [lon, lat]
            standard['lon'] = float(location_data['coordinates'][0])
            standard['lat'] = float(location_data['coordinates'][1])
        
        # Extract name/title
        for key in ['name', 'title', 'location', 'place', 'address']:
            if key in location_data and location_data[key]:
                standard['name'] = str(location_data[key])
                break
                
        if 'name' not in standard:
            standard['name'] = "Unnamed Location"
        
        # Extract timestamp/date
        for key in ['timestamp', 'date', 'time', 'created', 'modified']:
            if key in location_data:
                value = location_data[key]
                if isinstance(value, str):
                    try:
                        # Try different date formats
                        formats = [
                            '%Y-%m-%dT%H:%M:%S',
                            '%Y-%m-%d %H:%M:%S',
                            '%Y-%m-%d',
                            '%d/%m/%Y',
                            '%m/%d/%Y'
                        ]
                        
                        for fmt in formats:
                            try:
                                standard['timestamp'] = datetime.strptime(value, fmt).isoformat()
                                break
                            except ValueError:
                                continue
                    except Exception:
                        pass
                elif isinstance(value, (int, float)):
                    try:
                        standard['timestamp'] = datetime.fromtimestamp(value).isoformat()
                    except Exception:
                        pass
                elif isinstance(value, datetime):
                    standard['timestamp'] = value.isoformat()
                    
                if 'timestamp' in standard:
                    break
        
        # Extract source information
        for key in ['source', 'plugin', 'provider']:
            if key in location_data:
                standard['source'] = str(location_data[key])
                break
                
        # Copy over any other fields that aren't already standardized
        for key, value in location_data.items():
            if key not in standard and not key.startswith('_'):
                standard[key] = value
                
        return standard
    
    @staticmethod
    def standardize_locations(locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Standardize a list of location dictionaries
        
        Args:
            locations: List of location dictionaries
            
        Returns:
            List of standardized location dictionaries
        """
        if not isinstance(locations, list):
            logger.warning(f"Cannot standardize non-list locations: {type(locations)}")
            return []
            
        standard_locations = []
        
        for location in locations:
            if isinstance(location, dict):
                standard = LocationStandardizer.standardize_location(location)
                
                # Only add if it has coordinates
                if 'lat' in standard and 'lon' in standard:
                    standard_locations.append(standard)
                    
        return standard_locations
