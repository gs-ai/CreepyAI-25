"""
EXIF Data Extraction Plugin for CreepyAI
"""
import os
import logging
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

logger = logging.getLogger(__name__)

def get_exif_data(image):
    """Extract all EXIF data from an image"""
    exif_data = {}
    try:
        img = Image.open(image)
        if hasattr(img, '_getexif'):
            exif_info = img._getexif()
            if exif_info:
                for tag, value in exif_info.items():
                    decoded = TAGS.get(tag, tag)
                    if decoded == "GPSInfo":
                        gps_data = {}
                        for t in value:
                            sub_decoded = GPSTAGS.get(t, t)
                            gps_data[sub_decoded] = value[t]
                        exif_data[decoded] = gps_data
                    else:
                        exif_data[decoded] = value
    except Exception as e:
        logger.error(f"Error getting EXIF data: {e}")
    return exif_data

def get_lat_lon(exif_data):
    """Extract latitude and longitude from EXIF data if available"""
    lat = None
    lon = None
    
    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]
        
        gps_latitude = gps_info.get("GPSLatitude")
        gps_latitude_ref = gps_info.get("GPSLatitudeRef")
        gps_longitude = gps_info.get("GPSLongitude")
        gps_longitude_ref = gps_info.get("GPSLongitudeRef")
        
        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            # Convert from DMS format to decimal degrees
            lat = convert_to_degrees(gps_latitude)
            if gps_latitude_ref != "N":
                lat = -lat
                
            lon = convert_to_degrees(gps_longitude)
            if gps_longitude_ref != "E":
                lon = -lon
                
    return lat, lon

def convert_to_degrees(value):
    """Convert EXIF GPS value to decimal degrees"""
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)

class Plugin:
    """EXIF data extraction plugin"""
    
    def __init__(self):
        self.name = "EXIF Extractor"
        self.description = "Extract location data from image EXIF metadata"
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
        
    def run(self, image_paths=None):
        """
        Extract location data from images
        
        Args:
            image_paths (list): List of image file paths to process
            
        Returns:
            list: List of location dictionaries with lat, lon, and metadata
        """
        if not image_paths:
            # No paths provided, return empty result
            return []
            
        results = []
        
        for path in image_paths:
            if not os.path.exists(path):
                logger.warning(f"Image file not found: {path}")
                continue
                
            try:
                exif_data = get_exif_data(path)
                lat, lon = get_lat_lon(exif_data)
                
                if lat is not None and lon is not None:
                    # Create a location object with EXIF data
                    location = {
                        "name": os.path.basename(path),
                        "lat": lat,
                        "lon": lon,
                        "type": "photo",
                        "source": "EXIF",
                        "path": path,
                        "metadata": exif_data
                    }
                    results.append(location)
                    logger.info(f"Extracted location from {path}: {lat}, {lon}")
                else:
                    logger.info(f"No GPS data found in image: {path}")
            except Exception as e:
                logger.error(f"Error processing image {path}: {e}")
                
        return results
    
    def configure(self):
        """Configure plugin settings"""
        # This plugin doesn't have settings to configure
        return True
