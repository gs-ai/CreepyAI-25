#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
General utility functions for the CreepyAI application.
"""

import os
import re
import json
import logging
import hashlib
import datetime
import platform
import subprocess
from pathlib import Path
import urllib.parse
import math
import webbrowser
import html
import time
from PyQt5.QtCore import QSettings

logger = logging.getLogger('CreepyAI.Utilities')

def sanitize_filename(filename):
    """
    Sanitize a filename to ensure it's valid across platforms
    
    Args:
        filename (str): The filename to sanitize
        
    Returns:
        str: The sanitized filename
    """
    # Remove invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Ensure it's not too long
    if len(sanitized) > 255:
        base, ext = os.path.splitext(sanitized)
        sanitized = base[:250] + ext
    
    return sanitized

def get_user_home_dir():
    """Get the user's home directory"""
    return str(Path.home())

def get_app_data_dir():
    """Get the appropriate application data directory for the platform"""
    if platform.system() == 'Windows':
        app_data = os.path.join(os.getenv('APPDATA'), 'CreepyAI')
    elif platform.system() == 'Darwin':  # macOS
        app_data = os.path.join(get_user_home_dir(), 'Library', 'Application Support', 'CreepyAI')
    else:  # Linux and others
        app_data = os.path.join(get_user_home_dir(), '.creepyai')
    
    # Create directory if it doesn't exist
    if not os.path.exists(app_data):
        os.makedirs(app_data)
    
    return app_data

def get_temp_dir():
    """Get the temporary directory for the application"""
    temp_dir = os.path.join(get_app_data_dir(), 'temp')
    
    # Create directory if it doesn't exist
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    return temp_dir

def get_projects_dir():
    """Get the projects directory"""
    projects_dir = os.path.join(get_user_home_dir(), 'CreepyAI_Projects')
    
    # Create directory if it doesn't exist
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir)
    
    return projects_dir

def create_unique_filename(directory, base_name, extension):
    """
    Create a unique filename in the specified directory
    
    Args:
        directory (str): Directory path
        base_name (str): Base filename
        extension (str): File extension (without dot)
    
    Returns:
        str: Unique filename
    """
    # Sanitize base name
    base_name = sanitize_filename(base_name)
    
    # Ensure extension starts with a dot
    if not extension.startswith('.'):
        extension = '.' + extension
    
    # Try the base name first
    filename = os.path.join(directory, base_name + extension)
    if not os.path.exists(filename):
        return filename
    
    # If the file already exists, append a counter
    counter = 1
    while True:
        filename = os.path.join(directory, f"{base_name}_{counter}{extension}")
        if not os.path.exists(filename):
            return filename
        counter += 1

def generate_hash(text):
    """Generate a SHA-256 hash for the given text"""
    hash_obj = hashlib.sha256(text.encode())
    return hash_obj.hexdigest()

def is_valid_url(url):
    """Check if a URL is valid"""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def is_valid_email(email):
    """Check if an email address is valid"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def format_timestamp(timestamp, include_time=True):
    """Format a timestamp for display"""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.datetime.fromisoformat(timestamp)
        except ValueError:
            return timestamp
    
    if not isinstance(timestamp, (datetime.datetime, datetime.date)):
        return str(timestamp)
    
    if include_time:
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return timestamp.strftime("%Y-%m-%d")

def open_file_with_default_app(file_path):
    """Open a file with the default application for the file type"""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    try:
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', file_path])
        else:  # Linux and others
            subprocess.call(['xdg-open', file_path])
        return True
    except Exception as e:
        logger.error(f"Error opening file {file_path}: {e}")
        return False

def open_url_in_browser(url):
    """Open a URL in the default web browser"""
    import webbrowser
    
    if not is_valid_url(url):
        logger.error(f"Invalid URL: {url}")
        return False
    
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        logger.error(f"Error opening URL {url}: {e}")
        return False

def read_json_file(file_path, default=None):
    """Read and parse a JSON file"""
    if not os.path.exists(file_path):
        return default
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading JSON file {file_path}: {e}")
        return default

def write_json_file(file_path, data):
    """Write data to a JSON file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error writing JSON file {file_path}: {e}")
        return False

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