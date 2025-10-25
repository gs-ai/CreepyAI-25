import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.plugins.base_plugin import LocationPoint
from app.plugins.geocoding_helper import GeocodingHelper
from app.plugins.social_media.base import ArchiveSocialMediaPlugin

logger = logging.getLogger(__name__)

class SnapchatPlugin(ArchiveSocialMediaPlugin):
    def __init__(self) -> None:
        super().__init__(
            name="Snapchat",
            description="Extract location data from Snapchat data exports without API",
            temp_subdir="temp_snapchat_extract",
        )
        self.geocoder = GeocodingHelper()
    
    def is_configured(self) -> Tuple[bool, str]:
        """Check if the plugin is properly configured"""
        if self.has_input_data():
            return True, "Snapchat plugin is configured"

        memories_json = self.config.get("memories_json", "")
        if memories_json:
            candidate = Path(memories_json).expanduser()
            if candidate.exists():
                return True, "Snapchat plugin is configured"

        data_dir = self.get_data_directory()
        return False, f"Add Snapchat exports to {data_dir}"

    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "process_memories",
                "display_name": "Process Memories",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Extract location data from Snapchat Memories"
            },
            {
                "name": "process_stories",
                "display_name": "Process Stories",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Extract location data from Snapchat Stories"
            }
        ]
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None, 
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
        """
        Collect location data from Snapchat data exports
        
        Args:
            target: Target directory containing Snapchat data
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            List of LocationPoint objects
        """
        locations: List[LocationPoint] = []
        archive_root = self.resolve_archive_root()
        memories_json = self.config.get("memories_json", "")
        process_memories = self.config.get("process_memories", True)
        process_stories = self.config.get("process_stories", True)

        configured_memories: Optional[Path] = None
        if memories_json:
            candidate = Path(memories_json).expanduser()
            if candidate.exists():
                configured_memories = candidate

        if archive_root is None and configured_memories is None:
            logger.warning("No valid Snapchat archive directory or memories file found")
            return locations

        # Process Snapchat Memories
        if process_memories:
            memories_files: List[Path] = []
            if configured_memories is not None:
                memories_files.append(configured_memories)
            if archive_root is not None:
                memories_patterns = ["**/memories.json", "**/memories_history.json"]
                memories_files.extend(self.iter_data_files(archive_root, memories_patterns))

            for memories_file in memories_files:
                memory_locations = self._extract_memories_locations(memories_file, date_from, date_to)
                locations.extend(memory_locations)
                logger.info(
                    "Extracted %d locations from memories file %s",
                    len(memory_locations),
                    memories_file,
                )

        # Process Snapchat Stories
        if process_stories and archive_root is not None:
            story_locations = self._extract_story_locations(archive_root, date_from, date_to)
            locations.extend(story_locations)
            logger.info("Extracted %d locations from story files", len(story_locations))
                
        logger.info(f"Total Snapchat locations found: {len(locations)}")
        return locations
    
    def _extract_memories_locations(self, file_path: Path, date_from: Optional[datetime],
                                   date_to: Optional[datetime]) -> List[LocationPoint]:
        """
        Extract location data from Snapchat memories file
        
        Args:
            file_path: Path to memories JSON file
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            List of LocationPoint objects
        """
        locations = []
        
        try:
            with file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check different possible formats
            memories_list = []
            
            # Format 1: Direct list of memories
            if isinstance(data, list):
                memories_list = data
            # Format 2: Under "Saved Media" key
            elif isinstance(data, dict) and "Saved Media" in data:
                memories_list = data["Saved Media"]
            # Format 3: Under "memories" key
            elif isinstance(data, dict) and "memories" in data:
                memories_list = data["memories"]
            
            for memory in memories_list:
                if not isinstance(memory, dict):
                    continue
                    
                # Get location if available
                location_data = None
                if "Location" in memory and memory["Location"]:
                    location_data = memory["Location"]
                elif "location" in memory and memory["location"]:
                    location_data = memory["location"]
                
                if not location_data:
                    continue
                    
                # Extract latitude and longitude
                lat = None
                lon = None
                
                # Format 1: Direct lat/lon
                if "Latitude" in location_data and "Longitude" in location_data:
                    lat = location_data["Latitude"]
                    lon = location_data["Longitude"]
                elif "latitude" in location_data and "longitude" in location_data:
                    lat = location_data["latitude"]
                    lon = location_data["longitude"]
                # Format 2: Coordinates as string "lat,lon"
                elif "coordinates" in location_data and isinstance(location_data["coordinates"], str):
                    coords = location_data["coordinates"].split(",")
                    if len(coords) >= 2:
                        try:
                            lat = float(coords[0].strip())
                            lon = float(coords[1].strip())
                        except ValueError:
                            continue
                
                if lat is None or lon is None:
                    continue
                    
                # Get timestamp
                timestamp = None
                
                for date_key in ["Date", "date", "Created", "created", "timestamp"]:
                    if date_key in memory:
                        date_str = memory[date_key]
                        if isinstance(date_str, str):
                            # Try different date formats
                            for fmt in ["%Y-%m-%d %H:%M:%S %Z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
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
                                # Maybe it's milliseconds
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
                    
                # Get memory type
                memory_type = memory.get("Media Type", memory.get("type", "Unknown"))
                
                # Get location name if available
                location_name = ""
                if isinstance(location_data, dict):
                    for name_key in ["Name", "name", "place_name", "location_name"]:
                        if name_key in location_data:
                            location_name = location_data[name_key]
                            break
                
                # Create location object
                locations.append(
                    LocationPoint(
                        latitude=float(lat),
                        longitude=float(lon),
                        timestamp=timestamp,
                        source="Snapchat Memory",
                        context=f"Snapchat {memory_type}" + (f" at {location_name}" if location_name else "")
                    )
                )
                
        except Exception as e:
            logger.error("Error processing Snapchat memories file %s: %s", file_path, e)
            
        return locations
    
    def _extract_story_locations(self, data_dir: Path, date_from: Optional[datetime],
                                date_to: Optional[datetime]) -> List[LocationPoint]:
        """
        Extract location data from Snapchat stories
        
        Args:
            data_dir: Directory containing Snapchat data
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            List of LocationPoint objects
        """
        locations: List[LocationPoint] = []

        # Look for story data files
        story_patterns = [
            "**/story_history.json",
            "**/stories.json",
            "**/user_stories.json",
        ]
        story_files = list(self.iter_data_files(data_dir, story_patterns))

        for story_file in story_files:
            try:
                with story_file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check different possible formats
                stories_list = []
                
                # Format 1: Direct list of stories
                if isinstance(data, list):
                    stories_list = data
                # Format 2: Under "Stories" key
                elif isinstance(data, dict) and "Stories" in data:
                    stories_list = data["Stories"]
                # Format 3: Under "stories" key
                elif isinstance(data, dict) and "stories" in data:
                    stories_list = data["stories"]
                # Format 4: Under "user_stories" key
                elif isinstance(data, dict) and "user_stories" in data:
                    stories_list = data["user_stories"]
                
                for story in stories_list:
                    if not isinstance(story, dict):
                        continue
                    
                    # Check if there's location data
                    location_data = None
                    if "Location" in story and story["Location"]:
                        location_data = story["Location"]
                    elif "location" in story and story["location"]:
                        location_data = story["location"]
                    
                    if not location_data:
                        # Some stories have location as part of media metadata
                        media_items = []
                        if "media" in story and isinstance(story["media"], list):
                            media_items = story["media"]
                        elif "Media" in story and isinstance(story["Media"], list):
                            media_items = story["Media"]
                        
                        for media in media_items:
                            if isinstance(media, dict) and "location" in media and media["location"]:
                                location_data = media["location"]
                                break
                    
                    if not location_data:
                        continue
                        
                    # Extract latitude and longitude
                    lat = None
                    lon = None
                    
                    # Format 1: Direct lat/lon
                    if "Latitude" in location_data and "Longitude" in location_data:
                        lat = location_data["Latitude"]
                        lon = location_data["Longitude"]
                    elif "latitude" in location_data and "longitude" in location_data:
                        lat = location_data["latitude"]
                        lon = location_data["longitude"]
                    # Format 2: Coordinates as string
                    elif "coordinates" in location_data and isinstance(location_data["coordinates"], str):
                        coords = location_data["coordinates"].split(",")
                        if len(coords) >= 2:
                            try:
                                lat = float(coords[0].strip())
                                lon = float(coords[1].strip())
                            except ValueError:
                                continue
                    
                    if lat is None or lon is None:
                        continue
                        
                    # Get timestamp
                    timestamp = None
                    
                    for date_key in ["Date", "date", "Created", "created", "timestamp", "time"]:
                        if date_key in story:
                            date_str = story[date_key]
                            if isinstance(date_str, str):
                                # Try different date formats
                                for fmt in ["%Y-%m-%d %H:%M:%S %Z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
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
                                    # Maybe it's milliseconds
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
                        
                    # Get location name if available
                    location_name = ""
                    if isinstance(location_data, dict):
                        for name_key in ["Name", "name", "place_name", "location_name"]:
                            if name_key in location_data:
                                location_name = location_data[name_key]
                                break
                    
                    # Create location object
                    locations.append(
                        LocationPoint(
                            latitude=float(lat),
                            longitude=float(lon),
                            timestamp=timestamp,
                            source="Snapchat Story",
                            context=f"Snapchat Story" + (f" at {location_name}" if location_name else "")
                        )
                    )
                    
            except Exception as e:
                logger.error(f"Error processing Snapchat story file {story_file}: {e}")
                
        return locations

    def search_for_targets(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for specific targets in Snapchat data
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching target dictionaries
        """
        targets: List[Dict[str, Any]] = []
        archive_root = self.resolve_archive_root()
        memories_json = self.config.get("memories_json", "")

        has_memories_file = False
        if memories_json:
            candidate = Path(memories_json).expanduser()
            has_memories_file = candidate.exists()

        if archive_root is None and not has_memories_file:
            return targets

        locations = self.collect_locations(target="")

        for location in locations:
            if search_term.lower() in location.context.lower():
                targets.append({
                    'targetId': f"{location.latitude},{location.longitude}",
                    'targetName': location.context,
                    'pluginName': self.name
                })
        
        return targets
