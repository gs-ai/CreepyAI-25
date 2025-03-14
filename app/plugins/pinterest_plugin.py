import os
import json
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional
import zipfile
import re
from app.plugins.base_plugin import BasePlugin, LocationPoint
from app.plugins.geocoding_helper import GeocodingHelper

class PinterestPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
        name="Pinterest",
        description="Extract location data from Pinterest data exports without API"
        )
        self.geocoder = GeocodingHelper()
    
    def is_configured(self):
        # Check if the plugin is properly configured
        return True, "PinterestPlugin is configured"
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
        {
        "name": "data_directory",
        "display_name": "Pinterest Data Directory",
        "type": "directory",
        "default": "",
        "required": True,
        "description": "Directory containing your Pinterest data export"
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
            locations = []
            data_dir = self.config.get("data_directory", "")
            attempt_geocoding = self.config.get("attempt_geocoding", True)
        
        if not data_dir or not os.path.exists(data_dir):
            return locations
            
        # Handle ZIP archives
        if data_dir.endswith('.zip') and zipfile.is_zipfile(data_dir):
            with zipfile.ZipFile(data_dir, 'r') as zip_ref:
                    temp_dir = os.path.join(self.data_dir, "temp_pinterest_extract")
                    os.makedirs(temp_dir, exist_ok=True)
                    zip_ref.extractall(temp_dir)
                    data_dir = temp_dir
        
        # Look for Pinterest data files that may contain location information
        
        # 1. Pins data
                    pin_files = []
        for pattern in ["**/pins*.json", "**/pins.json", "**/board_pins*.json"]:
                        pin_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
        # Process pin files
        for pin_file in pin_files:
            try:
                with open(pin_file, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                
                # Different formats depending on export version
                                    pins_list = []
                
                # Format 1: Direct list of pins
                if isinstance(data, list):
                                        pins_list = data
                # Format 2: Nested under a key
                elif isinstance(data, dict):
                    for key in ["pins", "board_pins", "items"]:
                        if key in data and isinstance(data[key], list):
                                                    pins_list = data[key]
                                                break
                
                # Process each pin
                for pin in pins_list:
                    if not isinstance(pin, dict):
                                                    continue
                    
                    # Check if pin has location data
                                                    location_info = None
                    
                    # Format 1: Direct location in pin
                    if "location" in pin and pin["location"]:
                                                        location_info = pin["location"]
                    # Format 2: Location in place object
                    elif "place" in pin and pin["place"]:
                                                            location_info = pin["place"]
                    # Format 3: Location in metadata
                    elif "metadata" in pin and isinstance(pin["metadata"], dict):
                                                                metadata = pin["metadata"]
                        if "location" in metadata:
                                                                    location_info = metadata["location"]
                        elif "place" in metadata:
                                                                        location_info = metadata["place"]
                    
                    # Extract coordinates
                                                                        lat = None
                                                                        lon = None
                                                                        location_name = ""
                    
                    if location_info:
                        if isinstance(location_info, dict):
                            # Try to get coordinates
                            if "latitude" in location_info and "longitude" in location_info:
                                                                                    lat = location_info["latitude"]
                                                                                    lon = location_info["longitude"]
                            elif "lat" in location_info and "lon" in location_info:
                                                                                        lat = location_info["lat"]
                                                                                        lon = location_info["lon"]
                            elif "lat" in location_info and "lng" in location_info:
                                                                                            lat = location_info["lat"]
                                                                                            lon = location_info["lng"]
                                
                            # Try to get location name
                            for name_key in ["name", "place_name", "title"]:
                                if name_key in location_info:
                                                                                                    location_name = location_info[name_key]
                                                                                                break
                        elif isinstance(location_info, str):
                            # See if it's a coordinate pair'
                                                                                                    coord_match = re.search(r'([-+]?\d+\.?\d*)[,\s]+\s*([-+]?\d+\.?\d*)', location_info)
                            if coord_match:
                                                                                                        lat = float(coord_match.group(1))
                                                                                                        lon = float(coord_match.group(2))
                            else:
                                # Assume it's a place name for geocoding'
                                                                                                            location_name = location_info''
                                                                                                            ''
                    # If we don't have coordinates but have a location name, try geocoding'
                                                                                                            if (lat is None or lon is None) and location_name and attempt_geocoding:''
                                                                                                            lat, lon = self.geocoder.geocode(location_name)''
                                                                                                            ''
                    # Skip if we don't have coordinates'
                                                                                                            if lat is None or lon is None:''
                                                                                                        continue''
                                                                                                        ''
                    # Get timestamp
                                                                                                        timestamp = None
                    for date_key in ["created_at", "created_time", "date", "timestamp"]:
                        if date_key in pin:
                                                                                                                date_str = pin[date_key]
                            if isinstance(date_str, str):
                                # Try different date formats
                                for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                                    try:
                                                                                                                            timestamp = datetime.strptime(date_str, fmt)
                                                                                                                        break
                                    except ValueError:
                                                                                                                        pass
                            elif isinstance(date_str, (int, float)):
                                # Assume timestamp in seconds
                                try:
                                                                                                                                timestamp = datetime.fromtimestamp(date_str)
                                except (ValueError, OverflowError):
                                    # Maybe it's milliseconds'
                                                                                                                                    try:''
                                                                                                                                    timestamp = datetime.fromtimestamp(date_str / 1000)''
                                                                                                                                    except (ValueError, OverflowError):''
                                                                                                                                pass
                                        
                            if timestamp:
                                                                                                                                break
                    
                    if not timestamp:
                                                                                                                                    timestamp = datetime.now()
                        
                    # Apply date filters
                    if date_from and timestamp < date_from:
                                                                                                                                    continue
                    if date_to and timestamp > date_to:
                                                                                                                                    continue
                    
                    # Get pin title and description
                                                                                                                                    title = ""
                                                                                                                                    description = ""
                    
                    for title_key in ["title", "name", "pin_title"]:
                        if title_key in pin:
                                                                                                                                            title = pin[title_key]
                                                                                                                                        break
                    
                    for desc_key in ["description", "note", "pin_description"]:
                        if desc_key in pin:
                                                                                                                                                description = pin[desc_key]
                                                                                                                                            break
                    
                    # Create context
                    if not location_name:
                                                                                                                                                location_name = "Unknown Location"
                        
                                                                                                                                                context = title or description or "Pinterest Pin"
                    if title and description:
                                                                                                                                                    context = f"{title} - {description}"
                        
                                                                                                                                                    locations.append(
                                                                                                                                                    LocationPoint(
                                                                                                                                                    latitude=float(lat),
                                                                                                                                                    longitude=float(lon),
                                                                                                                                                    timestamp=timestamp,
                                                                                                                                                    source="Pinterest",
                                                                                                                                                    context=context[:200]
                                                                                                                                                    )
                                                                                                                                                    )
                    
            except Exception as e:
                                                                                                                                                        print(f"Error processing Pinterest file {pin_file}: {e}")
                
        # 2. Look for boards data that might contain location info
                                                                                                                                                        board_files = []
        for pattern in ["**/boards*.json", "**/boards.json"]:
                                                                                                                                                            board_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
            
        # Process board files
        for board_file in board_files:
            try:
                with open(board_file, 'r', encoding='utf-8') as f:
                                                                                                                                                                        data = json.load(f)
                    
                # Different formats depending on export version
                                                                                                                                                                        boards_list = []
                
                # Format 1: Direct list of boards
                if isinstance(data, list):
                                                                                                                                                                            boards_list = data
                # Format 2: Nested under a key
                elif isinstance(data, dict):
                    for key in ["boards", "user_boards", "items"]:
                        if key in data and isinstance(data[key], list):
                                                                                                                                                                                        boards_list = data[key]
                                                                                                                                                                                    break
                            
                # Process each board
                for board in boards_list:
                    if not isinstance(board, dict):
                                                                                                                                                                                        continue
                        
                    # Check if board has location data
                                                                                                                                                                                        location_info = None
                    
                    # Format 1: Direct location in board
                    if "location" in board and board["location"]:
                                                                                                                                                                                            location_info = board["location"]
                    # Format 2: Location in metadata
                    elif "metadata" in board and isinstance(board["metadata"], dict):
                                                                                                                                                                                                metadata = board["metadata"]
                        if "location" in metadata:
                                                                                                                                                                                                    location_info = metadata["location"]
                            
                    # Extract coordinates
                                                                                                                                                                                                    lat = None
                                                                                                                                                                                                    lon = None
                                                                                                                                                                                                    location_name = ""
                    
                    if location_info:
                        if isinstance(location_info, dict):
                            # Try to get coordinates
                            if "latitude" in location_info and "longitude" in location_info:
                                                                                                                                                                                                                lat = location_info["latitude"]
                                                                                                                                                                                                                lon = location_info["longitude"]
                            elif "lat" in location_info and "lon" in location_info:
                                                                                                                                                                                                                    lat = location_info["lat"]
                                                                                                                                                                                                                    lon = location_info["lon"]
                            elif "lat" in location_info and "lng" in location_info:
                                                                                                                                                                                                                        lat = location_info["lat"]
                                                                                                                                                                                                                        lon = location_info["lng"]
                                
                            # Try to get location name
                            for name_key in ["name", "place_name", "title"]:
                                if name_key in location_info:
                                                                                                                                                                                                                                location_name = location_info[name_key]
                                                                                                                                                                                                                            break
                        elif isinstance(location_info, str):
                            # See if it's a coordinate pair'
                                                                                                                                                                                                                                coord_match = re.search(r'([-+]?\d+\.?\d*)[,\s]+\s*([-+]?\d+\.?\d*)', location_info)
                            if coord_match:
                                                                                                                                                                                                                                    lat = float(coord_match.group(1))
                                                                                                                                                                                                                                    lon = float(coord_match.group(2))
                            else:
                                # Assume it's a place name for geocoding'
                                                                                                                                                                                                                                        location_name = location_info''
                                                                                                                                                                                                                                        ''
                    # If we don't have coordinates but have a location name, try geocoding'
                                                                                                                                                                                                                                        if (lat is None or lon is None) and location_name and attempt_geocoding:''
                                                                                                                                                                                                                                        lat, lon = self.geocoder.geocode(location_name)''
                                                                                                                                                                                                                                        ''
                    # Skip if we don't have coordinates'
                                                                                                                                                                                                                                        if lat is None or lon is None:''
                                                                                                                                                                                                                                    continue''
                                                                                                                                                                                                                                    ''
                    # Get board name
                                                                                                                                                                                                                                    board_name = ""
                    for name_key in ["name", "title", "board_name"]:
                        if name_key in board:
                                                                                                                                                                                                                                            board_name = board[name_key]
                                                                                                                                                                                                                                        break
                            
                    if not board_name:
                                                                                                                                                                                                                                            board_name = "Pinterest Board"
                        
                    # Get timestamp (creation date or last modified)
                                                                                                                                                                                                                                            timestamp = None
                    for date_key in ["created_at", "created_time", "date", "last_modified"]:
                        if date_key in board:
                                                                                                                                                                                                                                                    date_str = board[date_key]
                            if isinstance(date_str, str):
                                # Try different date formats
                                for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                                    try:
                                                                                                                                                                                                                                                                timestamp = datetime.strptime(date_str, fmt)
                                                                                                                                                                                                                                                            break
                                    except ValueError:
                                                                                                                                                                                                                                                            pass
                            elif isinstance(date_str, (int, float)):
                                try:
                                                                                                                                                                                                                                                                    timestamp = datetime.fromtimestamp(date_str)
                                except (ValueError, OverflowError):
                                    try:
                                                                                                                                                                                                                                                                            timestamp = datetime.fromtimestamp(date_str / 1000)
                                    except (ValueError, OverflowError):
                                                                                                                                                                                                                                                                            pass
                                        
                            if timestamp:
                                                                                                                                                                                                                                                                            break
                                
                    if not timestamp:
                                                                                                                                                                                                                                                                                timestamp = datetime.now()
                        
                    # Apply date filters
                    if date_from and timestamp < date_from:
                                                                                                                                                                                                                                                                                continue
                    if date_to and timestamp > date_to:
                                                                                                                                                                                                                                                                                continue
                        
                    # Create location point
                                                                                                                                                                                                                                                                                locations.append(
                                                                                                                                                                                                                                                                                LocationPoint(
                                                                                                                                                                                                                                                                                latitude=float(lat),
                                                                                                                                                                                                                                                                                longitude=float(lon),
                                                                                                                                                                                                                                                                                timestamp=timestamp,
                                                                                                                                                                                                                                                                                source="Pinterest Board",
                                                                                                                                                                                                                                                                                context=f"Board: {board_name} - {location_name}"[:200]
                                                                                                                                                                                                                                                                                )
                                                                                                                                                                                                                                                                                )
                    
            except Exception as e:
                                                                                                                                                                                                                                                                                    print(f"Error processing Pinterest board file {board_file}: {e}")
                
                                                                                                                                                                                                                                                                                return locations
