import os
import glob
from typing import List, Dict, Any, Optional
from datetime import datetime
import piexif
from PIL import Image, ExifTags
from plugins.base_plugin import BasePlugin, LocationPoint

class LocalFilesPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="Local Files",
            description="Extract location data from local image files"
        )
    
    def is_configured(self):
        # Check if the plugin is properly configured
        return True, "LocalFilesPlugin is configured"
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "photos_directory",
                "display_name": "Photos Directory",
                "type": "directory",
                "default": "",
                "required": True,
                "description": "Directory containing your photos with geolocation data"
            },
            {
                "name": "recursive",
                "display_name": "Search Recursively",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Search for photos in subdirectories"
            },
            {
                "name": "file_types",
                "display_name": "File Types",
                "type": "string",
                "default": "jpg,jpeg,png,tiff",
                "required": False,
                "description": "Comma-separated list of file extensions to search"
            }
        ]
    
    def _convert_to_degrees(self, value):
        """Convert the GPS coordinates stored in the EXIF to degrees in float format."""
        degrees = float(value[0])
        minutes = float(value[1]) / 60.0
        seconds = float(value[2]) / 3600.0
        
        return degrees + minutes + seconds
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None, 
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
        locations = []
        photos_dir = self.config.get("photos_directory", "")
        recursive = self.config.get("recursive", True)
        
        if not photos_dir or not os.path.exists(photos_dir):
            return locations
            
        # Build file types pattern
        file_types = self.config.get("file_types", "jpg,jpeg,png,tiff")
        file_patterns = []
        for ext in file_types.split(","):
            ext = ext.strip().lower()
            if ext:
                file_patterns.append(f"*.{ext}")
                file_patterns.append(f"*.{ext.upper()}")
        
        # Find all matching files
        image_files = []
        for pattern in file_patterns:
            if recursive:
                image_files.extend(glob.glob(os.path.join(photos_dir, "**", pattern), recursive=True))
            else:
                image_files.extend(glob.glob(os.path.join(photos_dir, pattern)))
        
        # Process each image
        for image_file in image_files:
            try:
                with Image.open(image_file) as img:
                    exif_data = None
                    timestamp = None
                    
                    # Get EXIF data if available
                    if hasattr(img, "_getexif") and img._getexif():
                        exif_data = {
                            ExifTags.TAGS[k]: v
                            for k, v in img._getexif().items()
                            if k in ExifTags.TAGS
                        }
                    
                    # Try to get timestamp from EXIF
                    if exif_data and "DateTimeOriginal" in exif_data:
                        try:
                            timestamp = datetime.strptime(
                                exif_data["DateTimeOriginal"], "%Y:%m:%d %H:%M:%S"
                            )
                        except ValueError:
                            pass
                    
                    if not timestamp and os.path.exists(image_file):
                        # Use file modification time as fallback
                        timestamp = datetime.fromtimestamp(os.path.getmtime(image_file))
                    
                    # Filter by date if needed
                    if date_from and timestamp and timestamp < date_from:
                        continue
                    if date_to and timestamp and timestamp > date_to:
                        continue
                    
                    # Extract GPS info
                    gps_info = {}
                    if exif_data and "GPSInfo" in exif_data:
                        for key, val in exif_data["GPSInfo"].items():
                            if key in ExifTags.GPSTAGS:
                                gps_info[ExifTags.GPSTAGS[key]] = val
                    
                    # Calculate lat/lon if available
                    if gps_info and "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
                        latitude = self._convert_to_degrees(gps_info["GPSLatitude"])
                        longitude = self._convert_to_degrees(gps_info["GPSLongitude"])
                        
                        # Adjust for N/S/E/W reference
                        if "GPSLatitudeRef" in gps_info and gps_info["GPSLatitudeRef"] == "S":
                            latitude = -latitude
                        if "GPSLongitudeRef" in gps_info and gps_info["GPSLongitudeRef"] == "W":
                            longitude = -longitude
                        
                        locations.append(
                            LocationPoint(
                                latitude=latitude,
                                longitude=longitude,
                                timestamp=timestamp or datetime.now(),
                                source="Local Image",
                                context=f"File: {os.path.basename(image_file)}"
                            )
                        )
            except Exception as e:
                print(f"Error processing image {image_file}: {e}")
                
        return locations
