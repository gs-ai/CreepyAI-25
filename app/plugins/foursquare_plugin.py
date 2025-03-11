import os
import json
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional
import zipfile
import re
from app.plugins.base_plugin import BasePlugin, LocationPoint
from app.plugins.geocoding_helper import GeocodingHelper

class FoursquarePlugin(BasePlugin):
    def __init__(self):
        super().__init__(
        name="Foursquare",
        description="Extract location data from Foursquare data exports without API"
        )
        self.geocoder = GeocodingHelper()
    
    def is_configured(self):
        # Check if the plugin is properly configured
        return True, "FoursquarePlugin is configured"
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
        {
        "name": "data_directory",
        "display_name": "Foursquare Data Directory",
        "type": "directory",
        "default": "",
        "required": True,
        "description": "Directory containing your Foursquare data export"
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
                    temp_dir = os.path.join(self.data_dir, "temp_foursquare_extract")
                    os.makedirs(temp_dir, exist_ok=True)
                    zip_ref.extractall(temp_dir)
                    data_dir = temp_dir
        
        # Look for check-in data in various formats
        # Format 1: checkins.json
                    checkin_files = glob.glob(os.path.join(data_dir, "**/checkins*.json"), recursive=True)
        
        # Format 2: check-ins folder with individual JSON files
                    checkin_dir = os.path.join(data_dir, "check-ins")
        if os.path.isdir(checkin_dir):
                        individual_checkins = glob.glob(os.path.join(checkin_dir, "*.json"), recursive=True)
                        checkin_files.extend(individual_checkins)
        
        # Process each file
        for checkin_file in checkin_files:
            try:
                with open(checkin_file, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                
                # Handle different formats
                                    checkins = []
                
                # Format 1: Array of check-ins
                if isinstance(data, list):
                                        checkins = data
                # Format 2: Nested under a key
                elif isinstance(data, dict):
                    for key in ["checkins", "check-ins", "checkIns", "items", "data"]:
                        if key in data and isinstance(data[key], list):
                                                    checkins = data[key]
                                                break
                
                # Process each check-in
                for checkin in checkins:
                    if not isinstance(checkin, dict):
                                                    continue
                    
                    # Extract data
                                                    timestamp = None
                                                    latitude = None
                                                    longitude = None
                                                    venue_name = None
                                                    venue_category = None
                    
                    # Try to find timestamp
                    for time_key in ["createdAt", "created", "timestamp", "time", "date"]:
                        if time_key in checkin:
                            try:
                                if isinstance(checkin[time_key], int):
                                                                    timestamp = datetime.fromtimestamp(checkin[time_key])
                                elif isinstance(checkin[time_key], str):
                                    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]:
                                        try:
                                                                                timestamp = datetime.strptime(checkin[time_key], fmt)
                                                                            break
                                        except ValueError:
                                                                            pass
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
                    
                    # Try to find location
                    # Format 1: Direct lat/lon
                    if all(k in checkin for k in ["latitude", "longitude"]):
                                                                                latitude = float(checkin["latitude"])
                                                                                longitude = float(checkin["longitude"])
                    # Format 2: Nested under 'venue'
                    elif "venue" in checkin and isinstance(checkin["venue"], dict):
                                                                                    venue = checkin["venue"]
                        
                        # Get venue name
                        if "name" in venue:
                                                                                        venue_name = venue["name"]
                        
                        # Get venue category
                        if "category" in venue and isinstance(venue["category"], str):
                                                                                            venue_category = venue["category"]
                        elif "categories" in venue and isinstance(venue["categories"], list) and venue["categories"]:
                                                                                                categories = []
                            for cat in venue["categories"]:
                                if isinstance(cat, str):
                                                                                                        categories.append(cat)
                                elif isinstance(cat, dict) and "name" in cat:
                                                                                                            categories.append(cat["name"])
                            if categories:
                                                                                                                venue_category = ", ".join(categories)
                        
                        # Get coordinates
                        if "location" in venue and isinstance(venue["location"], dict):
                                                                                                                    loc = venue["location"]
                            if "lat" in loc and "lng" in loc:
                                                                                                                        latitude = float(loc["lat"])
                                                                                                                        longitude = float(loc["lng"])
                            elif "latitude" in loc and "longitude" in loc:
                                                                                                                            latitude = float(loc["latitude"])
                                                                                                                            longitude = float(loc["longitude"])
                        
                        # No coordinates but have address - try geocoding
                        if (not latitude or not longitude) and attempt_geocoding:
                                                                                                                                location_text = None
                            
                            if "location" in venue and isinstance(venue["location"], dict):
                                                                                                                                    loc_parts = []
                                
                                for field in ["address", "city", "state", "country"]:
                                    if field in venue["location"] and venue["location"][field]:
                                                                                                                                            loc_parts.append(str(venue["location"][field]))
                                
                                if loc_parts:
                                                                                                                                                location_text = ", ".join(loc_parts)
                            
                            # If we have a location text, geocode it
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
                                                                                                                                                                    context = []
                        if venue_name:
                                                                                                                                                                        context.append(f"Venue: {venue_name}")
                        if venue_category:
                                                                                                                                                                            context.append(f"Category: {venue_category}")
                        
                        # Look for additional info (shout, comments, etc)
                        for field in ["shout", "comment", "text", "message"]:
                            if field in checkin and checkin[field]:
                                                                                                                                                                                    context.append(f"{field.capitalize()}: {checkin[field]}")
                        
                                                                                                                                                                                    context_str = " | ".join(context) if context else "Foursquare Check-in"
                        
                        # Create location point
                                                                                                                                                                                    locations.append(
                                                                                                                                                                                    LocationPoint(
                                                                                                                                                                                    latitude=latitude,
                                                                                                                                                                                    longitude=longitude,
                                                                                                                                                                                    timestamp=timestamp,
                                                                                                                                                                                    source="Foursquare",
                                                                                                                                                                                    context=context_str
                                                                                                                                                                                    )
                                                                                                                                                                                    )
            except Exception as e:
                                                                                                                                                                                        print(f"Error processing Foursquare check-in file {checkin_file}: {e}")
                
                                                                                                                                                                                    return locations
    
    def search_for_targets(self, search_term: str) -> List[Dict[str, Any]]:
                                                                                                                                                                                        targets = []
                                                                                                                                                                                        data_dir = self.config.get("data_directory", "")
        
        if not data_dir or not os.path.exists(data_dir):
                                                                                                                                                                                        return targets
        
        # Handle ZIP archives
        if data_dir.endswith('.zip') and zipfile.is_zipfile(data_dir):
            with zipfile.ZipFile(data_dir, 'r') as zip_ref:
                                                                                                                                                                                                temp_dir = os.path.join(self.data_dir, "temp_foursquare_extract")
                                                                                                                                                                                                os.makedirs(temp_dir, exist_ok=True)
                                                                                                                                                                                                zip_ref.extractall(temp_dir)
                                                                                                                                                                                                data_dir = temp_dir
        
        # Look for check-in data in various formats
                                                                                                                                                                                                checkin_files = glob.glob(os.path.join(data_dir, "**/checkins*.json"), recursive=True)
                                                                                                                                                                                                checkin_dir = os.path.join(data_dir, "check-ins")
        if os.path.isdir(checkin_dir):
                                                                                                                                                                                                    individual_checkins = glob.glob(os.path.join(checkin_dir, "*.json"), recursive=True)
                                                                                                                                                                                                    checkin_files.extend(individual_checkins)
        
        # Process each file
        for checkin_file in checkin_files:
            try:
                with open(checkin_file, 'r', encoding='utf-8') as f:
                                                                                                                                                                                                                data = json.load(f)
                
                                                                                                                                                                                                                checkins = []
                if isinstance(data, list):
                                                                                                                                                                                                                    checkins = data
                elif isinstance(data, dict):
                    for key in ["checkins", "check-ins", "checkIns", "items", "data"]:
                        if key in data and isinstance(data[key], list):
                                                                                                                                                                                                                                checkins = data[key]
                                                                                                                                                                                                                            break
                
                for checkin in checkins:
                    if not isinstance(checkin, dict):
                                                                                                                                                                                                                                continue
                    
                                                                                                                                                                                                                                venue_name = None
                    if "venue" in checkin and isinstance(checkin["venue"], dict):
                                                                                                                                                                                                                                    venue = checkin["venue"]
                        if "name" in venue:
                                                                                                                                                                                                                                        venue_name = venue["name"]
                    
                    if venue_name and search_term.lower() in venue_name.lower():
                                                                                                                                                                                                                                            targets.append({
                                                                                                                                                                                                                                            'targetId': venue_name,
                                                                                                                                                                                                                                            'targetName': venue_name,
                                                                                                                                                                                                                                            'pluginName': self.name
                                                                                                                                                                                                                                            })
            except Exception as e:
                                                                                                                                                                                                                                                print(f"Error processing Foursquare check-in file {checkin_file}: {e}")
        
                                                                                                                                                                                                                                            return targets
