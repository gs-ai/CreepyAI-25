# Description: Default configuration settings for CreepyAI."""
Default configuration settings for CreepyAI.

This module defines fallback configuration values when settings
are not specified in configuration files.
"""
import os
import sys
from pathlib import Path

# Calculate paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
TEMP_DIR = PROJECT_ROOT / 'temp'
PROJECTS_DIR = PROJECT_ROOT / 'projects'
PLUGINS_DIR = PROJECT_ROOT / 'plugins'
PLUGIN_CONFIGS_DIR = PROJECT_ROOT / 'plugins' / 'configs'

# Default application configuration
DEFAULT_CONFIG = {
    'app': {
        'name': 'CreepyAI',
        'version': '2.5.0',
        'debug': False,
        'environment': 'production',
        'data_directory': str(DATA_DIR),
        'temp_directory': str(TEMP_DIR),
        'projects_directory': str(PROJECTS_DIR),
        'max_recent_projects': 10,
        'autosave_interval': 300,  # seconds
        'check_updates': True,
        'update_url': 'https://api.github.com/repos/user/creepyai/releases/latest',
    },
    'plugins': {
        'directory': str(PLUGINS_DIR),
        'configs_directory': str(PLUGIN_CONFIGS_DIR),
        'enabled': True,
        'max_threads': 4,
        'timeout': 60,  # seconds
        'disabled_plugins': [],
    },
    'ui': {
        'theme': 'light',
        'start_maximized': False,
        'window_width': 1200,
        'window_height': 800,
        'font_size': 10,
        'show_toolbar': True,
        'toolbar_icon_size': 24,
        'statusbar_enabled': True,
    },
    'geo': {
        'default_map_center': [51.505, -0.09],  # London
        'default_zoom': 13,
        'map_provider': 'osm',
        'gps_format': 'decimal',  # Options: 'decimal', 'dms'
        'distance_units': 'km',  # Options: 'km', 'mi'
        'geolocation_services': {
            'nominatim': {
                'enabled': True,
                'user_agent': 'CreepyAI/2.5.0',
            }
        },
        'location_history': {
            'max_points': 10000,
            'cluster_threshold_meters': 25,
            'cluster_min_time_minutes': 10,
        }
    },
    'security': {
        'anonymize_exports': False,
        'encrypt_project_files': False,
        'password_hash_algorithm': 'pbkdf2_sha256',
        'rate_limiting': {
            'enabled': True,
            'max_requests': 50,
            'period_seconds': 60,
        }
    },
    'network': {
        'proxy': {
            'enabled': False,
            'http': '',
            'https': '',
            'username': '',
            'password': '',
        },
        'timeout': 30,  # seconds
        'retries': 3,
        'user_agent': 'CreepyAI/2.5.0',
    },
    'logging': {
        'level': 'INFO',
        'log_to_file': True,
        'log_directory': str(PROJECT_ROOT / 'logs'),
        'max_log_size': 10485760,  # 10 MB
        'max_log_files': 5,
    }
}

# Default export configuration
DEFAULT_EXPORT_CONFIG = {
    'kml': {
        'include_timestamps': True,
        'include_descriptions': True,
        'add_metadata': False,
        'icon_style': 'default',
    },
    'csv': {
        'delimiter': ',',
        'include_headers': True,
        'quote_strings': True,
        'encoding': 'utf-8',
    },
    'html': {
        'include_timestamps': True,
        'cluster_markers': True,
        'map_height_px': 800,
        'add_legend': True,
    },
    'json': {
        'pretty_print': True,
        'include_metadata': True,
        'compress': False,
    }
}

# Update defaults with export configuration
DEFAULT_CONFIG['export'] = DEFAULT_EXPORT_CONFIG
