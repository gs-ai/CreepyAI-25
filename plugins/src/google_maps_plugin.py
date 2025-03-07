import os
import json
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional
import zipfile
from plugins.base_plugin import BasePlugin, LocationPoint

class GoogleMapsPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="Google Maps",
            description="Extract location data from Google Maps data export without API"
        )
    
    def is_configured(self):
        # Check if the plugin is properly configured
        return True, "GoogleMapsPlugin is configured"
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "data_directory",
                "display_name": "Google Maps Data Directory",
                "type": "directory",
                "default": "",
                "required": True,
                "description": "Directory containing your Google Maps export (part of Google Takeout)"
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
                temp_dir = os.path.join(self.data_dir, "temp_googlemaps_extract")
                os.makedirs(temp_dir, exist_ok=True)
                zip_ref.extractall(temp_dir)
                data_dir = temp_dir
        
        # Look for various files that might contain location data
        
        # 1. Saved places
        saved_places_files = glob.glob(os.path.join(data_dir, "**/Saved Places.json"), recursive=True)
        if not saved_places_files:
            saved_places_files = glob.glob(os.path.join(data_dir, "**/saved_places.json"), recursive=True)
        
        for file_path in saved_places_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    places_data = json.load(f)
                
                # Process saved places
                if isinstance(places_data, dict) and "features" in places_data:
                    features = places_data["features"]
                    for feature in features:
                        if not isinstance(feature, dict):
                            continue
                        
                        properties = feature.get("properties", {})
                        geometry = feature.get("geometry", {})
                        
                        # Get location name
                        name = properties.get("Title", "Saved Place")
                        description = properties.get("Description", "")
                        
                        # Get coordinates
                        coordinates = None
                        if geometry.get("type") == "Point" and "coordinates" in geometry:
                            # GeoJSON format uses [longitude, latitude]
                            coordinates = geometry["coordinates"]
                            if len(coordinates) >= 2:
                                # Extract longitude and latitude
                                longitude, latitude = coordinates[0], coordinates[1]
                                
                                # Get timestamp if available, otherwise use current time
                                timestamp = datetime.now()
                                if "Google Maps URL" in properties:
                                    # Try to extract date from URL or properties
                                    url = properties["Google Maps URL"]
                                    # Get creation time if available
                                    if "Created" in properties:
                                        try:
                                            date_str = properties["Created"]
                                            timestamp = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                                        except (ValueError, TypeError):
                                            pass
                                
                                # Filter by date if needed
                                if date_from and timestamp < date_from:
                                    continue
                                if date_to and timestamp > date_to:
                                    continue
                                
                                # Build context
                                context = name
                                if description:
                                    context += f" - {description}"
                                
                                locations.append(
                                    LocationPoint(
                                        latitude=float(latitude),
                                        longitude=float(longitude),
                                        timestamp=timestamp,
                                        source="Google Maps - Saved Place",
                                        context=context
                                    )
                                )
            except Exception as e:
                print(f"Error processing Google Maps saved places: {e}")
        
        # 2. Search history with locations
        search_files = glob.glob(os.path.join(data_dir, "**/Search/MyActivity.json"), recursive=True)
        if not search_files:
            search_files = glob.glob(os.path.join(data_dir, "**/Maps/search_history.json"), recursive=True)
        
        for file_path in search_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    search_data = json.load(f)
                
                search_items = []
                
                # Format 1: List of activities
                if isinstance(search_data, list):
                    search_items = search_data
                # Format 2: Under 'items' key
                elif isinstance(search_data, dict) and "items" in search_data:
                    search_items = search_data["items"]
                
                for item in search_items:
                    if not isinstance(item, dict):
                        continue
                    
                    # Skip items without location data
                    if not any(key in item for key in ["location", "geocode", "coordinates", "latitudeE7"]):
                        continue
                    
                    latitude = None
                    longitude = None
                    timestamp = None
                    search_query = ""
                    
                    # Extract search query
                    if "title" in item:
                        search_query = item["title"]
                    elif "query" in item:
                        search_query = item["query"]
                    elif "text" in item:
                        search_query = item["text"]
                    
                    # Extract timestamp
                    if "time" in item:
                        try:
                            timestamp = datetime.fromisoformat(item["time"].replace("Z", "+00:00"))
                        except (ValueError, TypeError):
                            pass
                    elif "timestamp" in item:
                        try:
                            if isinstance(item["timestamp"], str):
                                timestamp = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
                            else:
                                # Assume timestamp in milliseconds
                                timestamp = datetime.fromtimestamp(item["timestamp"] / 1000)
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
                    
                    # Extract coordinates
                    if "location" in item and isinstance(item["location"], dict):
                        loc = item["location"]
                        if "latitudeE7" in loc and "longitudeE7" in loc:
                            latitude = loc["latitudeE7"] / 1e7
                            longitude = loc["longitudeE7"] / 1e7
                        elif "latitude" in loc and "longitude" in loc:
                            latitude = loc["latitude"]
                            longitude = loc["longitude"]
                    elif "latitudeE7" in item and "longitudeE7" in item:
                        latitude = item["latitudeE7"] / 1e7
                        longitude = item["longitudeE7"] / 1e7
                    
                    if latitude is not None and longitude is not None:
                        locations.append(
                            LocationPoint(
                                latitude=float(latitude),
                                longitude=float(longitude),
                                timestamp=timestamp,
                                source="Google Maps - Search",
                                context=f"Search for: {search_query}"
                            )
                        )
            except Exception as e:
                print(f"Error processing Google Maps search history: {e}")
        
        # 3. Timeline data
        timeline_files = glob.glob(os.path.join(data_dir, "**/Semantic Location History/**/*.json"), recursive=True)
        
        record_count = 0
        for file_path in timeline_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    timeline_data = json.load(f)
                
                if isinstance(timeline_data, dict) and "timelineObjects" in timeline_data:
                    for timeline_obj in timeline_data["timelineObjects"]:
                        # Check if we're over the max records limit
                        if record_count >= max_records:
                            break
                        
                        # Process place visits
                        if "placeVisit" in timeline_obj:
                            place_visit = timeline_obj["placeVisit"]
                            location = place_visit.get("location", {})
                            
                            latitude = None
                            longitude = None
                            
                            # Extract coordinates
                            if "latitudeE7" in location and "longitudeE7" in location:
                                latitude = location["latitudeE7"] / 1e7
                                longitude = location["longitudeE7"] / 1e7
                            elif "centerLatE7" in location and "centerLngE7" in location:
                                latitude = location["centerLatE7"] / 1e7
                                longitude = location["centerLngE7"] / 1e7
                            
                            if latitude is not None and longitude is not None:
                                # Get place name
                                name = location.get("name", "Unknown Place")
                                address = location.get("address", "")
                                
                                # Get timestamp
                                timestamp = None
                                if "duration" in place_visit:
                                    duration = place_visit["duration"]
                                    if "startTimestampMs" in duration:
                                        try:
                                            timestamp = datetime.fromtimestamp(int(duration["startTimestampMs"]) / 1000)
                                        except (ValueError, TypeError):
                                            pass
                                
                                if not timestamp:
                                    timestamp = datetime.now()
                                
                                # Filter by date if needed
                                if date_from and timestamp < date_from:
                                    continue
                                if date_to and timestamp > date_to:
                                    continue
                                
                                # Build context
                                context = name
                                if address:
                                    context += f" - {address}"
                                
                                record_count += 1
                                locations.append(
                                    LocationPoint(
                                        latitude=float(latitude),
                                        longitude=float(longitude),
                                        timestamp=timestamp,
                                        source="Google Maps - Timeline",
                                        context=context
                                    )
                                )
                        
                        # Process activity segments (travel between places)
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
                                            timestamp = datetime.fromtimestamp(int(activity["duration"]["startTimestampMs"]) / 1000)
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
                                    
                                    record_count += 1
                                    locations.append(
                                        LocationPoint(
                                            latitude=float(latitude),
                                            longitude=float(longitude),
                                            timestamp=timestamp,
                                            source="Google Maps - Activity",
                                            context=f"Started {activity_type} activity"
                                        )
                                    )
            except Exception as e:
                print(f"Error processing Google Maps timeline: {e}")
            
            # Check if we've reached the maximum records
            if record_count >= max_records:
                break
        
        return locations
    
    def search_for_targets(self, search_term: str) -> List[Dict[str, Any]]:
        targets = []
        data_dir = self.config.get("data_directory", "")
        
        if not data_dir or not os.path.exists(data_dir):
            return targets
        
        # Handle ZIP archives
        if data_dir.endswith('.zip') and zipfile.is_zipfile(data_dir):
            with zipfile.ZipFile(data_dir, 'r') as zip_ref:
                temp_dir = os.path.join(self.data_dir, "temp_googlemaps_extract")
                os.makedirs(temp_dir, exist_ok=True)
                zip_ref.extractall(temp_dir)
                data_dir = temp_dir
        
        # Look for various files that might contain location data
        saved_places_files = glob.glob(os.path.join(data_dir, "**/Saved Places.json"), recursive=True)
        if not saved_places_files:
            saved_places_files = glob.glob(os.path.join(data_dir, "**/saved_places.json"), recursive=True)
        
        for file_path in saved_places_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    places_data = json.load(f)
                
                if isinstance(places_data, dict) and "features" in places_data:
                    features = places_data["features"]
                    for feature in features:
                        if not isinstance(feature, dict):
                            continue
                        
                        properties = feature.get("properties", {})
                        name = properties.get("Title", "Saved Place")
                        
                        if name and search_term.lower() in name.lower():
                            targets.append({
                                'targetId': name,
                                'targetName': name,
                                'pluginName': self.name
                            })
            except Exception as e:
                print(f"Error processing Google Maps saved places: {e}")
        
        return targets
