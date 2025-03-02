#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import math
import webbrowser
import html
import logging
import re
import json
import hashlib
import time
from PyQt5.QtCore import QSettings

# set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(os.getcwd(), 'creepy_utilities.log'))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

def getUserHome():
    """
    Returns the user's home directory 
    """
    return os.path.expanduser("~")

def calcDistance(lat1, lon1, lat2, lon2):
    """Calculate distance in meters between two points using Haversine formula"""
    R = 6371  # Radius of the earth in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c * 1000  # Distance in meters
    return distance

def html_escape(text):
    """Escapes HTML special characters in a text string"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def reportProblem():
    """Opens the GitHub issues page to report a problem"""
    webbrowser.open('https://github.com/ilektrojohn/creepy/issues')

def createFolderStructure():
    """
    Creates the necessary folder structure for the application
    """
    try:
        os.makedirs(os.path.join(os.getcwd(), 'projects'), exist_ok=True)
        os.makedirs(os.path.join(os.getcwd(), 'temp'), exist_ok=True)
        os.makedirs(os.path.join(os.getcwd(), 'logs'), exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating folder structure: {e}")
        return False

def isPluginConfigured(plugin):
    """
    Checks if a plugin is properly configured
    """
    try:
        return plugin.plugin_object.isConfigured()[0]
    except Exception as e:
        logger.error(f"Error checking plugin configuration: {e}")
        return False

def get_settings():
    """Gets application settings"""
    settings = QSettings("CreepyAI", "Creepy")
    return settings

def save_setting(key, value):
    """Saves a setting"""
    settings = get_settings()
    settings.setValue(key, value)
    
def get_setting(key, default=None):
    """Gets a setting with a default value"""
    settings = get_settings()
    value = settings.value(key)
    return value if value is not None else default

def sanitize_filename(filename):
    """Removes invalid characters from a filename"""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def ensure_dir(directory):
    """Ensures that a directory exists, creating it if necessary"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def create_cache_key(data):
    """Creates a cache key from arbitrary data"""
    if isinstance(data, dict):
        # Sort dictionary to ensure consistent keys
        data_str = json.dumps(data, sort_keys=True)
    else:
        data_str = str(data)
    
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()

def get_cached_data(cache_key, expiry_seconds=86400):
    """Get cached data if it exists and hasn't expired"""
    cache_dir = ensure_dir(os.path.join(os.getcwd(), '.cache'))
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")
    
    if os.path.exists(cache_file):
        # Check if cache has expired
        modified_time = os.path.getmtime(cache_file)
        if (time.time() - modified_time) < expiry_seconds:
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error reading cache file {cache_file}: {str(e)}")
                
    return None

def save_cached_data(cache_key, data):
    """Save data to cache"""
    cache_dir = ensure_dir(os.path.join(os.getcwd(), '.cache'))
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        logger.warning(f"Error saving cache file {cache_file}: {str(e)}")
        return False

def parse_coordinates(coord_str):
    """Parse various coordinate string formats into decimal latitude/longitude"""
    # Remove any whitespace and punctuation
    coord_str = coord_str.strip()
    
    # Check for decimal format (e.g., "40.7128, -74.0060")
    decimal_pattern = r"^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$"
    match = re.search(decimal_pattern, coord_str)
    if match:
        lat = float(match.group(1))
        lon = float(match.group(2))
        return lat, lon
    
    # Check for DMS format (e.g., "40° 42' 46" N, 74° 0' 21" W")
    dms_pattern = r"""
        \s*(\d+)\s*[°]\s*                # Degrees
        (\d+)\s*[']\s*                   # Minutes
        (\d+(?:\.\d+)?)\s*["]\s*         # Seconds
        ([NS])\s*,\s*                    # N/S indicator
        (\d+)\s*[°]\s*                   # Degrees
        (\d+)\s*[']\s*                   # Minutes
        (\d+(?:\.\d+)?)\s*["]\s*         # Seconds
        ([EW])\s*                        # E/W indicator
    """
    match = re.search(dms_pattern, coord_str, re.VERBOSE)
    if match:
        lat_deg, lat_min, lat_sec, lat_dir, lon_deg, lon_min, lon_sec, lon_dir = match.groups()
        lat = float(lat_deg) + float(lat_min)/60 + float(lat_sec)/3600
        if lat_dir == 'S':
            lat = -lat
        lon = float(lon_deg) + float(lon_min)/60 + float(lon_sec)/3600
        if lon_dir == 'W':
            lon = -lon
        return lat, lon
    
    # Invalid format
    return None, None