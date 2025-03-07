import os
import json
import glob
import csv
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import zipfile
from plugins.base_plugin import BasePlugin, LocationPoint
from plugins.geocoding_helper import GeocodingHelper

class YelpPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="Yelp",
            description="Extract location data from Yelp data exports without API"
        )
        self.geocoder = GeocodingHelper()
    
    def is_configured(self):
        # Check if the plugin is properly configured
        return True, "YelpPlugin is configured"
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "data_directory",
                "display_name": "Yelp Data Directory",
                "type": "directory",
                "default": "",
                "required": True,
                "description": "Directory containing your Yelp data export or saved reviews/bookmarks"
            },
            {
                "name": "attempt_geocoding",
                "display_name": "Attempt Geocoding",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Try to convert business addresses to coordinates"
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
                temp_dir = os.path.join(self.data_dir, "temp_yelp_extract")
                os.makedirs(temp_dir, exist_ok=True)
                zip_ref.extractall(temp_dir)
                data_dir = temp_dir
                
        # Process JSON files (Yelp user data exports)
        json_locations = self._process_json_files(data_dir, target, attempt_geocoding, date_from, date_to)
        locations.extend(json_locations)
        
        # Process CSV files (saved business lists, reviews)
        csv_locations = self._process_csv_files(data_dir, target, attempt_geocoding, date_from, date_to)
        locations.extend(csv_locations)
        
        # Process bookmarks HTML files (saved from Yelp bookmarks page)
        html_locations = self._process_html_files(data_dir, target, attempt_geocoding, date_from, date_to)
        locations.extend(html_locations)
        
        return locations
    
    def _process_json_files(self, data_dir: str, target: str, attempt_geocoding: bool, 
                           date_from: Optional[datetime], date_to: Optional[datetime]) -> List[LocationPoint]:
        """Process JSON files containing Yelp data."""
        locations = []
        
        json_files = []
        for pattern in ["**/reviews.json", "**/bookmarks.json", "**/user_data.json", "*.json"]:
            json_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8', errors='ignore') as f:
                    data = json.load(f)
                    
                # Format 1: Direct list of reviews/bookmarks
                if isinstance(data, list):
                    for item in data:
                        if not isinstance(item, dict):
                            continue
                            
                        # Process business info
                        business = item.get('business')
                        if business and isinstance(business, dict):
                            loc = self._extract_business_location(business, item, attempt_geocoding, date_from, date_to)
                            if loc:
                                locations.append(loc)
                
                # Format 2: Reviews under a key
                elif isinstance(data, dict):
                    # Try various possible keys for reviews/bookmarks
                    for key in ['reviews', 'bookmarks', 'businesses', 'user_reviews']:
                        if key in data and isinstance(data[key], list):
                            for item in data[key]:
                                if not isinstance(item, dict):
                                    continue
                                    
                                # Process business info
                                business = item.get('business')
                                if business and isinstance(business, dict):
                                    loc = self._extract_business_location(business, item, attempt_geocoding, date_from, date_to)
                                    if loc:
                                        locations.append(loc)
            except Exception as e:
                print(f"Error processing JSON file {json_file}: {e}")
        
        return locations
    
    def _process_csv_files(self, data_dir: str, target: str, attempt_geocoding: bool,
                          date_from: Optional[datetime], date_to: Optional[datetime]) -> List[LocationPoint]:
        """Process CSV files containing Yelp data."""
        locations = []
        
        csv_files = []
        for pattern in ["*.csv"]:
            csv_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.reader(f)
                    headers = next(reader, None)
                    
                    # Skip if no headers
                    if not headers:
                        continue
                    
                    # Identify columns that might contain business data
                    business_name_col = None
                    address_col = None
                    lat_col = None
                    lon_col = None
                    date_col = None
                    
                    for i, header in enumerate(headers):
                        header_lower = header.lower()
                        if any(name in header_lower for name in ['business', 'name', 'restaurant', 'store']):
                            business_name_col = i
                        elif any(addr in header_lower for addr in ['address', 'location']):
                            address_col = i
                        elif 'latitude' in header_lower or header_lower == 'lat':
                            lat_col = i
                        elif 'longitude' in header_lower or header_lower == 'lon' or header_lower == 'lng':
                            lon_col = i
                        elif any(date in header_lower for date in ['date', 'visited', 'timestamp']):
                            date_col = i
                    
                    # Skip if we can't identify necessary columns
                    if business_name_col is None:
                        continue
                    
                    for row in reader:
                        try:
                            if len(row) <= business_name_col:
                                continue
                                
                            business_name = row[business_name_col]
                            if not business_name:
                                continue
                            
                            # Get coordinates if available
                            lat = None
                            lon = None
                            if lat_col is not None and lon_col is not None and len(row) > max(lat_col, lon_col):
                                try:
                                    lat = float(row[lat_col]) if row[lat_col] else None
                                    lon = float(row[lon_col]) if row[lon_col] else None
                                except ValueError:
                                    lat = None
                                    lon = None
                            
                            # Get address if available
                            address = None
                            if address_col is not None and len(row) > address_col:
                                address = row[address_col]
                            
                            # Try geocoding if we don't have coordinates but have an address
                            if (lat is None or lon is None) and address and attempt_geocoding:
                                lat, lon = self.geocoder.geocode(f"{business_name}, {address}")
                            
                            # If we still don't have coordinates but have a business name, try geocoding just the name
                            if (lat is None or lon is None) and attempt_geocoding:
                                lat, lon = self.geocoder.geocode(business_name)
                            
                            # Skip if we couldn't determine coordinates
                            if lat is None or lon is None:
                                continue
                            
                            # Get date if available
                            timestamp = datetime.now()
                            if date_col is not None and len(row) > date_col and row[date_col]:
                                try:
                                    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]:
                                        try:
                                            timestamp = datetime.strptime(row[date_col], fmt)
                                            break
                                        except ValueError:
                                            continue
                                except Exception:
                                    pass
                            
                            # Apply date filters
                            if date_from and timestamp < date_from:
                                continue
                            if date_to and timestamp > date_to:
                                continue
                            
                            # Create context
                            context = business_name
                            if address:
                                context += f" at {address}"
                            
                            locations.append(
                                LocationPoint(
                                    latitude=lat,
                                    longitude=lon,
                                    timestamp=timestamp,
                                    source="Yelp Business",
                                    context=context
                                )
                            )
                        except Exception as e:
                            print(f"Error processing CSV row: {e}")
            except Exception as e:
                print(f"Error processing CSV file {csv_file}: {e}")
        
        return locations
    
    def _process_html_files(self, data_dir: str, target: str, attempt_geocoding: bool,
                           date_from: Optional[datetime], date_to: Optional[datetime]) -> List[LocationPoint]:
        """Process HTML files containing Yelp bookmarks or reviews."""
        locations = []
        
        html_files = []
        for pattern in ["*.html", "*.htm"]:
            html_files.extend(glob.glob(os.path.join(data_dir, pattern), recursive=True))
        
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Look for Yelp business name patterns
                business_matches = re.finditer(r'<[^>]*class="[^"]*business-name[^"]*"[^>]*>(.*?)</a>', content, re.IGNORECASE)
                
                for match in business_matches:
                    try:
                        business_name = re.sub(r'<[^>]*>', '', match.group(1)).strip()
                        if not business_name:
                            continue
                        
                        # Look for address in nearby HTML
                        address = None
                        context_around = content[max(0, match.start() - 200):min(len(content), match.end() + 200)]
                        address_match = re.search(r'<[^>]*class="[^"]*address[^"]*"[^>]*>(.*?)</[a-z]+>', context_around, re.IGNORECASE)
                        if address_match:
                            address = re.sub(r'<[^>]*>', '', address_match.group(1)).strip()
                        
                        # Look for date in nearby HTML
                        timestamp = datetime.now()
                        date_match = re.search(r'<[^>]*class="[^"]*date[^"]*"[^>]*>(.*?)</[a-z]+>', context_around, re.IGNORECASE)
                        if date_match:
                            date_text = re.sub(r'<[^>]*>', '', date_match.group(1)).strip()
                            # Try to parse common date formats
                            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y"]:
                                try:
                                    timestamp = datetime.strptime(date_text, fmt)
                                    break
                                except ValueError:
                                    continue
                        
                        # Apply date filters
                        if date_from and timestamp < date_from:
                            continue
                        if date_to and timestamp > date_to:
                            continue
                        
                        # Try geocoding the business
                        lat = None
                        lon = None
                        if attempt_geocoding:
                            if address:
                                lat, lon = self.geocoder.geocode(f"{business_name}, {address}")
                            
                            # If we still don't have coordinates, try just the business name
                            if lat is None or lon is None:
                                lat, lon = self.geocoder.geocode(business_name)
                        
                        if lat is not None and lon is not None:
                            context = business_name
                            if address:
                                context += f" at {address}"
                            
                            locations.append(
                                LocationPoint(
                                    latitude=lat,
                                    longitude=lon,
                                    timestamp=timestamp,
                                    source="Yelp HTML Export",
                                    context=context
                                )
                            )
                    except Exception as e:
                        print(f"Error processing business match: {e}")
            except Exception as e:
                print(f"Error processing HTML file {html_file}: {e}")
                
        return locations
    
    def _extract_business_location(self, business: Dict, item: Dict, attempt_geocoding: bool,
                                 date_from: Optional[datetime], date_to: Optional[datetime]) -> Optional[LocationPoint]:
        """Extract location data from a business object."""
        try:
            # Get business name
            business_name = business.get('name', 'Unknown Business')
            
            # Get coordinates if available directly
            lat = None
            lon = None
            
            # Check if coordinates are available in business object
            coordinates = business.get('coordinates')
            if coordinates and isinstance(coordinates, dict):
                lat = coordinates.get('latitude')
                lon = coordinates.get('longitude')
                
            # Extract address components
            address = None
            location = business.get('location')
            if location and isinstance(location, dict):
                address_parts = location.get('display_address', [])
                if address_parts:
                    address = ", ".join(address_parts)
            
            # Try geocoding if we don't have coordinates but have an address
            if (lat is None or lon is None) and address and attempt_geocoding:
                lat, lon = self.geocoder.geocode(f"{business_name}, {address}")
            
            # If we still don't have coordinates, try just the business name
            if (lat is None or lon is None) and attempt_geocoding:
                lat, lon = self.geocoder.geocode(business_name)
            
            # Skip if we couldn't determine coordinates
            if lat is None or lon is None:
                return None
            
            # Get timestamp from item (review date or visit date)
            timestamp = datetime.now()
            
            # Try to extract date from different possible fields
            for date_field in ['time_created', 'created_at', 'date', 'visit_date']:
                if date_field in item and item[date_field]:
                    date_value = item[date_field]
                    if isinstance(date_value, str):
                        # Try different date formats
                        for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y"]:
                            try:
                                timestamp = datetime.strptime(date_value, fmt)
                                break
                            except ValueError:
                                continue
                    break
            
            # Apply date filters
            if date_from and timestamp < date_from:
                return None
            if date_to and timestamp > date_to:
                return None
            
            # Create context string
            context = business_name
            
            # Add address if available
            if address:
                context += f" at {address}"
            
            # Add rating if available
            if 'rating' in item:
                rating = item['rating']
                stars = "★" * int(rating) + "☆" * (5 - int(rating))
                context += f" | Rating: {stars} ({rating}/5)"
            
            # Create location point
            return LocationPoint(
                latitude=float(lat),
                longitude=float(lon),
                timestamp=timestamp,
                source="Yelp Business",
                context=context
            )
        
        except Exception as e:
            print(f"Error extracting business location: {e}")
            return None
