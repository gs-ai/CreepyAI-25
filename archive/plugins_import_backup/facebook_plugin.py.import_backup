import os
import json
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional
import zipfile
import re
from creepy.plugins.base_plugin import BasePlugin, LocationPoint

class FacebookPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="Facebook",
            description="Extract location data from Facebook data export without API"
        )
    
    def is_configured(self):
        # Check if the plugin is properly configured
        return True, "FacebookPlugin is configured"
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "data_directory",
                "display_name": "Facebook Data Directory",
                "type": "directory",
                "default": "",
                "required": True,
                "description": "Directory containing your Facebook data export"
            }
        ]
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None, 
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
        locations = []
        data_dir = self.config.get("data_directory", "")
        
        if not data_dir or not os.path.exists(data_dir):
            return locations
            
        # Handle ZIP archives
        if data_dir.endswith('.zip') and zipfile.is_zipfile(data_dir):
            with zipfile.ZipFile(data_dir, 'r') as zip_ref:
                temp_dir = os.path.join(self.data_dir, "temp_facebook_extract")
                os.makedirs(temp_dir, exist_ok=True)
                zip_ref.extractall(temp_dir)
                data_dir = temp_dir
        
        # Possible file paths for location data in Facebook exports
        location_files = []
        
        # Check for location history
        for pattern in [
            "**/location_history.json", 
            "**/your_location_history.json",
            "**/location_history*.json",
            "**/places_visited.json",
            "**/check-ins.json"
        ]:
            location_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
        # Check for posts data (may contain locations)
        post_files = []
        for pattern in ["**/posts*.json", "**/your_posts*.json"]:
            post_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
        # Process location history files
        for location_file in location_files:
            try:
                with open(location_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Different formats depending on export version
                location_items = []
                
                # Format 1: Direct list of location items
                if isinstance(data, list):
                    location_items = data
                # Format 2: Nested under a key
                elif isinstance(data, dict):
                    for key in ["location_history", "locations", "history", "visits", "places_visited", "check_ins"]:
                        if key in data and isinstance(data[key], list):
                            location_items = data[key]
                            break
                
                for item in location_items:
                    timestamp = None
                    latitude = None
                    longitude = None
                    name = ""
                    
                    # Try different possible structures
                    if isinstance(item, dict):
                        # Extract timestamp
                        for time_key in ["timestamp", "time", "date", "creation_timestamp"]:
                            if time_key in item:
                                try:
                                    if isinstance(item[time_key], int):
                                        timestamp = datetime.fromtimestamp(item[time_key])
                                    elif isinstance(item[time_key], str):
                                        # Try different formats
                                        for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                                            try:
                                                timestamp = datetime.strptime(item[time_key], fmt)
                                                break
                                            except ValueError:
                                                pass
                                        
                                        # If still no match, try to parse ISO format
                                        if not timestamp:
                                            try:
                                                timestamp = datetime.fromisoformat(item[time_key].replace("Z", "+00:00"))
                                            except ValueError:
                                                pass
                                    break
                                except (ValueError, TypeError):
                                    pass
                        
                        # Extract coordinates
                        # Format 1: Direct lat/lon
                        if "latitude" in item and "longitude" in item:
                            latitude = item["latitude"]
                            longitude = item["longitude"]
                        # Format 2: Nested under 'coordinate'
                        elif "coordinate" in item and isinstance(item["coordinate"], dict):
                            coord = item["coordinate"]
                            latitude = coord.get("latitude")
                            longitude = coord.get("longitude")
                        # Format 3: Nested under 'place' or 'location'
                        elif "place" in item and isinstance(item["place"], dict):
                            place = item["place"]
                            if "coordinate" in place:
                                coord = place["coordinate"]
                                latitude = coord.get("latitude")
                                longitude = coord.get("longitude")
                            elif "location" in place and isinstance(place["location"], dict):
                                loc = place["location"]
                                latitude = loc.get("latitude")
                                longitude = loc.get("longitude")
                        elif "location" in item and isinstance(item["location"], dict):
                            loc = item["location"]
                            latitude = loc.get("latitude")
                            longitude = loc.get("longitude")
                        
                        # Get place name or address
                        for name_key in ["name", "place_name", "address", "city"]:
                            if name_key in item and item[name_key]:
                                name = str(item[name_key])
                                break
                            elif "place" in item and isinstance(item["place"], dict) and name_key in item["place"]:
                                name = str(item["place"][name_key])
                                break
                    
                    # Only add if we have coordinates
                    if latitude is not None and longitude is not None:
                        if not timestamp:
                            timestamp = datetime.now()
                        
                        # Filter by date if needed
                        if date_from and timestamp < date_from:
                            continue
                        if date_to and timestamp > date_to:
                            continue
                        
                        locations.append(
                            LocationPoint(
                                latitude=float(latitude),
                                longitude=float(longitude),
                                timestamp=timestamp,
                                source="Facebook Location",
                                context=name[:200] if name else "Location"
                            )
                        )
            except Exception as e:
                print(f"Error processing Facebook location file {location_file}: {e}")
        
        # Process post files for location data
        for post_file in post_files:
            try:
                with open(post_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                posts = []
                # Format 1: Direct list
                if isinstance(data, list):
                    posts = data
                # Format 2: Nested under a key
                elif isinstance(data, dict):
                    for key in ["posts", "your_posts", "activity"]:
                        if key in data and isinstance(data[key], list):
                            posts = data[key]
                            break
                
                for post in posts:
                    if not isinstance(post, dict):
                        continue
                        
                    # Check if post has location data
                    timestamp = None
                    latitude = None
                    longitude = None
                    context = ""
                    
                    # Get post text/content
                    for content_key in ["post", "content", "message", "text"]:
                        if content_key in post and post[content_key]:
                            context = str(post[content_key])
                            break
                    
                    # Get timestamp
                    for time_key in ["timestamp", "time", "created_time"]:
                        if time_key in post:
                            try:
                                if isinstance(post[time_key], int):
                                    timestamp = datetime.fromtimestamp(post[time_key])
                                elif isinstance(post[time_key], str):
                                    timestamp = datetime.fromisoformat(post[time_key].replace("Z", "+00:00"))
                                break
                            except (ValueError, TypeError):
                                pass
                    
                    # Check for location data in various formats
                    location_found = False
                    
                    # Format 1: Direct lat/lon
                    if "latitude" in post and "longitude" in post:
                        latitude = post["latitude"]
                        longitude = post["longitude"]
                        location_found = True
                    # Format 2: Nested under 'place'
                    elif "place" in post and isinstance(post["place"], dict):
                        place = post["place"]
                        if "coordinate" in place and isinstance(place["coordinate"], dict):
                            coord = place["coordinate"]
                            latitude = coord.get("latitude")
                            longitude = coord.get("longitude")
                            location_found = True
                        elif "location" in place and isinstance(place["location"], dict):
                            loc = place["location"]
                            latitude = loc.get("latitude")
                            longitude = loc.get("longitude")
                            location_found = True
                    # Format 3: Nested under 'location'
                    elif "location" in post and isinstance(post["location"], dict):
                        loc = post["location"]
                        latitude = loc.get("latitude")
                        longitude = loc.get("longitude")
                        location_found = True
                    
                    if location_found and latitude is not None and longitude is not None:
                        if not timestamp:
                            timestamp = datetime.now()
                            
                        # Filter by date if needed
                        if date_from and timestamp < date_from:
                            continue
                        if date_to and timestamp > date_to:
                            continue
                            
                        locations.append(
                            LocationPoint(
                                latitude=float(latitude),
                                longitude=float(longitude),
                                timestamp=timestamp,
                                source="Facebook Post",
                                context=context[:200]
                            )
                        )
            except Exception as e:
                print(f"Error processing Facebook posts file {post_file}: {e}")
        
        return locations
