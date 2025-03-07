import os
import json
import csv
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from plugins.base_plugin import BasePlugin, LocationPoint
from plugins.geocoding_helper import GeocodingHelper

class IDCrawlPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="IDCrawl",
            description="Extract location data from IDCrawl exports (offline)"
        )
        self.geocoder = GeocodingHelper()
    
    def is_configured(self):
        # Check if the plugin is properly configured
        return True, "IDCrawlPlugin is configured"
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "data_directory",
                "display_name": "IDCrawl Data Directory",
                "type": "directory",
                "default": "",
                "required": True,
                "description": "Directory containing your saved IDCrawl results or social media exports"
            },
            {
                "name": "attempt_geocoding",
                "display_name": "Attempt Geocoding",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Try to convert textual locations to coordinates"
            }
        ]
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None, 
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
        """Collect location data from saved IDCrawl exports."""
        locations = []
        data_dir = self.config.get("data_directory", "")
        attempt_geocoding = self.config.get("attempt_geocoding", True)
        
        if not data_dir or not os.path.exists(data_dir):
            return locations
        
        # Process CSV files (common export format)
        csv_locations = self._process_csv_files(data_dir, target, attempt_geocoding)
        locations.extend(csv_locations)
        
        # Process JSON files (another common export format)
        json_locations = self._process_json_files(data_dir, target, attempt_geocoding)
        locations.extend(json_locations)
        
        # Process text files (sometimes people save search results as text)
        text_locations = self._process_text_files(data_dir, target, attempt_geocoding)
        locations.extend(text_locations)
        
        # Apply date filters if provided
        if date_from or date_to:
            filtered_locations = []
            for loc in locations:
                if date_from and loc.timestamp < date_from:
                    continue
                if date_to and loc.timestamp > date_to:
                    continue
                filtered_locations.append(loc)
            return filtered_locations
        
        return locations
    
    def _process_csv_files(self, data_dir: str, target: str, attempt_geocoding: bool) -> List[LocationPoint]:
        """Process CSV files for location data."""
        locations = []
        
        csv_files = []
        for root, _, files in os.walk(data_dir):
            for file in files:
                if file.lower().endswith('.csv'):
                    csv_files.append(os.path.join(root, file))
        
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.reader(f)
                    headers = next(reader, None)
                    
                    # Skip if no headers
                    if not headers:
                        continue
                    
                    # Identify columns that might contain location data
                    location_col = None
                    username_col = None
                    platform_col = None
                    date_col = None
                    
                    for i, header in enumerate(headers):
                        header_lower = header.lower()
                        if 'location' in header_lower or 'address' in header_lower or 'place' in header_lower:
                            location_col = i
                        elif 'username' in header_lower or 'user' in header_lower or 'handle' in header_lower:
                            username_col = i
                        elif 'platform' in header_lower or 'source' in header_lower or 'site' in header_lower:
                            platform_col = i
                        elif 'date' in header_lower or 'time' in header_lower:
                            date_col = i
                    
                    # Skip if we can't identify a location column
                    if location_col is None:
                        continue
                    
                    for row in reader:
                        if len(row) <= location_col:
                            continue
                            
                        location_text = row[location_col]
                        if not location_text:
                            continue
                            
                        # Get username if available
                        username = row[username_col] if username_col is not None and len(row) > username_col else target
                        
                        # Get platform if available
                        platform = row[platform_col] if platform_col is not None and len(row) > platform_col else "Unknown"
                        
                        # Get date if available
                        timestamp = datetime.now()
                        if date_col is not None and len(row) > date_col and row[date_col]:
                            try:
                                # Try common date formats
                                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
                                    try:
                                        timestamp = datetime.strptime(row[date_col], fmt)
                                        break
                                    except ValueError:
                                        continue
                            except Exception:
                                pass
                        
                        # Try to geocode the location
                        lat = None
                        lon = None
                        
                        # Check if the location text already contains coordinates
                        coords = self._extract_coordinates_from_text(location_text)
                        if coords:
                            lat, lon = coords
                        # Otherwise try geocoding
                        elif attempt_geocoding:
                            lat, lon = self.geocoder.geocode(location_text)
                        
                        if lat is not None and lon is not None:
                            location_point = LocationPoint(
                                latitude=lat,
                                longitude=lon,
                                timestamp=timestamp,
                                source=f"IDCrawl - {platform}",
                                context=f"{platform} - {username} - {location_text}"
                            )
                            locations.append(location_point)
            except Exception as e:
                print(f"Error processing CSV file {csv_file}: {e}")
        
        return locations
    
    def _process_json_files(self, data_dir: str, target: str, attempt_geocoding: bool) -> List[LocationPoint]:
        """Process JSON files for location data."""
        locations = []
        
        json_files = []
        for root, _, files in os.walk(data_dir):
            for file in files:
                if file.lower().endswith('.json'):
                    json_files.append(os.path.join(root, file))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8', errors='ignore') as f:
                    data = json.load(f)
                
                # Try to find location data in different JSON structures
                
                # Format 1: List of results
                if isinstance(data, list):
                    for item in data:
                        if not isinstance(item, dict):
                            continue
                            
                        # Look for location information
                        location_text = None
                        for key in ['location', 'address', 'place', 'geo']:
                            if key in item and item[key]:
                                location_text = item[key]
                                break
                        
                        if not location_text:
                            continue
                            
                        # Get username and platform
                        username = item.get('username', item.get('user', item.get('handle', target)))
                        platform = item.get('platform', item.get('source', item.get('site', 'Unknown')))
                        
                        # Get timestamp
                        timestamp = datetime.now()
                        for date_key in ['date', 'created_at', 'timestamp', 'time']:
                            if date_key in item and item[date_key]:
                                try:
                                    if isinstance(item[date_key], str):
                                        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y"]:
                                            try:
                                                timestamp = datetime.strptime(item[date_key], fmt)
                                                break
                                            except ValueError:
                                                continue
                                    elif isinstance(item[date_key], (int, float)):
                                        timestamp = datetime.fromtimestamp(item[date_key])
                                    break
                                except Exception:
                                    pass
                        
                        # Try to geocode the location
                        lat = None
                        lon = None
                        
                        # Check if location is already a coordinate object
                        if isinstance(location_text, dict):
                            lat = location_text.get('latitude', location_text.get('lat'))
                            lon = location_text.get('longitude', location_text.get('lon', location_text.get('lng')))
                            location_text = location_text.get('name', str(location_text))
                        # Check if the location text contains coordinates
                        elif isinstance(location_text, str):
                            coords = self._extract_coordinates_from_text(location_text)
                            if coords:
                                lat, lon = coords
                        
                        # If still no coordinates, try geocoding
                        if (lat is None or lon is None) and attempt_geocoding and isinstance(location_text, str):
                            lat, lon = self.geocoder.geocode(location_text)
                        
                        if lat is not None and lon is not None:
                            location_point = LocationPoint(
                                latitude=float(lat),
                                longitude=float(lon),
                                timestamp=timestamp,
                                source=f"IDCrawl - {platform}",
                                context=f"{platform} - {username} - {location_text}"
                            )
                            locations.append(location_point)
                
                # Format 2: Nested structure
                elif isinstance(data, dict):
                    # Look for results lists
                    for key in ['results', 'data', 'items', 'profiles']:
                        if key in data and isinstance(data[key], list):
                            for item in data[key]:
                                if not isinstance(item, dict):
                                    continue
                                    
                                # Process the same as Format 1
                                location_text = None
                                for loc_key in ['location', 'address', 'place', 'geo']:
                                    if loc_key in item and item[loc_key]:
                                        location_text = item[loc_key]
                                        break
                                
                                if not location_text:
                                    continue
                                
                                # Similar processing to above...
                                # To avoid duplicate code, just extract the essential parts
                                
                                username = item.get('username', item.get('user', target))
                                platform = item.get('platform', item.get('source', 'Unknown'))
                                
                                # Try to geocode the location
                                lat = None
                                lon = None
                                
                                if isinstance(location_text, dict):
                                    lat = location_text.get('latitude', location_text.get('lat'))
                                    lon = location_text.get('longitude', location_text.get('lon', location_text.get('lng')))
                                    location_text = location_text.get('name', str(location_text))
                                elif isinstance(location_text, str):
                                    coords = self._extract_coordinates_from_text(location_text)
                                    if coords:
                                        lat, lon = coords
                                
                                if (lat is None or lon is None) and attempt_geocoding and isinstance(location_text, str):
                                    lat, lon = self.geocoder.geocode(location_text)
                                
                                if lat is not None and lon is not None:
                                    location_point = LocationPoint(
                                        latitude=float(lat),
                                        longitude=float(lon),
                                        timestamp=datetime.now(), # No timestamp in this format
                                        source=f"IDCrawl - {platform}",
                                        context=f"{platform} - {username} - {location_text}"
                                    )
                                    locations.append(location_point)
            except Exception as e:
                print(f"Error processing JSON file {json_file}: {e}")
        
        return locations
    
    def _process_text_files(self, data_dir: str, target: str, attempt_geocoding: bool) -> List[LocationPoint]:
        """Process text files that might contain location information."""
        locations = []
        
        text_files = []
        for root, _, files in os.walk(data_dir):
            for file in files:
                if file.lower().endswith(('.txt', '.html', '.htm')):
                    text_files.append(os.path.join(root, file))
        
        for text_file in text_files:
            try:
                with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Look for location patterns
                
                # Pattern 1: Address or location followed by coordinates
                location_matches = re.finditer(r'(?:location|address|place)[:\s]+([^,\n]+(?:,[^,\n]+){1,3})', content, re.IGNORECASE)
                
                for match in location_matches:
                    location_text = match.group(1).strip()
                    
                    # Try to geocode the location
                    lat = None
                    lon = None
                    
                    # Check if the location text contains coordinates
                    coords = self._extract_coordinates_from_text(location_text)
                    if coords:
                        lat, lon = coords
                    # Otherwise try geocoding
                    elif attempt_geocoding:
                        lat, lon = self.geocoder.geocode(location_text)
                    
                    if lat is not None and lon is not None:
                        # Look for nearby username and platform
                        context_before = content[max(0, match.start() - 100):match.start()]
                        context_after = content[match.end():min(len(content), match.end() + 100)]
                        
                        username = target
                        platform = "Unknown"
                        
                        username_match = re.search(r'(?:username|user|handle)[:\s]+(@?\w+)', context_before + context_after, re.IGNORECASE)
                        if username_match:
                            username = username_match.group(1)
                            
                        platform_match = re.search(r'(?:platform|source|site)[:\s]+(\w+)', context_before + context_after, re.IGNORECASE)
                        if platform_match:
                            platform = platform_match.group(1)
                        
                        location_point = LocationPoint(
                            latitude=lat,
                            longitude=lon,
                            timestamp=datetime.now(), # No timestamp in this format
                            source=f"IDCrawl - {platform}",
                            context=f"{platform} - {username} - {location_text}"
                        )
                        locations.append(location_point)
                
                # Pattern 2: Direct coordinates
                coord_matches = re.finditer(r'([-+]?\d+\.\d+)[,\s]+([-+]?\d+\.\d+)', content)
                
                for match in coord_matches:
                    try:
                        lat = float(match.group(1))
                        lon = float(match.group(2))
                        
                        # Only use if they look like valid coordinates
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                            # Look for nearby context
                            context_before = content[max(0, match.start() - 50):match.start()]
                            context_after = content[match.end():min(len(content), match.end() + 50)]
                            
                            # Simple text extraction
                            context = (context_before + context_after).replace('\n', ' ')
                            
                            location_point = LocationPoint(
                                latitude=lat,
                                longitude=lon,
                                timestamp=datetime.now(),
                                source="IDCrawl - TextExtract",
                                context=f"Extracted from text: {context[:100]}..."
                            )
                            locations.append(location_point)
                    except ValueError:
                        continue
            
            except Exception as e:
                print(f"Error processing text file {text_file}: {e}")
        
        return locations
    
    def _extract_coordinates_from_text(self, text: str) -> Optional[List[float]]:
        """Extract coordinates from text string."""
        if not text or not isinstance(text, str):
            return None
        
        # Check for common coordinate formats
        patterns = [
            # Decimal degrees: 40.7128, -74.0060
            r'(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)',
            
            # Alternative format: lat=40.7128 lon=-74.0060
            r'lat(?:itude)?=(-?\d+\.\d+).*lon(?:gitude)?=(-?\d+\.\d+)',
            
            # Alternative format: location:40.7128,-74.0060
            r'location:(-?\d+\.\d+),(-?\d+\.\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    lat = float(match.group(1))
                    lon = float(match.group(2))
                    # Validate coordinates
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        return [lat, lon]
                except (ValueError, IndexError):
                    pass
        
        return None
