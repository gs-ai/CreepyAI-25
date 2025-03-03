#!/usr/bin/python
# -*- coding: utf-8 -*-
from creepy.models.InputPlugin import InputPlugin
import os
import datetime
import json
import logging
import requests
import time
import traceback
import threading
import re
import tempfile
import urllib.request
from configobj import ConfigObj
from PyQt5.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QTextBrowser, QApplication,
                            QMessageBox, QProgressBar, QCheckBox, QComboBox)
from PyQt5.QtCore import QUrl, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QDesktopServices
import webbrowser

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class RateLimiter:
    """Rate limiter for API calls"""
    def __init__(self, max_calls=10, time_window=60):
        self.max_calls = max_calls  # Max calls allowed in time window
        self.time_window = time_window  # Time window in seconds
        self.calls = []  # List to track timestamps of calls
        self.lock = threading.Lock()  # Thread safety

    def wait_if_needed(self):
        """Wait if we're exceeding rate limits"""
        with self.lock:
            now = time.time()
            # Remove calls that are outside the time window
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            
            # If we're at the limit, wait until oldest call expires
            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_window - (now - self.calls[0])
                if sleep_time > 0:
                    logger.debug(f"Rate limit reached, waiting {sleep_time:.2f} seconds")
                    time.sleep(sleep_time + 0.1)  # Add a small buffer
            
            # Record this call
            self.calls.append(time.time())

class FacebookAuthHandler(QObject):
    auth_complete = pyqtSignal(str)
    
    def __init__(self, client_id, redirect_uri):
        super().__init__()
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        
    def start_auth(self):
        """Open browser to start Facebook OAuth flow"""
        auth_url = (
            f"https://www.facebook.com/v16.0/dialog/oauth?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"scope=user_photos,user_posts,user_location,user_tagged_places&"
            f"response_type=token"
        )
        QDesktopServices.openUrl(QUrl(auth_url))

class TokenRefreshThread(QThread):
    """Thread to check token validity and refresh if needed"""
    token_expired = pyqtSignal()
    token_valid = pyqtSignal(str)
    
    def __init__(self, access_token, client_id, client_secret):
        super().__init__()
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        
    def run(self):
        try:
            # Check token validity with a basic API call
            url = f"https://graph.facebook.com/v16.0/me?access_token={self.access_token}"
            response = requests.get(url)
            
            # If unauthorized, try to refresh the token
            if response.status_code != 200:
                logger.warning("Token appears to be invalid or expired")
                self.token_expired.emit()
                return
                
            # Token is valid
            self.token_valid.emit(self.access_token)
        except Exception as e:
            logger.error(f"Error checking token validity: {str(e)}")
            self.token_expired.emit()

class FacebookDataFetchThread(QThread):
    """Thread to fetch data from Facebook in the background"""
    progress_signal = pyqtSignal(int, str)
    complete_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, api, user_id, max_results=1000):
        super().__init__()
        self.api = api
        self.user_id = user_id
        self.max_results = max_results
        self.rate_limiter = RateLimiter(20, 60)  # 20 calls per minute
        self.locations = []
        self.should_stop = False
        
    def run(self):
        try:
            total_fetched = 0
            
            # Step 1: Fetch photos with locations
            self.progress_signal.emit(5, "Fetching photos with location data...")
            photos = self._extract_photos_with_locations(self.user_id, self.max_results//2)
            if self.should_stop:
                return
            
            total_fetched += len(photos)
            self.progress_signal.emit(40, f"Found {len(photos)} photos with location data")
            
            # Step 2: Fetch check-ins
            self.progress_signal.emit(45, "Fetching check-ins...")
            check_ins = self._extract_check_ins(self.user_id, self.max_results//2)
            if self.should_stop:
                return
                
            total_fetched += len(check_ins)
            self.progress_signal.emit(70, f"Found {len(check_ins)} check-ins")
            
            # Step 3: Fetch tagged places
            self.progress_signal.emit(75, "Fetching tagged places...")
            tagged_places = self._extract_tagged_places(self.user_id, self.max_results//2)
            if self.should_stop:
                return
                
            total_fetched += len(tagged_places)
            self.progress_signal.emit(90, f"Found {len(tagged_places)} tagged places")
            
            # Step 4: Process all data into locations
            self.progress_signal.emit(95, "Processing location data...")
            locations = []
            
            # Process photos
            for photo in photos:
                try:
                    if 'place' in photo and 'location' in photo['place']:
                        location = photo['place']['location']
                        
                        if 'latitude' in location and 'longitude' in location:
                            # Parse date
                            try:
                                date = datetime.datetime.strptime(
                                    photo.get('created_time', ''), 
                                    '%Y-%m-%dT%H:%M:%S%z'
                                )
                            except:
                                date = datetime.datetime.now()
                            
                            # Create location object
                            loc = {
                                'plugin': 'facebook',
                                'lat': location['latitude'],
                                'lon': location['longitude'],
                                'date': date,
                                'context': f"Photo at {photo['place'].get('name', 'Unknown Location')}",
                                'infowindow': self._create_photo_infowindow(photo),
                                'shortName': photo['place'].get('name', 'Photo'),
                                'data_type': 'photo',
                                'raw_data': photo
                            }
                            locations.append(loc)
                except Exception as e:
                    logger.error(f"Error processing photo: {str(e)}")
            
            # Process check-ins
            for check_in in check_ins:
                try:
                    if 'place' in check_in and 'location' in check_in['place']:
                        location = check_in['place']['location']
                        
                        if 'latitude' in location and 'longitude' in location:
                            # Parse date
                            try:
                                date = datetime.datetime.strptime(
                                    check_in.get('created_time', ''), 
                                    '%Y-%m-%dT%H:%M:%S%z'
                                )
                            except:
                                date = datetime.datetime.now()
                            
                            # Create location object
                            loc = {
                                'plugin': 'facebook',
                                'lat': location['latitude'],
                                'lon': location['longitude'],
                                'date': date,
                                'context': f"Check-in at {check_in['place'].get('name', 'Unknown Location')}",
                                'infowindow': self._create_checkin_infowindow(check_in),
                                'shortName': check_in['place'].get('name', 'Check-in'),
                                'data_type': 'checkin',
                                'raw_data': check_in
                            }
                            locations.append(loc)
                except Exception as e:
                    logger.error(f"Error processing check-in: {str(e)}")
            
            # Process tagged places
            for place in tagged_places:
                try:
                    if 'place' in place and 'location' in place['place']:
                        location = place['place']['location']
                        
                        if 'latitude' in location and 'longitude' in location:
                            # Parse date
                            try:
                                date = datetime.datetime.strptime(
                                    place.get('created_time', ''), 
                                    '%Y-%m-%dT%H:%M:%S%z'
                                )
                            except:
                                date = datetime.datetime.now()
                            
                            # Create location object
                            loc = {
                                'plugin': 'facebook',
                                'lat': location['latitude'],
                                'lon': location['longitude'],
                                'date': date,
                                'context': f"Tagged at {place['place'].get('name', 'Unknown Location')}",
                                'infowindow': self._create_tagged_place_infowindow(place),
                                'shortName': place['place'].get('name', 'Tagged'),
                                'data_type': 'tagged',
                                'raw_data': place
                            }
                            locations.append(loc)
                except Exception as e:
                    logger.error(f"Error processing tagged place: {str(e)}")
            
            # Sort by date
            locations.sort(key=lambda x: x['date'])
            
            self.progress_signal.emit(100, f"Completed! Found {len(locations)} locations")
            self.complete_signal.emit(locations)
            
        except Exception as e:
            logger.error(f"Error in data fetch thread: {str(e)}")
            logger.debug(traceback.format_exc())
            self.error_signal.emit(str(e))
            
    def _extract_photos_with_locations(self, user_id, limit=500):
        """Extract photos with location data for the user"""
        logger.info(f"Extracting photos with location data for user {user_id}")
        
        photos_with_locations = []
        next_page = f"{self.api['base_url']}/{user_id}/photos?fields=id,created_time,place,name,link,picture,source&limit=100&access_token={self.api['access_token']}"
        
        while next_page and len(photos_with_locations) < limit and not self.should_stop:
            try:
                self.rate_limiter.wait_if_needed()
                logger.debug(f"Fetching page of photo results")
                response = requests.get(next_page)
                
                if response.status_code != 200:
                    error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                    logger.error(f"API error: {error_msg}")
                    break
                    
                data = response.json()
                photos = data.get('data', [])
                
                # Process photos with location data
                for photo in photos:
                    if 'place' in photo and 'location' in photo['place']:
                        location = photo['place']['location']
                        
                        if 'latitude' in location and 'longitude' in location:
                            photos_with_locations.append(photo)
                            logger.debug(f"Found photo with location: {photo.get('id')}")
                
                # Check for pagination
                next_page = data.get('paging', {}).get('next')
                
                # Update progress
                if limit > 0:
                    progress = min(35, int(35 * len(photos_with_locations) / limit))
                    self.progress_signal.emit(progress, f"Found {len(photos_with_locations)} photos with location data")
                    
            except Exception as e:
                logger.error(f"Error fetching photos: {str(e)}")
                logger.debug(traceback.format_exc())
                break
                
        logger.info(f"Found {len(photos_with_locations)} photos with location data")
        return photos_with_locations
    
    def _extract_check_ins(self, user_id, limit=250):
        """Extract check-ins for the user"""
        logger.info(f"Extracting check-ins for user {user_id}")
        
        check_ins = []
        next_page = f"{self.api['base_url']}/{user_id}/posts?fields=place,message,created_time&limit=100&access_token={self.api['access_token']}"
        
        while next_page and len(check_ins) < limit and not self.should_stop:
            try:
                self.rate_limiter.wait_if_needed()
                logger.debug(f"Fetching page of posts")
                response = requests.get(next_page)
                
                if response.status_code != 200:
                    error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                    logger.error(f"API error: {error_msg}")
                    break
                    
                data = response.json()
                posts = data.get('data', [])
                
                # Process posts with place data
                for post in posts:
                    if 'place' in post and 'location' in post['place']:
                        location = post['place']['location']
                        
                        if 'latitude' in location and 'longitude' in location:
                            check_ins.append(post)
                            logger.debug(f"Found check-in: {post.get('id')}")
                
                # Check for pagination
                next_page = data.get('paging', {}).get('next')
                
                # Update progress
                if limit > 0:
                    progress = 40 + min(25, int(25 * len(check_ins) / limit))
                    self.progress_signal.emit(progress, f"Found {len(check_ins)} check-ins")
                    
            except Exception as e:
                logger.error(f"Error fetching check-ins: {str(e)}")
                logger.debug(traceback.format_exc())
                break
                
        logger.info(f"Found {len(check_ins)} check-ins with location data")
        return check_ins
    
    def _extract_tagged_places(self, user_id, limit=250):
        """Extract places where the user was tagged"""
        logger.info(f"Extracting tagged places for user {user_id}")
        
        tagged_places = []
        next_page = f"{self.api['base_url']}/{user_id}/tagged_places?limit=100&access_token={self.api['access_token']}"
        
        while next_page and len(tagged_places) < limit and not self.should_stop:
            try:
                self.rate_limiter.wait_if_needed()
                logger.debug(f"Fetching page of tagged places")
                response = requests.get(next_page)
                
                if response.status_code != 200:
                    error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                    logger.error(f"API error: {error_msg}")
                    break
                    
                data = response.json()
                places = data.get('data', [])
                
                # All tagged places have location data
                tagged_places.extend(places)
                
                # Check for pagination
                next_page = data.get('paging', {}).get('next')
                
                # Update progress
                if limit > 0:
                    progress = 70 + min(20, int(20 * len(tagged_places) / limit))
                    self.progress_signal.emit(progress, f"Found {len(tagged_places)} tagged places")
                    
            except Exception as e:
                logger.error(f"Error fetching tagged places: {str(e)}")
                logger.debug(traceback.format_exc())
                break
                
        logger.info(f"Found {len(tagged_places)} tagged places")
        return tagged_places
            
    def _create_photo_infowindow(self, photo):
        """Create info window HTML for a photo"""
        place_name = photo.get('place', {}).get('name', 'Unknown Location')
        photo_name = photo.get('name', 'No caption')
        created_time = photo.get('created_time', 'Unknown date')
        
        try:
            date_obj = datetime.datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S%z')
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            formatted_date = created_time
            
        thumbnail = photo.get('picture', '')
        source = photo.get('source', '')  # Full-size image if available
        link = photo.get('link', f"https://www.facebook.com/{photo.get('id', '')}")
        
        html = f"""<div class="facebook-photo">
            <h3>Photo at {place_name}</h3>
            <div class="photo-content">
                <img src="{thumbnail}" alt="Photo thumbnail" class="thumbnail" onclick="window.open('{source or link}', '_blank')">
                <div class="photo-details">
                    <p><strong>Caption:</strong> {photo_name}</p>
                    <p><strong>Date:</strong> {formatted_date}</p>
                    <p><strong>Location:</strong> {place_name}</p>
                </div>
            </div>
            <p><a href="{link}" target="_blank">View on Facebook</a></p>
        </div>"""
        
        return html
    
    def _create_checkin_infowindow(self, check_in):
        """Create info window HTML for a check-in"""
        place_name = check_in.get('place', {}).get('name', 'Unknown Location')
        message = check_in.get('message', 'No message')
        created_time = check_in.get('created_time', 'Unknown date')
        
        try:
            date_obj = datetime.datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S%z')
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            formatted_date = created_time
            
        link = f"https://www.facebook.com/{check_in.get('id', '')}"
        
        html = f"""<div class="facebook-checkin">
            <h3>Check-in at {place_name}</h3>
            <div class="checkin-details">
                <p><strong>Message:</strong> {message}</p>
                <p><strong>Date:</strong> {formatted_date}</p>
                <p><strong>Location:</strong> {place_name}</p>
                <p><strong>Address:</strong> {self._format_address(check_in.get('place', {}).get('location', {}))}</p>
            </div>
            <p><a href="{link}" target="_blank">View on Facebook</a></p>
        </div>"""
        
        return html
        
    def _create_tagged_place_infowindow(self, place):
        """Create info window HTML for a tagged place"""
        place_name = place.get('place', {}).get('name', 'Unknown Location')
        created_time = place.get('created_time', 'Unknown date')
        
        try:
            date_obj = datetime.datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S%z')
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            formatted_date = created_time
            
        link = f"https://www.facebook.com/{place.get('id', '')}"
        
        html = f"""<div class="facebook-tagged">
            <h3>Tagged at {place_name}</h3>
            <div class="place-details">
                <p><strong>Date:</strong> {formatted_date}</p>
                <p><strong>Location:</strong> {place_name}</p>
                <p><strong>Address:</strong> {self._format_address(place.get('place', {}).get('location', {}))}</p>
            </div>
            <p><a href="{link}" target="_blank">View on Facebook</a></p>
        </div>"""
        
        return html
        
    def _format_address(self, location_obj):
        """Format the address from location components"""
        address_parts = []
        
        if 'street' in location_obj:
            address_parts.append(location_obj['street'])
        
        city_parts = []
        if 'city' in location_obj:
            city_parts.append(location_obj['city'])
        if 'state' in location_obj:
            city_parts.append(location_obj['state'])
        if 'zip' in location_obj:
            city_parts.append(location_obj['zip'])
        
        if city_parts:
            address_parts.append(", ".join(city_parts))
            
        if 'country' in location_obj:
            address_parts.append(location_obj['country'])
            
        if address_parts:
            return "<br>".join(address_parts)
        return "No address available"
        
    def stop(self):
        """Stop the thread"""
        self.should_stop = True

class FacebookPlugin(InputPlugin):
    name = "facebook"
    hasWizard = True
    
    def __init__(self):
        InputPlugin.__init__(self)
        self.description = "Extract location data from Facebook photos, check-ins and tagged places"
        self.searchOffline = False
        
        # Load configuration
        self._config_path = os.path.join(os.path.expanduser("~"), ".creepy", "facebook.conf")
        self._cache_path = os.path.join(os.path.expanduser("~"), ".creepy", "facebook_cache")
        os.makedirs(self._cache_path, exist_ok=True)
        self._load_config()
        
        # Load labels
        try:
            labels_file = os.path.join(os.path.dirname(__file__), 'facebook.labels')
            labels_config = ConfigObj(infile=labels_file)
            self.labels = labels_config.get('labels', {})
        except Exception as e:
            logger.error(f"Error loading labels: {str(e)}")
            self.labels = {}
        
        # Initialize API client
        self.api = None
        self.fetch_thread = None
        if self.configured:
            self._initialize_api()
            
    def _load_config(self):
        """Load configuration from file"""
        self.configured = False
        self.config = {}
        
        config_dir = os.path.dirname(self._config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r') as f:
                    self.config = json.load(f)
                    
                # Check if we have the necessary config values
                if (self.config.get('client_id') and 
                    self.config.get('access_token')):
                    self.configured = True
            except Exception as e:
                logger.error(f"Failed to load config: {str(e)}")
                
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self._config_path, 'w') as f:
                json.dump(self.config, f)
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")
            
    def _initialize_api(self):
        """Initialize the Facebook API client"""
        self.api = {
            'access_token': self.config.get('access_token', ''),
            'base_url': 'https://graph.facebook.com/v16.0'
        }
        self._check_token_validity()
        
    def _check_token_validity(self):
        """Check if the token is still valid"""
        if not self.configured or not self.api:
            return False
            
        try:
            me_url = f"{self.api['base_url']}/me?access_token={self.api['access_token']}"
            response = requests.get(me_url)
            return response.status_code == 200
        except:
            return False
        
    def activate(self):
        logger.info("FacebookPlugin activated")
        if not self.configured:
            logger.warning("Facebook plugin is not configured yet")
        
    def deactivate(self):
        logger.info("FacebookPlugin deactivated")
        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.stop()
    
    def isConfigured(self):
        """Check if the plugin is properly configured"""
        if not self.configured:
            return (False, "Please configure Facebook API credentials")
            
        # Test the API with a simple request
        try:
            token_valid = self._check_token_validity()
            if token_valid:
                me_url = f"{self.api['base_url']}/me?access_token={self.api['access_token']}"
                response = requests.get(me_url)
                user_data = response.json()
                return (True, f"Authenticated as {user_data.get('name', 'Unknown')}")
            else:
                return (False, "Facebook access token is invalid or expired")
        except Exception as e:
            logger.error(f"Error checking API connection: {str(e)}")
            return (False, f"Failed to connect to Facebook API: {str(e)}")
    
    def searchForTargets(self, search_term):
        """Search for targets matching the search term"""
        logger.info(f"Searching for Facebook users matching: {search_term}")
        
        if not self.configured or not self.api:
            logger.error("Plugin not configured properly")
            return []
            
        targets = []
        
        # First check if the token is valid
        if not self._check_token_validity():
            return [{
                'targetUsername': 'token_expired',
                'targetUserid': 'token_expired',
                'targetFullname': 'Facebook token expired - please reconfigure',
                'targetPicture': '',
                'pluginName': self.name
            }]
        
        # First, try to search by ID or username if it looks like one
        if search_term.isdigit() or not any(c.isspace() for c in search_term):
            try:
                # Try direct profile lookup
                profile_url = f"{self.api['base_url']}/{search_term}?fields=id,name,picture&access_token={self.api['access_token']}"
                response = requests.get(profile_url)
                
                if response.status_code == 200:
                    user = response.json()
                    logger.debug(f"Found exact match: {user.get('name')}")
                    
                    # Get profile picture URL
                    pic_url = user.get('picture', {}).get('data', {}).get('url', '')
                    pic_filename = f"{user.get('id')}_profile.jpg"
                    pic_path = os.path.join(os.getcwd(), "temp", pic_filename)
                    
                    # Download profile picture if it doesn't exist already
                    if pic_url and not os.path.exists(pic_path):
                        try:
                            urllib.request.urlretrieve(pic_url, pic_path)
                        except Exception as e:
                            logger.error(f"Error downloading profile picture: {str(e)}")
                    
                    # Create target
                    targets.append({
                        'targetUsername': user.get('id'),
                        'targetUserid': user.get('id'),
                        'targetFullname': user.get('name', 'Unknown User'),
                        'targetPicture': pic_filename if os.path.exists(pic_path) else '',
                        'pluginName': self.name
                    })
            except Exception as e:
                logger.error(f"Error in direct lookup: {str(e)}")
        
        # If no direct match, use search API
        if not targets:
            try:
                search_url = f"{self.api['base_url']}/search?q={search_term}&type=user&fields=id,name,picture&access_token={self.api['access_token']}"
                response = requests.get(search_url)
                
                if response.status_code == 200:
                    results = response.json().get('data', [])
                    logger.debug(f"Found {len(results)} search results")
                    
                    for user in results:
                        # Get profile picture URL
                        pic_url = user.get('picture', {}).get('data', {}).get('url', '')
                        pic_filename = f"{user.get('id')}_profile.jpg"
                        pic_path = os.path.join(os.getcwd(), "temp", pic_filename)
                        
                        # Download profile picture if it doesn't exist already
                        if pic_url and not os.path.exists(pic_path):
                            try:
                                urllib.request.urlretrieve(pic_url, pic_path)
                            except Exception as e:
                                logger.error(f"Error downloading profile picture: {str(e)}")
                        
                        targets.append({
                            'targetUsername': user.get('id'),
                            'targetUserid': user.get('id'),
                            'targetFullname': user.get('name', 'Unknown User'),
                            'targetPicture': pic_filename if os.path.exists(pic_path) else '',
                            'pluginName': self.name
                        })
            except Exception as e:
                logger.error(f"Error in search: {str(e)}")
                
        # If still no results, offer to search manually
        if not targets:
            targets.append({
                'targetUsername': search_term,
                'targetUserid': search_term,
                'targetFullname': f"Search manually: {search_term}",
                'targetPicture': '',
                'pluginName': self.name
            })
            
        return targets
    
    def returnLocations(self, target, search_params):
        """Return location data for the target"""
        logger.info(f"Getting locations for {target.get('targetFullname', target.get('targetUsername'))}")
        
        if not self.configured or not self.api:
            logger.error("Plugin not configured properly")
            return []
            
        # Check if token is valid
        if not self._check_token_validity():
            logger.error("Facebook access token is invalid or expired")
            return []
            
        user_id = target['targetUserid']
        
        # Check if we already have cached results for this target
        cache_file = os.path.join(self._cache_path, f"{user_id}_locations.json")
        if os.path.exists(cache_file) and self.config.get('use_cache', True):
            try:
                cache_age = time.time() - os.path.getmtime(cache_file)
                # Use cache if it's less than 24 hours old
                if cache_age < 86400:
                    logger.info(f"Using cached location data for {user_id}")
                    with open(cache_file, 'r') as f:
                        locations = json.load(f)
                    return locations
            except Exception as e:
                logger.warning(f"Error reading cache: {str(e)}")
        
        # Show progress dialog and start data fetch thread
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
            from PyQt5.QtCore import Qt
            
            # Create progress dialog
            dialog = QDialog()
            dialog.setWindowTitle("Facebook Data Fetch")
            dialog.setFixedSize(400, 150)
            layout = QVBoxLayout()
            
            status_label = QLabel("Initializing...")
            layout.addWidget(status_label)
            
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            layout.addWidget(progress_bar)
            
            cancel_button = QPushButton("Cancel")
            layout.addWidget(cancel_button)
            
            dialog.setLayout(layout)
            
            # Create and start data fetch thread
            fetch_thread = FacebookDataFetchThread(self.api, user_id)
            
            # Connect signals
            def update_progress(value, message):
                progress_bar.setValue(value)
                status_label.setText(message)
                
            def fetch_complete(locations_data):
                # Cache the results
                try:
                    with open(cache_file, 'w') as f:
                        json.dump(locations_data, f)
                except Exception as e:
                    logger.warning(f"Error writing cache: {str(e)}")
                
                dialog.accept()
                
            def fetch_error(error_message):
                from PyQt5.QtWidgets import QMessageBox
                dialog.accept()
                QMessageBox.warning(dialog, "Error", f"Error fetching data: {error_message}")
                
            def cancel_fetch():
                fetch_thread.stop()
                dialog.reject()
                
            fetch_thread.progress_signal.connect(update_progress)
            fetch_thread.complete_signal.connect(fetch_complete)
            fetch_thread.error_signal.connect(fetch_error)
            cancel_button.clicked.connect(cancel_fetch)
            
            # Start thread and show dialog
            fetch_thread.start()
            if dialog.exec_() == QDialog.Accepted and not fetch_thread.should_stop:
                return fetch_thread.locations
            else:
                return []
                
        except ImportError:
            # Fall back to non-GUI method if we can't import PyQt
            logger.warning("PyQt not available, falling back to non-GUI method")
            return self._fetch_locations_non_gui(user_id, cache_file)
        
    def _fetch_locations_non_gui(self, user_id, cache_file):
        """Fetch locations without GUI progress dialog"""
        logger.info(f"Starting non-GUI data fetch for {user_id}")
        
        try:
            # Create data fetch manually
            locations = []
            
            # Step 1: Fetch photos with locations
            photos = self._extract_photos_with_locations_non_threaded(user_id, 200)
            logger.info(f"Found {len(photos)} photos with location data")
            
            # Process photos
            for photo in photos:
                try:
                    if 'place' in photo and 'location' in photo['place']:
                        location = photo['place']['location']
                        
                        if 'latitude' in location and 'longitude' in location:
                            # Parse date
                            try:
                                date = datetime.datetime.strptime(
                                    photo.get('created_time', ''), 
                                    '%Y-%m-%dT%H:%M:%S%z'
                                )
                            except:
                                date = datetime.datetime.now()
                            
                            # Create location object
                            loc = {
                                'plugin': self.name,
                                'lat': location['latitude'],
                                'lon': location['longitude'],
                                'date': date.strftime('%Y-%m-%dT%H:%M:%S%z'),  # Serialize datetime
                                'context': f"Photo at {photo['place'].get('name', 'Unknown Location')}",
                                'infowindow': self._create_photo_infowindow_static(photo),
                                'shortName': photo['place'].get('name', 'Photo')
                            }
                            locations.append(loc)
                except Exception as e:
                    logger.error(f"Error processing photo: {str(e)}")
            
            # Step 2: Fetch check-ins
            check_ins = self._extract_check_ins_non_threaded(user_id, 100)
            logger.info(f"Found {len(check_ins)} check-ins")
            
            # Process check-ins
            for check_in in check_ins:
                try:
                    if 'place' in check_in and 'location' in check_in['place']:
                        location = check_in['place']['location']
                        
                        if 'latitude' in location and 'longitude' in location:
                            # Parse date
                            try:
                                date = datetime.datetime.strptime(
                                    check_in.get('created_time', ''), 
                                    '%Y-%m-%dT%H:%M:%S%z'
                                )
                            except:
                                date = datetime.datetime.now()
                            
                            # Create location object
                            loc = {
                                'plugin': self.name,
                                'lat': location['latitude'],
                                'lon': location['longitude'],
                                'date': date.strftime('%Y-%m-%dT%H:%M:%S%z'),  # Serialize datetime
                                'context': f"Check-in at {check_in['place'].get('name', 'Unknown Location')}",
                                'infowindow': self._create_checkin_infowindow_static(check_in),
                                'shortName': check_in['place'].get('name', 'Check-in')
                            }
                            locations.append(loc)
                except Exception as e:
                    logger.error(f"Error processing check-in: {str(e)}")
            
            # Step 3: Fetch tagged places
            tagged_places = self._extract_tagged_places_non_threaded(user_id, 100)
            logger.info(f"Found {len(tagged_places)} tagged places")
            
            # Process tagged places
            for place in tagged_places:
                try:
                    if 'place' in place and 'location' in place['place']:
                        location = place['place']['location']
                        
                        if 'latitude' in location and 'longitude' in location:
                            # Parse date
                            try:
                                date = datetime.datetime.strptime(
                                    place.get('created_time', ''), 
                                    '%Y-%m-%dT%H:%M:%S%z'
                                )
                            except:
                                date = datetime.datetime.now()
                            
                            # Create location object
                            loc = {
                                'plugin': self.name,
                                'lat': location['latitude'],
                                'lon': location['longitude'],
                                'date': date.strftime('%Y-%m-%dT%H:%M:%S%z'),  # Serialize datetime
                                'context': f"Tagged at {place['place'].get('name', 'Unknown Location')}",
                                'infowindow': self._create_tagged_place_infowindow_static(place),
                                'shortName': place['place'].get('name', 'Tagged')
                            }
                            locations.append(loc)
                except Exception as e:
                    logger.error(f"Error processing tagged place: {str(e)}")
            
            # Sort by date
            locations.sort(key=lambda x: x['date'])
            
            # Cache the results
            try:
                with open(cache_file, 'w') as f:
                    json.dump(locations, f)
            except Exception as e:
                logger.warning(f"Error writing cache: {str(e)}")
                
            return locations
        except Exception as e:
            logger.error(f"Error in non-GUI fetch: {str(e)}")
            logger.debug(traceback.format_exc())
            return []
            
    def _extract_photos_with_locations_non_threaded(self, user_id, limit=200):
        """Extract photos with location data (non-threaded version)"""
        rate_limiter = RateLimiter(20, 60)  # 20 calls per minute
        photos_with_locations = []
        next_page = f"{self.api['base_url']}/{user_id}/photos?fields=id,created_time,place,name,link,picture,source&limit=100&access_token={self.api['access_token']}"
        
        while next_page and len(photos_with_locations) < limit:
            try:
                rate_limiter.wait_if_needed()
                response = requests.get(next_page)
                
                if response.status_code != 200:
                    break
                    
                data = response.json()
                photos = data.get('data', [])
                
                for photo in photos:
                    if 'place' in photo and 'location' in photo['place']:
                        location = photo['place']['location']
                        if 'latitude' in location and 'longitude' in location:
                            photos_with_locations.append(photo)
                
                next_page = data.get('paging', {}).get('next')
            except:
                break
                
        return photos_with_locations
        
    def _extract_check_ins_non_threaded(self, user_id, limit=100):
        """Extract check-ins (non-threaded version)"""
        rate_limiter = RateLimiter(20, 60)
        check_ins = []
        next_page = f"{self.api['base_url']}/{user_id}/posts?fields=place,message,created_time&limit=100&access_token={self.api['access_token']}"
        
        while next_page and len(check_ins) < limit:
            try:
                rate_limiter.wait_if_needed()
                response = requests.get(next_page)
                
                if response.status_code != 200:
                    break
                    
                data = response.json()
                posts = data.get('data', [])
                
                for post in posts:
                    if 'place' in post and 'location' in post['place']:
                        location = post['place']['location']
                        if 'latitude' in location and 'longitude' in location:
                            check_ins.append(post)
                
                next_page = data.get('paging', {}).get('next')
            except:
                break
                
        return check_ins
        
    def _extract_tagged_places_non_threaded(self, user_id, limit=100):
        """Extract tagged places (non-threaded version)"""
        rate_limiter = RateLimiter(20, 60)
        tagged_places = []
        next_page = f"{self.api['base_url']}/{user_id}/tagged_places?limit=100&access_token={self.api['access_token']}"
        
        while next_page and len(tagged_places) < limit:
            try:
                rate_limiter.wait_if_needed()
                response = requests.get(next_page)
                
                if response.status_code != 200:
                    break
                    
                data = response.json()
                places = data.get('data', [])
                tagged_places.extend(places)
                
                next_page = data.get('paging', {}).get('next')
            except:
                break
                
        return tagged_places
    
    def _create_photo_infowindow_static(self, photo):
        """Create static info window HTML for a photo"""
        place_name = photo.get('place', {}).get('name', 'Unknown Location')
        photo_name = photo.get('name', 'No caption')
        created_time = photo.get('created_time', 'Unknown date')
        
        try:
            date_obj = datetime.datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S%z')
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            formatted_date = created_time
            
        thumbnail = photo.get('picture', '')
        source = photo.get('source', '')
        link = photo.get('link', f"https://www.facebook.com/{photo.get('id', '')}")
        
        html = f"""<div class="facebook-photo">
            <h3>Photo at {place_name}</h3>
            <div class="photo-content">
                <img src="{thumbnail}" alt="Photo thumbnail" class="thumbnail" onclick="window.open('{source or link}', '_blank')">
                <div class="photo-details">
                    <p><strong>Caption:</strong> {photo_name}</p>
                    <p><strong>Date:</strong> {formatted_date}</p>
                    <p><strong>Location:</strong> {place_name}</p>
                </div>
            </div>
            <p><a href="{link}" target="_blank">View on Facebook</a></p>
        </div>"""
        
        return html
    
    def _create_checkin_infowindow_static(self, check_in):
        """Create static info window HTML for a check-in"""
        place_name = check_in.get('place', {}).get('name', 'Unknown Location')
        message = check_in.get('message', 'No message')
        created_time = check_in.get('created_time', 'Unknown date')
        
        try:
            date_obj = datetime.datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S%z')
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            formatted_date = created_time
            
        link = f"https://www.facebook.com/{check_in.get('id', '')}"
        
        html = f"""<div class="facebook-checkin">
            <h3>Check-in at {place_name}</h3>
            <div class="checkin-details">
                <p><strong>Message:</strong> {message}</p>
                <p><strong>Date:</strong> {formatted_date}</p>
                <p><strong>Location:</strong> {place_name}</p>
                <p><strong>Address:</strong> {self._format_address_static(check_in.get('place', {}).get('location', {}))}</p>
            </div>
            <p><a href="{link}" target="_blank">View on Facebook</a></p>
        </div>"""
        
        return html
        
    def _create_tagged_place_infowindow_static(self, place):
        """Create static info window HTML for a tagged place"""
        place_name = place.get('place', {}).get('name', 'Unknown Location')
        created_time = place.get('created_time', 'Unknown date')
        
        try:
            date_obj = datetime.datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S%z')
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            formatted_date = created_time
            
        link = f"https://www.facebook.com/{place.get('id', '')}"
        
        html = f"""<div class="facebook-tagged">
            <h3>Tagged at {place_name}</h3>
            <div class="place-details">
                <p><strong>Date:</strong> {formatted_date}</p>
                <p><strong>Location:</strong> {place_name}</p>
                <p><strong>Address:</strong> {self._format_address_static(place.get('place', {}).get('location', {}))}</p>
            </div>
            <p><a href="{link}" target="_blank">View on Facebook</a></p>
        </div>"""
        
        return html
        
    def _format_address_static(self, location_obj):
        """Format address from location components (static version)"""
        address_parts = []
        
        if 'street' in location_obj:
            address_parts.append(location_obj['street'])
        
        city_parts = []
        if 'city' in location_obj:
            city_parts.append(location_obj['city'])
        if 'state' in location_obj:
            city_parts.append(location_obj['state'])
        if 'zip' in location_obj:
            city_parts.append(location_obj['zip'])
        
        if city_parts:
            address_parts.append(", ".join(city_parts))
            
        if 'country' in location_obj:
            address_parts.append(location_obj['country'])
            
        if address_parts:
            return "<br>".join(address_parts)
        return "No address available"
    
    def runConfigWizard(self):
        """Run configuration wizard to set up Facebook API access"""
        from PyQt5.QtWidgets import QWizard, QWizardPage, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextBrowser, QMessageBox
        from PyQt5.QtCore import Qt
        
        wizard = QWizard()
        wizard.setWindowTitle("Facebook Plugin Configuration")
        wizard.setMinimumSize(600, 500)
        
        # Welcome page
        welcome_page = QWizardPage()
        welcome_page.setTitle("Facebook Plugin Setup")
        
        welcome_layout = QVBoxLayout()
        welcome_text = QTextBrowser()
        welcome_text.setOpenExternalLinks(True)
        welcome_text.setHtml("""
        <h2>Welcome to Facebook Plugin Setup</h2>
        <p>This wizard will help you set up the Facebook plugin for CreepyAI.</p>
        <p>You'll need to create a Facebook Developer account and set up an app:</p>
        <ol>
            <li>Go to <a href="https://developers.facebook.com/">Facebook for Developers</a></li>
            <li>Create a new app (choose "Consumer" type)</li>
            <li>Add "Facebook Login" product to your app</li>
            <li>Set up a valid OAuth redirect URL (can be http://localhost/)</li>
        </ol>
        <p>After creating your app, you'll need the App ID and App Secret.</p>
        """)
        welcome_layout.addWidget(welcome_text)
        welcome_page.setLayout(welcome_layout)
        wizard.addPage(welcome_page)
        
        # App credentials page
        credentials_page = QWizardPage()
        credentials_page.setTitle("App Credentials")
        
        credentials_layout = QVBoxLayout()
        
        # App ID
        app_id_label = QLabel("App ID:")
        app_id_input = QLineEdit()
        app_id_input.setText(self.config.get('client_id', ''))
        credentials_layout.addWidget(app_id_label)
        credentials_layout.addWidget(app_id_input)
        
        # App Secret
        app_secret_label = QLabel("App Secret:")
        app_secret_input = QLineEdit()
        app_secret_input.setText(self.config.get('client_secret', ''))
        app_secret_input.setEchoMode(QLineEdit.Password)
        credentials_layout.addWidget(app_secret_label)
        credentials_layout.addWidget(app_secret_input)
        
        # Redirect URI
        redirect_uri_label = QLabel("Redirect URI:")
        redirect_uri_input = QLineEdit()
        redirect_uri_input.setText(self.config.get('redirect_uri', 'http://localhost/'))
        credentials_layout.addWidget(redirect_uri_label)
        credentials_layout.addWidget(redirect_uri_input)
        
        # Use cache option
        use_cache_checkbox = QCheckBox("Cache results to improve performance")
        use_cache_checkbox.setChecked(self.config.get('use_cache', True))
        credentials_layout.addWidget(use_cache_checkbox)
        
        # Note about data protection
        note_label = QLabel("<b>Note:</b> This plugin will download and cache data from Facebook. "
                           "Handle this data in accordance with local privacy laws.")
        credentials_layout.addWidget(note_label)
        
        credentials_page.setLayout(credentials_layout)
        wizard.addPage(credentials_page)
        
        # Auth page
        auth_page = QWizardPage()
        auth_page.setTitle("Authenticate with Facebook")
        
        auth_layout = QVBoxLayout()
        auth_text = QTextBrowser()
        auth_text.setHtml("""
        <h3>Facebook Authentication</h3>
        <p>Click the button below to open Facebook authentication in your browser.</p>
        <p>After authorizing, copy the access token from the URL and paste it below.</p>
        <p>The URL will look like: <code>http://localhost/#access_token=XXXXXXXX&...</code></p>
        """)
        auth_layout.addWidget(auth_text)
        
        # Auth button
        auth_button = QPushButton("Open Facebook Login")
        auth_layout.addWidget(auth_button)
        
        # Token input
        token_label = QLabel("Access Token:")
        token_input = QLineEdit()
        token_input.setText(self.config.get('access_token', ''))
        auth_layout.addWidget(token_label)
        auth_layout.addWidget(token_input)
        
        # Status label
        status_label = QLabel("")
        auth_layout.addWidget(status_label)
        
        auth_page.setLayout(auth_layout)
        wizard.addPage(auth_page)
        
        # Connect auth button
        def start_auth():
            client_id = app_id_input.text()
            redirect = redirect_uri_input.text()
            if client_id and redirect:
                auth_handler = FacebookAuthHandler(client_id, redirect)
                auth_handler.start_auth()
                status_label.setText("Browser opened, please authorize and copy the token")
            else:
                status_label.setText("Please enter App ID and Redirect URI first")
                
        auth_button.clicked.connect(start_auth)
        
        # Final page
        final_page = QWizardPage()
        final_page.setTitle("Setup Complete")
        
        final_layout = QVBoxLayout()
        final_text = QTextBrowser()
        final_text.setHtml("""
        <h3>Configuration Complete!</h3>
        <p>Your Facebook plugin is now configured and ready to use.</p>
        <p>You can now search for Facebook users and extract their location data.</p>
        <p>Note: The access token may expire after some time. If that happens, run this wizard again.</p>
        """)
        final_layout.addWidget(final_text)
        final_page.setLayout(final_layout)
        wizard.addPage(final_page)
        
        # Process results
        if wizard.exec_():
            # Save configuration
            self.config['client_id'] = app_id_input.text()
            self.config['client_secret'] = app_secret_input.text()
            self.config['redirect_uri'] = redirect_uri_input.text()
            self.config['access_token'] = token_input.text()
            self.config['use_cache'] = use_cache_checkbox.isChecked()
            
            self._save_config()
            self._initialize_api()
            self.configured = True
            
            QMessageBox.information(None, "Configuration Saved", 
                                   "Facebook plugin configuration has been saved successfully.")
            return True
        else:
            return False
    
    def getConfigurationParameters(self):
        """Return configuration parameters for the plugin"""
        return [
            {'name': 'client_id', 'type': 'string', 'default': ''},
            {'name': 'client_secret', 'type': 'password', 'default': ''},
            {'name': 'redirect_uri', 'type': 'string', 'default': 'http://localhost/'},
            {'name': 'access_token', 'type': 'password', 'default': ''},
            {'name': 'use_cache', 'type': 'boolean', 'default': True}
        ]
        
    def setConfigurationParameters(self, params):
        """Set configuration parameters for the plugin"""
        if 'client_id' in params and 'access_token' in params:
            self.config['client_id'] = params['client_id']
            self.config['client_secret'] = params.get('client_secret', '')
            self.config['redirect_uri'] = params.get('redirect_uri', 'http://localhost/')
            self.config['access_token'] = params['access_token']
            self.config['use_cache'] = params.get('use_cache', True)
            
            self._save_config()
            self._initialize_api()
            self.configured = True
            return (True, "Configuration saved successfully")
        else:
            return (False, "Required parameters missing")
            
    def getLabelForKey(self, key):
        """Return user-friendly labels for configuration keys"""
        labels = {
            "client_id": "Facebook App ID",
            "client_secret": "Facebook App Secret",
            "redirect_uri": "OAuth Redirect URI",
            "access_token": "Facebook Access Token",
            "use_cache": "Cache Results"
        }
        return labels.get(key, key)
