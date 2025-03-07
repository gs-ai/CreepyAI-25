#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import json
import logging
import datetime
import urllib.request
import urllib.parse
from urllib.error import URLError
import time
import random
import ssl
from models.InputPlugin import InputPlugin

logger = logging.getLogger(__name__)

class SocialMediaPlugin(InputPlugin):
    """
    Social Media Plugin for CreepyAI
    
    This plugin discovers location data from public social media profiles
    through username searches and web scraping.
    """
    
    def __init__(self):
        InputPlugin.__init__(self)
        self.name = "Social Media Plugin"
        self.description = "Find locations from public social media profiles"
        
        # API endpoints for the various platforms
        self.endpoints = {
            'twitter_profile': 'https://nitter.net/{}',
            'instagram_profile': 'https://www.picuki.com/profile/{}',
            'reddit_profile': 'https://www.reddit.com/user/{}',
            'search_api': 'https://api.instantusername.com/check/{}',
            'location_data': 'https://nominatim.openstreetmap.org/search?q={}&format=json'
        }
        
        # Common regular expressions for finding location data
        self.location_patterns = [
            r'location[\s:]+([^,\n\r\<\>]{3,50})',
            r'based[\s:]+in[\s:]+([^,\n\r\<\>]{3,50})',
            r'lives[\s:]+in[\s:]+([^,\n\r\<\>]{3,50})',
            r'from[\s:]+([^,\n\r\<\>]{3,50})',
            r'([a-zA-Z\s]+, [a-zA-Z\s]+)',  # City, State/Country
            r'📍([^,\n\r\<\>]{3,50})'  # Location pin emoji
        ]
        
        self.error_count = 0
        self.hasWizard = False
        self._ensure_config_exists()
    
    def _ensure_config_exists(self):
        """Create default config if it doesn't exist"""
        config_path = self.getConfigurationFilePath()
        if not os.path.exists(config_path):
            logger.info(f"Creating default configuration for {self.__class__.__name__}")
            default_config = {
                'string_options': {
                    'proxy_server': '',
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'rate_limit': '0.5',  # requests per second
                    'timeout': '15'      # seconds
                },
                'boolean_options': {
                    'enabled': 'True',
                    'search_twitter': 'True',
                    'search_instagram': 'True',
                    'search_reddit': 'True',
                    'verify_ssl': 'True',
                    'use_proxy': 'False'
                }
            }
            self.saveConfiguration(default_config)
    
    def isConfigured(self):
        """Check if the plugin is properly configured"""
        success, boolean_options = self.readConfiguration('boolean_options')
        if not success or not boolean_options:
            return (False, "Plugin configuration is missing")
        
        if boolean_options.get('enabled', 'True') != 'True':
            return (False, "Plugin is disabled")
        
        # Check that at least one platform is enabled
        if not (boolean_options.get('search_twitter', 'False') == 'True' or
                boolean_options.get('search_instagram', 'False') == 'True' or
                boolean_options.get('search_reddit', 'False') == 'True'):
            return (False, "No social media platforms selected")
        
        # Check proxy settings if proxy is enabled
        if boolean_options.get('use_proxy', 'False') == 'True':
            success, string_options = self.readConfiguration('string_options')
            if not success or not string_options:
                return (False, "String options missing")
            
            if not string_options.get('proxy_server'):
                return (False, "Proxy server is enabled but not configured")
        
        return (True, "Plugin is properly configured")
    
    def searchForTargets(self, search_term):
        """
        Search for social media profile targets based on username.
        This is typically a username or real name.
        
        Args:
            search_term: Username or name to search for
            
        Returns:
            list: List of found profile targets
        """
        logger.info(f"SocialMediaPlugin.searchForTargets called with term: {search_term}")
        
        targets = []
        
        # Remove any @ symbol if present
        clean_term = search_term.lstrip('@')
        
        # Check for multiple usernames (comma separated)
        usernames = [u.strip() for u in clean_term.split(',') if u.strip()]
        
        # If only one username was provided
        if len(usernames) == 1:
            username = usernames[0]
            
            # Check if we have a real name (with spaces) or a username
            if ' ' in username:
                # It's likely a real name, try to generate potential usernames
                potential_usernames = self._generate_potential_usernames(username)
                potential_usernames.append(username.replace(' ', ''))  # Also add without spaces
                usernames = potential_usernames
        
        # Get configuration
        success, boolean_options = self.readConfiguration('boolean_options')
        success2, string_options = self.readConfiguration('string_options')
        
        if not success or not success2:
            logger.error("Failed to read configuration")
            return targets
        
        # Process each username
        for username in usernames:
            # Skip if too short
            if len(username) < 3:
                continue
            
            # Add basic target for the username
            targets.append({
                'pluginName': 'SocialMediaPlugin',
                'targetName': f"Social Media: {username}",
                'targetUser': username,
                'targetId': f"socialmedia_{username.lower()}",
                'username': username
            })
            
            # Check for platform-specific targets
            platforms_to_check = []
            if boolean_options.get('search_twitter', 'False') == 'True':
                platforms_to_check.append('twitter')
            if boolean_options.get('search_instagram', 'False') == 'True':
                platforms_to_check.append('instagram')
            if boolean_options.get('search_reddit', 'False') == 'True':
                platforms_to_check.append('reddit')
            
            # Set rate limiting
            try:
                rate_limit = float(string_options.get('rate_limit', '0.5'))
            except (ValueError, TypeError):
                rate_limit = 0.5
            
            # Check if the username exists on each platform
            for platform in platforms_to_check:
                try:
                    exists = self._check_platform_username(platform, username, string_options)
                    if exists:
                        targets.append({
                            'pluginName': 'SocialMediaPlugin',
                            'targetName': f"{platform.capitalize()}: {username}",
                            'targetUser': username,
                            'targetId': f"{platform}_{username.lower()}",
                            'username': username,
                            'platform': platform
                        })
                    
                    # Respect rate limiting
                    if rate_limit > 0:
                        time.sleep(1.0 / rate_limit)
                        
                except Exception as e:
                    logger.error(f"Error checking {platform} for username {username}: {str(e)}")
                    self.error_count += 1
        
        logger.info(f"SocialMediaPlugin found {len(targets)} targets")
        return targets
    
    def returnLocations(self, target, search_params):
        """
        Return locations for social media profiles.
        
        Args:
            target: Target to find locations for
            search_params: Additional search parameters
            
        Returns:
            list: List of locations found
        """
        logger.info(f"SocialMediaPlugin.returnLocations called for target: {target.get('targetName')}")
        locations = []
        
        # Get configuration
        success, boolean_options = self.readConfiguration('boolean_options')
        if not success or not boolean_options:
            logger.error("Failed to read boolean options")
            return locations
        
        success, string_options = self.readConfiguration('string_options')
        if not success or not string_options:
            logger.error("Failed to read string options")
            return locations
        
        if boolean_options.get('enabled', 'True') != 'True':
            logger.warning("SocialMediaPlugin is disabled")
            return locations
        
        # Get username and platform from target
        username = target.get('username')
        if not username:
            logger.error("No username in target")
            return locations
        
        platform = target.get('platform')
        
        # Set timeout
        try:
            timeout = float(string_options.get('timeout', '15'))
        except (ValueError, TypeError):
            timeout = 15.0
        
        # If no specific platform, check all enabled platforms
        if not platform:
            platforms_to_check = []
            if boolean_options.get('search_twitter', 'False') == 'True':
                platforms_to_check.append('twitter')
            if boolean_options.get('search_instagram', 'False') == 'True':
                platforms_to_check.append('instagram')
            if boolean_options.get('search_reddit', 'False') == 'True':
                platforms_to_check.append('reddit')
        else:
            platforms_to_check = [platform]
        
        # Set rate limiting
        try:
            rate_limit = float(string_options.get('rate_limit', '0.5'))
        except (ValueError, TypeError):
            rate_limit = 0.5
        
        # For each platform, try to find location data
        for platform in platforms_to_check:
            try:
                platform_locations = self._get_locations_for_platform(platform, username, string_options, timeout)
                if platform_locations:
                    locations.extend(platform_locations)
                
                # Respect rate limiting
                if rate_limit > 0:
                    time.sleep(1.0 / rate_limit)
            
            except Exception as e:
                logger.error(f"Error getting locations for {platform} user {username}: {str(e)}")
                self.error_count += 1
        
        logger.info(f"Found {len(locations)} locations for {username}")
        return locations
    
    def _check_platform_username(self, platform, username, string_options):
        """
        Check if a username exists on a specific platform.
        
        Args:
            platform: The platform to check (twitter, instagram, reddit)
            username: Username to check
            string_options: Configuration options
            
        Returns:
            bool: True if the username exists, False otherwise
        """
        # Use a different strategy based on the platform
        if platform == 'twitter':
            url = self.endpoints['twitter_profile'].format(username)
            response = self._make_request(url, string_options)
            
            # Return True if the response contains indicators of a valid profile
            if response and not "doesn't exist" in response and not "User not found" in response:
                return True
        
        elif platform == 'instagram':
            url = self.endpoints['instagram_profile'].format(username)
            response = self._make_request(url, string_options)
            
            # Return True if the response contains indicators of a valid profile
            if response and not "Page not found" in response and "Posts" in response:
                return True
        
        elif platform == 'reddit':
            url = self.endpoints['reddit_profile'].format(username)
            response = self._make_request(url, string_options)
            
            # Return True if the response contains indicators of a valid profile
            if response and not "Sorry, nobody on Reddit goes by that name" in response:
                return True
        
        return False
    
    def _get_locations_for_platform(self, platform, username, string_options, timeout):
        """
        Get location data from a specific platform.
        
        Args:
            platform: The platform to check (twitter, instagram, reddit)
            username: Username to check
            string_options: Configuration options
            timeout: Request timeout in seconds
            
        Returns:
            list: List of locations found
        """
        locations = []
        
        # Set URL based on platform
        if platform == 'twitter':
            url = self.endpoints['twitter_profile'].format(username)
        elif platform == 'instagram':
            url = self.endpoints['instagram_profile'].format(username)
        elif platform == 'reddit':
            url = self.endpoints['reddit_profile'].format(username)
        else:
            logger.warning(f"Unknown platform: {platform}")
            return locations
        
        # Make request
        response = self._make_request(url, string_options, timeout)
        if not response:
            return locations
        
        # Extract location information from response
        location_names = self._extract_location_data(response)
        logger.debug(f"Found location names: {location_names}")
        
        # For each extracted location, try to get coordinates
        for location_name in location_names:
            try:
                lat, lon = self._geocode_location(location_name, string_options)
                if lat and lon:
                    locations.append(self._create_location_dict(
                        lat, lon,
                        f"{platform.capitalize()} profile: {username}",
                        f"Location: {location_name}",
                        platform
                    ))
                    
                    # Only use the first valid location to avoid duplicates
                    break
                    
            except Exception as e:
                logger.error(f"Error geocoding location {location_name}: {str(e)}")
        
        return locations
    
    def _extract_location_data(self, response):
        """
        Extract location data from a response using regular expressions.
        
        Args:
            response: HTML response from a social media profile
            
        Returns:
            list: List of location strings found
        """
        locations = []
        
        # Check all patterns
        for pattern in self.location_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                # Clean up the match
                clean_match = match.strip()
                
                # Skip generic or short location indicators
                if len(clean_match) < 3 or clean_match.lower() in [
                    'n/a', 'worldwide', 'earth', 'global', 'internet', 'web', 'cyberspace'
                ]:
                    continue
                
                # Add to locations list if not already present
                if clean_match not in locations:
                    locations.append(clean_match)
        
        return locations
    
    def _geocode_location(self, location_name, string_options):
        """
        Convert a location name to coordinates using OpenStreetMap Nominatim.
        
        Args:
            location_name: Name of the location to geocode
            string_options: Configuration options
            
        Returns:
            tuple: (latitude, longitude) or (None, None) if not found
        """
        # URL encode the location name
        encoded_location = urllib.parse.quote(location_name)
        
        # Build and make the request
        url = self.endpoints['location_data'].format(encoded_location)
        response = self._make_request(url, string_options)
        
        if not response:
            return None, None
        
        # Parse the JSON response
        try:
            data = json.loads(response)
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Error parsing geocoding response: {str(e)}")
        
        return None, None
    
    def _make_request(self, url, string_options, timeout=15):
        """Make a HTTP request with proper error handling"""
        try:
            # Get configuration
            success, boolean_options = self.readConfiguration('boolean_options')
            if not success:
                boolean_options = {}
            
            # Configure SSL verification
            ctx = ssl.create_default_context()
            if boolean_options.get('verify_ssl', 'True') != 'True':
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            
            # Get proxy settings
            proxy = None
            if boolean_options.get('use_proxy', 'False') == 'True':
                proxy_server = string_options.get('proxy_server', '')
                if proxy_server:
                    proxy = urllib.request.ProxyHandler({
                        'http': proxy_server,
                        'https': proxy_server
                    })
            
            # Set up the opener with proxy if needed
            if proxy:
                opener = urllib.request.build_opener(proxy, urllib.request.HTTPSHandler(context=ctx))
                urllib.request.install_opener(opener)
            
            # Create the request
            user_agent = string_options.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml,application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/'
            }
            
            request = urllib.request.Request(url, headers=headers)
            
            # Make the request
            response = urllib.request.urlopen(request, timeout=timeout, context=ctx)
            return response.read().decode('utf-8')
        
        except URLError as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error making request to {url}: {str(e)}")
            return None
    
    def _create_location_dict(self, lat, lon, source_name, context, platform):
        """
        Create a standardized location dictionary.
        
        Args:
            lat: Latitude
            lon: Longitude
            source_name: Name of the source
            context: Context of the location
            platform: Social media platform
            
        Returns:
            dict: Location dictionary
        """
        now = datetime.datetime.now()
        
        return {
            'plugin': 'SocialMediaPlugin',
            'date': now,
            'lat': lat,
            'lon': lon,
            'shortName': source_name,
            'context': context,
            'infowindow': f"<b>{source_name}</b><br>{context}<br>Located via {platform} at {now.strftime('%Y-%m-%d %H:%M:%S')}"
        }
    
    def _generate_potential_usernames(self, full_name):
        """
        Generate potential usernames from a full name.
        
        Args:
            full_name: Full name to generate usernames from
            
        Returns:
            list: List of potential usernames
        """
        usernames = []
        parts = full_name.lower().split()
        
        if len(parts) >= 2:
            # first name + last name
            usernames.append(parts[0] + parts[-1])
            
            # first name + underscore + last name
            usernames.append(parts[0] + "_" + parts[-1])
            
            # first name + dot + last name
            usernames.append(parts[0] + "." + parts[-1])
            
            # first initial + last name
            usernames.append(parts[0][0] + parts[-1])
            
            # first name + last initial
            usernames.append(parts[0] + parts[-1][0])
            
            # first initial + underscore + last name
            usernames.append(parts[0][0] + "_" + parts[-1])
        
        if len(parts) >= 1:
            # just the first name
            usernames.append(parts[0])
            
            # first name + random digits
            usernames.append(parts[0] + "123")
        
        return usernames
    
    def getLabelForKey(self, key):
        """Get human-readable label for a configuration key"""
        labels = {
            'proxy_server': 'Proxy Server (host:port)',
            'user_agent': 'User Agent String',
            'rate_limit': 'Rate Limit (requests/second)',
            'timeout': 'Request Timeout (seconds)',
            'enabled': 'Plugin Enabled',
            'search_twitter': 'Search Twitter Profiles',
            'search_instagram': 'Search Instagram Profiles',
            'search_reddit': 'Search Reddit Profiles',
            'verify_ssl': 'Verify SSL Certificates',
            'use_proxy': 'Use Proxy Server'
        }
        return labels.get(key, InputPlugin.getLabelForKey(self, key))
