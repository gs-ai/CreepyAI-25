import logging
import os
from yapsy.IPlugin import IPlugin
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import re
from datetime import datetime
import hashlib

# Try to import EXIF library for photo analysis
try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logging.warning("PIL not available. Photo EXIF extraction will be limited.")

logger = logging.getLogger(__name__)

class LocalFilesPlugin(IPlugin):
    """
    Plugin to analyze local files for geolocation data.
    """
    
    def __init__(self):
        super(LocalFilesPlugin, self).__init__()
        self.name = "Local Files"
        self.description = "Analyzes local files for geolocation data"
        self.database = None
        self.config_manager = None
        self.supported_extensions = {
            'images': ['.jpg', '.jpeg', '.png', '.tiff', '.heic'],
            'geospatial': ['.kml', '.kmz', '.gpx', '.geojson'],
            'data': ['.json', '.csv', '.txt', '.html', '.htm']
        }
    
    def activate(self):
        """Initialize the plugin."""
        super(LocalFilesPlugin, self).activate()
        logger.info(f"Activating plugin: {self.name}")

    def deactivate(self):
        """Deactivate the plugin."""
        super(LocalFilesPlugin, self).deactivate()
        logger.info(f"Deactivating plugin: {self.name}")
    
    def set_database(self, database):
        """Set the database instance for the plugin."""
        self.database = database
    
    def set_config_manager(self, config_manager):
        """Set the configuration manager for the plugin."""
        self.config_manager = config_manager
    
    def is_configured(self):
        """Check if the plugin is configured properly."""
        if self.config_manager is None:
            logger.warning(f"{self.name} plugin is not configured: No config manager")
            return False
        
        # Check if the plugin is enabled
        enabled = self.config_manager.get_plugin_setting("local_files", "enabled", True)
        return enabled
    
    def search_locations(self, target, search_params=None):
        """
        Search for location data in local files.
        
        Args:
            target (dict): Target information
            search_params (dict): Parameters including:
                - directory: Directory to scan for files
                - file_paths: List of specific files to analyze
                - recursive: Whether to scan recursively
                - max_files: Maximum number of files to analyze
                
        Returns:
            list: List of found locations
        """
        if not self.is_configured():
            logger.warning("Local files plugin is not properly configured")
            return []
        
        locations = []
        
        # Get search parameters
        if not search_params:
            search_params = {}
        
        directory = search_params.get('directory')
        file_paths = search_params.get('file_paths', [])
        recursive = search_params.get('recursive', True)
        max_files = search_params.get('max_files', 1000)
        
        # Process specific files if provided
        if file_paths:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    locations.extend(self._analyze_file(file_path, target))
        
        # Process directory if provided
        if directory and os.path.isdir(directory):
            processed_files = 0
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if processed_files >= max_files:
                        break
                        
                    file_path = os.path.join(root, file)
                    locations.extend(self._analyze_file(file_path, target))
                    processed_files += 1
                
                if not recursive:
                    break  # Don't process subdirectories
                    
                if processed_files >= max_files:
                    break
        
        return locations
    
    def _analyze_file(self, file_path, target):
        """
        Analyze a file for location data.
        
        Args:
            file_path (str): Path to the file
            target (dict): Target information
            
        Returns:
            list: List of locations found
        """
        locations = []
        
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return []
                
            extension = file_path.suffix.lower()
                
            # Process based on file type
            if extension in self.supported_extensions['images']:
                # Process image files for EXIF data
                locations.extend(self._extract_exif_location(file_path))
                
            elif extension in self.supported_extensions['geospatial']:
                # Process geospatial files
                locations.extend(self._extract_geospatial_data(file_path))
                
            elif extension in self.supported_extensions['data']:
                # Process data files
                locations.extend(self._extract_data_file_locations(file_path))
            
            # Store the file as a source if we found locations and have a database
            if locations and self.database and hasattr(target, 'id'):
                self._store_file_as_source(file_path, target.id)
                
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            
        return locations
    
    def _extract_exif_location(self, file_path):
        """Extract location data from image EXIF."""
        locations = []
        
        if not HAS_PIL:
            logger.warning("PIL not available for extracting EXIF data")
            return locations
            
        try:
            with Image.open(file_path) as img:
                if not hasattr(img, '_getexif') or img._getexif() is None:
                    return locations
                    
                exif_data = {
                    TAGS.get(tag, tag): value
                    for tag, value in img._getexif().items()
                }
                
                if 'GPSInfo' not in exif_data:
                    return locations
                    
                gps_info = {
                    GPSTAGS.get(tag, tag): value
                    for tag, value in exif_data['GPSInfo'].items()
                }
                
                lat, lon = self._get_lat_lon(gps_info)
                if lat is not None and lon is not None:
                    date_taken = self._extract_date_taken(exif_data)
                    filename = file_path.name
                    
                    location = {
                        'plugin': self.name,
                        'lat': lat,
                        'lon': lon,
                        'date': date_taken,
                        'context': f"Image file: {filename}",
                        'infowindow': f"<div><strong>Image: {filename}</strong><br/>Date: {date_taken}</div>",
                        'shortName': filename
                    }
                    
                    locations.append(location)
                    
        except Exception as e:
            logger.error(f"Error extracting EXIF data from {file_path}: {str(e)}")
            
        return locations
    
    def _get_lat_lon(self, gps_info):
        """Extract latitude and longitude from GPS info."""
        lat = None
        lon = None
        
        try:
            if "GPSLatitude" in gps_info and "GPSLatitudeRef" in gps_info and "GPSLongitude" in gps_info and "GPSLongitudeRef" in gps_info:
                lat_d, lat_m, lat_s = gps_info["GPSLatitude"]
                lat_ref = gps_info["GPSLatitudeRef"]
                latitude = float(lat_d) + (float(lat_m) / 60.0) + (float(lat_s) / 3600.0)
                if lat_ref != "N":
                    latitude = -latitude
                
                lon_d, lon_m, lon_s = gps_info["GPSLongitude"]
                lon_ref = gps_info["GPSLongitudeRef"]
                longitude = float(lon_d) + (float(lon_m) / 60.0) + (float(lon_s) / 3600.0)
                if lon_ref != "E":
                    longitude = -longitude
                    
                lat = latitude
                lon = longitude
                
        except Exception as e:
            logger.error(f"Error converting GPS coordinates: {str(e)}")
            
        return (lat, lon)
    
    def _extract_date_taken(self, exif_data):
        """Extract the date the image was taken from EXIF data."""
        if "DateTimeOriginal" in exif_data:
            try:
                date_str = exif_data["DateTimeOriginal"]
                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
            except Exception as e:
                logger.error(f"Error parsing date: {str(e)}")
        return datetime.now()
    
    def _extract_geospatial_data(self, file_path):
        """Extract location data from geospatial files."""
        locations = []
        
        try:
            if file_path.suffix.lower() == '.kml':
                locations.extend(self._extract_kml_locations(file_path))
            elif file_path.suffix.lower() == '.gpx':
                locations.extend(self._extract_gpx_locations(file_path))
            elif file_path.suffix.lower() == '.geojson':
                locations.extend(self._extract_geojson_locations(file_path))
                
        except Exception as e:
            logger.error(f"Error extracting geospatial data from {file_path}: {str(e)}")
            
        return locations
    
    def _extract_kml_locations(self, file_path):
        """Extract locations from KML files."""
        locations = []
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for placemark in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
                name = placemark.find('{http://www.opengis.net/kml/2.2}name').text
                coordinates = placemark.find('.//{http://www.opengis.net/kml/2.2}coordinates').text.strip()
                lon, lat, _ = map(float, coordinates.split(','))
                
                location = {
                    'plugin': self.name,
                    'lat': lat,
                    'lon': lon,
                    'context': f"KML file: {file_path.name}",
                    'infowindow': f"<div><strong>Placemark: {name}</strong><br/>Coordinates: {lat}, {lon}</div>",
                    'shortName': name
                }
                
                locations.append(location)
                
        except Exception as e:
            logger.error(f"Error extracting KML locations from {file_path}: {str(e)}")
            
        return locations
    
    def _extract_gpx_locations(self, file_path):
        """Extract locations from GPX files."""
        locations = []
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for trkpt in root.findall('.//{http://www.topografix.com/GPX/1/1}trkpt'):
                lat = float(trkpt.get('lat'))
                lon = float(trkpt.get('lon'))
                name = trkpt.find('{http://www.topografix.com/GPX/1/1}name')
                name = name.text if name is not None else "Track Point"
                
                location = {
                    'plugin': self.name,
                    'lat': lat,
                    'lon': lon,
                    'context': f"GPX file: {file_path.name}",
                    'infowindow': f"<div><strong>Track Point: {name}</strong><br/>Coordinates: {lat}, {lon}</div>",
                    'shortName': name
                }
                
                locations.append(location)
                
        except Exception as e:
            logger.error(f"Error extracting GPX locations from {file_path}: {str(e)}")
            
        return locations
    
    def _extract_geojson_locations(self, file_path):
        """Extract locations from GeoJSON files."""
        locations = []
        
        try:
            with open(file_path, 'r') as f:
                geojson_data = json.load(f)
                
                for feature in geojson_data.get('features', []):
                    if feature.get('geometry', {}).get('type') == 'Point':
                        coordinates = feature['geometry']['coordinates']
                        lon, lat = coordinates[0], coordinates[1]
                        name = feature.get('properties', {}).get('name', 'GeoJSON Point')
                        
                        location = {
                            'plugin': self.name,
                            'lat': lat,
                            'lon': lon,
                            'context': f"GeoJSON file: {file_path.name}",
                            'infowindow': f"<div><strong>GeoJSON Point: {name}</strong><br/>Coordinates: {lat}, {lon}</div>",
                            'shortName': name
                        }
                        
                        locations.append(location)
                        
        except Exception as e:
            logger.error(f"Error extracting GeoJSON locations from {file_path}: {str(e)}")
            
        return locations
    
    def _extract_data_file_locations(self, file_path):
        """Extract locations from data files."""
        locations = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Extract coordinates from the content using regex
                pattern = re.compile(r'(-?\d+\.\d+),\s*(-?\d+\.\d+)')
                matches = pattern.findall(content)
                
                for match in matches:
                    lat, lon = map(float, match)
                    location = {
                        'plugin': self.name,
                        'lat': lat,
                        'lon': lon,
                        'context': f"Data file: {file_path.name}",
                        'infowindow': f"<div><strong>Coordinates: {lat}, {lon}</strong></div>",
                        'shortName': f"{lat}, {lon}"
                    }
                    
                    locations.append(location)
                    
        except Exception as e:
            logger.error(f"Error extracting data file locations from {file_path}: {str(e)}")
            
        return locations
    
    def _store_file_as_source(self, file_path, target_id):
        """Store the file as a source in the database."""
        try:
            file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
            source = {
                'target_id': target_id,
                'file_path': str(file_path),
                'file_hash': file_hash,
                'plugin': self.name
            }
            self.database.insert_source(source)
            
        except Exception as e:
            logger.error(f"Error storing file as source: {str(e)}")
