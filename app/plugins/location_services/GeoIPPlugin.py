#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import datetime
import json
import logging
import urllib.request
import urllib.parse
from urllib.error import URLError, HTTPError
import socket
import time
import random
import re
import traceback
from typing import Dict, List, Tuple, Optional, Any, Union

logger = logging.getLogger(__name__)

# Import the proper InputPlugin base class based on its availability
try:
    from app.models.InputPlugin import InputPlugin
except ImportError:
    try:
            from app.plugins.base_plugin import BasePlugin as InputPlugin
            logger.info("Using base_plugin.BasePlugin as fallback for InputPlugin")
    except ImportError:
        # Define a minimal InputPlugin if neither is available
        class InputPlugin:
            def __init__(self):
                        self.name = "Generic Plugin"
                        self.description = "Generic plugin description"
                
            def readConfiguration(self, section):
                        return False, {}
                
            def getConfigurationFilePath(self):
                        return ""
                
            def saveConfiguration(self, config):
                        pass
                
            def getLabelForKey(self, key):
                        return key
                        logger.warning("Could not import InputPlugin, using minimal implementation")


class GeoIPPlugin(InputPlugin):
                            """"""""""""
                            GeoIP Plugin for CreepyAI""
                            ""
                            This plugin uses IP geolocation services to find the location of IP addresses.""
                            It can query multiple free services and combine the results.
                            """"""""""""
                            ""
                            def __init__(self):""
                            try:""
                            InputPlugin.__init__(self)
        except:
                            pass  # Handle case where parent __init__ might fail
            
                            self.name = "GeoIP Plugin"
                            self.description = "Find locations based on IP addresses"
                            self.api_urls = {
                            'ipapi': 'https://ipapi.co/{}/json/',
                            'ipinfo': 'https://ipinfo.io/{}/json',
                            'ipgeolocation': 'https://api.ipgeolocation.io/ipgeo?apiKey={}&ip={}',
                            'freegeoip': 'https://freegeoip.app/json/{}'
                            }
                            self.error_count = 0
                            self.hasWizard = False
                            self._ensure_config_exists()
        
    def _ensure_config_exists(self):
                                """Create default config if it doesn't exist"""'""""""""
                                try:''
                                config_path = self.getConfigurationFilePath()''
                                if not os.path.exists(config_path):''
                                logger.info(f"Creating default configuration for {self.__class__.__name__}")
                                default_config = {
                                'string_options': {
                                'ipgeolocation_api_key': '',
                                'target_list': '8.8.8.8, 1.1.1.1',  # Include some default IPs
                                'rate_limit': '1',  # requests per second
                                'timeout': '10',    # seconds
                                'default_service': 'ipapi',
                                'cache_directory': os.path.join(os.path.expanduser('~'), '.creepyai', 'geoip_cache')
                                },
                                'boolean_options': {
                                'enabled': 'True',
                                'use_ipapi': 'True',
                                'use_ipinfo': 'True',
                                'use_ipgeolocation': 'False',
                                'use_freegeoip': 'False',
                                'use_cache': 'True',
                                'skip_private_ips': 'True'
                                }
                                }
                                self.saveConfiguration(default_config)
                
                # Create cache directory
                                os.makedirs(default_config['string_options']['cache_directory'], exist_ok=True)
        except Exception as e:
                                    logger.error(f"Error creating default configuration: {str(e)}")
            
    def isConfigured(self):
                                        """Check if the plugin is properly configured"""""""""""
        try:
                                            success, boolean_options = self.readConfiguration('boolean_options')
            if not success or not boolean_options:
                                            return (False, "Plugin configuration is missing")
                
            if boolean_options.get('enabled', 'True') != 'True':
                                            return (False, "Plugin is disabled")
                
            # Need at least one service enabled
                                            services_enabled = (
                                            boolean_options.get('use_ipapi', 'False') == 'True' or
                                            boolean_options.get('use_ipinfo', 'False') == 'True' or
                                            boolean_options.get('use_ipgeolocation', 'False') == 'True' or
                                            boolean_options.get('use_freegeoip', 'False') == 'True'
                                            )
            
            if not services_enabled:
                                            return (False, "No geolocation services are enabled")
                
            # Check if API key is set for services that require it
                                            success, string_options = self.readConfiguration('string_options')
            if not success:
                                            return (False, "String options missing")
                
                                            if (boolean_options.get('use_ipgeolocation', 'False') == 'True' and 
                                            (not string_options.get('ipgeolocation_api_key') or 
                    string_options.get('ipgeolocation_api_key') == '')):
                                            return (False, "ipgeolocation.io API key is required")
                
                                        return (True, "Plugin is properly configured")
        except Exception as e:
                                            logger.error(f"Error checking configuration: {str(e)}")
                                        return (False, f"Configuration error: {str(e)}")
        
    def searchForTargets(self, search_term):
                                            """"""""""""
                                            Search for targets based on search term.""
                                            For GeoIP, we treat the search term as an IP address or hostname to lookup.""
                                            ""
        Args:
                                                search_term: IP address, hostname, or list of IPs
            
        Returns:
                                                    list: List of targets found
                                                    """"""""""""
                                                    logger.info(f"GeoIPPlugin.searchForTargets called with term: {search_term}")
        
                                                    targets = []
        try:
            # Check if search term contains multiple IPs (comma or newline separated)
            if ',' in search_term or '\n' in search_term:
                # Split and process multiple IPs
                                                            ip_list = []
                for sep in [',', '\n']:
                    if sep in search_term:
                                                                    ip_list.extend([ip.strip() for ip in search_term.split(sep) if ip.strip()])
            else:
                # Single IP or hostname
                                                                        ip_list = [search_term.strip()]
            
            # Get configuration
                                                                        success, boolean_options = self.readConfiguration('boolean_options')
            if not success:
                                                                            boolean_options = {}
            
                                                                            skip_private_ips = boolean_options.get('skip_private_ips', 'True') == 'True'
            
            # Process each IP
            for ip in ip_list:
                # Skip empty items
                if not ip:
                                                                                continue
                    
                # If it's a hostname, try to resolve it'
                                                                                if not self._is_ip_address(ip):''
                                                                                try:''
                                                                                resolved_ip = socket.gethostbyname(ip)''
                                                                                logger.debug(f"Resolved {ip} to {resolved_ip}")
                                                                                ip_for_target = resolved_ip
                                                                                hostname = ip  # Store original hostname
                    except socket.gaierror:
                                                                                    logger.warning(f"Could not resolve hostname: {ip}")
                                                                                continue  # Skip this target
                else:
                                                                                    ip_for_target = ip
                                                                                    hostname = None  # No hostname
                    
                # Skip private IPs if configured to do so
                if skip_private_ips and self._is_private_ip(ip_for_target):
                                                                                        logger.info(f"Skipping private IP: {ip_for_target}")
                                                                                    continue
                    
                # Create a target
                                                                                    targets.append({
                                                                                    'pluginName': 'GeoIPPlugin',
                                                                                    'targetName': hostname or ip_for_target,
                                                                                    'targetUser': ip_for_target,
                                                                                    'targetId': 'geoip_' + ip_for_target.replace('.', '_'),
                                                                                    'hostname': hostname,
                                                                                    'ip': ip_for_target
                                                                                    })
        except Exception as e:
                                                                                        logger.error(f"Error searching for targets: {str(e)}", exc_info=True)
            
                                                                                        logger.info(f"GeoIPPlugin found {len(targets)} targets")
                                                                                    return targets
        
    def returnLocations(self, target, search_params):
                                                                                        """"""""""""
                                                                                        Return locations for IP addresses.""
                                                                                        ""
                                                                                        Args:""
                                                                                        target: Target to find locations for
                                                                                        search_params: Additional search parameters
            
        Returns:
                                                                                            list: List of locations found
                                                                                            """"""""""""
                                                                                            logger.info(f"GeoIPPlugin.returnLocations called for target: {target.get('targetName')}")
                                                                                            locations = []
        
        try:
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
                                                                                                    logger.warning("GeoIPPlugin is disabled")
                                                                                                return locations
                
            # Get IP from target
                                                                                                ip = target.get('ip')
            if not ip:
                                                                                                    logger.error("No IP address in target")
                                                                                                return locations
                
            # Check cache first if enabled
            if boolean_options.get('use_cache', 'True') == 'True':
                                                                                                    cache_location = self._get_from_cache(ip, string_options.get('cache_directory'))
                if cache_location:
                                                                                                        logger.info(f"Using cached location for {ip}")
                                                                                                        locations.append(cache_location)
                                                                                                    return locations
                
            # Check which services are enabled and query them
                                                                                                    services = []
            if boolean_options.get('use_ipapi', 'False') == 'True':
                                                                                                        services.append('ipapi')
            if boolean_options.get('use_ipinfo', 'False') == 'True':
                                                                                                            services.append('ipinfo')
            if boolean_options.get('use_ipgeolocation', 'False') == 'True':
                if string_options.get('ipgeolocation_api_key'):
                                                                                                                    services.append('ipgeolocation')
                    
            if boolean_options.get('use_freegeoip', 'False') == 'True':
                                                                                                                        services.append('freegeoip')
                
            if not services:
                                                                                                                            logger.warning("No geolocation services enabled")
                                                                                                                        return locations
                
            # Get default service if specified
                                                                                                                        default_service = string_options.get('default_service')
            if default_service and default_service in services:
                                                                                                                            services.insert(0, services.pop(services.index(default_service)))
                
            # Get rate limit and timeout
            try:
                                                                                                                                rate_limit = float(string_options.get('rate_limit', '1'))
            except ValueError:
                                                                                                                                    rate_limit = 1.0
                
            try:
                                                                                                                                        timeout = float(string_options.get('timeout', '10'))
            except ValueError:
                                                                                                                                            timeout = 10.0
                
            # Query each service
            for service in services:
                try:
                                                                                                                                                    location = self._query_service(service, ip, string_options, timeout)
                    if location:
                        # Save to cache if enabled
                        if boolean_options.get('use_cache', 'True') == 'True':
                                                                                                                                                            self._save_to_cache(ip, location, string_options.get('cache_directory'))
                            
                                                                                                                                                            locations.append(location)
                                                                                                                                                        break  # Stop after first successful lookup
                except Exception as e:
                                                                                                                                                            logger.error(f"Error querying {service} for {ip}: {str(e)}")
                                                                                                                                                            self.error_count += 1
                    
                # Respect rate limiting
                if rate_limit > 0:
                                                                                                                                                                time.sleep(1.0 / rate_limit)
                    
                                                                                                                                                                logger.info(f"Found {len(locations)} locations for {ip}")
        except Exception as e:
                                                                                                                                                                    logger.error(f"Error in returnLocations: {str(e)}", exc_info=True)
            
                                                                                                                                                                return locations
        
    def _get_from_cache(self, ip, cache_dir):
                                                                                                                                                                    """Get location from cache if available and not expired"""""""""""
        try:
            if not cache_dir:
                                                                                                                                                                            cache_dir = os.path.join(os.path.expanduser('~'), '.creepyai', 'geoip_cache')
                
                                                                                                                                                                            os.makedirs(cache_dir, exist_ok=True)
            
                                                                                                                                                                            cache_file = os.path.join(cache_dir, f"{ip.replace('.', '_')}.json")
            
            if not os.path.exists(cache_file):
                                                                                                                                                                            return None
                
            # Check if cache is older than 30 days
                                                                                                                                                                            file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(cache_file))
            if file_age.days > 30:
                                                                                                                                                                                logger.debug(f"Cache for {ip} is expired")
                                                                                                                                                                            return None
                
            with open(cache_file, 'r') as f:
                                                                                                                                                                                location = json.load(f)
                
            # Convert cached date string back to datetime
            if 'date' in location and isinstance(location['date'], str):
                try:
                                                                                                                                                                                        location['date'] = datetime.datetime.fromisoformat(location['date'])
                except ValueError:
                                                                                                                                                                                            location['date'] = datetime.datetime.now()
                    
                                                                                                                                                                                        return location
        except Exception as e:
                                                                                                                                                                                            logger.error(f"Error reading from cache: {str(e)}")
                                                                                                                                                                                        return None
            
    def _save_to_cache(self, ip, location, cache_dir):
                                                                                                                                                                                            """Save location to cache"""""""""""
        try:
            if not cache_dir:
                                                                                                                                                                                                    cache_dir = os.path.join(os.path.expanduser('~'), '.creepyai', 'geoip_cache')
                
                                                                                                                                                                                                    os.makedirs(cache_dir, exist_ok=True)
            
                                                                                                                                                                                                    cache_file = os.path.join(cache_dir, f"{ip.replace('.', '_')}.json")
            
            # Convert datetime to string for serialization
                                                                                                                                                                                                    location_copy = location.copy()
            if 'date' in location_copy and isinstance(location_copy['date'], datetime.datetime):
                                                                                                                                                                                                        location_copy['date'] = location_copy['date'].isoformat()
                
            with open(cache_file, 'w') as f:
                                                                                                                                                                                                            json.dump(location_copy, f)
        except Exception as e:
                                                                                                                                                                                                                logger.error(f"Error saving to cache: {str(e)}")
        
    def _query_service(self, service, ip, string_options, timeout):
                                                                                                                                                                                                                    """Query a specific geolocation service for IP location"""""""""""
        if service == 'ipapi':
                                                                                                                                                                                                                    return self._query_ipapi(ip, timeout)
        elif service == 'ipinfo':
                                                                                                                                                                                                                    return self._query_ipinfo(ip, timeout)
        elif service == 'ipgeolocation':
                                                                                                                                                                                                                        api_key = string_options.get('ipgeolocation_api_key', '')
                                                                                                                                                                                                                    return self._query_ipgeolocation(ip, api_key, timeout)
        elif service == 'freegeoip':
                                                                                                                                                                                                                    return self._query_freegeoip(ip, timeout)
        else:
                                                                                                                                                                                                                        logger.warning(f"Unknown service: {service}")
                                                                                                                                                                                                                    return None
            
    def _query_ipapi(self, ip, timeout):
                                                                                                                                                                                                                        """Query ipapi.co for IP location"""""""""""
        try:
                                                                                                                                                                                                                            url = self.api_urls['ipapi'].format(ip)
                                                                                                                                                                                                                            response = self._make_request(url, timeout)
            
            if not response:
                                                                                                                                                                                                                            return None
                
                                                                                                                                                                                                                            data = json.loads(response)
            
            if 'error' in data or 'latitude' not in data or 'longitude' not in data:
                                                                                                                                                                                                                                logger.warning(f"Invalid response from ipapi.co: {data}")
                                                                                                                                                                                                                            return None
                
                                                                                                                                                                                                                            lat = data.get('latitude')
                                                                                                                                                                                                                            lon = data.get('longitude')
                                                                                                                                                                                                                            city = data.get('city', '')
                                                                                                                                                                                                                            country = data.get('country_name', '')
                                                                                                                                                                                                                            region = data.get('region', '')
            
                                                                                                                                                                                                                        return self._create_location_dict(
                                                                                                                                                                                                                        lat, lon, 
                                                                                                                                                                                                                        f"IP: {ip} ({city}, {region}, {country})",
                                                                                                                                                                                                                        "ipapi.co"
                                                                                                                                                                                                                        )
        except Exception as e:
                                                                                                                                                                                                                            logger.error(f"Error in _query_ipapi: {str(e)}")
                                                                                                                                                                                                                        return None
            
    def _query_ipinfo(self, ip, timeout):
                                                                                                                                                                                                                            """Query ipinfo.io for IP location"""""""""""
        try:
                                                                                                                                                                                                                                url = self.api_urls['ipinfo'].format(ip)
                                                                                                                                                                                                                                response = self._make_request(url, timeout)
            
            if not response:
                                                                                                                                                                                                                                return None
                
                                                                                                                                                                                                                                data = json.loads(response)
            
            if 'loc' not in data:
                                                                                                                                                                                                                                    logger.warning(f"Invalid response from ipinfo.io: {data}")
                                                                                                                                                                                                                                return None
                
            # Location comes as "lat,lon"
            try:
                                                                                                                                                                                                                                    lat, lon = map(float, data['loc'].split(','))
            except (ValueError, IndexError):
                                                                                                                                                                                                                                        logger.warning(f"Invalid location format from ipinfo.io: {data['loc']}")
                                                                                                                                                                                                                                    return None
                
                                                                                                                                                                                                                                    city = data.get('city', '')
                                                                                                                                                                                                                                    country = data.get('country', '')
                                                                                                                                                                                                                                    region = data.get('region', '')
            
                                                                                                                                                                                                                                return self._create_location_dict(
                                                                                                                                                                                                                                lat, lon, 
                                                                                                                                                                                                                                f"IP: {ip} ({city}, {region}, {country})",
                                                                                                                                                                                                                                "ipinfo.io"
                                                                                                                                                                                                                                )
        except Exception as e:
                                                                                                                                                                                                                                    logger.error(f"Error in _query_ipinfo: {str(e)}")
                                                                                                                                                                                                                                return None
            
    def _query_ipgeolocation(self, ip, api_key, timeout):
                                                                                                                                                                                                                                    """Query ipgeolocation.io for IP location"""""""""""
        try:
                                                                                                                                                                                                                                        url = self.api_urls['ipgeolocation'].format(api_key, ip)
                                                                                                                                                                                                                                        response = self._make_request(url, timeout)
            
            if not response:
                                                                                                                                                                                                                                        return None
                
                                                                                                                                                                                                                                        data = json.loads(response)
            
            if 'latitude' not in data or 'longitude' not in data:
                                                                                                                                                                                                                                            logger.warning(f"Invalid response from ipgeolocation.io: {data}")
                                                                                                                                                                                                                                        return None
                
                                                                                                                                                                                                                                        lat = float(data.get('latitude'))
                                                                                                                                                                                                                                        lon = float(data.get('longitude'))
                                                                                                                                                                                                                                        city = data.get('city', '')
                                                                                                                                                                                                                                        country = data.get('country_name', '')
                                                                                                                                                                                                                                        state = data.get('state_prov', '')
            
                                                                                                                                                                                                                                    return self._create_location_dict(
                                                                                                                                                                                                                                    lat, lon, 
                                                                                                                                                                                                                                    f"IP: {ip} ({city}, {state}, {country})",
                                                                                                                                                                                                                                    "ipgeolocation.io"
                                                                                                                                                                                                                                    )
        except Exception as e:
                                                                                                                                                                                                                                        logger.error(f"Error in _query_ipgeolocation: {str(e)}")
                                                                                                                                                                                                                                    return None
            
    def _query_freegeoip(self, ip, timeout):
                                                                                                                                                                                                                                        """Query freegeoip.app for IP location"""""""""""
        try:
                                                                                                                                                                                                                                            url = self.api_urls['freegeoip'].format(ip)
                                                                                                                                                                                                                                            response = self._make_request(url, timeout)
            
            if not response:
                                                                                                                                                                                                                                            return None
                
                                                                                                                                                                                                                                            data = json.loads(response)
            
            if 'latitude' not in data or 'longitude' not in data:
                                                                                                                                                                                                                                                logger.warning(f"Invalid response from freegeoip.app: {data}")
                                                                                                                                                                                                                                            return None
                
                                                                                                                                                                                                                                            lat = data.get('latitude')
                                                                                                                                                                                                                                            lon = data.get('longitude')
                                                                                                                                                                                                                                            city = data.get('city', '')
                                                                                                                                                                                                                                            country = data.get('country_name', '')
                                                                                                                                                                                                                                            region = data.get('region_name', '')
            
                                                                                                                                                                                                                                        return self._create_location_dict(
                                                                                                                                                                                                                                        lat, lon, 
                                                                                                                                                                                                                                        f"IP: {ip} ({city}, {region}, {country})",
                                                                                                                                                                                                                                        "freegeoip.app"
                                                                                                                                                                                                                                        )
        except Exception as e:
                                                                                                                                                                                                                                            logger.error(f"Error in _query_freegeoip: {str(e)}")
                                                                                                                                                                                                                                        return None
            
    def _create_location_dict(self, lat, lon, location_name, source):
                                                                                                                                                                                                                                            """Create a standardized location dictionary"""""""""""
                                                                                                                                                                                                                                            now = datetime.datetime.now()
        
                                                                                                                                                                                                                                        return {
                                                                                                                                                                                                                                        'plugin': 'GeoIPPlugin',
                                                                                                                                                                                                                                        'date': now,
                                                                                                                                                                                                                                        'lat': float(lat),
                                                                                                                                                                                                                                        'lon': float(lon),
                                                                                                                                                                                                                                        'shortName': location_name,
                                                                                                                                                                                                                                        'context': f"Located via {source} at {now.strftime('%Y-%m-%d %H:%M:%S')}",
                                                                                                                                                                                                                                        'infowindow': f"<b>{location_name}</b><br>Located via {source}<br>at {now.strftime('%Y-%m-%d %H:%M:%S')}"
                                                                                                                                                                                                                                        }
        
    def _make_request(self, url, timeout=10):
                                                                                                                                                                                                                                            """Make a HTTP request with proper error handling"""""""""""
        try:
                                                                                                                                                                                                                                                request = urllib.request.Request(
                                                                                                                                                                                                                                                url,
                                                                                                                                                                                                                                                headers={
                                                                                                                                                                                                                                                'User-Agent': f'CreepyAI/1.0 GeoIPPlugin/1.0',
                                                                                                                                                                                                                                                'Accept': 'application/json'
                                                                                                                                                                                                                                                }
                                                                                                                                                                                                                                                )
            
                                                                                                                                                                                                                                                response = urllib.request.urlopen(request, timeout=timeout)
                                                                                                                                                                                                                                            return response.read().decode('utf-8')
        except HTTPError as e:
                                                                                                                                                                                                                                                logger.error(f"HTTP Error making request to {url}: {e.code} - {e.reason}")
                                                                                                                                                                                                                                            return None
        except URLError as e:
                                                                                                                                                                                                                                                logger.error(f"URL Error making request to {url}: {str(e.reason)}")
                                                                                                                                                                                                                                            return None
        except Exception as e:
                                                                                                                                                                                                                                                logger.error(f"Unexpected error making request to {url}: {str(e)}")
                                                                                                                                                                                                                                            return None
            
    def _is_ip_address(self, ip):
                                                                                                                                                                                                                                                """Check if string is a valid IP address"""""""""""
        try:
                                                                                                                                                                                                                                                    socket.inet_aton(ip)
                                                                                                                                                                                                                                                return True
        except socket.error:
                                                                                                                                                                                                                                                return False
    
    def _is_private_ip(self, ip):
                                                                                                                                                                                                                                                    """Check if IP address is private"""""""""""
        # Check for localhost
        if ip.startswith('127.') or ip == '::1':
                                                                                                                                                                                                                                                    return True
            
        # Check for RFC1918 private addresses
                                                                                                                                                                                                                                                    octets = ip.split('.')
        if len(octets) == 4:
            try:
                                                                                                                                                                                                                                                            first = int(octets[0])
                                                                                                                                                                                                                                                            second = int(octets[1])
                
                                                                                                                                                                                                                                                            if first == 10:  # 10.0.0.0/8
                                                                                                                                                                                                                                                        return True
                                                                                                                                                                                                                                                        elif first == 172 and 16 <= second <= 31:  # 172.16.0.0/12
                                                                                                                                                                                                                                                    return True
                                                                                                                                                                                                                                                    elif first == 192 and second == 168:  # 192.168.0.0/16
                                                                                                                                                                                                                                                return True
                                                                                                                                                                                                                                                elif first == 169 and second == 254:  # 169.254.0.0/16 (link-local)
                                                                                                                                                                                                                                            return True
                                                                                                                                                                                                                                            elif first == 0:  # 0.0.0.0/8 (current network)
                                                                                                                                                                                                                                        return True
            except ValueError:
                                                                                                                                                                                                                                        pass
                
                                                                                                                                                                                                                                    return False
            
    def getLabelForKey(self, key):
                                                                                                                                                                                                                                        """Get human-readable label for a configuration key"""""""""""
                                                                                                                                                                                                                                        labels = {
                                                                                                                                                                                                                                        'ipgeolocation_api_key': 'IPGeolocation.io API Key',
                                                                                                                                                                                                                                        'target_list': 'Default Target IP List',
                                                                                                                                                                                                                                        'rate_limit': 'Rate Limit (requests/second)',
                                                                                                                                                                                                                                        'timeout': 'Request Timeout (seconds)',
                                                                                                                                                                                                                                        'default_service': 'Default Geolocation Service',
                                                                                                                                                                                                                                        'cache_directory': 'Cache Directory',
                                                                                                                                                                                                                                        'enabled': 'Plugin Enabled',
                                                                                                                                                                                                                                        'use_ipapi': 'Use ipapi.co Service',
                                                                                                                                                                                                                                        'use_ipinfo': 'Use ipinfo.io Service',
                                                                                                                                                                                                                                        'use_ipgeolocation': 'Use ipgeolocation.io Service (requires API key)',
                                                                                                                                                                                                                                        'use_freegeoip': 'Use freegeoip.app Service',
                                                                                                                                                                                                                                        'use_cache': 'Use Location Cache (30 days)',
                                                                                                                                                                                                                                        'skip_private_ips': 'Skip Private IP Addresses'
                                                                                                                                                                                                                                        }
                                                                                                                                                                                                                                    return labels.get(key, InputPlugin.getLabelForKey(self, key))
