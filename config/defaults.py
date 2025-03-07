"""
Default configuration values for CreepyAI.
"""

DEFAULT_SETTINGS = {
    'app': {
        'name': 'CreepyAI',
        'version': '2.5.0',
        'last_update_check': None,
        'check_for_updates': True,
        'theme': 'light',
        'debug_mode': False,
        'log_level': 'INFO',
        'data_directory': 'projects',
        'export_formats': ['kml', 'csv', 'json'],
        'max_locations': 1000,
        'map_provider': 'leaflet',
        'auto_save': True,
        'auto_save_interval': 300,  # seconds
        'session_timeout': 1800,  # seconds
    },
    'logging': {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.FileHandler',
                'filename': 'debug.log',
                'mode': 'a',
            }
        },
        'loggers': {
            '': {
                'handlers': ['default', 'file'],
                'level': 'INFO',
                'propagate': True
            }
        }
    },
    'plugins': {
        'DummyPlugin': {
            'Main': {
                'enabled': 'true',
                'debug': 'false',
                'log_level': 'INFO'
            }
        },
        'GeoIPPlugin': {
            'Main': {
                'enabled': 'true',
                'api_key': '',
                'database_path': '',
                'log_level': 'INFO'
            }
        },
        'SocialMediaPlugin': {
            'Main': {
                'enabled': 'true',
                'api_timeout': '30',
                'cache_results': 'true',
                'log_level': 'INFO'
            },
            'Twitter': {
                'enabled': 'true',
                'api_key': '',
                'api_secret': ''
            },
            'Facebook': {
                'enabled': 'true',
                'api_key': ''
            },
            'Instagram': {
                'enabled': 'true',
                'api_key': ''
            }
        }
    },
    'file_extensions': {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
        'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
        'data': ['.csv', '.json', '.xml', '.kml', '.kmz'],
        'archive': ['.zip', '.tar', '.gz', '.7z', '.rar']
    },
    'proxy': {
        'enabled': False,
        'http': '',
        'https': '',
        'username': '',
        'password': ''
    }
}
