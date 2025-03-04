#!/usr/bin/python
# -*- coding: utf-8 -*-
from models.InputPlugin import InputPlugin
import os
import datetime
import json
import logging
import glob
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class LocalFilesPlugin(InputPlugin):
    name = "local_files"
    
    def __init__(self):
        InputPlugin.__init__(self)
        self.description = "Extract locations from local image files with EXIF data."
        self.searchOffline = True
        self.hasWizard = False
        
    def activate(self):
        pass
    
    def deactivate(self):
        pass
    
    def isConfigured(self):
        return (True, "")
        
    def get_exif_data(self, image):
        """Returns a dictionary from the exif data of an PIL Image item"""
        exif_data = {}
        try:
            info = image._getexif()
            if info:
                for tag, value in info.items():
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
            logger.error(f"Error extracting EXIF data: {e}")
        return exif_data
        
    def get_lat_lon(self, exif_data):
        """Returns the latitude and longitude, if available, from the provided exif_data"""
        lat = None
        lon = None
        
        if "GPSInfo" in exif_data:        
            gps_info = exif_data["GPSInfo"]
            
            # Check for latitude and longitude
            if "GPSLatitude" in gps_info and "GPSLatitudeRef" in gps_info and "GPSLongitude" in gps_info and "GPSLongitudeRef" in gps_info:
                try:
                    # Convert the GPS coordinates from degrees, minutes, seconds to decimal
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
                    logger.error(f"Error converting GPS coordinates: {e}")
                
        return (lat, lon)
    
    def extract_date_taken(self, exif_data):
        """Extract the date the image was taken from EXIF data"""
        if "DateTimeOriginal" in exif_data:
            try:
                date_str = exif_data["DateTimeOriginal"]
                return datetime.datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
            except Exception as e:
                logger.error(f"Error parsing date: {e}")
        # If date extraction fails, use current time
        return datetime.datetime.now()
        
    def searchForTargets(self, search_term):
        """Search for directories containing images"""
        try:
            # Search in the provided path for directories
            if os.path.exists(search_term) and os.path.isdir(search_term):
                return [{
                    'targetUsername': os.path.basename(search_term),
                    'targetUserid': search_term,
                    'targetFullname': search_term,
                    'targetPicture': 'default.png',
                    'pluginName': self.name
                }]
            elif os.path.exists(os.path.dirname(search_term)) and os.path.isdir(os.path.dirname(search_term)):
                return [{
                    'targetUsername': os.path.basename(os.path.dirname(search_term)),
                    'targetUserid': os.path.dirname(search_term),
                    'targetFullname': os.path.dirname(search_term),
                    'targetPicture': 'default.png',
                    'pluginName': self.name
                }]
        except Exception as e:
            logger.error(f"Error searching for directories: {e}")
            
        return []
    
    def returnLocations(self, target, search_params):
        """Extract location data from images in the target directory"""
        locations = []
        
        try:
            directory = target['targetUserid']
            
            # If max_images is not defined, set a reasonable default
            max_images = 1000
            if search_params and 'max_images' in search_params:
                try:
                    max_images = int(search_params['max_images'])
                except:
                    pass
                    
            # Find all image files in the directory
            image_files = []
            for ext in ['jpg', 'jpeg', 'png', 'tiff', 'JPG', 'JPEG', 'PNG', 'TIFF']:
                image_files.extend(glob.glob(os.path.join(directory, f"*.{ext}")))
                image_files.extend(glob.glob(os.path.join(directory, "**", f"*.{ext}"), recursive=True))
                
            # Limit the number of images to process
            image_files = image_files[:max_images]
                
            for image_file in image_files:
                try:
                    with Image.open(image_file) as img:
                        exif_data = self.get_exif_data(img)
                        lat, lon = self.get_lat_lon(exif_data)
                        
                        if lat is not None and lon is not None:
                            date_taken = self.extract_date_taken(exif_data)
                            filename = os.path.basename(image_file)
                            
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
                    logger.error(f"Error processing image {image_file}: {e}")
        
        except Exception as e:
            logger.error(f"Error retrieving locations: {e}")
            
        return locations
        
    def getLabelForKey(self, key):
        """Return user-friendly labels for configuration keys"""
        if key == "max_images":
            return "Maximum number of images to process"
        return key
