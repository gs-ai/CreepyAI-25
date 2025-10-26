import glob
import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.plugins.base_plugin import LocationPoint
from app.plugins.geocoding_helper import GeocodingHelper
from app.plugins.social_media.base import ArchiveSocialMediaPlugin

logger = logging.getLogger(__name__)

class TikTokPlugin(ArchiveSocialMediaPlugin):
    data_source_url = "https://www.tiktok.com"
    collection_terms = (
        "TikTok headquarters",
        "TikTok office",
        "ByteDance campus",
    )

    def __init__(self) -> None:
        super().__init__(
            name="TikTok",
            description="Extract location data from TikTok data export without API",
            temp_subdir="temp_tiktok_extract",
        )
        self.geocoder = GeocodingHelper()

    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "attempt_geocoding",
                "display_name": "Attempt Geocoding",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Try to convert location names to coordinates"
            }
        ]
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None, 
                          date_to: Optional[datetime] = None) -> List[LocationPoint]:
        """Collect location data from TikTok data export"""
        collected = self.load_collected_locations(
            target=target, date_from=date_from, date_to=date_to
        )
        if collected is not None:
            return collected

        locations: List[LocationPoint] = []

        archive_root = self.resolve_archive_root()
        if archive_root is None:
            logger.warning("TikTok data directory not found")
            return locations

        data_dir = str(archive_root)
        attempt_geocoding = self.config.get("attempt_geocoding", True)
        
        # Look for different types of TikTok data files that might contain location data
        
        # 1. Video data - newer exports
        video_files = []
        for pattern in ["**/videos*.json", "**/video_list.json", "**/Videos/*.json"]:
            video_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
        logger.info(f"Found {len(video_files)} TikTok video files")
        
        # Process video files
        for video_file in video_files:
            try:
                logger.debug(f"Processing TikTok video file: {video_file}")
                with open(video_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle different possible structures
                videos_list = []
                
                # Format 1: Direct list of videos
                if isinstance(data, list):
                    videos_list = data
                # Format 2: Under "ItemList" or "videos" key
                elif isinstance(data, dict):
                    for key in ["ItemList", "videos", "Video", "VideoList"]:
                        if key in data and isinstance(data[key], list):
                            videos_list = data[key]
                            break
                
                # Process each video
                for video in videos_list:
                    if not isinstance(video, dict):
                        continue
                    
                    # Check for location data
                    location_data = None
                    lat = None
                    lon = None
                    location_name = None
                    
                    # Format 1: Direct location data
                    if "Location" in video:
                        location_data = video["Location"]
                    elif "location" in video:
                        location_data = video["location"]
                    # Format 2: Location in details/metadata
                    elif "Details" in video and isinstance(video["Details"], dict):
                        if "Location" in video["Details"]:
                            location_data = video["Details"]["Location"]
                    # Format 3: Location in poiInfo
                    elif "poiInfo" in video and video["poiInfo"]:
                        location_data = video["poiInfo"]
                        if isinstance(location_data, dict):
                            location_name = location_data.get("poiName", "")
                            if "coordinates" in location_data:
                                coords = location_data["coordinates"]
                                if "latitude" in coords and "longitude" in coords:
                                    lat = coords["latitude"]
                                    lon = coords["longitude"]
                    
                    # Extract coordinates if we have location data
                    if location_data and not (lat and lon):
                        if isinstance(location_data, dict):
                            # Try to get coordinates
                            if "latitude" in location_data and "longitude" in location_data:
                                lat = location_data["latitude"]
                                lon = location_data["longitude"]
                            elif "lat" in location_data and "lng" in location_data:
                                lat = location_data["lat"]
                                lon = location_data["lng"]
                            elif "lat" in location_data and "lon" in location_data:
                                lat = location_data["lat"]
                                lon = location_data["lon"]
                            
                            # Try to get location name
                            if not location_name:
                                for name_key in ["name", "locationName", "place", "title"]:
                                    if name_key in location_data:
                                        location_name = location_data[name_key]
                                        break
                        elif isinstance(location_data, str):
                            # Try to extract coordinates from string
                            coords = self._extract_coordinates_from_text(location_data)
                            if coords:
                                lat, lon = coords
                            else:
                                # If no coordinates, save as location name for geocoding
                                location_name = location_data
                    
                    # Extract location from video description if we still don't have coordinates
                    if not (lat and lon):
                        description = ""
                        for desc_key in ["Description", "description", "desc", "text", "caption"]:
                            if desc_key in video:
                                description = video[desc_key]
                                break
                        
                        if description:
                            # Try to extract coordinates
                            coords = self._extract_coordinates_from_text(description)
                            if coords:
                                lat, lon = coords
                            
                            # Try to extract location hashtags
                            if not location_name:
                                location_tags = re.findall(r'#([^\s#]+?(?:location|place|city|town|village|country))', description, re.IGNORECASE)
                                if location_tags:
                                    location_name = location_tags[0]
                    
                    # If we have a location name but no coordinates, try geocoding
                    if not (lat and lon) and location_name and attempt_geocoding:
                        lat, lon = self.geocoder.geocode(location_name)
                    
                    # Skip if we still don't have coordinates
                    if lat is None or lon is None:
                        continue
                    
                    # Get timestamp
                    timestamp = None
                    for date_key in ["CreateTime", "createTime", "Date", "date", "timestamp", "createdTime"]:
                        if date_key in video:
                            date_value = video[date_key]
                            if isinstance(date_value, str):
                                # Try common date formats
                                for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                                    try:
                                        timestamp = datetime.strptime(date_value, fmt)
                                        break
                                    except ValueError:
                                        pass
                            elif isinstance(date_value, (int, float)):
                                # Try as timestamp in seconds or milliseconds
                                try:
                                    timestamp = datetime.fromtimestamp(date_value)
                                except ValueError:
                                    try:
                                        timestamp = datetime.fromtimestamp(date_value / 1000)
                                    except ValueError:
                                        pass
                            
                            if timestamp:
                                break
                    
                    # Use current time if we couldn't find a timestamp
                    if not timestamp:
                        timestamp = datetime.now()
                    
                    # Filter by date if needed
                    if date_from and timestamp < date_from:
                        continue
                    if date_to and timestamp > date_to:
                        continue
                    
                    # Get video description for context
                    description = ""
                    for desc_key in ["Description", "description", "desc", "text", "caption"]:
                        if desc_key in video:
                            description = video[desc_key]
                            break
                    
                    # Create location object
                    context = description[:200] or f"TikTok Video" + (f" at {location_name}" if location_name else "")
                    
                    locations.append(
                        LocationPoint(
                            latitude=float(lat),
                            longitude=float(lon),
                            timestamp=timestamp,
                            source="TikTok Video",
                            context=context
                        )
                    )
            except Exception as e:
                logger.error(f"Error processing TikTok video file {video_file}: {e}")
        
        # 2. Look for user activity data that might have location info
        activity_files = []
        for pattern in ["**/user_data.json", "**/activity.json", "**/UserActivity/*.json"]:
            activity_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
        logger.info(f"Found {len(activity_files)} TikTok activity files")
        
        for activity_file in activity_files:
            try:
                logger.debug(f"Processing TikTok activity file: {activity_file}")
                with open(activity_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Different possible data structures
                activity_list = []
                
                if isinstance(data, list):
                    activity_list = data
                elif isinstance(data, dict):
                    # Try different keys where activity might be stored
                    for key in ["Activity", "activity", "UserActivity", "LoginHistory", "login_history"]:
                        if key in data and isinstance(data[key], list):
                            activity_list = data[key]
                            break
                
                # Look for login history with location data
                for activity in activity_list:
                    if not isinstance(activity, dict):
                        continue
                    
                    # Skip if no location info
                    location_data = None
                    for loc_key in ["Location", "location", "loginLocation", "login_location", "ipLocation"]:
                        if loc_key in activity:
                            location_data = activity[loc_key]
                            break
                    
                    if not location_data:
                        continue
                    
                    lat = None
                    lon = None
                    location_name = None
                    
                    # Extract coordinates
                    if isinstance(location_data, dict):
                        # Try to get coordinates
                        if "latitude" in location_data and "longitude" in location_data:
                            lat = location_data["latitude"]
                            lon = location_data["longitude"]
                        elif "lat" in location_data and "lng" in location_data:
                            lat = location_data["lat"]
                            lon = location_data["lng"]
                        elif "lat" in location_data and "lon" in location_data:
                            lat = location_data["lat"]
                            lon = location_data["lon"]
                        
                        # Try to get location name
                        for name_key in ["name", "city", "country", "region", "area"]:
                            if name_key in location_data:
                                location_name = location_data[name_key]
                                break
                    elif isinstance(location_data, str):
                        # Try to extract coordinates from string
                        coords = self._extract_coordinates_from_text(location_data)
                        if coords:
                            lat, lon = coords
                        else:
                            # If no coordinates, save as location name for geocoding
                            location_name = location_data
                    
                    # If we have a location name but no coordinates, try geocoding
                    if not (lat and lon) and location_name and attempt_geocoding:
                        lat, lon = self.geocoder.geocode(location_name)
                    
                    # Skip if we still don't have coordinates
                    if lat is None or lon is None:
                        continue
                    
                    # Get timestamp
                    timestamp = None
                    for date_key in ["Date", "date", "timestamp", "loginTime", "login_time", "time"]:
                        if date_key in activity:
                            date_value = activity[date_key]
                            if isinstance(date_value, str):
                                # Try common date formats
                                for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                                    try:
                                        timestamp = datetime.strptime(date_value, fmt)
                                        break
                                    except ValueError:
                                        pass
                            elif isinstance(date_value, (int, float)):
                                # Try as timestamp in seconds or milliseconds
                                try:
                                    timestamp = datetime.fromtimestamp(date_value)
                                except ValueError:
                                    try:
                                        timestamp = datetime.fromtimestamp(date_value / 1000)
                                    except ValueError:
                                        pass
                            
                            if timestamp:
                                break
                    
                    # Use current time if we couldn't find a timestamp
                    if not timestamp:
                        timestamp = datetime.now()
                    
                    # Filter by date if needed
                    if date_from and timestamp < date_from:
                        continue
                    if date_to and timestamp > date_to:
                        continue
                    
                    # Create context
                    context = "TikTok Login"
                    if "platform" in activity:
                        context += f" from {activity['platform']}"
                    if "device" in activity:
                        context += f" on {activity['device']}"
                    if location_name:
                        context += f" at {location_name}"
                    
                    locations.append(
                        LocationPoint(
                            latitude=float(lat),
                            longitude=float(lon),
                            timestamp=timestamp,
                            source="TikTok Login",
                            context=context
                        )
                    )
            except Exception as e:
                logger.error(f"Error processing TikTok activity file {activity_file}: {e}")
        
        logger.info(f"Extracted {len(locations)} locations from TikTok data")
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
            r'location:(-?\d+\.\d+),(-?\d+\.\d+)',
            
            # HTML format: geo.position:40.7128;-74.0060
            r'geo.position:(-?\d+\.\d+);(-?\d+\.\d+)'
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
