#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
import time
import random
from bs4 import BeautifulSoup
import sys
import os

# Fix import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from creepy.models.ScrapingPlugin import ScrapingPlugin
from creepy.models.Location import Location
from datetime import datetime

logger = logging.getLogger(__name__)

class TwitterPlugin(ScrapingPlugin):
    """
    Twitter plugin that uses web scraping instead of Twitter API.
    """
    
    def __init__(self):
        ScrapingPlugin.__init__(self)
        self.name = "Twitter"
        self.description = "Collects location data from Twitter profiles and posts"
        
        # Patterns for extracting location data
        self.search_patterns = {
            'coordinates': r'[-+]?\d{1,2}\.\d+,\s*[-+]?\d{1,3}\.\d+',  # Basic lat,long pattern
            'location_meta': ['twitter:geo', 'geo.position', 'geo'],
            'post_location': r'location:([^,\n]+)',
            'profile_location': r'(?:location|based in|lives in):\s*([^,\n]+)',
        }
        
        # Maximum number of posts to scrape
        self.max_posts = 50
    
    def search_locations(self, target, search_params=None):
        """
        Search for locations in Twitter profiles and posts.
        
        Args:
            target (dict): Target information (name, username, etc.)
            search_params (dict): Additional search parameters
            
        Returns:
            list: List of locations found
        """
        if not self.is_configured():
            logger.warning("Twitter plugin is not properly configured")
            return []
        
        locations = []
        username = target.get('username', '')
        if not username:
            logger.warning("No username provided for Twitter plugin")
            return []
            
        # Clean the username
        username = self._clean_username(username)
        
        # Generate profile URL
        profile_urls = self._extract_profile_urls(username, 'twitter')
        
        # Mock location data for now (we'd normally scrape this)
        mock_location = Location()
        mock_location.latitude = 40.7128  # New York City
        mock_location.longitude = -74.0060
        mock_location.datetime = datetime.now()
        mock_location.source = f"Twitter profile @{username}"
        mock_location.context = {"source": "Twitter Placeholder"}
        mock_location.accuracy = "medium"
        
        locations.append(mock_location)
        
        return locations


