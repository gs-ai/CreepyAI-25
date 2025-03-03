import os
import json
import glob
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import zipfile
from .base_plugin import BasePlugin, LocationPoint
from .geocoding_helper import GeocodingHelper

class FlickrPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="Flickr",
            description="Extract location data from Flickr data exports without API"
        )
        self.geocoder = GeocodingHelper()
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "data_directory",
                "display_name": "Flickr Data Directory",
                "type": "directory",
                "default": "",
                "required": True,
                "description": "Directory containing your Flickr data export"
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
                temp_dir = os.path.join(self.data_dir, "temp_flickr_extract")
                os.makedirs(temp_dir, exist_ok=True)
                zip_ref.extractall(temp_dir)
                data_dir = temp_dir
        
        # Look for various files that might contain location data
        
        # 1. Photos metadata files
        photo_files = []
        for pattern in ["**/photo*.json", "**/photos*.json", "**/albums*.json", "**/metadata*.json"]:
            photo_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
        # Process photo metadata
        for photo_file in photo_files:
            try:
                with open(photo_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Different formats depending on export version
                photos = []
                
                # Format 1: Direct list of photos
                if isinstance(data, list):
                    photos = data
                # Format 2: Nested under a key
                elif isinstance(data, dict):
                    for key in ["photos", "photo", "items"]:
                        if key in data and isinstance(data[key], list):
                            photos = data[key]
                            break
                
                # Process each photo
                for photo in photos:
                    if not isinstance(photo, dict):
                        continue
                    
                    # Extract data
                    timestamp = None
                    latitude = None
                    longitude = None
                    title = None
                    description = None
                    
                    # Try to find timestamp
                    for time_key in ["dateTaken", "date_taken", "dateUploaded", "date", "timestamp"]:
                        if time_key in photo:
                            try:
                                if isinstance(photo[time_key], int):
                                    timestamp = datetime.fromtimestamp(photo[time_key])
                                elif isinstance(photo[time_key], str):
                                    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]:
                                        try:
                                            timestamp = datetime.strptime(photo[time_key], fmt)
                                            break
                                        except ValueError:
                                            pass
                                    
                                    # If still no match, try to extract date with regex
                                    if not timestamp:
                                        match = re.search(r'(\d{4})[/-](\d{2})[/-](\d{2})', photo[time_key])
                                        if match:
                                            year, month, day = map(int, match.groups())
                                            timestamp = datetime(year, month, day)
                            except Exception:
                                pass
                            break
                    
                    # Default timestamp if not found
                    if not timestamp:
                        timestamp = datetime.now()
                    
                    # Apply date filters
                    if date_from and timestamp < date_from:
                        continue
                    if date_to and timestamp > date_to:
                        continue
                    
                    # Get title/description
                    if "title" in photo:
                        title = photo["title"]
                    if "description" in photo:
                        description = photo["description"]
                    
                    # Try to find location
                    # Format 1: Direct lat/lon
                    if all(k in photo for k in ["latitude", "longitude"]):
                        latitude = float(photo["latitude"])
                        longitude = float(photo["longitude"])
                    # Format 2: Nested under 'location' or 'geo'
                    elif "location" in photo and isinstance(photo["location"], dict):
                        loc = photo["location"]
                        if "latitude" in loc and "longitude" in loc:
                            latitude = float(loc["latitude"])
                            longitude = float(loc["longitude"])
                        elif "lat" in loc and "lon" in loc:
                            latitude = float(loc["lat"])
                            longitude = float(loc["lon"])
                    elif "geo" in photo and isinstance(photo["geo"], dict):
                        geo = photo["geo"]
                        if "lat" in geo and "lon" in geo:
                            latitude = float(geo["lat"])
                            longitude = float(geo["lon"])
                    
                    # Try to geocode from location text if no coordinates
                    if (not latitude or not longitude) and attempt_geocoding:
                        location_text = None
                        
                        # Try to find location text
                        if "location" in photo and isinstance(photo["location"], str):
                            location_text = photo["location"]
                        elif "place" in photo:
                            if isinstance(photo["place"], str):
                                location_text = photo["place"]
                            elif isinstance(photo["place"], dict) and "name" in photo["place"]:
                                location_text = photo["place"]["name"]
                        
                        # If we found a location text, geocode it
                        if location_text:
                            try:
                                lat, lon = self.geocoder.geocode(location_text)
                                if lat is not None and lon is not None:
                                    latitude = lat
                                    longitude = lon
                            except Exception as e:
                                print(f"Geocoding error: {e}")
                    
                    # Only add if we have coordinates
                    if latitude is not None and longitude is not None:
                        # Build context string
                        context_parts = []
                        if title:
                            context_parts.append(f"Title: {title}")
                        if description:
                            context_parts.append(f"Description: {description}")
                        
                        context = " | ".join(context_parts) if context_parts else "Flickr Photo"
                        
                        # Create location point
                        locations.append(
                            LocationPoint(
                                latitude=latitude,
                                longitude=longitude,
                                timestamp=timestamp,
                                source="Flickr",
                                context=context
                            )
                        )
            except Exception as e:
                print(f"Error processing Flickr photo file {photo_file}: {e}")
        
        return locations
