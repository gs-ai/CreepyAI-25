import logging
import requests
import time
import random
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pathlib import Path

logger = logging.getLogger(__name__)

class WebScrapingUtility:
    """Utility class for web scraping operations without using APIs."""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        # Default configuration if no config manager provided
        self.timeout = 30
        self.retry_count = 3
        self.delay = 5
        self.respect_robots = True
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.stealth_mode = False
        
        # Load configuration if available
        if self.config_manager:
            self.timeout = self.config_manager.get_scraping_setting("timeout", self.timeout)
            self.retry_count = self.config_manager.get_scraping_setting("retry_count", self.retry_count)
            self.delay = self.config_manager.get_scraping_setting("delay_between_requests", self.delay)
            self.respect_robots = self.config_manager.get_scraping_setting("respect_robots_txt", self.respect_robots)
            self.user_agent = self.config_manager.get_setting("browser_user_agent", self.user_agent)
            self.stealth_mode = self.config_manager.get_scraping_setting("use_stealth_mode", self.stealth_mode)
        
        # Initialize cache for robots.txt
        self.robots_cache = {}
        
        # Initialize session
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
    
    def fetch_page(self, url):
        """Fetch a web page with retry logic."""
        if not url:
            logger.error("Invalid URL provided")
            return None
        
        # Check robots.txt compliance if enabled
        if self.respect_robots and not self._is_allowed_by_robots(url):
            logger.warning(f"URL {url} not allowed by robots.txt. Skipping.")
            return None
            
        for attempt in range(self.retry_count):
            try:
                # Add jitter to delay for stealth mode
                if attempt > 0 and self.stealth_mode:
                    jitter = random.uniform(0.5, 2.0)
                    time.sleep(self.delay * jitter)
                elif attempt > 0:
                    time.sleep(self.delay)
                
                response = self.session.get(url, timeout=self.timeout)
                
                # Check if successful
                if response.status_code == 200:
                    return response.text
                else:
                    logger.warning(f"Failed to fetch {url}, status code: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error fetching {url}: {str(e)}")
                
        logger.error(f"Failed to fetch {url} after {self.retry_count} attempts")
        return None
    
    def extract_locations(self, html_content, extraction_patterns=None):
        """
        Extract location information from HTML content using patterns.
        This is a simplified example - real implementation would need
        platform-specific extraction logic.
        """
        if not html_content:
            return []
        
        locations = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Default patterns for location extraction (simplified example)
        default_patterns = {
            'coordinates': r'[-+]?\d{1,2}\.\d+,\s*[-+]?\d{1,3}\.\d+',  # Basic lat,long pattern
            'place_tags': ['location', 'place', 'geo', 'coordinates']
        }
        
        patterns = extraction_patterns or default_patterns
        
        # Extract using regex pattern for coordinates
        if 'coordinates' in patterns:
            coord_matches = re.finditer(patterns['coordinates'], html_content)
            for match in coord_matches:
                try:
                    lat_lng = match.group(0).split(',')
                    lat = float(lat_lng[0].strip())
                    lng = float(lat_lng[1].strip())
                    
                    # Basic validation
                    if -90 <= lat <= 90 and -180 <= lng <= 180:
                        locations.append({
                            'latitude': lat,
                            'longitude': lng,
                            'source': 'regex_pattern',
                            'accuracy': 'medium'
                        })
                except Exception as e:
                    logger.debug(f"Failed to parse coordinates: {str(e)}")
        
        # Extract location information from metadata
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            try:
                # Look for OpenGraph location metadata
                if tag.get('property') in ['og:latitude', 'place:location:latitude']:
                    lat = float(tag.get('content', 0))
                    # Find corresponding longitude
                    lng_tag = soup.find('meta', property=tag.get('property').replace('latitude', 'longitude'))
                    if lng_tag:
                        lng = float(lng_tag.get('content', 0))
                        locations.append({
                            'latitude': lat,
                            'longitude': lng,
                            'source': 'meta_tags',
                            'accuracy': 'high'
                        })
            except Exception as e:
                logger.debug(f"Failed to parse meta tags: {str(e)}")
        
        return locations
    
    def parse_local_file(self, file_path):
        """Parse local files for location data"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
                
            # Handle different file types
            if file_path.suffix.lower() in ['.html', '.htm']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return self.extract_locations(f.read())
            elif file_path.suffix.lower() in ['.json']:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return self._extract_locations_from_json(data)
            elif file_path.suffix.lower() in ['.kml', '.kmz', '.gpx']:
                return self._parse_geospatial_file(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_path.suffix}")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {str(e)}")
            return None
    
    def _extract_locations_from_json(self, data):
        """Extract location data from JSON objects"""
        locations = []
        
        def search_json(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    
                    # Look for common location keys
                    if key.lower() in ['location', 'geo', 'position', 'coordinates']:
                        if isinstance(value, dict):
                            lat = value.get('lat') or value.get('latitude')
                            lng = value.get('lng') or value.get('longitude') or value.get('long')
                            
                            if lat is not None and lng is not None:
                                try:
                                    locations.append({
                                        'latitude': float(lat),
                                        'longitude': float(lng),
                                        'source': f'json_field:{new_path}',
                                        'accuracy': 'high'
                                    })
                                except (ValueError, TypeError):
                                    pass
                        elif isinstance(value, list) and len(value) >= 2:
                            # Common format is [longitude, latitude] or [latitude, longitude]
                            try:
                                # Try both formats
                                if -90 <= float(value[0]) <= 90 and -180 <= float(value[1]) <= 180:
                                    locations.append({
                                        'latitude': float(value[0]),
                                        'longitude': float(value[1]),
                                        'source': f'json_field:{new_path}',
                                        'accuracy': 'medium'
                                    })
                                elif -90 <= float(value[1]) <= 90 and -180 <= float(value[0]) <= 180:
                                    locations.append({
                                        'latitude': float(value[1]),
                                        'longitude': float(value[0]),
                                        'source': f'json_field:{new_path}',
                                        'accuracy': 'medium'
                                    })
                            except (ValueError, TypeError):
                                pass
                    
                    # Recursive search
                    search_json(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{path}[{i}]"
                    search_json(item, new_path)
        
        search_json(data)
        return locations
    
    def _parse_geospatial_file(self, file_path):
        """Parse geospatial files like KML, KMZ, GPX"""
        try:
            # This is a simplified implementation
            # A real implementation would use libraries like fastkml, pykml, or gpxpy
            
            file_type = file_path.suffix.lower()
            locations = []
            
            if file_type == '.gpx':
                # Simple GPX parsing
                import xml.etree.ElementTree as ET
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                # Extract waypoints
                for wpt in root.findall('.//{*}wpt'):
                    try:
                        lat = float(wpt.get('lat'))
                        lon = float(wpt.get('lon'))
                        
                        name = None
                        name_elem = wpt.find('.//{*}name')
                        if name_elem is not None and name_elem.text:
                            name = name_elem.text.strip()
                            
                        locations.append({
                            'latitude': lat,
                            'longitude': lon,
                            'name': name,
                            'source': 'gpx_waypoint',
                            'accuracy': 'high'
                        })
                    except Exception as e:
                        logger.debug(f"Failed to parse GPX waypoint: {str(e)}")
                
                # Extract track points
                for trkpt in root.findall('.//{*}trkpt'):
                    try:
                        lat = float(trkpt.get('lat'))
                        lon = float(trkpt.get('lon'))
                        
                        time_elem = trkpt.find('.//{*}time')
                        time_str = time_elem.text if time_elem is not None else None
                        
                        locations.append({
                            'latitude': lat,
                            'longitude': lon,
                            'time': time_str,
                            'source': 'gpx_trackpoint',
                            'accuracy': 'high'
                        })
                    except Exception as e:
                        logger.debug(f"Failed to parse GPX trackpoint: {str(e)}")
                
            elif file_type == '.kml':
                # Simple KML parsing
                import xml.etree.ElementTree as ET
                
                # Parse KML
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                # Find namespace
                ns = ''
                if root.tag.startswith('{'):
                    ns = root.tag.split('}')[0] + '}'
                
                # Find all placemarks
                for placemark in root.findall(f'.//{ns}Placemark'):
                    name_elem = placemark.find(f'{ns}name')
                    name = name_elem.text if name_elem is not None else None
                    
                    # Get point coordinates
                    point = placemark.find(f'.//{ns}Point/{ns}coordinates')
                    if point is not None and point.text:
                        try:
                            coords = point.text.strip().split(',')
                            if len(coords) >= 2:
                                # KML format is lon,lat[,alt]
                                lon = float(coords[0])
                                lat = float(coords[1])
                                alt = float(coords[2]) if len(coords) > 2 else None
                                
                                locations.append({
                                    'latitude': lat,
                                    'longitude': lon,
                                    'altitude': alt,
                                    'name': name,
                                    'source': 'kml_placemark',
                                    'accuracy': 'high'
                                })
                        except Exception as e:
                            logger.debug(f"Failed to parse KML coordinates: {str(e)}")
            
            elif file_type == '.kmz':
                # KMZ is a zipped KML file
                import zipfile
                import tempfile
                
                with tempfile.TemporaryDirectory() as tmpdirname:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(tmpdirname)
                    
                    # Find the main KML file (usually doc.kml)
                    kml_files = list(Path(tmpdirname).glob('*.kml'))
                    if not kml_files:
                        logger.error("No KML file found in KMZ archive")
                        return []
                        
                    # Parse the first KML file found
                    kml_locations = self._parse_geospatial_file(kml_files[0])
                    locations.extend(kml_locations)
            
            return locations
                
        except Exception as e:
            logger.error(f"Error parsing geospatial file {file_path}: {str(e)}")
            return []
    
    def _is_allowed_by_robots(self, url):
        """Check if URL is allowed by robots.txt"""
        if not self.respect_robots:
            return True
            
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Check cache first
            if base_url in self.robots_cache:
                return self._check_path_against_robots(self.robots_cache[base_url], parsed_url.path)
                
            # Fetch robots.txt
            robots_url = f"{base_url}/robots.txt"
            try:
                response = requests.get(robots_url, timeout=self.timeout)
                if response.status_code == 200:
                    self.robots_cache[base_url] = response.text
                    return self._check_path_against_robots(response.text, parsed_url.path)
            except Exception:
                # If we can't fetch robots.txt, assume it's allowed
                pass
                
            # Default to allowed
            return True
            
        except Exception as e:
            logger.error(f"Error checking robots.txt: {str(e)}")
            return True
    
    def _check_path_against_robots(self, robots_txt, path):
        """Check if path is allowed by the robots.txt content"""
        # Simple robots.txt parser
        current_agent = None
        our_agent = "Mozilla"  # Simplified user agent matching
        
        for line in robots_txt.split('\n'):
            line = line.strip().lower()
            
            if not line or line.startswith('#'):
                continue
                
            parts = line.split(':', 1)
            if len(parts) != 2:
                continue
                
            directive, value = parts[0].strip(), parts[1].strip()
            
            if directive == 'user-agent':
                current_agent = value
            elif directive == 'disallow' and (current_agent == '*' or current_agent == our_agent):
                if path.startswith(value) and value:
                    return False
                    
        return True
