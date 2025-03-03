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
                            QProgressBar, QCheckBox)
from PyQt5.QtCore import QUrl, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QDesktopServices
import webbrowser
import base64
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

class PinterestDataFetchThread(QThread):
    """Thread to fetch data from Pinterest in the background"""
    progress_signal = pyqtSignal(int, str)
    complete_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, api, username, max_pins=200):
        super().__init__()
        self.api = api
        self.username = username
        self.max_pins = max_pins
        self.rate_limiter = RateLimiter(20, 60)
        self.should_stop = False
        
    def run(self):
        """Main thread execution to fetch Pinterest data"""
        try:
            pins = []
            self.progress_signal.emit(5, f"Fetching profile data for {self.username}...")
            
            # Get user profile data
            user_data = self._get_user_profile(self.username)
            if not user_data:
                self.error_signal.emit(f"Could not find Pinterest user: {self.username}")
                return
                
            self.progress_signal.emit(10, "Retrieving user boards...")
            
            # Get user boards
            boards = self._get_user_boards(user_data['id'])
            if not boards:
                self.progress_signal.emit(100, "No boards found for this user")
                self.complete_signal.emit([])
                return
                
            total_boards = len(boards)
            self.progress_signal.emit(20, f"Found {total_boards} boards. Retrieving pins...")
            
            # Retrieve pins from each board
            for i, board in enumerate(boards):
                if self.should_stop:
                    return
                
                board_progress = 20 + (70 * i // total_boards)
                self.progress_signal.emit(board_progress, f"Processing board {i+1} of {total_boards}: {board['name']}")
                
                board_pins = self._get_board_pins(board['id'])
                for pin in board_pins:
                    if len(pins) >= self.max_pins:
                        break
                    pins.append(pin)
                
                if len(pins) >= self.max_pins:
                    break
                    
            # Find pins with location data
            self.progress_signal.emit(90, "Processing location data...")
            locations = self._extract_locations_from_pins(pins)
            
            self.progress_signal.emit(100, f"Completed! Found {len(locations)} items with location data")
            self.complete_signal.emit(locations)
            
        except Exception as e:
            logger.error(f"Error in Pinterest data fetch: {str(e)}")
            logger.debug(traceback.format_exc())
            self.error_signal.emit(str(e))
    
    def _get_user_profile(self, username):
        """Get Pinterest user profile data"""
        try:
            self.rate_limiter.wait_if_needed()
            
            headers = {
                'Authorization': f"Bearer {self.api['access_token']}",
                'Accept': 'application/json'
            }
            
            response = requests.get(
                f"{self.api['base_url']}/v5/user_account",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
                
            # If API fails, try scraping as fallback
            return self._scrape_user_profile(username)
            
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return self._scrape_user_profile(username)
    
    def _scrape_user_profile(self, username):
        """Scrape Pinterest user profile as fallback"""
        try:
            url = f"https://www.pinterest.com/{username}/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return None
                
            # Extract user ID and data from page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for JSON data in script tags
            for script in soup.find_all('script'):
                if script.string and 'id' in script.string and 'username' in script.string:
                    data = re.search(r'"user":\s*({.*?})', script.string)
                    if data:
                        try:
                            user_data = json.loads(data.group(1))
                            return {
                                'id': user_data.get('id'),
                                'username': user_data.get('username')
                            }
                        except:
                            pass
            
            return {
                'id': username,
                'username': username
            }
                
        except Exception as e:
            logger.error(f"Error scraping user profile: {str(e)}")
            return None
    
    def _get_user_boards(self, user_id):
        """Get Pinterest user boards"""
        try:
            self.rate_limiter.wait_if_needed()
            
            headers = {
                'Authorization': f"Bearer {self.api['access_token']}",
                'Accept': 'application/json'
            }
            
            response = requests.get(
                f"{self.api['base_url']}/v3/users/{user_id}/boards",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()['items']
                
            # If API fails, try scraping as fallback
            return self._scrape_user_boards(user_id)
            
        except Exception as e:
            logger.error(f"Error getting user boards: {str(e)}")
            return self._scrape_user_boards(user_id)
    
    def _scrape_user_boards(self, username):
        """Scrape Pinterest user boards as fallback"""
        try:
            url = f"https://www.pinterest.com/{username}/boards/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return []
                
            # Extract boards from page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            boards = []
            # Iterate through board elements
            board_elements = soup.select('div[data-test-id="board"]')
            for element in board_elements:
                board_url_element = element.select_one('a[href*="/boards/"]')
                if board_url_element:
                    href = board_url_element.get('href', '')
                    board_id = href.split('/')[-1]
                    board_name = board_url_element.get_text().strip()
                    boards.append({
                        'id': board_id,
                        'name': board_name,
                        'url': f"https://www.pinterest.com{href}"
                    })
            
            return boards
                
        except Exception as e:
            logger.error(f"Error scraping user boards: {str(e)}")
            return []
    
    def _get_board_pins(self, board_id):
        """Get pins from a Pinterest board"""
        try:
            self.rate_limiter.wait_if_needed()
            
            headers = {
                'Authorization': f"Bearer {self.api['access_token']}",
                'Accept': 'application/json'
            }
            
            params = {
                'bookmark': '',
                'page_size': 50
            }
            
            all_pins = []
            while len(all_pins) < self.max_pins:
                response = requests.get(
                    f"{self.api['base_url']}/v3/boards/{board_id}/pins",
                    headers=headers,
                    params=params
                )
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                pins = data.get('items', [])
                if not pins:
                    break
                    
                all_pins.extend(pins)
                
                # Check if there's a next page
                if 'bookmark' in data and data['bookmark']:
                    params['bookmark'] = data['bookmark']
                    self.rate_limiter.wait_if_needed()
                else:
                    break
            
            # If API fails or returns empty, try scraping as fallback
            if not all_pins:
                return self._scrape_board_pins(board_id)
                
            return all_pins
            
        except Exception as e:
            logger.error(f"Error getting board pins: {str(e)}")
            return self._scrape_board_pins(board_id)
    
    def _scrape_board_pins(self, board_id):
        """Scrape pins from a Pinterest board as fallback"""
        try:
            url = f"https://www.pinterest.com/boards/{board_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return []
                
            # Extract pins from page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pins = []
            # Look for pin elements
            pin_elements = soup.select('div[data-test-id="pin"]')
            for element in pin_elements:
                pin_url_element = element.select_one('a[href*="/pin/"]')
                if pin_url_element:
                    href = pin_url_element.get('href', '')
                    pin_id = href.split('/')[-1]
                    
                    # Try to get image
                    img_element = element.select_one('img')
                    image_url = img_element.get('src') if img_element else ''
                    
                    # Try to get title
                    title_element = element.select_one('.tBJ.dyH.iFc.yTZ.pBj.DrD.IZT.mWe')
                    title = title_element.get_text().strip() if title_element else ''
                    
                    pins.append({
                        'id': pin_id,
                        'title': title,
                        'link': f"https://www.pinterest.com{href}",
                        'image': {
                            'original': {
                                'url': image_url
                            }
                        },
                        'created_at': ''
                    })
                    
                    if len(pins) >= self.max_pins:
                        break
            
            return pins
                
        except Exception as e:
            logger.error(f"Error scraping board pins: {str(e)}")
            return []
    
    def _extract_locations_from_pins(self, pins):
        """Extract location data from Pinterest pins"""
        locations = []
        
        for pin in pins:
            try:
                # Check if pin has location data
                if 'location' not in pin or not pin['location']:
                    # Try to extract location from metadata
                    location_info = self._extract_location_from_pin_metadata(pin['id'])
                    if location_info:
                        pin['extracted_location'] = location_info
                    else:
                        continue
                
                # Get location data
                location = pin.get('location') or pin.get('extracted_location')
                if not location or 'latitude' not in location or 'longitude' not in location:
                    continue
                    
                # Parse date
                try:
                    date = datetime.datetime.strptime(
                        pin.get('created_at', ''), 
                        '%Y-%m-%dT%H:%M:%S%z'
                    )
                except:
                    date = datetime.datetime.now()
                
                # Create location object
                loc = {
                    'plugin': 'pinterest',
                    'lat': float(location['latitude']),
                    'lon': float(location['longitude']),
                    'date': date,
                    'context': pin.get('title', 'Pinterest Pin'),
                    'infowindow': self._create_pin_infowindow(pin),
                    'shortName': location.get('name', 'Pinterest Location'),
                }
                locations.append(loc)
                
            except Exception as e:
                logger.error(f"Error processing pin: {str(e)}")
        
        return locations
    
    def _extract_location_from_pin_metadata(self, pin_id):
        """Try to extract location data from pin metadata"""
        try:
            self.rate_limiter.wait_if_needed()
            
            url = f"https://www.pinterest.com/pin/{pin_id}/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return None
                
            # Look for location data in page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for schema.org metadata
            for script in soup.find_all('script', {'type': 'application/ld+json'}):
                if script.string:
                    try:
                        data = json.loads(script.string)
                        if 'contentLocation' in data:
                            location = data['contentLocation']
                            if 'geo' in location:
                                return {
                                    'name': location.get('name', 'Pinterest Location'),
                                    'latitude': location['geo'].get('latitude'),
                                    'longitude': location['geo'].get('longitude')
                                }
                    except:
                        pass
            
            # Look for coordinates in text
            for text in soup.stripped_strings:
                # Look for common location patterns
                coord_match = re.search(r'(?:location|coordinates|position)[\s:]{1,3}([-+]?\d+\.?\d*)[,\s]+\s*([-+]?\d+\.?\d*)', text, re.I)
                if coord_match:
                    lat, lon = coord_match.groups()
                    return {
                        'name': 'Extracted Location',
                        'latitude': float(lat),
                        'longitude': float(lon)
                    }
            
            return None
                
        except Exception as e:
            logger.error(f"Error extracting location from pin metadata: {str(e)}")
            return None
    
    def _create_pin_infowindow(self, pin):
        """Create info window HTML for a Pinterest pin"""
        title = pin.get('title', 'No title')
        location_name = pin.get('location', {}).get('name', 'Unknown Location')
        created_at = pin.get('created_at', 'Unknown date')
        
        try:
            date_obj = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S%z')
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            formatted_date = created_at
            
        image_url = pin.get('image', {}).get('original', {}).get('url', '')
        link = f"https://www.pinterest.com/pin/{pin.get('id', '')}"
        
        html = f"""<div class="pinterest-pin">
            <h3>Pinterest Pin at {location_name}</h3>
            <div class="pin-content">
                <img src="{image_url}" alt="Pin image" class="thumbnail" onclick="window.open('{link}', '_blank')">
                <div class="pin-details">
                    <p><strong>Title:</strong> {title}</p>
                    <p><strong>Date:</strong> {formatted_date}</p>
                    <p><strong>Location:</strong> {location_name}</p>
                </div>
            </div>
            <p><a href="{link}" target="_blank">View on Pinterest</a></p>
        </div>"""
        
        return html
        
    def stop(self):
        """Stop the thread"""
        self.should_stop = True

class PinterestPlugin(InputPlugin):
    name = "pinterest"
    hasWizard = True
    
    def __init__(self):
        InputPlugin.__init__(self)
        self.description = "Extract location data from Pinterest pins"
        self.searchOffline = False
        
        # Load configuration
        self._config_path = os.path.join(os.path.expanduser("~"), ".creepy", "pinterest.conf")
        self._cache_path = os.path.join(os.path.expanduser("~"), ".creepy", "pinterest_cache")
        os.makedirs(self._cache_path, exist_ok=True)
        self._load_config()
        
        # Load labels
        try:
            labels_file = os.path.join(os.path.dirname(__file__), 'pinterest.labels')
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
                if (self.config.get('app_id') and 
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
        """Initialize the Pinterest API client"""
        self.api = {
            'access_token': self.config.get('access_token', ''),
            'base_url': 'https://api.pinterest.com'
        }
        
    def activate(self):
        logger.info("PinterestPlugin activated")
        if not self.configured:
            logger.warning("Pinterest plugin is not configured yet")
        
    def deactivate(self):
        logger.info("PinterestPlugin deactivated")
        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.stop()
    
    def isConfigured(self):
        """Check if the plugin is properly configured"""
        if not self.configured:
            return (False, "Please configure Pinterest API credentials")
        
        return (True, "Plugin is configured and ready to use")
    
    def searchForTargets(self, search_term):
        """Search for targets matching the search term"""
        logger.info(f"Searching for Pinterest users matching: {search_term}")
        
        if not self.configured:
            logger.warning("Plugin not configured properly")
            return [{
                'targetUsername': search_term,
                'targetUserid': search_term,
                'targetFullname': f"Pinterest user: {search_term} (plugin not configured)",
                'targetPicture': '',
                'pluginName': self.name
            }]
        
        try:
            # For Pinterest, the most straightforward approach is to search by username
            return [{
                'targetUsername': search_term,
                'targetUserid': search_term,
                'targetFullname': f"Pinterest user: {search_term}",
                'targetPicture': '',
                'pluginName': self.name
            }]
        except Exception as e:
            logger.error(f"Error searching for targets: {str(e)}")
            return []
    
    def returnLocations(self, target, search_params):
        """Return location data for the target"""
        logger.info(f"Getting locations for Pinterest user {target['targetUsername']}")
        
        if not self.configured:
            logger.error("Plugin not configured properly")
            return []
            
        username = target['targetUsername']
        
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
            dialog.setWindowTitle("Pinterest Data Fetch")
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
            fetch_thread = PinterestDataFetchThread(self.api, username)
            
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
            return []  # In a real implementation, add a non-GUI method
    
    def runConfigWizard(self):
        """Run configuration wizard to set up Pinterest API access"""
        from PyQt5.QtWidgets import QWizard, QWizardPage, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextBrowser, QMessageBox
        
        wizard = QWizard()
        wizard.setWindowTitle("Pinterest Plugin Configuration")
        
        # Welcome page
        welcome_page = QWizardPage()
        welcome_page.setTitle("Pinterest Plugin Setup")
        
        welcome_layout = QVBoxLayout()
        welcome_text = QTextBrowser()
        welcome_text.setOpenExternalLinks(True)
        welcome_text.setHtml("""
        <h2>Welcome to Pinterest Plugin Setup</h2>
        <p>This wizard will help you set up the Pinterest plugin for CreepyAI.</p>
        <p>You'll need to create a Pinterest Developer account and set up an app:</p>
        <ol>
            <li>Go to <a href="https://developers.pinterest.com/">Pinterest for Developers</a></li>
            <li>Create a new app</li>
            <li>Add OAuth scopes for read_users, read_pins, and read_boards</li>
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
        app_id_input.setText(self.config.get('app_id', ''))
        credentials_layout.addWidget(app_id_label)
        credentials_layout.addWidget(app_id_input)
        
        # App Secret
        app_secret_label = QLabel("App Secret:")
        app_secret_input = QLineEdit()
        app_secret_input.setText(self.config.get('app_secret', ''))
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
        
        credentials_page.setLayout(credentials_layout)
        wizard.addPage(credentials_page)
        
        # Auth page
        auth_page = QWizardPage()
        auth_page.setTitle("Authenticate with Pinterest")
        
        auth_layout = QVBoxLayout()
        auth_text = QTextBrowser()
        auth_text.setHtml("""
        <h3>Pinterest Authentication</h3>
        <p>Click the button below to open Pinterest authentication in your browser.</p>
        <p>After authorizing, copy the access token from the URL and paste it below.</p>
        <p>The URL will look like: <code>http://localhost/?code=XXXXXXXX</code></p>
        """)
        auth_layout.addWidget(auth_text)
        
        # Auth button
        auth_button = QPushButton("Open Pinterest Login")
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
                auth_url = (
                    f"https://www.pinterest.com/oauth?client_id={client_id}&"
                    f"redirect_uri={redirect}&"
                    f"response_type=code&"
                    f"scope=boards:read,pins:read,user_accounts:read,pins:write"
                )
                webbrowser.open(auth_url)
                status_label.setText("Browser opened, please authorize and copy the code")
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
        <p>Your Pinterest plugin is now configured and ready to use.</p>
        <p>You can now search for Pinterest users and extract their location data.</p>
        <p>Note: The access token may expire after some time. If that happens, run this wizard again.</p>
        """)
        final_layout.addWidget(final_text)
        final_page.setLayout(final_layout)
        wizard.addPage(final_page)
        
        # Process results
        if wizard.exec_():
            # Save configuration
            self.config['app_id'] = app_id_input.text()
            self.config['app_secret'] = app_secret_input.text()
            self.config['redirect_uri'] = redirect_uri_input.text()
            self.config['access_token'] = token_input.text()
            self.config['use_cache'] = use_cache_checkbox.isChecked()
            
            self._save_config()
            self._initialize_api()
            self.configured = True
            
            QMessageBox.information(None, "Configuration Saved", 
                                   "Pinterest plugin configuration has been saved successfully.")
            return True
        else:
            return False
    
    def getConfigurationParameters(self):
        """Return configuration parameters for the plugin"""
        return [
            {'name': 'app_id', 'type': 'string', 'default': ''},
            {'name': 'app_secret', 'type': 'password', 'default': ''},
            {'name': 'redirect_uri', 'type': 'string', 'default': 'http://localhost/'},
            {'name': 'access_token', 'type': 'password', 'default': ''},
            {'name': 'use_cache', 'type': 'boolean', 'default': True}
        ]
        
    def setConfigurationParameters(self, params):
        """Set configuration parameters for the plugin"""
        if 'app_id' in params and 'access_token' in params:
            self.config['app_id'] = params['app_id']
            self.config['app_secret'] = params.get('app_secret', '')
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
            "app_id": "Pinterest App ID",
            "app_secret": "Pinterest App Secret",
            "redirect_uri": "OAuth Redirect URI",
            "access_token": "Pinterest Access Token",
            "use_cache": "Cache Results"
        }
        return labels.get(key, key)
