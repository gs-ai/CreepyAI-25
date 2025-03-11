"""
Constants for CreepyAI
Application-wide constant definitions
"""

from enum import Enum, auto
import os
from pathlib import Path

# Application information
APP_NAME = "CreepyAI"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "OSINT Location Intelligence Tool"
APP_AUTHOR = "CreepyAI Team"
APP_WEBSITE = "https://creepyai.example.com"
APP_COPYRIGHT = "© 2023 CreepyAI Team"

# Default data directory name (within user directory)
DATA_DIR_NAME = "CreepyAI-Data" 

# Project file extensions
PROJECT_EXTENSION = ".cai"
PROJECT_FILTER = f"{APP_NAME} Projects (*{PROJECT_EXTENSION})"

# File export types
class ExportFormat(Enum):
    """File export formats supported by the application"""
    CSV = auto()
    JSON = auto()
    KML = auto()
    HTML = auto()
    GPX = auto()

# File type filters for file dialogs
EXPORT_FILTERS = {
    ExportFormat.CSV: "CSV Files (*.csv)",
    ExportFormat.JSON: "JSON Files (*.json)",
    ExportFormat.KML: "KML Files (*.kml)",
    ExportFormat.HTML: "HTML Reports (*.html)",
    ExportFormat.GPX: "GPX Files (*.gpx)"
}

# UI related constants
ICON_SIZE = 24
MAP_DEFAULT_ZOOM = 4
MAP_MIN_ZOOM = 2
MAP_MAX_ZOOM = 18
UI_REFRESH_INTERVAL = 500  # ms

# Map layer types
class MapLayer(Enum):
    """Map layer types available in the application"""
    STREET = "Street Map"
    SATELLITE = "Satellite"
    TERRAIN = "Terrain"
    DARK = "Dark Mode"
    HYBRID = "Hybrid"

# Map providers
MAP_PROVIDERS = {
    MapLayer.STREET: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    MapLayer.SATELLITE: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    MapLayer.TERRAIN: "https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png",
    MapLayer.DARK: "https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png",
    MapLayer.HYBRID: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
}

# Attribution text for different map providers
MAP_ATTRIBUTION = {
    MapLayer.STREET: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    MapLayer.SATELLITE: 'Imagery &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    MapLayer.TERRAIN: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    MapLayer.DARK: '&copy; <a href="https://carto.com/attributions">CARTO</a>, &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    MapLayer.HYBRID: 'Imagery &copy; Esri &mdash; Sources: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom'
}

# Plugin related constants
PLUGIN_CACHE_TIME = 3600  # seconds
DEFAULT_PLUGIN_CONFIG_PATH = os.path.join("configs", "plugins")

# Settings keys
class SettingsKey:
    """Settings keys for QSettings"""
    FIRST_RUN = "firstRun"
    THEME = "theme"
    DATA_DIRECTORY = "dataDirectory"
    MAP_LAYER = "mapLayer"
    LOG_LEVEL = "log_level"
    LANGUAGE = "language"
    SKIP_WELCOME = "skipWelcomeDialog"
    COLLECT_USAGE_DATA = "collectUsageData"
    ENABLE_CRASH_REPORTS = "enableCrashReports"
    CHECK_FOR_UPDATES = "checkForUpdates"
    LAST_OPENED_PROJECT = "lastOpenedProject"
    RECENT_PROJECTS = "recentProjects"

# Date formats
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"

# Timeouts (in seconds)
REQUEST_TIMEOUT = 30
GEOCODING_TIMEOUT = 10

# Social media icon prefix mapping
SOCIAL_MEDIA_ICONS = {
    "Facebook": "facebook-icon.png",
    "Instagram": "instagram-icon.png",
    "LinkedIn": "linkedin-icon.png",
    "Pinterest": "pinterest-icon.png",
    "Snapchat": "snapchat-icon.png",
    "TikTok": "tiktok-icon.png",
    "Twitter": "twitter-icon.png",
    "Yelp": "yelp-icon.png"
}

# Default values
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_MAP_LAYER = MapLayer.STREET.value

# Paths
APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
APP_RESOURCES_DIR = os.path.join(APP_ROOT, "app", "resources")
APP_ICONS_DIR = os.path.join(APP_RESOURCES_DIR, "icons")
APP_MAP_DIR = os.path.join(APP_RESOURCES_DIR, "map")

# Configuration
CONFIG_DIR_NAME = "configs"
CONFIG_DIR = os.path.join(APP_ROOT, CONFIG_DIR_NAME)
PLUGIN_CONFIG_DIR = os.path.join(CONFIG_DIR, "plugins")
DEFAULT_CONFIG_FILE = os.path.join(CONFIG_DIR, "creepyai.conf")

# Plugins
PLUGIN_DIR = os.path.join(APP_ROOT, "app", "plugins")
BUILTIN_PLUGINS = [
    "SocialMediaPlugin",
    "GeoIPPlugin",
    "DocumentAnalyzer",
    "MetadataExtractor",
    "LocalDataHarvester"
]

# Data storage
DATA_DIR_NAME = "data"
DATA_DIR = os.path.join(APP_ROOT, DATA_DIR_NAME)
CACHE_DIR = os.path.join(DATA_DIR, "cache")
EXPORT_DIR = os.path.join(DATA_DIR, "exports")

# Logging
LOG_DIR_NAME = "logs"
LOG_DIR = os.path.join(APP_ROOT, LOG_DIR_NAME)
DEFAULT_LOG_FILE = os.path.join(LOG_DIR, "creepyai.log")

# UI
UI_DEFAULT_THEME = "system"
UI_AVAILABLE_THEMES = ["system", "light", "dark"]
UI_DEFAULT_FONT_SIZE = 10

# Geocoding
DEFAULT_GEOCODING_SERVICE = "nominatim"
GEOCODING_SERVICES = ["nominatim", "google", "bing", "mapquest", "arcgis"]
MAX_GEOCODING_RETRIES = 3

# Export formats
EXPORT_FORMATS = ["csv", "json", "kml", "geojson"]

# Map settings
DEFAULT_MAP_LAYER = "Street Map"
DEFAULT_MAP_ZOOM = 4
DEFAULT_MAP_CENTER_LAT = 39.8283
DEFAULT_MAP_CENTER_LON = -98.5795  # Center of USA

# Supported file formats for export
EXPORT_FORMATS = {
    "csv": "Comma Separated Values (*.csv)",
    "json": "JavaScript Object Notation (*.json)",
    "kml": "Keyhole Markup Language (*.kml)",
    "gpx": "GPS Exchange Format (*.gpx)",
    "xlsx": "Excel Spreadsheet (*.xlsx)",
    "image": "PNG Image (*.png)"
}

# API timeouts (in seconds)
DEFAULT_API_TIMEOUT = 10
GEOCODING_API_TIMEOUT = 5

# Cache settings
CACHE_EXPIRY_DAYS = 30
