import os
import json
import glob
from datetime import datetime
import logging
import zipfile
import re
from typing import List, Dict, Any, Optional, Tuple
import traceback
import codecs
from app.plugins.base_plugin import BasePlugin, LocationPoint
from app.plugins.enhanced_geocoding_helper import EnhancedGeocodingHelper

logger = logging.getLogger(__name__)

class FacebookPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
        name="Facebook",
        description="Extract location data from Facebook data export without API"
        )
        self.geocoder = EnhancedGeocodingHelper()
        self.temp_dir = None
    
    def is_configured(self) -> Tuple[bool, str]:
            """Check if the plugin is properly configured"""""""""""
            data_dir = self.config.get("data_directory", "")
        if not data_dir:
            return False, "Data directory not configured"
        
        if data_dir.endswith('.zip'):
            if not os.path.isfile(data_dir):
                return False, "ZIP file does not exist"
        else:
            if not os.path.isdir(data_dir):
                    return False, "Data directory does not exist"
        
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
            
        if data_dir.endswith('.zip') and zipfile.is_zipfile(data_dir):
            with zipfile.ZipFile(data_dir, 'r') as zip_ref:
                            self.temp_dir = os.path.join(self.data_dir, "temp_facebook_extract")
                            os.makedirs(self.temp_dir, exist_ok=True)
                            zip_ref.extractall(self.temp_dir)
                            data_dir = self.temp_dir
        
                            location_files = []
        
                            for pattern in [
                            "**/location_history.json", 
                            "**/your_location_history.json",
                            "**/location_history*.json",
                            "**/places_visited.json",
                            "**/check-ins.json"
        ]:
                                location_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
                                post_files = []
        for pattern in ["**/posts*.json", "**/your_posts*.json"]:
                                    post_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
        for location_file in location_files:
            try:
                with open(location_file, 'r', encoding='utf-8') as f:
                                                data = json.load(f)
                
                                                location_items = []
                
                if isinstance(data, list):
                                                    location_items = data
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
                    
                    if isinstance(item, dict):
                        for time_key in ["timestamp", "time", "date", "creation_timestamp"]:
                            if time_key in item:
                                try:
                                    if isinstance(item[time_key], int):
                                                                                    timestamp = datetime.fromtimestamp(item[time_key])
                                    elif isinstance(item[time_key], str):
                                        for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                                            try:
                                                                                                timestamp = datetime.strptime(item[time_key], fmt)
                                                                                            break
                                            except ValueError:
                                                                                            pass
                                        
                                        if not timestamp:
                                            try:
                                                                                                    timestamp = datetime.fromisoformat(item[time_key].replace("Z", "+00:00"))
                                            except ValueError:
                                                                                                    pass
                                                                                                break
                                except (ValueError, TypeError):
                                                                                                pass
                        
                        if "latitude" in item and "longitude" in item:
                                                                                                    latitude = item["latitude"]
                                                                                                    longitude = item["longitude"]
                        elif "coordinate" in item and isinstance(item["coordinate"], dict):
                                                                                                        coord = item["coordinate"]
                                                                                                        latitude = coord.get("latitude")
                                                                                                        longitude = coord.get("longitude")
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
                        
                        for name_key in ["name", "place_name", "address", "city"]:
                            if name_key in item and item[name_key]:
                                                                                                                                name = str(item[name_key])
                                                                                                                            break
                            elif "place" in item and isinstance(item["place"], dict) and name_key in item["place"]:
                                                                                                                                name = str(item["place"][name_key])
                                                                                                                            break
                    
                    if latitude is not None and longitude is not None:
                        if not timestamp:
                                                                                                                                    timestamp = datetime.now()
                        
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
                                                                                                                                        logger.error(f"Error processing Facebook location file {location_file}: {e}")
                                                                                                                                        logger.debug(traceback.format_exc())
        
        for post_file in post_files:
            try:
                with open(post_file, 'r', encoding='utf-8') as f:
                                                                                                                                                    data = json.load(f)
                
                                                                                                                                                    posts = []
                if isinstance(data, list):
                                                                                                                                                        posts = data
                elif isinstance(data, dict):
                    for key in ["posts", "your_posts", "activity"]:
                        if key in data and isinstance(data[key], list):
                                                                                                                                                                    posts = data[key]
                                                                                                                                                                break
                
                for post in posts:
                    if not isinstance(post, dict):
                                                                                                                                                                    continue
                        
                                                                                                                                                                    timestamp = None
                                                                                                                                                                    latitude = None
                                                                                                                                                                    longitude = None
                                                                                                                                                                    context = ""
                    
                    for content_key in ["post", "content", "message", "text"]:
                        if content_key in post and post[content_key]:
                                                                                                                                                                            context = str(post[content_key])
                                                                                                                                                                        break
                    
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
                    
                                                                                                                                                                                        location_found = False
                    
                    if "latitude" in post and "longitude" in post:
                                                                                                                                                                                            latitude = post["latitude"]
                                                                                                                                                                                            longitude = post["longitude"]
                                                                                                                                                                                            location_found = True
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
                    elif "location" in post and isinstance(post["location"], dict):
                                                                                                                                                                                                            loc = post["location"]
                                                                                                                                                                                                            latitude = loc.get("latitude")
                                                                                                                                                                                                            longitude = loc.get("longitude")
                                                                                                                                                                                                            location_found = True
                    
                    if location_found and latitude is not None and longitude is not None:
                        if not timestamp:
                                                                                                                                                                                                                    timestamp = datetime.now()
                            
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
                                                                                                                                                                                                                        logger.error(f"Error processing Facebook posts file {post_file}: {e}")
                                                                                                                                                                                                                        logger.debug(traceback.format_exc())
        
                                                                                                                                                                                                                    return locations
    
    def search_for_targets(self, search_term: str) -> List[Dict[str, Any]]:
                                                                                                                                                                                                                        targets = []
                                                                                                                                                                                                                        data_dir = self.config.get("data_directory", "")
        
        if not data_dir or not os.path.exists(data_dir):
                                                                                                                                                                                                                        return targets
        
        if data_dir.endswith('.zip') and zipfile.is_zipfile(data_dir):
            with zipfile.ZipFile(data_dir, 'r') as zip_ref:
                                                                                                                                                                                                                                self.temp_dir = os.path.join(self.data_dir, "temp_facebook_extract")
                                                                                                                                                                                                                                os.makedirs(self.temp_dir, exist_ok=True)
                                                                                                                                                                                                                                zip_ref.extractall(self.temp_dir)
                                                                                                                                                                                                                                data_dir = self.temp_dir
        
                                                                                                                                                                                                                                location_files = []
                                                                                                                                                                                                                                for pattern in [
                                                                                                                                                                                                                                "**/location_history.json", 
                                                                                                                                                                                                                                "**/your_location_history.json",
                                                                                                                                                                                                                                "**/location_history*.json",
                                                                                                                                                                                                                                "**/places_visited.json",
                                                                                                                                                                                                                                "**/check-ins.json"
        ]:
                                                                                                                                                                                                                                    location_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
                                                                                                                                                                                                                                    post_files = []
        for pattern in ["**/posts*.json", "**/your_posts*.json"]:
                                                                                                                                                                                                                                        post_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
        for location_file in location_files:
            try:
                with open(location_file, 'r', encoding='utf-8') as f:
                                                                                                                                                                                                                                                    data = json.load(f)
                
                                                                                                                                                                                                                                                    location_items = []
                if isinstance(data, list):
                                                                                                                                                                                                                                                        location_items = data
                elif isinstance(data, dict):
                    for key in ["location_history", "locations", "history", "visits", "places_visited", "check_ins"]:
                        if key in data and isinstance(data[key], list):
                                                                                                                                                                                                                                                                    location_items = data[key]
                                                                                                                                                                                                                                                                break
                
                for item in location_items:
                                                                                                                                                                                                                                                                    name = ""
                    if isinstance(item, dict):
                        for name_key in ["name", "place_name", "address", "city"]:
                            if name_key in item and item[name_key]:
                                                                                                                                                                                                                                                                                name = str(item[name_key])
                                                                                                                                                                                                                                                                            break
                            elif "place" in item and isinstance(item["place"], dict) and name_key in item["place"]:
                                                                                                                                                                                                                                                                                name = str(item["place"][name_key])
                                                                                                                                                                                                                                                                            break
                    
                    if name and search_term.lower() in name.lower():
                                                                                                                                                                                                                                                                                targets.append({
                                                                                                                                                                                                                                                                                'targetId': name,
                                                                                                                                                                                                                                                                                'targetName': name,
                                                                                                                                                                                                                                                                                'pluginName': self.name
                                                                                                                                                                                                                                                                                })
            except Exception as e:
                                                                                                                                                                                                                                                                                    logger.error(f"Error processing Facebook location file {location_file}: {e}")
                                                                                                                                                                                                                                                                                    logger.debug(traceback.format_exc())
        
        for post_file in post_files:
            try:
                with open(post_file, 'r', encoding='utf-8') as f:
                                                                                                                                                                                                                                                                                                data = json.load(f)
                
                                                                                                                                                                                                                                                                                                posts = []
                if isinstance(data, list):
                                                                                                                                                                                                                                                                                                    posts = data
                elif isinstance(data, dict):
                    for key in ["posts", "your_posts", "activity"]:
                        if key in data and isinstance(data[key], list):
                                                                                                                                                                                                                                                                                                                posts = data[key]
                                                                                                                                                                                                                                                                                                            break
                
                for post in posts:
                    if not isinstance(post, dict):
                                                                                                                                                                                                                                                                                                                continue
                    
                                                                                                                                                                                                                                                                                                                context = ""
                    for content_key in ["post", "content", "message", "text"]:
                        if content_key in post and post[content_key]:
                                                                                                                                                                                                                                                                                                                        context = str(post[content_key])
                                                                                                                                                                                                                                                                                                                    break
                    
                    if context and search_term.lower() in context.lower():
                                                                                                                                                                                                                                                                                                                        targets.append({
                                                                                                                                                                                                                                                                                                                        'targetId': context[:50],
                                                                                                                                                                                                                                                                                                                        'targetName': context[:50],
                                                                                                                                                                                                                                                                                                                        'pluginName': self.name
                                                                                                                                                                                                                                                                                                                        })
            except Exception as e:
                                                                                                                                                                                                                                                                                                                            logger.error(f"Error processing Facebook posts file {post_file}: {e}")
                                                                                                                                                                                                                                                                                                                            logger.debug(traceback.format_exc())
        
                                                                                                                                                                                                                                                                                                                        return targets
