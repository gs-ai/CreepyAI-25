import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.plugins.base_plugin import LocationPoint
from app.plugins.social_media.base import ArchiveSocialMediaPlugin

logger = logging.getLogger(__name__)

class InstagramPlugin(ArchiveSocialMediaPlugin):
    def __init__(self) -> None:
        super().__init__(
            name="Instagram",
            description="Extract location data from Instagram data export without API",
            temp_subdir="temp_instagram_extract",
        )
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None, 
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
        """Collect location data from Instagram data export"""
        locations: List[LocationPoint] = []

        archive_root = self.resolve_archive_root()
        if archive_root is None:
            logger.warning("Instagram data directory not found")
            return locations

        media_patterns = ["**/media.json", "**/posts_1.json", "**/posts*.json"]
        media_files = list(self.iter_data_files(archive_root, media_patterns))

        logger.info("Found %d Instagram media files", len(media_files))
        
        for media_file in media_files:
            try:
                with media_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Handle different archive formats
                media_items = []
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
                logger.error(f"Error processing Instagram media file {media_file}: {e}")
        
        logger.info(f"Extracted {len(locations)} locations from Instagram data")
        return locations
