#!/usr/bin/python
# -*- coding: utf-8 -*-
from models.InputPlugin import InputPlugin
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
                           QProgressBar, QCheckBox, QComboBox)
from PyQt5.QtCore import QUrl, pyqtSignal, QObject, QThread
import webbrowser
from bs4 import BeautifulSoup

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

class TwitterDataFetchThread(QThread):
    """Thread to fetch data from Twitter/X in the background"""
    progress_signal = pyqtSignal(int, str)
    complete_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, api, username, max_tweets=500):
        super().__init__()
        self.api = api
        self.username = username
        self.max_tweets = max_tweets
        self.rate_limiter = RateLimiter(30, 60)  # 30 calls per minute
        self.should_stop = False
        
    def run(self):
        """Main thread execution to fetch Twitter/X data"""
        try:
            self.progress_signal.emit(5, f"Fetching profile data for {self.username}...")
            
            # Get user profile data
            user_data = self._get_user_profile(self.username)
            if not user_data:
                self.error_signal.emit(f"Could not find Twitter user: {self.username}")
                return
                
            self.progress_signal.emit(15, "Retrieving tweets...")
            
            # Get user tweets
            tweets = self._get_user_tweets(user_data['id'])
            if not tweets:
                self.progress_signal.emit(100, "No tweets found or no location data available")
                self.complete_signal.emit([])
                return
                
            self.progress_signal.emit(80, f"Found {len(tweets)} tweets. Processing location data...")
            
            # Extract locations from tweets
            locations = self._extract_locations_from_tweets(tweets)
            
            self.progress_signal.emit(100, f"Completed! Found {len(locations)} tweets with location data")
            self.complete_signal.emit(locations)
            
        except Exception as e:
            logger.error(f"Error in Twitter data fetch: {str(e)}")
            logger.debug(traceback.format_exc())
            self.error_signal.emit(str(e))
    
    def _get_user_profile(self, username):
        """Get Twitter/X user profile data"""
        try:
            self.rate_limiter.wait_if_needed()
            
            headers = {
                'Authorization': f"Bearer {self.api['bearer_token']}",
                'Accept': 'application/json'
            }
            
            url = f"{self.api['base_url']}/users/by/username/{username}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json().get('data', {})
            else:
                # Fall back to user ID search if available
                return self._get_user_profile_by_id(username)
                
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return self._get_user_profile_by_id(username)
            
    def _get_user_profile_by_id(self, user_id):
        """Get Twitter/X user profile data by ID"""
        try:
            if not user_id.isdigit():
                return None
                
            self.rate_limiter.wait_if_needed()
            
            headers = {
                'Authorization': f"Bearer {self.api['bearer_token']}",
                'Accept': 'application/json'
            }
            
            url = f"{self.api['base_url']}/users/{user_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json().get('data', {})
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting user profile by ID: {str(e)}")
            return None
    
    def _get_user_tweets(self, user_id):
        """Get tweets from a user"""
        try:
            tweets = []
            next_token = None
            
            # Parameters to request geo data, media, and place data
            params = {
                'max_results': 100,
                'tweet.fields': 'created_at,geo,entities,attachments',
                'expansions': 'geo.place_id,attachments.media_keys',
                'place.fields': 'contained_within,country,country_code,full_name,geo,id,name,place_type',
                'media.fields': 'url,preview_image_url'
            }
            
            while len(tweets) < self.max_tweets:
                if self.should_stop:
                    break
                    
                self.rate_limiter.wait_if_needed()
                
                if next_token:
                    params['pagination_token'] = next_token
                    
                headers = {
                    'Authorization': f"Bearer {self.api['bearer_token']}",
                    'Accept': 'application/json'
                }
                
                url = f"{self.api['base_url']}/users/{user_id}/tweets"
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code != 200:
                    break
                    
                data = response.json()
                batch_tweets = data.get('data', [])
                
                if not batch_tweets:
                    break
                    
                # Build a mapping of places for quick lookup
                places = {}
                if 'includes' in data and 'places' in data['includes']:
                    for place in data['includes']['places']:
                        places[place['id']] = place
                
                # Add places data to tweets
                for tweet in batch_tweets:
                    if 'geo' in tweet and 'place_id' in tweet['geo']:
                        place_id = tweet['geo']['place_id']
                        if place_id in places:
                            tweet['place_details'] = places[place_id]
                
                tweets.extend(batch_tweets)
                
                # Check for next page
                meta = data.get('meta', {})
                if 'next_token' in meta:
                    next_token = meta['next_token']
                else:
                    break
                    
                progress = min(75, int(30 + (45 * len(tweets) / self.max_tweets)))
                self.progress_signal.emit(progress, f"Retrieved {len(tweets)} tweets...")
                
            return tweets
            
        except Exception as e:
            logger.error(f"Error getting user tweets: {str(e)}")
            return []
    
    def _extract_locations_from_tweets(self, tweets):
        """Extract location data from tweets"""
        locations = []
        
        for tweet in tweets:
            try:
                coords = None
                place_name = None
                
                # First check for explicit geo coordinates
                if 'geo' in tweet and 'coordinates' in tweet['geo']:
                    coords = tweet['geo']['coordinates']
                    if len(coords) == 2:
                        lat, lon = coords
                
                # Check for place details
                elif 'place_details' in tweet:
                    place = tweet['place_details']
                    place_name = place.get('full_name')
                    
                    # Extract coordinates from place
                    if 'geo' in place and 'bbox' in place['geo']:
                        bbox = place['geo']['bbox']
                        # Calculate center of bounding box
                        lon = (bbox[0] + bbox[2]) / 2
                        lat = (bbox[1] + bbox[3]) / 2
                        coords = [lat, lon]
                
                # If no explicit geo, try to extract location from text
                if not coords:
                    coords = self._extract_location_from_text(tweet.get('text', ''))
                    
                # If we found coordinates, create a location object
                if coords:
                    # Parse date
                    try:
                        date = datetime.datetime.strptime(
                            tweet.get('created_at', ''), 
                            '%Y-%m-%dT%H:%M:%S.%fZ'
                        )
                    except:
                        date = datetime.datetime.now()
                    
                    # Create location object
                    loc = {
                        'plugin': 'twitter',
                        'lat': coords[0],
                        'lon': coords[1],
                        'date': date,
                        'context': tweet.get('text', '').replace('\n', ' ')[:100],
                        'infowindow': self._create_tweet_infowindow(tweet, place_name),
                        'shortName': place_name or 'Twitter Location',
                    }
                    locations.append(loc)
                
            except Exception as e:
                logger.error(f"Error processing tweet: {str(e)}")
        
        return locations
    
    def _extract_location_from_text(self, text):
        """Extract location coordinates from tweet text"""
        # Check for common GPS coordinate formats
        coord_patterns = [
            # Decimal degrees: 40.7128, -74.0060
            r'(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)',
            
            # Degrees, minutes, seconds: 40°41'21.1"N 74°02'40.2"W
            r'(\d+)°(\d+)\'(\d+(?:\.\d+)?)"([NS])\s+(\d+)°(\d+)\'(\d+(?:\.\d+)?)"([EW])',
            
            # Location tag format: #location=40.7128,-74.0060
            r'#location=(-?\d+\.\d+),(-?\d+\.\d+)'
        ]
        
        for pattern in coord_patterns:
            matches = re.search(pattern, text)
            if matches:
                if len(matches.groups()) == 2:
                    # Decimal degrees
                    try:
                        lat = float(matches.group(1))
                        lon = float(matches.group(2))
                        return [lat, lon]
                    except:
                        pass
                elif len(matches.groups()) == 8:
                    # DMS format
                    try:
                        lat_deg = int(matches.group(1))
                        lat_min = int(matches.group(2))
                        lat_sec = float(matches.group(3))
                        lat_dir = matches.group(4)
                        
                        lon_deg = int(matches.group(5))
                        lon_min = int(matches.group(6))
                        lon_sec = float(matches.group(7))
                        lon_dir = matches.group(8)
                        
                        lat = lat_deg + lat_min/60 + lat_sec/3600
                        if lat_dir == 'S':
                            lat = -lat
                            
                        lon = lon_deg + lon_min/60 + lon_sec/3600
                        if lon_dir == 'W':
                            lon = -lon
                            
                        return [lat, lon]
                    except:
                        pass
        
        return None
    
    def _create_tweet_infowindow(self, tweet, place_name=None):
        """Create info window HTML for a tweet"""
        text = tweet.get('text', 'No text').replace('\n', '<br>')
        created_at = tweet.get('created_at', 'Unknown date')
        
        try:
            date_obj = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            formatted_date = created_at
            
        # Get tweet URL
        tweet_id = tweet.get('id')
        link = f"https://twitter.com/x/status/{tweet_id}" if tweet_id else ""
        
        # Get media if available
        media_html = ""
        if 'includes' in tweet and 'media' in tweet['includes']:
            for media in tweet['includes']['media']:
                if media.get('type') == 'photo':
                    url = media.get('url', '')
                    if url:
                        media_html += f'<img src="{url}" alt="Tweet media" class="thumbnail" onclick="window.open(\'{url}\', \'_blank\')">'
        
        # Get place details
        place_details = ""
        if 'place_details' in tweet:
            place = tweet['place_details']
            place_details = f"""
            <div class="place-details">
                <p><strong>Location:</strong> {place.get('full_name', 'Unknown')}</p>
                <p><strong>Type:</strong> {place.get('place_type', 'Unknown')}</p>
                <p><strong>Country:</strong> {place.get('country', 'Unknown')}</p>
            </div>
            """
        
        html = f"""<div class="twitter-tweet">
            <h3>Tweet from {formatted_date}</h3>
            <div class="tweet-content">
                <p>{text}</p>
                {media_html}
                {place_details}
            </div>
            <p><a href="{link}" target="_blank">View on Twitter</a></p>
        </div>"""
        
        return html
        
    def stop(self):
        """Stop the thread"""
        self.should_stop = True

class TwitterPlugin(InputPlugin):
    name = "twitter"
    hasWizard = True
    
    def __init__(self):
        InputPlugin.__init__(self)
        self.description = "Extract location data from Twitter/X posts"
        self.searchOffline = False
        
        # Load configuration
        self._config_path = os.path.join(os.path.expanduser("~"), ".creepy", "twitter.conf")
        self._cache_path = os.path.join(os.path.expanduser("~"), ".creepy", "twitter_cache")
        os.makedirs(self._cache_path, exist_ok=True)
        self._load_config()
        
        # Load labels
        try:
            labels_file = os.path.join(os.path.dirname(__file__), 'twitter.labels')
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
                if self.config.get('bearer_token'):
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
        """Initialize the Twitter/X API client"""
        self.api = {
            'bearer_token': self.config.get('bearer_token', ''),
            'api_key': self.config.get('api_key', ''),
            'api_key_secret': self.config.get('api_key_secret', ''),
            'base_url': 'https://api.twitter.com/2'
        }
        
    def activate(self):
        logger.info("TwitterPlugin activated")
        if not self.configured:
            logger.warning("Twitter/X plugin is not configured yet")
        
    def deactivate(self):
        logger.info("TwitterPlugin deactivated")
        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.stop()
    
    def isConfigured(self):
        """Check if the plugin is properly configured"""
        if not self.configured:
            return (False, "Please configure Twitter/X API credentials")
        
        # Test the API with a simple request
        try:
            headers = {
                'Authorization': f"Bearer {self.api['bearer_token']}",
                'Accept': 'application/json'
            }
            
            response = requests.get(f"{self.api['base_url']}/users/me", headers=headers)
            
            if response.status_code == 200:
                return (True, "Plugin is configured and ready to use")
            else:
                error = response.json().get('errors', [{}])[0].get('message', 'Unknown error')
                return (False, f"API test failed: {error}")
        except Exception as e:
            logger.error(f"Error testing API: {str(e)}")
            return (False, f"Error testing API: {str(e)}")
    
    def searchForTargets(self, search_term):
        """Search for targets matching the search term"""
        logger.info(f"Searching for Twitter/X users matching: {search_term}")
        
        if not self.configured:
            logger.warning("Plugin not configured properly")
            return [{
                'targetUsername': search_term,
                'targetUserid': search_term,
                'targetFullname': f"Twitter/X user: {search_term} (plugin not configured)",
                'targetPicture': '',
                'pluginName': self.name
            }]
        
        try:
            # Search for users
            headers = {
                'Authorization': f"Bearer {self.api['bearer_token']}",
                'Accept': 'application/json'
            }
            
            params = {
                'query': search_term,
                'user.fields': 'profile_image_url,description,location',
                'max_results': 10
            }
            
            response = requests.get(f"{self.api['base_url']}/users/search", headers=headers, params=params)
            
            if response.status_code == 200:
                users = response.json().get('data', [])
                targets = []
                
                for user in users:
                    # Get profile picture
                    pic_url = user.get('profile_image_url', '')
                    pic_filename = f"{user.get('id')}_profile.jpg"
                    pic_path = os.path.join(os.getcwd(), "temp", pic_filename)
                    
                    # Download profile picture if it doesn't exist already
                    if pic_url and not os.path.exists(pic_path):
                        try:
                            urllib.request.urlretrieve(pic_url, pic_path)
                        except Exception as e:
                            logger.error(f"Error downloading profile picture: {str(e)}")
                    
                    targets.append({
                        'targetUsername': user.get('username'),
                        'targetUserid': user.get('id'),
                        'targetFullname': user.get('name', f"@{user.get('username')}"),
                        'targetPicture': pic_filename if os.path.exists(pic_path) else '',
                        'pluginName': self.name
                    })
                    
                if targets:
                    return targets
            
            # If no results or API call failed, just return the search term
            return [{
                'targetUsername': search_term,
                'targetUserid': search_term,
                'targetFullname': f"Twitter/X user: {search_term}",
                'targetPicture': '',
                'pluginName': self.name
            }]
            
        except Exception as e:
            logger.error(f"Error searching for targets: {str(e)}")
            return [{
                'targetUsername': search_term,
                'targetUserid': search_term,
                'targetFullname': f"Twitter/X user: {search_term}",
                'targetPicture': '',
                'pluginName': self.name
            }]
    
    def returnLocations(self, target, search_params):
        """Return location data for the target"""
        logger.info(f"Getting locations for Twitter/X user {target['targetUsername']}")
        
        if not self.configured:
            logger.error("Plugin not configured properly")
            return []
            
        username = target['targetUsername']
        user_id = target['targetUserid']
        
        # Check if we already have cached results for this target
        cache_file = os.path.join(self._cache_path, f"{username}_locations.json")
        if os.path.exists(cache_file) and self.config.get('use_cache', True):
            try:
                cache_age = time.time() - os.path.getmtime(cache_file)
                # Use cache if it's less than 24 hours old
                if cache_age < 86400:
                    logger.info(f"Using cached location data for {username}")
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
            dialog.setWindowTitle("Twitter/X Data Fetch")
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
            fetch_thread = TwitterDataFetchThread(self.api, username)
            
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
            logger.warning("PyQt not available, falling back to non-GUI method")
            return []
    
    def runConfigWizard(self):
        """Run configuration wizard to set up Twitter/X API access"""
        from PyQt5.QtWidgets import QWizard, QWizardPage, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextBrowser, QMessageBox
        
        wizard = QWizard()
        wizard.setWindowTitle("Twitter/X Plugin Configuration")
        
        # Welcome page
        welcome_page = QWizardPage()
        welcome_page.setTitle("Twitter/X Plugin Setup")
        
        welcome_layout = QVBoxLayout()
        welcome_text = QTextBrowser()
        welcome_text.setOpenExternalLinks(True)
        welcome_text.setHtml("""
        <h2>Welcome to Twitter/X Plugin Setup</h2>
        <p>This wizard will help you set up the Twitter/X plugin for CreepyAI.</p>
        <p>You'll need to create a Twitter Developer account and set up an app:</p>
        <ol>
            <li>Go to <a href="https://developer.twitter.com/">Twitter Developer Platform</a></li>
            <li>Create a new Project and App</li>
            <li>Enable OAuth 2.0 and set up a redirect URL (can be http://localhost/)</li>
            <li>Get the API key, API secret, and Bearer Token</li>
        </ol>
        <p>You'll need your Bearer Token for this configuration.</p>
        """)
        welcome_layout.addWidget(welcome_text)
        welcome_page.setLayout(welcome_layout)
        wizard.addPage(welcome_page)
        
        # App credentials page
        credentials_page = QWizardPage()
        credentials_page.setTitle("API Credentials")
        
        credentials_layout = QVBoxLayout()
        
        # API key
        api_key_label = QLabel("API Key:")
        api_key_input = QLineEdit()
        api_key_input.setText(self.config.get('api_key', ''))
        credentials_layout.addWidget(api_key_label)
        credentials_layout.addWidget(api_key_input)
        
        # API secret
        api_secret_label = QLabel("API Secret:")
        api_secret_input = QLineEdit()
        api_secret_input.setText(self.config.get('api_key_secret', ''))
        api_secret_input.setEchoMode(QLineEdit.Password)
        credentials_layout.addWidget(api_secret_label)
        credentials_layout.addWidget(api_secret_input)
        
        # Bearer token
        bearer_token_label = QLabel("Bearer Token (required):")
        bearer_token_input = QLineEdit()
        bearer_token_input.setText(self.config.get('bearer_token', ''))
        bearer_token_input.setEchoMode(QLineEdit.Password)
        credentials_layout.addWidget(bearer_token_label)
        credentials_layout.addWidget(bearer_token_input)
        
        # Use cache option
        use_cache_checkbox = QCheckBox("Cache results to improve performance")
        use_cache_checkbox.setChecked(self.config.get('use_cache', True))
        credentials_layout.addWidget(use_cache_checkbox)
        
        credentials_page.setLayout(credentials_layout)
        wizard.addPage(credentials_page)
        
        # Test credentials page
        test_page = QWizardPage()
        test_page.setTitle("Test API Connection")
        
        test_layout = QVBoxLayout()
        test_text = QTextBrowser()
        test_text.setHtml("""
        <h3>Testing API Connection</h3>
        <p>Click the button below to test your Twitter/X API credentials.</p>
        <p>If successful, you'll be able to proceed to complete the setup.</p>
        """)
        test_layout.addWidget(test_text)
        
        # Test button
        test_button = QPushButton("Test Connection")
        test_layout.addWidget(test_button)
        
        # Status label
        status_label = QLabel("")
        test_layout.addWidget(status_label)
        
        test_page.setLayout(test_layout)
        wizard.addPage(test_page)
        
        # Connect test button
        def test_connection():
            bearer = bearer_token_input.text()
            if not bearer:
                status_label.setText("Bearer token is required")
                return
                
            try:
                # Test API connection
                headers = {
                    'Authorization': f"Bearer {bearer}",
                    'Accept': 'application/json'
                }
                
                url = "https://api.twitter.com/2/tweets/search/recent?query=twitter&max_results=10"
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    status_label.setText("<span style='color:green;'>Connection successful! You can proceed.</span>")
                else:
                    error = response.json().get('errors', [{}])[0].get('message', 'Unknown error')
                    status_label.setText(f"<span style='color:red;'>Connection failed: {error}</span>")
            except Exception as e:
                status_label.setText(f"<span style='color:red;'>Error testing connection: {str(e)}</span>")
                
        test_button.clicked.connect(test_connection)
        
        # Final page
        final_page = QWizardPage()
        final_page.setTitle("Setup Complete")
        
        final_layout = QVBoxLayout()
        final_text = QTextBrowser()
        final_text.setHtml("""
        <h3>Configuration Complete!</h3>
        <p>Your Twitter/X plugin is now configured and ready to use.</p>
        <p>You can now search for Twitter/X users and extract their location data.</p>
        <p>Note: API access may require a paid Twitter Developer account or may have usage limits.</p>
        """)
        final_layout.addWidget(final_text)
        final_page.setLayout(final_layout)
        wizard.addPage(final_page)
        
        # Process results
        if wizard.exec_():
            # Save configuration
            self.config['api_key'] = api_key_input.text()
            self.config['api_key_secret'] = api_secret_input.text()
            self.config['bearer_token'] = bearer_token_input.text()
            self.config['use_cache'] = use_cache_checkbox.isChecked()
            
            self._save_config()
            self._initialize_api()
            self.configured = True
            
            QMessageBox.information(None, "Configuration Saved", 
                                   "Twitter/X plugin configuration has been saved successfully.")
            return True
        else:
            return False
    
    def getConfigurationParameters(self):
        """Return configuration parameters for the plugin"""
        return [
            {'name': 'api_key', 'type': 'string', 'default': ''},
            {'name': 'api_key_secret', 'type': 'password', 'default': ''},
            {'name': 'bearer_token', 'type': 'password', 'default': ''},
            {'name': 'use_cache', 'type': 'boolean', 'default': True}
        ]
        
    def setConfigurationParameters(self, params):
        """Set configuration parameters for the plugin"""
        if 'bearer_token' in params:
            self.config['api_key'] = params.get('api_key', '')
            self.config['api_key_secret'] = params.get('api_key_secret', '')
            self.config['bearer_token'] = params['bearer_token']
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
            "api_key": "Twitter API Key",
            "api_key_secret": "Twitter API Secret",
            "bearer_token": "Twitter Bearer Token",
            "use_cache": "Cache Results"
        }
        return labels.get(key, key)


