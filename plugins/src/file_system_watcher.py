#!/usr/bin/python
# -*- coding: utf-8 -*-

""""
File System Watcher plugin for CreepyAI
Monitors directories for file changes and extracts location data from new or modified files.
""""

import os
import sys
import time
import logging
import json
import traceback
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
import configparser
import hashlib
import threading
from queue import Queue, Empty
from pathlib import Path

from plugins.base_plugin import BasePlugin, LocationPoint
from plugins.metadata_extractor import MetadataExtractor

logger = logging.getLogger(__name__)

class FileSystemWatcher(BasePlugin):
    """"
    Plugin for monitoring directories and extracting location data from new or modified files.
    Integrates with MetadataExtractor to process files.
    """"
    
    def __init__(self):
        super().__init__(
            name="File System Watcher",
            description="Monitors directories for files with location data"
        )
        self.metadata_extractor = MetadataExtractor()
        self.watch_thread = None
        self.stop_event = threading.Event()
        self.queue = Queue()
        self._load_config_from_conf()
        self._file_cache = {}
        
    def _load_config_from_conf(self) -> None:
        """Load configuration from .conf file if available"""
        conf_path = os.path.join(os.path.dirname(__file__), 'FileSystemWatcher.conf')
        if os.path.exists(conf_path):
            try:
                config = configparser.ConfigParser()
                config.read(conf_path)
                
                # Convert the conf sections to our config format
                new_config = {}
                
                if 'string_options' in config:
                    for key, value in config['string_options'].items():
                        new_config[key] = value
                
                if 'boolean_options' in config:
                    for key, value in config['boolean_options'].items():
                        new_config[key] = value.lower() == 'true'
                
                if 'integer_options' in config:
                    for key, value in config['integer_options'].items():
                        try:
                            new_config[key] = int(value)
                        except (ValueError, TypeError):
                            pass
                
                if 'array_options' in config:
                    for key, value in config['array_options'].items():
                        try:
                            # Parse JSON arrays
                            new_config[key] = json.loads(value)
                        except:
                            # Fallback to comma-separated
                            new_config[key] = [item.strip() for item in value.split(',')]
                
                # Update config
                self.config.update(new_config)
                self._save_config()
                
            except Exception as e:
                logger.error(f"Error loading .conf file: {e}")
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        """Return configuration options for this plugin"""
        return [
            {
                "name": "watch_directories",
                "display_name": "Directories to Watch",
                "type": "array",
                "default": [],
                "required": True,
                "description": "List of directories to monitor for changes"
            },
            {
                "name": "file_patterns",
                "display_name": "File Patterns",
                "type": "array",
                "default": ["*.jpg", "*.jpeg", "*.png", "*.heic", "*.pdf"],
                "required": False,
                "description": "List of file patterns to monitor"
            },
            {
                "name": "scan_interval",
                "display_name": "Scan Interval (seconds)",
                "type": "integer",
                "default": 60,
                "min": 10,
                "max": 3600,
                "required": False,
                "description": "How often to scan for changes (seconds)"
            },
            {
                "name": "recursive",
                "display_name": "Recursive Scanning",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Scan subdirectories recursively"
            },
            {
                "name": "enabled",
                "display_name": "Enabled",
                "type": "boolean",
                "default": False,
                "required": False,
                "description": "Enable file system watching"
            },
            {
                "name": "min_file_age",
                "display_name": "Minimum File Age (seconds)",
                "type": "integer",
                "default": 10