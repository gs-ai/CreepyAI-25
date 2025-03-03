#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import time
import random
import requests
import json
import hashlib
from datetime import datetime
from yapsy.IPlugin import IPlugin

logger = logging.getLogger(__name__)

class ScrapingPlugin(IPlugin):
    """
    Base class for plugins that use web scraping instead of APIs.
    This provides common functionality for all scraping plugins.
    """
    
    def __init__(self):
        """Initialize the plugin."""
        IPlugin.__init__(self)
        self.name = "ScrapingPlugin"
        self.description = "Base class for scraping plugins"
        self.is_activated = False
        self.config_manager = None
        self.database = None
        self.web_scraper = None
        self.cache_dir = None
        
        # Initialize cache directory
        self._init_cache_dir()
    
    def _init_cache_dir(self):
        """Initialize the cache directory."""
        cache_base = os.path.join(os.path.expanduser("~"), ".creepyai", "cache")
        self.cache_dir = os.path.join(cache_base, self.name.lower().replace(" ", "_"))
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def activate(self):
        """Activate the plugin."""
        if not self.is_activated:
            logger.info(f"Activating plugin: {self.name}")
            self.is_activated = True
    
    def deactivate(self):
        """Deactivate the plugin."""
        if self.is_activated:
            logger.info(f"Deactivating plugin: {self.name}")
            self.is_activated = False
    
    def set_config_manager(self, config_manager):
        """Set the configuration manager."""
        self.config_manager = config_manager
    
    def set_database(self, database):
        """Set the database."""
        self.database = database
    
    def set_web_scraper(self, web_scraper):
        """Set the web scraper utility."""
        self.web_scraper = web_scraper
    
    def is_configured(self):
        """Check if the plugin is properly configured."""
        return self.web_scraper is not None
    
    def _clean_username(self, username):
        """Clean a username by removing @ and spaces."""
        if not username:
            return ""
        return username.strip().replace("@", "")
    
    def _extract_profile_urls(self, username, platform):
        """Extract possible profile URLs from username."""
        username = self._clean_username(username)
        urls = []
        
        if platform == 'instagram':
            urls = [
                f"https://www.instagram.com/{username}/",
                f"https://instagram.com/{username}/"
            ]
        elif platform == 'twitter':
            urls = [
                f"https://twitter.com/{username}",
                f"https://x.com/{username}"
            ]
        elif platform == 'facebook':
            urls = [
                f"https://www.facebook.com/{username}",
                f"https://facebook.com/{username}"
            ]
        
        return urls
    
    def _get_cache_file_path(self, url, target_id=None):
        """Get the cache file path for a URL."""
        # Create a stable file name from the URL
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        if target_id:
            return os.path.join(self.cache_dir, f"{target_id}_{url_hash}.json")
        return os.path.join(self.cache_dir, f"{url_hash}.json")
    
    def _get_cached_result(self, url, max_age_days=7):
        """Get cached result for a URL if available and not expired."""
        cache_file = self._get_cache_file_path(url)
        if not os.path.exists(cache_file):
            return None
            
        try:
            # Check if file is too old
            file_age = time.time() - os.path.getmtime(cache_file)
            max_age = max_age_days * 24 * 60 * 60  # convert days to seconds
            
            if file_age > max_age:
                return None
                
            # Load cached data
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                
            return cached_data
        except Exception as e:
            logger.error(f"Error reading cache file: {str(e)}")
            return None
    
    def _cache_result(self, url, content, target_id=None):
        """Cache the result of a URL fetch."""
        try:
            cache_file = self._get_cache_file_path(url, target_id)
            
            cached_data = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'target_id': target_id,
                'content': content
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cached_data, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error caching result: {str(e)}")
            return False
