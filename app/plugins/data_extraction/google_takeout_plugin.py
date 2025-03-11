import os
import json
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional
import zipfile
from app.plugins.base_plugin import BasePlugin, LocationPoint

class GoogleTakeoutPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
        name="Google Takeout",
        description="Extract location data from Google Takeout data export without API"
        )
    
    def is_configured(self):
        # Check if the plugin is properly configured
        return True, "GoogleTakeoutPlugin is configured"
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
        {
        "name": "data_directory",
        "display_name": "Google Takeout Directory",
        "type": "directory",
        "default": "",
        "required": True,
        "description": "Directory containing your Google Takeout export"
        },
        {
        "name": "max_records",
        "display_name": "Maximum Records",
        "type": "integer",
        "default": 5000,
        "min": 100,
        "max": 50000,
        "required": False,
        "description": "Maximum number of location records to process"
        }
        ]
    
        def collect_locations(self, target: str, date_from: Optional[datetime] = None, 
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
            locations = []
            data_dir = self.config.get("data_directory", "")
            max_records = self.config.get("max_records", 5000)
        
        if not data_dir or not os.path.exists(data_dir):
            return locations
            
        # Handle ZIP archives
        if data_dir.endswith('.zip') and zipfile.is_zipfile(data_dir):
            with zipfile.ZipFile(data_dir, 'r') as zip_ref:
                    temp_dir = os.path.join(self.data_dir, "temp_google_extract")
                    os.makedirs(temp_dir, exist_ok=True)
                    zip_ref.extractall(temp_dir)
                    data_dir = temp_dir
        
        # Look for location history files
                    location_files = []
                    for pattern in [
                    "**/Location History/Location History.json",
                    "**/Location History/Records.json", 
                    "**/LocationHistory.json"
        ]:
                        location_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
        # Process location history files
                        record_count = 0
        for location_file in location_files:
            try:
                with open(location_file, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                
                # Different formats depending on export version
                                    location_items = []
                
                # Format 1: Locations under 'locations' key
                if isinstance(data, dict) and "locations" in data:
                                        location_items = data["locations"]
                # Format 2: Locations under 'timelineObjects' key
                elif isinstance(data, dict) and "timelineObjects" in data:
                    for item in data["timelineObjects"]:
                        if "placeVisit" in item:
                                                    location_items.append(item["placeVisit"])
                        elif "activitySegment" in item:
                            # For activity segments, we can extract start and end locations
                            if "startLocation" in item["activitySegment"]:
                                                            location_items.append({"location": item["activitySegment"]["startLocation"]})
                            if "endLocation" in item["activitySegment"]:
                                                                location_items.append({"location": item["activitySegment"]["endLocation"]})
                # Format 3: Direct list of locations
                elif isinstance(data, list):
                                                                    location_items = data
                
                for item in location_items:
                                                                        timestamp = None
                                                                        latitude = None
                                                                        longitude = None
                                                                        accuracy = None
                                                                        context = ""
                    
                    # Try different possible structures
                    if isinstance(item, dict):
                        # Format 1: Google's standard format'
                                                                            if "latitudeE7" in item and "longitudeE7" in item:''
                                                                            latitude = item["latitudeE7"] / 1e7''
                                                                            longitude = item["longitudeE7"] / 1e7''
                            
                        # Format 2: Direct lat/lon
                        elif "latitude" in item and "longitude" in item:
                                                                                latitude = item["latitude"]
                                                                                longitude = item["longitude"]
                            
                        # Format 3: Nested under 'location'
                        elif "location" in item and isinstance(item["location"], dict):
                                                                                    loc = item["location"]
                            if "latitudeE7" in loc and "longitudeE7" in loc:
                                                                                        latitude = loc["latitudeE7"] / 1e7
                                                                                        longitude = loc["longitudeE7"] / 1e7
                            elif "latitude" in loc and "longitude" in loc:
                                                                                            latitude = loc["latitude"]
                                                                                            longitude = loc["longitude"]
                        
                        # Extract timestamp
                        if "timestampMs" in item:
                            try:
                                # Convert milliseconds to seconds
                                                                                                    timestamp = datetime.fromtimestamp(int(item["timestampMs"]) / 1000)
                            except (ValueError, TypeError):
                                                                                                    pass
                        elif "timestamp" in item:
                            try:
                                if isinstance(item["timestamp"], str):
                                    # Try parsing ISO format
                                                                                                                timestamp = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
                                else:
                                    # Assume timestamp in seconds
                                                                                                                    timestamp = datetime.fromtimestamp(item["timestamp"])
                            except (ValueError, TypeError):
                                                                                                                    pass
                        
                        # Get accuracy if available
                        if "accuracy" in item:
                                                                                                                        accuracy = item["accuracy"]
                        elif "accuracyMeters" in item:
                                                                                                                            accuracy = item["accuracyMeters"]
                        
                        # Extract context
                        if "address" in item:
                                                                                                                                context = item["address"]
                        elif "name" in item:
                                                                                                                                    context = item["name"]
                        elif "placeVisit" in item and isinstance(item["placeVisit"], dict):
                            if "location" in item["placeVisit"]:
                                                                                                                                            location_data = item["placeVisit"]["location"]
                                if "name" in location_data:
                                                                                                                                                context = location_data["name"]
                                elif "address" in location_data:
                                                                                                                                                    context = location_data["address"]
                    
                    # Only add if we have coordinates
                    if latitude is not None and longitude is not None:
                        if not timestamp:
                                                                                                                                                            timestamp = datetime.now()
                        
                        # Filter by date if needed
                        if date_from and timestamp < date_from:
                                                                                                                                                            continue
                        if date_to and timestamp > date_to:
                                                                                                                                                            continue
                            
                        # Check if we're at the maximum record count'
                                                                                                                                                            record_count += 1''
                                                                                                                                                            if record_count > max_records:''
                                                                                                                                                        break''
                        
                                                                                                                                                        locations.append(
                                                                                                                                                        LocationPoint(
                                                                                                                                                        latitude=float(latitude),
                                                                                                                                                        longitude=float(longitude),
                                                                                                                                                        timestamp=timestamp,
                                                                                                                                                        source="Google Takeout",
                                                                                                                                                        context=context[:200] if context else "Location History",
                                                                                                                                                        accuracy=accuracy or 0
                                                                                                                                                        )
                                                                                                                                                        )
                
                # If we've reached the maximum records, stop processing files'
                                                                                                                                                        if record_count > max_records:''
                                                                                                                                                    break''
                                                                                                                                                    ''
            except Exception as e:
                                                                                                                                                        print(f"Error processing Google Takeout file {location_file}: {e}")
        
                                                                                                                                                    return locations
