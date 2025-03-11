#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Base plugin class and data structures for CreepyAI
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import hashlib
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LocationPoint:
    """Represents a geographic point with metadata"""
    latitude: float
    longitude: float
    timestamp: datetime
    source: str
    context: str

class BasePlugin:
    """Base class for all CreepyAI plugins"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.config = {}
        self.data_dir = os.path.join(
            os.path.expanduser("~"), 
            ".creepyai", 
            "data", 
            self.__class__.__name__
        )
        os.makedirs(self.data_dir, exist_ok=True)
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        """
        Return configuration options for this plugin
        
        Returns:
            List of dictionaries with the following keys:
            - name: Configuration option name
            - display_name: Display name for the UI
            - type: Type of configuration (string, boolean, directory, file, etc.)
            - default: Default value
            - required: Whether the option is required
            - description: Description of the option
        """
        return []
    
    def is_configured(self) -> Tuple[bool, str]:
        """
        Check if the plugin is properly configured
        
        Returns:
            Tuple of (is_configured, message)
        """
        return True, f"{self.name} is configured"
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """
        Update the configuration for this plugin
        
        Args:
            config: Dictionary of configuration options
            
        Returns:
            True if successful, False otherwise
        """
        self.config.update(config)
        return True
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None, 
                          date_to: Optional[datetime] = None) -> List[LocationPoint]:
        """
        Collect location data for the specified target
        
        Args:
            target: Target to collect locations for (e.g., username, path)
            date_from: Filter results to those after this date
            date_to: Filter results to those before this date
            
        Returns:
            List of LocationPoint objects
        """
        return []
    
    def search_for_targets(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for potential targets matching the search term
        
        Args:
            search_term: Search term
            
        Returns:
            List of dictionaries with the following keys:
            - targetId: Unique identifier for the target
            - targetName: Display name for the target
            - pluginName: Name of the plugin that found the target
        """
        return []
