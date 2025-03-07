import os
import json
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional
import zipfile
import re
from creepy.plugins.base_plugin import BasePlugin, LocationPoint
from creepy.plugins.geocoding_helper import GeocodingHelper

class LinkedInPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="LinkedIn",
            description="Extract location data from LinkedIn data export without API"
        )
        self.geocoder = GeocodingHelper()
    
    def is_configured(self):
        # Check if the plugin is properly configured
        return True, "LinkedInPlugin is configured"
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "data_directory",
                "display_name": "LinkedIn Data Directory",
                "type": "directory",
                "default": "",
                "required": True,
                "description": "Directory containing your LinkedIn data export"
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
                temp_dir = os.path.join(self.data_dir, "temp_linkedin_extract")
                os.makedirs(temp_dir, exist_ok=True)
                zip_ref.extractall(temp_dir)
                data_dir = temp_dir
        
        # Process various LinkedIn data files that may contain location data
        
        # 1. Profile data with location information
        profile_files = glob.glob(os.path.join(data_dir, "**/Profile.json"), recursive=True)
        for file_path in profile_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                
                if isinstance(profile_data, dict):
                    location_text = None
                    
                    # Extract location string
                    if "geoLocation" in profile_data and profile_data["geoLocation"]:
                        if isinstance(profile_data["geoLocation"], str):
                            location_text = profile_data["geoLocation"]
                        elif isinstance(profile_data["geoLocation"], dict):
                            location_text = profile_data["geoLocation"].get("name", "")
                    elif "locationName" in profile_data and profile_data["locationName"]:
                        location_text = profile_data["locationName"]
                    
                    if location_text and attempt_geocoding:
                        lat, lon = self.geocoder.geocode(location_text)
                        if lat is not None and lon is not None:
                            # Use current time as LinkedIn doesn't specify when profile location was set
                            locations.append(
                                LocationPoint(
                                    latitude=lat,
                                    longitude=lon,
                                    timestamp=datetime.now(),
                                    source="LinkedIn Profile",
                                    context=f"Profile location: {location_text}"
                                )
                            )
            except Exception as e:
                print(f"Error processing LinkedIn profile: {e}")
        
        # 2. Position/work history data
        position_files = glob.glob(os.path.join(data_dir, "**/Positions.json"), recursive=True)
        for file_path in position_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    positions_data = json.load(f)
                
                if isinstance(positions_data, list):
                    for position in positions_data:
                        if isinstance(position, dict):
                            location_text = None
                            start_date = None
                            end_date = None
                            company_name = None
                            
                            # Get location
                            if "locationName" in position and position["locationName"]:
                                location_text = position["locationName"]
                            elif "location" in position and position["location"]:
                                if isinstance(position["location"], str):
                                    location_text = position["location"]
                                elif isinstance(position["location"], dict):
                                    location_text = position["location"].get("name", "")
                            
                            # Get start date
                            if "startDate" in position and position["startDate"]:
                                start_data = position["startDate"]
                                try:
                                    if isinstance(start_data, dict) and "year" in start_data:
                                        year = start_data["year"]
                                        month = start_data.get("month", 1)
                                        day = start_data.get("day", 1)
                                        start_date = datetime(year, month, day)
                                    elif isinstance(start_data, str):
                                        # Try common date formats
                                        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d-%m-%Y"]:
                                            try:
                                                start_date = datetime.strptime(start_data, fmt)
                                                break
                                            except ValueError:
                                                pass
                                except Exception:
                                    pass
                            
                            # Get end date
                            if "endDate" in position and position["endDate"]:
                                end_data = position["endDate"]
                                try:
                                    if isinstance(end_data, dict) and "year" in end_data:
                                        year = end_data["year"]
                                        month = end_data.get("month", 12)
                                        day = end_data.get("day", 28)
                                        end_date = datetime(year, month, day)
                                    elif isinstance(end_data, str):
                                        # Try common date formats
                                        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d-%m-%Y"]:
                                            try:
                                                end_date = datetime.strptime(end_data, fmt)
                                                break
                                            except ValueError:
                                                pass
                                except Exception:
                                    pass
                            
                            # Get company name
                            if "companyName" in position:
                                company_name = position["companyName"]
                            elif "company" in position and isinstance(position["company"], dict):
                                company_name = position["company"].get("name", "")
                            
                            # Only process if we have a location and it can be geocoded
                            if location_text and attempt_geocoding:
                                lat, lon = self.geocoder.geocode(location_text)
                                if lat is not None and lon is not None:
                                    # Use start date, end date, or current time
                                    if end_date and date_to and end_date > date_to:
                                        continue
                                    if start_date and date_from and start_date < date_from:
                                        continue
                                    
                                    # Create context
                                    context = f"Worked at {company_name}" if company_name else "Work location"
                                    if start_date:
                                        context += f" (from {start_date.strftime('%Y-%m-%d')}"
                                        if end_date:
                                            context += f" to {end_date.strftime('%Y-%m-%d')}"
                                        else:
                                            context += " to present"
                                        context += ")"
                                    
                                    # Use start date as timestamp, or now if not available
                                    timestamp = start_date or datetime.now()
                                    
                                    locations.append(
                                        LocationPoint(
                                            latitude=lat,
                                            longitude=lon,
                                            timestamp=timestamp,
                                            source="LinkedIn Position",
                                            context=f"{context} - {location_text}"
                                        )
                                    )
            except Exception as e:
                print(f"Error processing LinkedIn positions: {e}")
        
        # 3. Education history with locations
        education_files = glob.glob(os.path.join(data_dir, "**/Education.json"), recursive=True)
        for file_path in education_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    education_data = json.load(f)
                
                if isinstance(education_data, list):
                    for education in education_data:
                        if isinstance(education, dict):
                            location_text = None
                            start_date = None
                            end_date = None
                            school_name = None
                            
                            # Get school name
                            if "schoolName" in education:
                                school_name = education["schoolName"]
                            
                            # Try to extract location from school name or explicit location field
                            if "locationName" in education and education["locationName"]:
                                location_text = education["locationName"]
                            elif school_name:
                                # Some school names contain location info like "University of California, Berkeley"
                                location_match = re.search(r'(?:University|College) of [^,]+, ([^,]+)', school_name)
                                if location_match:
                                    location_text = location_match.group(1)
                            
                            # Get date info
                            if "startDate" in education and education["startDate"]:
                                start_data = education["startDate"]
                                try:
                                    if isinstance(start_data, dict) and "year" in start_data:
                                        year = start_data["year"]
                                        start_date = datetime(year, 1, 1)
                                except Exception:
                                    pass
                            
                            if "endDate" in education and education["endDate"]:
                                end_data = education["endDate"]
                                try:
                                    if isinstance(end_data, dict) and "year" in end_data:
                                        year = end_data["year"]
                                        end_date = datetime(year, 12, 31)
                                except Exception:
                                    pass
                            
                            # Only process if we have a location and it can be geocoded
                            if location_text and attempt_geocoding:
                                lat, lon = self.geocoder.geocode(location_text)
                                if lat is not None and lon is not None:
                                    # Use start date, end date, or current time
                                    if end_date and date_to and end_date > date_to:
                                        continue
                                    if start_date and date_from and start_date < date_from:
                                        continue
                                    
                                    # Create context
                                    context = f"Studied at {school_name}" if school_name else "Education"
                                    if start_date:
                                        context += f" ({start_date.year}"
                                        if end_date:
                                            context += f"-{end_date.year}"
                                        context += ")"
                                    
                                    # Use start date as timestamp, or now if not available
                                    timestamp = start_date or datetime.now()
                                    
                                    locations.append(
                                        LocationPoint(
                                            latitude=lat,
                                            longitude=lon,
                                            timestamp=timestamp,
                                            source="LinkedIn Education",
                                            context=f"{context} - {location_text}"
                                        )
                                    )
            except Exception as e:
                print(f"Error processing LinkedIn education: {e}")
        
        return locations
