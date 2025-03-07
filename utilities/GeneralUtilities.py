#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
    """Sanitize a filename to be filesystem-safe"""
    # Replace invalid characters with underscore
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    # Collapse multiple underscores
    filename = re.sub(r'_+', "_", filename)
    # Trim leading/trailing spaces and dots
    filename = filename.strip(". ")
    # Ensure we have a valid filename
    if not filename:
        filename = "unnamed"
    return filename

def get_user_home_dir():
    return str(Path.home())

def get_app_data_dir():
    if platform.system() == 'Windows':
        app_data = os.path.join(os.getenv('APPDATA'), 'CreepyAI')
    elif platform.system() == 'Darwin':
        app_data = os.path.join(get_user_home_dir(), 'Library', 'Application Support', 'CreepyAI')
    else:
        app_data = os.path.join(get_user_home_dir(), '.creepyai')
    
    if not os.path.exists(app_data):
        os.makedirs(app_data)
    
    return app_data

def get_temp_dir():
    temp_dir = os.path.join(get_app_data_dir(), 'temp')
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    return temp_dir

def get_projects_dir():
    projects_dir = os.path.join(get_user_home_dir(), 'CreepyAI_Projects')
    
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir)
    
    return projects_dir

def create_unique_filename(directory, base_name, extension):
    base_name = sanitize_filename(base_name)
    
    if not extension.startswith('.'):
        extension = '.' + extension
    
    filename = os.path.join(directory, base_name + extension)
    if not os.path.exists(filename):
        return filename
    
    counter = 1
    while True:
        filename = os.path.join(directory, f"{base_name}_{counter}{extension}")
        if not os.path.exists(filename):
            return filename
        counter += 1

def generate_hash(text):
    hash_obj = hashlib.sha256(text.encode())
    return hash_obj.hexdigest()

def is_valid_url(url):
    """Check if a string is a valid URL"""
    pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ipv4
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return pattern.match(url) is not None

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def format_timestamp(timestamp, include_time=True):
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
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    try:
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':
            subprocess.call(['open', file_path])
        else:
            subprocess.call(['xdg-open', file_path])
        return True
    except Exception as e:
        logger.error(f"Error opening file {file_path}: {e}")
        return False

def open_url_in_browser(url):
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
    if not os.path.exists(file_path):
        return default
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading JSON file {file_path}: {e}")
        return default

def write_json_file(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error writing JSON file {file_path}: {e}")
        return False

def calcDistance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points in kilometers
    using the haversine formula
    """
    R = 6371  # Radius of the earth in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c  # Distance in km
    return distance

def html_escape(text):
    """Escape HTML characters in text"""
    if isinstance(text, str):
        return html.escape(text)
    return str(text)

def reportProblem():
    """Open the GitHub issue tracker in a browser"""
    url = "https://github.com/gs-ai/CreepyAI-25/issues/new"
    try:
        webbrowser.open(url)
    except Exception as e:
        logger.error(f"Failed to open browser: {str(e)}")
        return False
    return True

def createFolderStructure():
    try:
        os.makedirs(os.path.join(os.getcwd(), 'projects'), exist_ok=True)
        os.makedirs(os.path.join(os.getcwd(), 'temp'), exist_ok=True)
        os.makedirs(os.path.join(os.getcwd(), 'logs'), exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating folder structure: {e}")
        return False

def isPluginConfigured(plugin):
    try:
        return plugin.plugin_object.isConfigured()[0]
    except Exception as e:
        logger.error(f"Error checking plugin configuration: {e}")
        return False

def get_settings():
    settings = QSettings("CreepyAI", "Creepy")
    return settings

def save_setting(key, value):
    settings = get_settings()
    settings.setValue(key, value)
    
def get_setting(key, default=None):
    settings = get_settings()
    value = settings.value(key)
    return value if value is not None else default

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def create_cache_key(data):
    if isinstance(data, dict):
        data_str = json.dumps(data, sort_keys=True)
    else:
        data_str = str(data)
    
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()

def get_cached_data(cache_key, expiry_seconds=86400):
    cache_dir = ensure_dir(os.path.join(os.getcwd(), '.cache'))
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")
    
    if os.path.exists(cache_file):
        modified_time = os.path.getmtime(cache_file)
        if (time.time() - modified_time) < expiry_seconds:
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error reading cache file {cache_file}: {str(e)}")
                
    return None

def save_cached_data(cache_key, data):
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
    coord_str = coord_str.strip()
    
    decimal_pattern = r"^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$"
    match = re.search(decimal_pattern, coord_str)
    if match:
        lat = float(match.group(1))
        lon = float(match.group(2))
        return lat, lon
    
    dms_pattern = r"""
        \s*(\d+)\s*[°]\s*                
        (\d+)\s*[']\s*                   
        (\d+(?:\.\d+)?)\s*["]\s*         
        ([NS])\s*,\s*                    
        (\d+)\s*[°]\s*                   
        (\d+)\s*[']\s*                   
        (\d+(?:\.\d+)?)\s*["]\s*         
        ([EW])\s*                        
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
    
    return None, None
