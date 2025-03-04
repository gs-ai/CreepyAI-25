import os
import json
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional
import zipfile
from creepy.plugins.base_plugin import BasePlugin, LocationPoint

class InstagramPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="Instagram",
            description="Extract location data from Instagram data export without API"
        )
    
    def is_configured(self):
        # Check if the plugin is properly configured
        return True, "InstagramPlugin is configured"
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "data_directory",
                "display_name": "Instagram Data Directory",
                "type": "directory",
                "default": "",
                "required": True,
                "description": "Directory containing your Instagram data export"
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
                temp_dir = os.path.join(self.data_dir, "temp_instagram_extract")
                os.makedirs(temp_dir, exist_ok=True)
                zip_ref.extractall(temp_dir)
                data_dir = temp_dir
        
        # Look for media files that contain location data
        media_files = []
        for pattern in ["**/media.json", "**/posts_1.json", "**/posts*.json"]:
            media_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
        for media_file in media_files:
            try:
                with open(media_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle different archive formats
                if isinstance(data, dict):
                    if "photos" in data:
                        media_items = data["photos"]
                    elif "videos" in data:
                        media_items = data["videos"]
                    elif "media" in data:
                        media_items = data["media"]
                    else:
                        media_items = []
                elif isinstance(data, list):
                    media_items = data
                else:
                    continue
                
                for item in media_items:
                    # Check if item has location data
                    location = None
                    timestamp = None
                    caption = ""
                    
                    # Different structures in exports
                    if isinstance(item, dict):
                        # Format 1
                        if "location" in item and item["location"]:
                            if isinstance(item["location"], dict) and "latitude" in item["location"]:
                                location = {
                                    "latitude": item["location"].get("latitude"),
                                    "longitude": item["location"].get("longitude")
                                }
                            elif isinstance(item["location"], str) and "," in item["location"]:
                                parts = item["location"].split(",")
                                if len(parts) >= 2:
                                    try:
                                        location = {
                                            "latitude": float(parts[0].strip()),
                                            "longitude": float(parts[1].strip())
                                        }
                                    except ValueError:
                                        pass
                                        
                        # Format 2
                        if not location and "place" in item and item["place"]:
                            if isinstance(item["place"], dict) and "location" in item["place"]:
                                loc = item["place"]["location"]
                                if "latitude" in loc and "longitude" in loc:
                                    location = {
                                        "latitude": loc["latitude"],
                                        "longitude": loc["longitude"]
                                    }
                        
                        # Get timestamp
                        for time_field in ["taken_at", "created_at", "timestamp", "creation_timestamp"]:
                            if time_field in item:
                                try:
                                    if isinstance(item[time_field], int):
                                        timestamp = datetime.fromtimestamp(item[time_field])
                                    else:
                                        timestamp = datetime.fromisoformat(item[time_field].replace("Z", "+00:00"))
                                    break
                                except (ValueError, TypeError):
                                    pass
                        
                        # Get caption
                        if "caption" in item:
                            if isinstance(item["caption"], dict) and "text" in item["caption"]:
                                caption = item["caption"]["text"]
                            elif isinstance(item["caption"], str):
                                caption = item["caption"]
                    
                    # Only add if we have location data
                    if location and location["latitude"] and location["longitude"]:
                        # Default timestamp if none found
                        if not timestamp:
                            timestamp = datetime.now()
                            
                        # Filter by date if needed
                        if date_from and timestamp < date_from:
                            continue
                        if date_to and timestamp > date_to:
                            continue
                            
                        locations.append(
                            LocationPoint(
                                latitude=location["latitude"],
                                longitude=location["longitude"],
                                timestamp=timestamp,
                                source="Instagram",
                                context=caption[:200]
                            )
                        )
            except Exception as e:
                print(f"Error processing {media_file}: {e}")
                
        return locations
