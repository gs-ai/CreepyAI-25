import os
import json
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional
import zipfile
import csv
from pathlib import Path
from .base_plugin import BasePlugin, LocationPoint

class LocationHistoryPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="Location History",
            description="Extract location data from Google or Apple Location History exports"
        )
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "data_directory",
                "display_name": "Location History Directory",
                "type": "directory",
                "default": "",
                "required": True,
                "description": "Directory containing your location history export"
            },
            {
                "name": "history_type",
                "display_name": "History Type",
                "type": "select",
                "options": ["auto_detect", "google", "apple"],
                "default": "auto_detect",
                "required": False,
                "description": "Type of location history data"
            },
            {
                "name": "max_records",
                "display_name": "Maximum Records",
                "type": "integer",
                "default": 1000,
                "min": 10,
                "max": 10000,
                "required": False,
                "description": "Maximum number of location records to process"
            }
        ]
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None, 
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
        locations = []
        data_dir = self.config.get("data_directory", "")
        history_type = self.config.get("history_type", "auto_detect")
        max_records = self.config.get("max_records", 1000)
        
        if not data_dir or not os.path.exists(data_dir):
            return locations
            
        # Handle ZIP archives
        if data_dir.endswith('.zip') and zipfile.is_zipfile(data_dir):
            with zipfile.ZipFile(data_dir, 'r') as zip_ref:
                temp_dir = os.path.join(self.data_dir, "temp_location_history_extract")
                os.makedirs(temp_dir, exist_ok=True)
                zip_ref.extractall(temp_dir)
                data_dir = temp_dir
        
        # Auto-detect file type if not specified
        if history_type == "auto_detect":
            # Check for Google Location History format
            google_files = glob.glob(os.path.join(data_dir, "**/Location History.json"), recursive=True)
            google_files.extend(glob.glob(os.path.join(data_dir, "**/Records.json"), recursive=True))
            
            # Check for Apple Location History format
            apple_files = list(Path(data_dir).glob("*.csv"))
            
            if google_files:
                history_type = "google"
            elif apple_files:
                history_type = "apple"
        
        # Process Google Location History
        if history_type == "google":
            locations = self._extract_google_locations(data_dir, max_records, date_from, date_to)
            
        # Process Apple Location History
        elif history_type == "apple":
            locations = self._extract_apple_locations(data_dir, max_records, date_from, date_to)
        
        return locations
        
    def _extract_google_locations(self, data_dir: str, max_records: int, 
                                 date_from: Optional[datetime], 
                                 date_to: Optional[datetime]) -> List[LocationPoint]:
        """Extract location data from Google Location History files."""
        locations = []
        location_files = []
        
        # Look for Google Location History files
        for pattern in [
            "**/Location History.json",
            "**/Records.json",
            "**/LocationHistory.json",
            "**/Semantic Location History/**/*.json",
        ]:
            location_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
        record_count = 0
        for location_file in location_files:
            try:
                with open(location_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Different formats depending on file and export version
                
                # Format 1: "locations" array in the root object
                if isinstance(data, dict) and "locations" in data:
                    for item in data["locations"]:
                        if record_count >= max_records:
                            break
                            
                        if isinstance(item, dict):
                            # Extract coordinates - Google typically uses E7 format (degrees * 10^7)
                            if "latitudeE7" in item and "longitudeE7" in item:
                                latitude = item["latitudeE7"] / 1e7
                                longitude = item["longitudeE7"] / 1e7
                                
                                # Extract timestamp (usually in milliseconds)
                                timestamp = None
                                if "timestampMs" in item:
                                    try:
                                        timestamp = datetime.fromtimestamp(int(item["timestampMs"]) / 1000)
                                    except (ValueError, TypeError):
                                        pass
                                
                                # Use current time if no timestamp found
                                if not timestamp:
                                    timestamp = datetime.now()
                                
                                # Filter by date if needed
                                if date_from and timestamp < date_from:
                                    continue
                                if date_to and timestamp > date_to:
                                    continue
                                
                                # Extract accuracy if available
                                accuracy = item.get("accuracy", 0)
                                
                                # Extract activity if available
                                activity = ""
                                if "activity" in item and isinstance(item["activity"], list) and len(item["activity"]) > 0:
                                    activities = []
                                    for activity_item in item["activity"]:
                                        if "activity" in activity_item and isinstance(activity_item["activity"], list):
                                            for a in activity_item["activity"]:
                                                if "type" in a:
                                                    activities.append(a["type"])
                                    if activities:
                                        activity = ", ".join(activities[:3])  # Limit to top 3 activities
                                
                                context = f"Location recorded with {accuracy}m accuracy"
                                if activity:
                                    context += f" | Activity: {activity}"
                                
                                locations.append(
                                    LocationPoint(
                                        latitude=float(latitude),
                                        longitude=float(longitude),
                                        timestamp=timestamp,
                                        source="Google Location History",
                                        context=context,
                                        accuracy=accuracy
                                    )
                                )
                                
                                record_count += 1
                
                # Format 2: "timelineObjects" array in root object (newer exports)
                elif isinstance(data, dict) and "timelineObjects" in data:
                    for timeline_obj in data["timelineObjects"]:
                        if record_count >= max_records:
                            break
                            
                        if isinstance(timeline_obj, dict):
                            # Handle place visits
                            if "placeVisit" in timeline_obj and isinstance(timeline_obj["placeVisit"], dict):
                                place_visit = timeline_obj["placeVisit"]
                                
                                if "location" in place_visit and isinstance(place_visit["location"], dict):
                                    location = place_visit["location"]
                                    
                                    # Extract coordinates
                                    latitude = None
                                    longitude = None
                                    
                                    if "latitudeE7" in location and "longitudeE7" in location:
                                        latitude = location["latitudeE7"] / 1e7
                                        longitude = location["longitudeE7"] / 1e7
                                    elif "centerLatE7" in location and "centerLngE7" in location:
                                        latitude = location["centerLatE7"] / 1e7
                                        longitude = location["centerLngE7"] / 1e7
                                        
                                    if latitude is not None and longitude is not None:
                                        # Extract timestamp
                                        timestamp = None
                                        if "duration" in place_visit and isinstance(place_visit["duration"], dict):
                                            if "startTimestampMs" in place_visit["duration"]:
                                                try:
                                                    timestamp = datetime.fromtimestamp(
                                                        int(place_visit["duration"]["startTimestampMs"]) / 1000
                                                    )
                                                except (ValueError, TypeError):
                                                    pass
                                        
                                        if not timestamp:
                                            timestamp = datetime.now()
                                        
                                        # Filter by date if needed
                                        if date_from and timestamp < date_from:
                                            continue
                                        if date_to and timestamp > date_to:
                                            continue
                                        
                                        # Extract place name
                                        place_name = location.get("name", "Unknown Place")
                                        address = location.get("address", "")
                                        
                                        context = place_name
                                        if address:
                                            context += f" | {address}"
                                            
                                        locations.append(
                                            LocationPoint(
                                                latitude=float(latitude),
                                                longitude=float(longitude),
                                                timestamp=timestamp,
                                                source="Google Place Visit",
                                                context=context
                                            )
                                        )
                                        
                                        record_count += 1
                            
                            # Handle activity segments (movement between places)
                            if "activitySegment" in timeline_obj and record_count < max_records:
                                activity = timeline_obj["activitySegment"]
                                
                                # Get start location
                                if "startLocation" in activity:
                                    start_loc = activity["startLocation"]
                                    if "latitudeE7" in start_loc and "longitudeE7" in start_loc:
                                        latitude = start_loc["latitudeE7"] / 1e7
                                        longitude = start_loc["longitudeE7"] / 1e7
                                        
                                        # Get timestamp
                                        timestamp = None
                                        if "duration" in activity and "startTimestampMs" in activity["duration"]:
                                            try:
                                                timestamp = datetime.fromtimestamp(
                                                    int(activity["duration"]["startTimestampMs"]) / 1000
                                                )
                                            except (ValueError, TypeError):
                                                pass
                                                
                                        if not timestamp:
                                            timestamp = datetime.now()
                                            
                                        # Filter by date if needed
                                        if date_from and timestamp < date_from:
                                            continue
                                        if date_to and timestamp > date_to:
                                            continue
                                            
                                        # Get activity type
                                        activity_type = activity.get("activityType", "UNKNOWN")
                                        
                                        locations.append(
                                            LocationPoint(
                                                latitude=float(latitude),
                                                longitude=float(longitude),
                                                timestamp=timestamp,
                                                source="Google Activity",
                                                context=f"Started {activity_type} activity"
                                            )
                                        )
                                        
                                        record_count += 1
                                        
            except Exception as e:
                print(f"Error processing Google location file {location_file}: {e}")
                
        return locations
    
    def _extract_apple_locations(self, data_dir: str, max_records: int, 
                               date_from: Optional[datetime],
                               date_to: Optional[datetime]) -> List[LocationPoint]:
        """Extract location data from Apple Location History files."""
        locations = []
        csv_files = list(Path(data_dir).glob("*.csv"))
        
        record_count = 0
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    csv_reader = csv.reader(f)
                    header = next(csv_reader, None)  # Skip header
                    
                    for row in csv_reader:
                        if record_count >= max_records:
                            break
                            
                        # Apple export format usually has fields like:
                        # Date,Time,Latitude,Longitude,Altitude,Horizontal Accuracy
                        if len(row) >= 6:  # Ensure we have enough fields
                            try:
                                date_str = row[0]
                                time_str = row[1]
                                latitude = float(row[2])
                                longitude = float(row[3])
                                altitude = float(row[4]) if row[4] else 0
                                accuracy = float(row[5]) if row[5] else 0
                                
                                # Parse date
                                try:
                                    timestamp = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                                except ValueError:
                                    # Try alternate format
                                    try:
                                        timestamp = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %H:%M:%S")
                                    except ValueError:
                                        timestamp = datetime.now()
                                
                                # Filter by date if needed
                                if date_from and timestamp < date_from:
                                    continue
                                if date_to and timestamp > date_to:
                                    continue
                                
                                locations.append(
                                    LocationPoint(
                                        latitude=latitude,
                                        longitude=longitude,
                                        timestamp=timestamp,
                                        source="Apple Location History",
                                        context=f"Location with {accuracy}m accuracy",
                                        accuracy=accuracy
                                    )
                                )
                                
                                record_count += 1
                            except (ValueError, IndexError) as e:
                                print(f"Error parsing row in Apple location data: {e}")
                                
            except Exception as e:
                print(f"Error processing Apple location file {csv_file}: {e}")
                
        return locations

