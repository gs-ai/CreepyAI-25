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
import urllib.request
from configobj import ConfigObj
from PyQt5.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QTextBrowser, QMessageBox,
                            QProgressBar, QCheckBox, QTableWidget, QTableWidgetItem,
                            QHBoxLayout, QHeaderView)
from PyQt5.QtCore import QUrl, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QDesktopServices
import webbrowser

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class RateLimiter:
    """Rate limiter for API calls"""
    def __init__(self, max_calls=10, time_window=60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = threading.Lock()

    def wait_if_needed(self):
        with self.lock:
            now = time.time()
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
            
            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_window - (now - self.calls[0])
                if sleep_time > 0:
                    logger.debug(f"Rate limit reached, waiting {sleep_time:.2f} seconds")
                    time.sleep(sleep_time + 0.1)
            
            self.calls.append(time.time())

class YelpDataFetchThread(QThread):
    """Thread to fetch data from Yelp in the background"""
    progress_signal = pyqtSignal(int, str)
    complete_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, api, search_params=None):
        super().__init__()
        self.api = api
        self.search_params = search_params or {}
        self.rate_limiter = RateLimiter(5, 60)  # 5 calls per minute - Yelp has strict limits
        self.should_stop = False
        
    def run(self):
        """Main thread execution to fetch Yelp data"""
        try:
            self.progress_signal.emit(10, "Initializing Yelp search...")
            
            # Get search parameters
            user_id = self.search_params.get('user_id', '')
            keyword = self.search_params.get('keyword', '')
            location = self.search_params.get('location', '')
            lat = self.search_params.get('lat')
            lon = self.search_params.get('lon')
            
            locations = []
            
            # Search by user's reviews
            if user_id:
                self.progress_signal.emit(20, f"Fetching reviews for Yelp user: {user_id}")
                reviews = self._get_user_reviews(user_id)
                
                if reviews:
                    self.progress_signal.emit(40, f"Found {len(reviews)} reviews. Processing location data...")
                    user_locations = self._extract_locations_from_reviews(reviews)
                    locations.extend(user_locations)
                
            # Search by keyword and location
            if keyword and (location or (lat is not None and lon is not None)):
                if location:
                    self.progress_signal.emit(60, f"Searching for businesses matching '{keyword}' in '{location}'")
                else:
                    self.progress_signal.emit(60, f"Searching for businesses matching '{keyword}' near coordinates")
                    
                businesses = self._search_businesses(keyword, location, lat, lon)
                
                if businesses:
                    self.progress_signal.emit(80, f"Found {len(businesses)} businesses. Processing location data...")
                    business_locations = self._extract_locations_from_businesses(businesses)
                    locations.extend(business_locations)
            
            self.progress_signal.emit(100, f"Completed! Found {len(locations)} locations from Yelp")
            self.complete_signal.emit(locations)
            
        except Exception as e:
            logger.error(f"Error in Yelp data fetch: {str(e)}")
            logger.debug(traceback.format_exc())
            self.error_signal.emit(str(e))
    
    def _get_user_reviews(self, user_id):
        """Get reviews for a Yelp user"""
        try:
            all_reviews = []
            offset = 0
            limit = 20
            
            while offset < 100 and not self.should_stop:  # Limit to 100 reviews max (5 pages)
                self.rate_limiter.wait_if_needed()
                
                headers = {
                    'Authorization': f"Bearer {self.api['api_key']}",
                    'Accept': 'application/json'
                }
                
                url = f"{self.api['base_url']}/users/{user_id}/reviews?limit={limit}&offset={offset}"
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"API Error: {response.status_code} - {response.text}")
                    break
                    
                data = response.json()
                reviews = data.get('reviews', [])
                
                if not reviews:
                    break
                    
                all_reviews.extend(reviews)
                
                # Update progress
                progress = min(50, int(20 + (30 * len(all_reviews) / 100)))
                self.progress_signal.emit(progress, f"Retrieved {len(all_reviews)} reviews...")
                
                # Move to next page
                offset += limit
            
            return all_reviews
            
        except Exception as e:
            logger.error(f"Error getting user reviews: {str(e)}")
            return []
    
    def _search_businesses(self, keyword, location=None, lat=None, lon=None):
        """Search for businesses by keyword and location"""
        try:
            all_businesses = []
            offset = 0
            limit = 50
            
            while offset < 200 and not self.should_stop:  # Limit to 200 businesses max (4 pages)
                self.rate_limiter.wait_if_needed()
                
                headers = {
                    'Authorization': f"Bearer {self.api['api_key']}",
                    'Accept': 'application/json'
                }
                
                params = {
                    'term': keyword,
                    'limit': limit,
                    'offset': offset
                }
                
                # Add location parameters
                if location:
                    params['location'] = location
                elif lat is not None and lon is not None:
                    params['latitude'] = lat
                    params['longitude'] = lon
                    params['radius'] = 10000  # 10km
                
                url = f"{self.api['base_url']}/businesses/search"
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code != 200:
                    logger.error(f"API Error: {response.status_code} - {response.text}")
                    break
                    
                data = response.json()
                businesses = data.get('businesses', [])
                
                if not businesses:
                    break
                    
                all_businesses.extend(businesses)
                
                # Update progress
                progress = min(75, int(60 + (15 * len(all_businesses) / 200)))
                self.progress_signal.emit(progress, f"Retrieved {len(all_businesses)} businesses...")
                
                # Check if there are more results
                total = data.get('total', 0)
                if offset + limit >= total:
                    break
                    
                # Move to next page
                offset += limit
            
            return all_businesses
            
        except Exception as e:
            logger.error(f"Error searching for businesses: {str(e)}")
            return []
    
    def _extract_locations_from_reviews(self, reviews):
        """Extract location data from Yelp reviews"""
        locations = []
        
        for review in reviews:
            try:
                # Skip reviews without business data
                if not review.get('business'):
                    continue
                    
                business = review['business']
                
                # Skip businesses without location data
                if not business.get('coordinates') or not business['coordinates'].get('latitude'):
                    continue
                    
                # Get coordinates
                lat = business['coordinates']['latitude']
                lon = business['coordinates']['longitude']
                
                # Parse date
                try:
                    # Yelp uses ISO format
                    date = datetime.datetime.fromisoformat(review.get('time_created').replace('Z', '+00:00'))
                except:
                    date = datetime.datetime.now()
                
                # Create location object
                loc = {
                    'plugin': 'yelp',
                    'lat': lat,
                    'lon': lon,
                    'date': date,
                    'context': f"Review of {business.get('name', 'Unknown Business')}",
                    'infowindow': self._create_review_infowindow(review, business),
                    'shortName': business.get('name', 'Yelp Review'),
                }
                locations.append(loc)
                
            except Exception as e:
                logger.error(f"Error processing review: {str(e)}")
        
        return locations
    
    def _extract_locations_from_businesses(self, businesses):
        """Extract location data from Yelp businesses"""
        locations = []
        
        for business in businesses:
            try:
                # Skip businesses without location data
                if not business.get('coordinates') or not business['coordinates'].get('latitude'):
                    continue
                    
                # Get coordinates
                lat = business['coordinates']['latitude']
                lon = business['coordinates']['longitude']
                
                # Create location object
                loc = {
                    'plugin': 'yelp',
                    'lat': lat,
                    'lon': lon,
                    'date': datetime.datetime.now(),  # No specific date for businesses
                    'context': business.get('categories', [{}])[0].get('title', 'Business'),
                    'infowindow': self._create_business_infowindow(business),
                    'shortName': business.get('name', 'Yelp Business'),
                }
                locations.append(loc)
                
            except Exception as e:
                logger.error(f"Error processing business: {str(e)}")
        
        return locations
    
    def _create_review_infowindow(self, review, business):
        """Create info window HTML for a Yelp review"""
        business_name = business.get('name', 'Unknown Business')
        rating = review.get('rating', 0)
        stars = "★" * rating + "☆" * (5 - rating)
        text = review.get('text', 'No review text')
        
        try:
            date = datetime.datetime.fromisoformat(review.get('time_created').replace('Z', '+00:00'))
            formatted_date = date.strftime('%Y-%m-%d')
        except:
            formatted_date = 'Unknown date'
            
        url = review.get('url', '')
        business_url = business.get('url', '')
        address = ', '.join(business.get('location', {}).get('display_address', ['No address']))
        
        html = f"""<div class="yelp-review">
            <h3><a href="{business_url}" target="_blank">{business_name}</a></h3>
            <div class="rating">{stars} ({rating}/5)</div>
            <div class="review-content">
                <p>{text}</p>
                <p><strong>Date:</strong> {formatted_date}</p>
                <p><strong>Address:</strong> {address}</p>
            </div>
            <p><a href="{url}" target="_blank">View on Yelp</a></p>
        </div>"""
        
        return html
    
    def _create_business_infowindow(self, business):
        """Create info window HTML for a Yelp business"""
        business_name = business.get('name', 'Unknown Business')
        rating = business.get('rating', 0)
        stars = "★" * int(rating) + "½" * (1 if rating % 1 >= 0.5 else 0) + "☆" * (5 - int(rating) - (1 if rating % 1 >= 0.5 else 0))
        review_count = business.get('review_count', 0)
        url = business.get('url', '')
        image_url = business.get('image_url', '')
        categories = ", ".join([cat.get('title', '') for cat in business.get('categories', [])])
        address = ', '.join(business.get('location', {}).get('display_address', ['No address']))
        price = business.get('price', '$')
        
        html = f"""<div class="yelp-business">
            <h3><a href="{url}" target="_blank">{business_name}</a></h3>
            <div class="business-content">
                <img src="{image_url}" alt="{business_name}" class="thumbnail" onclick="window.open('{url}', '_blank')">
                <div class="business-details">
                    <p><strong>Rating:</strong> {stars} ({rating}/5) · {review_count} reviews</p>
                    <p><strong>Categories:</strong> {categories}</p>
                    <p><strong>Price:</strong> {price}</p>
                    <p><strong>Address:</strong> {address}</p>
                </div>
            </div>
            <p><a href="{url}" target="_blank">View on Yelp</a></p>
        </div>"""
        
        return html
        
    def stop(self):
        """Stop the thread"""
        self.should_stop = True

class YelpPlugin(InputPlugin):
    name = "yelp"
    hasWizard = True
    
    def __init__(self):
        InputPlugin.__init__(self)
        self.description = "Extract location data from Yelp users and businesses"
        self.searchOffline = False
        
        # Load configuration
        self._config_path = os.path.join(os.path.expanduser("~"), ".creepy", "yelp.conf")
        self._cache_path = os.path.join(os.path.expanduser("~"), ".creepy", "yelp_cache")
        os.makedirs(self._cache_path, exist_ok=True)
        self._load_config()
        
        # Load labels
        try:
            labels_file = os.path.join(os.path.dirname(__file__), 'yelp.labels')
            labels_config = ConfigObj(infile=labels_file)
            self.labels = labels_config.get('labels', {})
        except Exception as e:
            logger.error(f"Error loading labels: {str(e)}")
            self.labels = {}
        
        # Initialize API client
        self.api = None
        if self.configured:
            self._initialize_api()
            
    def _load_config(self):
        """Load configuration from file"""
        self.configured = False
        self.config = {
            'api_key': '',
            'use_cache': True
        }
        
        config_dir = os.path.dirname(self._config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r') as f:
                    self.config = json.load(f)
                    
                # Check if we have the necessary config values
                if self.config.get('api_key'):
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
        """Initialize the Yelp API client"""
        self.api = {
            'api_key': self.config.get('api_key', ''),
            'base_url': 'https://api.yelp.com/v3'
        }
        
    def activate(self):
        logger.info("YelpPlugin activated")
        if not self.configured:
            logger.warning("Yelp plugin is not configured yet")
        
    def deactivate(self):
        logger.info("YelpPlugin deactivated")
    
    def isConfigured(self):
        """Check if the plugin is properly configured"""
        if not self.configured:
            return (False, "Please configure Yelp API credentials")
        
        # Test the API with a simple request
        try:
            headers = {
                'Authorization': f"Bearer {self.api['api_key']}",
                'Accept': 'application/json'
            }
            
            response = requests.get(f"{self.api['base_url']}/businesses/search?location=San Francisco&limit=1", headers=headers)
            
            if response.status_code == 200:
                return (True, "Plugin is configured and ready to use")
            else:
                error = response.json().get('error', {}).get('description', 'Unknown error')
                return (False, f"API test failed: {error}")
        except Exception as e:
            logger.error(f"Error testing API: {str(e)}")
            return (False, f"Error testing API: {str(e)}")
    
    def searchForTargets(self, search_term):
        """Search for targets matching the search term"""
        logger.info(f"Processing Yelp search term: {search_term}")
        
        if not self.configured:
            logger.warning("Plugin not configured properly")
            return [{
                'targetUsername': search_term,
                'targetUserid': search_term,
                'targetFullname': f"Yelp search: {search_term} (plugin not configured)",
                'targetPicture': '',
                'pluginName': self.name
            }]
        
        targets = []
        
        # Check if search_term is a Yelp user ID
        if search_term.startswith('user_') or re.match(r'^[a-zA-Z0-9_-]{22}$', search_term):
            targets.append({
                'targetUsername': search_term,
                'targetUserid': search_term,
                'targetFullname': f"Yelp user: {search_term}",
                'targetPicture': '',
                'pluginName': self.name,
                'search_type': 'user'
            })
        
        # Add a keyword search target
        targets.append({
            'targetUsername': f"search:{search_term}",
            'targetUserid': f"search:{search_term}",
            'targetFullname': f"Yelp search: {search_term}",
            'targetPicture': '',
            'pluginName': self.name,
            'search_type': 'keyword',
            'keyword': search_term
        })
        
        return targets
    
    def returnLocations(self, target, search_params):
        """Return location data for the target"""
        logger.info(f"Getting locations for Yelp target: {target.get('targetFullname')}")
        
        if not self.configured:
            logger.error("Plugin not configured properly")
            return []
            
        # Parse target info
        search_type = target.get('search_type', '')
        user_id = None
        keyword = None
        location = None
        lat = None
        lon = None
        
        if search_type == 'user':
            user_id = target.get('targetUserid', '')
        elif search_type == 'keyword':
            keyword = target.get('keyword', '')
            
            # Check if search params contain location
            if search_params:
                location = search_params.get('location', '')
                lat = search_params.get('latitude')
                lon = search_params.get('longitude')
                
            # If no location provided, ask user
            if not location and lat is None and lon is None:
                from PyQt5.QtWidgets import QInputDialog
                location, ok = QInputDialog.getText(None, "Location Required", 
                                                  "Enter a location (city, address) for search:")
                if not ok or not location:
                    return []
        
        # Create a unique cache key based on search parameters
        cache_key_parts = []
        if user_id:
            cache_key_parts.append(f"user_{user_id}")
        if keyword:
            cache_key_parts.append(f"kw_{keyword}")
        if location:
            cache_key_parts.append(f"loc_{location}")
        if lat is not None and lon is not None:
            cache_key_parts.append(f"coord_{lat}_{lon}")
            
        cache_key = "_".join(cache_key_parts).replace(" ", "_")
        
        # Check if we already have cached results
        cache_file = os.path.join(self._cache_path, f"{cache_key}_locations.json")
        if os.path.exists(cache_file) and self.config.get('use_cache', True):
            try:
                cache_age = time.time() - os.path.getmtime(cache_file)
                # Use cache if it's less than 24 hours old
                if cache_age < 86400:
                    logger.info(f"Using cached location data for {cache_key}")
                    with open(cache_file, 'r') as f:
                        locations = json.load(f)
                    return locations
            except Exception as e:
                logger.warning(f"Error reading cache: {str(e)}")
        
        # Prepare search parameters
        params = {
            'term': term,
            'location': location,
            'limit': limit,
            'sort_by': 'best_match'
        }
        
        # Start data fetch thread
        self.data_fetch_thread = YelpDataFetchThread(self.api, params)
        self.data_fetch_thread.progress_signal.connect(self._on_progress)
        self.data_fetch_thread.complete_signal.connect(self._on_complete)
        self.data_fetch_thread.error_signal.connect(self._on_error)
        self.data_fetch_thread.start()
        
        return []
    
    def _on_progress(self, progress, message):
        """Handle progress updates from the data fetch thread"""
        logger.info(f"Progress: {progress}% - {message}")
        
    def _on_complete(self, locations):
        """Handle completion of the data fetch thread"""
        logger.info(f"Data fetch complete. Found {len(locations)} locations.")
        
        # Save locations to cache
        cache_file = os.path.join(self._cache_path, f"{self.cache_key}_locations.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump(locations, f)
        except Exception as e:
            logger.warning(f"Error saving cache: {str(e)}")
        
        # Emit locations
        self.locations_signal.emit(locations)
        
    def _on_error(self, error_message):
        """Handle errors from the data fetch thread"""
        logger.error(f"Data fetch error: {error_message}")
        self.error_signal.emit(error_message)
