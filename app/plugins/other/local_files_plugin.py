"""
Local Files Plugin for CreepyAI
Extracts location data from local files (images, videos, etc.)
"""
import os
import logging
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

logger = logging.getLogger(__name__)

def get_exif_data(image_path):
    """Extract EXIF data from an image file"""
    exif_data = {}
    try:
        with Image.open(image_path) as img:
            if hasattr(img, '_getexif') and img._getexif():
                for tag, value in img._getexif().items():
                    tag_name = TAGS.get(tag, tag)
                    exif_data[tag_name] = value
    except Exception as e:
        logger.error(f"Error getting EXIF data: {e}")
    return exif_data

def get_gps_info(exif_data):
    """Extract GPS information from EXIF data"""
    gps_info = {}
    if 'GPSInfo' in exif_data:
        for key, value in exif_data['GPSInfo'].items():
            tag_name = GPSTAGS.get(key, key)
            gps_info[tag_name] = value
    return gps_info

def convert_to_degrees(value):
    """Convert GPS coordinates to degrees"""
    if value is None:
        return None
        
    degrees = value[0]
    minutes = value[1] / 60.0
    seconds = value[2] / 3600.0
    return degrees + minutes + seconds

class Plugin:
    """Local files plugin for CreepyAI"""
    
    def __init__(self):
        self.name = "Local Files Plugin"
        self.description = "Extract location data from local files"
        self.version = "1.0.0"
        self.author = "CreepyAI Team"
        
    def get_info(self):
        """Return plugin information"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author
        }
        
    def scan_directory(self, directory, recursive=True):
        """Scan a directory for image files with location data"""
        results = []
        
        if not os.path.exists(directory) or not os.path.isdir(directory):
            logger.error(f"Directory not found: {directory}")
            return results
            
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff')):
                    file_path = os.path.join(root, file)
                    try:
                        exif_data = get_exif_data(file_path)
                        gps_info = get_gps_info(exif_data)
                        
                        if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
                            lat = convert_to_degrees(gps_info['GPSLatitude'])
                            lon = convert_to_degrees(gps_info['GPSLongitude'])
                            
                            # Apply N/S and E/W reference
                            if 'GPSLatitudeRef' in gps_info and gps_info['GPSLatitudeRef'] == 'S':
                                lat = -lat
                            if 'GPSLongitudeRef' in gps_info and gps_info['GPSLongitudeRef'] == 'W':
                                lon = -lon
                                
                            results.append({
                                'name': file,
                                'path': file_path,
                                'lat': lat,
                                'lon': lon,
                                'type': 'image',
                                'metadata': {
                                    'exif': exif_data
                                }
                            })
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {e}")
                        
            if not recursive:
                break
                
        return results
        
    def run(self, directory=None, recursive=True):
        """Run the plugin to scan the specified directory"""
        if not directory:
            logger.error("No directory specified")
            return []
            
        return self.scan_directory(directory, recursive)
