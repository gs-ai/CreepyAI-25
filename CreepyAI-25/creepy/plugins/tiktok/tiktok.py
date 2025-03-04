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
                           QProgressBar, QCheckBox, QFileDialog)
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

class TikTokDataFetchThread(QThread):
    """Thread to fetch data from TikTok in the background"""
    progress_signal = pyqtSignal(int, str)
    complete_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, api, username, max_videos=100):
        super().__init__()
        self.api = api
        self.username = username
        self.max_videos = max_videos
        self.rate_limiter = RateLimiter(10, 60)  # 10 calls per minute
        self.should_stop = False
        
    def run(self):
        """Main thread execution to fetch TikTok data"""
        try:
            self.progress_signal.emit(5, f"Fetching profile data for {self.username}...")
            
            # Get user profile data
            user_data = self._get_user_profile(self.username)
            if not user_data:
                self.error_signal.emit(f"Could not find TikTok user: {self.username}")
                return
                
            self.progress_signal.emit(20, "Retrieving videos...")
            
            # Get user videos
            videos = self._get_user_videos(user_data['secUid'], user_data['id'])
            if not videos:
                self.progress_signal.emit(100, "No videos found or no location data available")
                self.complete_signal.emit([])
                return
                
            self.progress_signal.emit(70, f"Found {len(videos)} videos. Processing location data...")
            
            # Extract locations from videos
            locations = self._extract_locations_from_videos(videos)
            
            self.progress_signal.emit(100, f"Completed! Found {len(locations)} videos with location data")
            self.complete_signal.emit(locations)
            
        except Exception as e:
            logger.error(f"Error in TikTok data fetch: {str(e)}")
            logger.debug(traceback.format_exc())
            self.error_signal.emit(str(e))
    
    def _get_user_profile(self, username):
        """Get TikTok user profile data"""
        try:
            self.rate_limiter.wait_if_needed()
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json'
            }
            
            # Check if username is already a secUid
            if username.startswith('MS4wLjABAAAA'):
                # Try to get user info directly
                url = f"https://www.tiktok.com/api/user/detail/?secUid={username}"
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('userInfo'):
                        return {
                            'id': data['userInfo']['user']['id'],
                            'secUid': username,
                            'uniqueId': data['userInfo']['user']['uniqueId'],
                            'nickname': data['userInfo']['user']['nickname'],
                            'avatarUrl': data['userInfo']['user'].get('avatarLarger', '')
                        }
            
            # Try to get user by username
            url = f"https://www.tiktok.com/api/search/user/full/?keyword={username}&count=1"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('userList', [])
                
                if users:
                    user = users[0]['user']
                    return {
                        'id': user['id'],
                        'secUid': user['secUid'],
                        'uniqueId': user['uniqueId'],
                        'nickname': user['nickname'],
                        'avatarUrl': user.get('avatarLarger', '')
                    }
                    
            # If API fails, try scraping
            return self._scrape_user_profile(username)
                
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return self._scrape_user_profile(username)
    
    def _scrape_user_profile(self, username):
        """Scrape TikTok user profile as fallback"""
        try:
            self.rate_limiter.wait_if_needed()
            
            url = f"https://www.tiktok.com/@{username}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return None
                
            # Parse HTML to extract user data
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for JSON data in script tags
            for script in soup.find_all('script'):
                if script.string and 'SIGI_STATE' in script.string:
                    data = re.search(r'SIGI_STATE"\s*:\s*(\{.*?\})\s*};', script.string)
                    if data:
                        try:
                            json_data = json.loads(data.group(1))
                            user_data = json_data.get('UserModule', {}).get('users', {}).get(username)
                            if user_data:
                                return {
                                    'id': user_data.get('id'),
                                    'secUid': user_data.get('secUid'),
                                    'uniqueId': user_data.get('uniqueId'),
                                    'nickname': user_data.get('nickname'),
                                    'avatarUrl': user_data.get('avatarLarger', '')
                                }
                        except:
                            pass
            
            # If we couldn't find the data in JSON, try basic extraction
            return {
                'id': username,
                'secUid': username,
                'uniqueId': username,
                'nickname': username,
                'avatarUrl': ''
            }
                
        except Exception as e:
            logger.error(f"Error scraping user profile: {str(e)}")
            # Return basic user info if scraping fails
            return {
                'id': username,
                'secUid': username,
                'uniqueId': username,
                'nickname': username,
                'avatarUrl': ''
            }
    
    def _get_user_videos(self, sec_uid, user_id, cursor=0):
        """Get videos from a TikTok user"""
        try:
            all_videos = []
            
            while len(all_videos) < self.max_videos and not self.should_stop:
                self.rate_limiter.wait_if_needed()
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'application/json'
                }
                
                url = (f"https://www.tiktok.com/api/post/item_list/?secUid={sec_uid}"
                      f"&id={user_id}&count=30&cursor={cursor}")
                
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    break
                    
                data = response.json()
                videos_batch = data.get('itemList', [])
                
                if not videos_batch:
                    break
                    
                all_videos.extend(videos_batch)
                
                # Update progress
                progress = min(60, int(20 + (40 * len(all_videos) / self.max_videos)))
                self.progress_signal.emit(progress, f"Retrieved {len(all_videos)} videos...")
                
                # Check if there are more videos
                has_more = data.get('hasMore', False)
                if not has_more:
                    break
                
                # Update cursor for next page
                cursor = data.get('cursor', 0)
            
            return all_videos
            
        except Exception as e:
            logger.error(f"Error getting user videos: {str(e)}")
            return []
    
    def _extract_locations_from_videos(self, videos):
        """Extract location data from TikTok videos"""
        locations = []
        
        for video in videos:
            try:
                # TikTok videos can have location data in 'locationCreated' or 'diversificationLabels'
                location_data = None
                lat = None
                lon = None
                location_name = None
                
                # Check for POI (Point of Interest) in the video
                if 'poiInfo' in video and video['poiInfo']:
                    poi = video['poiInfo']
                    location_name = poi.get('poiName', '')
                    # Some POIs have coordinates
                    if 'coordinates' in poi:
                        lat = poi['coordinates'].get('latitude')
                        lon = poi['coordinates'].get('longitude')
                
                # Check for location in text
                if not (lat and lon):
                    location_match = self._extract_location_from_text(video.get('desc', ''))
                    if location_match:
                        lat, lon = location_match
                
                # If we found coordinates, create location object
                if lat and lon:
                    # Parse date
                    try:
                        created_at = video.get('createTime', 0)
                        date = datetime.datetime.fromtimestamp(created_at)
                    except:
                        date = datetime.datetime.now()
                    
                    # Create location object
                    loc = {
                        'plugin': 'tiktok',
                        'lat': lat,
                        'lon': lon,
                        'date': date,
                        'context': video.get('desc', '')[:100],
                        'infowindow': self._create_video_infowindow(video, location_name),
                        'shortName': location_name or 'TikTok Location',
                    }
                    locations.append(loc)
                
            except Exception as e:
                logger.error(f"Error processing video: {str(e)}")
        
        return locations
    
    def _extract_location_from_text(self, text):
        """Extract location coordinates from video text/description"""
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
    
    def _create_video_infowindow(self, video, location_name=None):
        """Create info window HTML for a TikTok video"""
        desc = video.get('desc', 'No description')
        
        try:
            created_at = video.get('createTime', 0)
            date = datetime.datetime.fromtimestamp(created_at)
            formatted_date = date.strftime('%Y-%m-%d %H:%M')
        except:
            formatted_date = 'Unknown date'
            
        # Get video cover image
        cover_image = ''
        if 'video' in video and 'cover' in video['video']:
            cover_image = video['video']['cover']
            
        # Get video URL
        video_id = video.get('id')
        author = video.get('author', {}).get('uniqueId', '')
        video_url = f"https://www.tiktok.com/@{author}/video/{video_id}" if video_id else ""
        
        # Location display
        location_html = f"<p><strong>Location:</strong> {location_name}</p>" if location_name else ""
        
        html = f"""<div class="tiktok-video">
            <h3>TikTok Video</h3>
            <div class="video-content">
                <img src="{cover_image}" alt="Video cover" class="thumbnail" onclick="window.open('{video_url}', '_blank')">
                <div class="video-details">
                    <p><strong>Caption:</strong> {desc}</p>
                    <p><strong>Date:</strong> {formatted_date}</p>
                    {location_html}
                </div>
            </div>
            <p><a href="{video_url}" target="_blank">View on TikTok</a></p>
        </div>"""
        
        return html
        
    def stop(self):
        """Stop the thread"""
        self.should_stop = True

class TikTokPlugin(InputPlugin):
    name = "tiktok"
    hasWizard = False  # No special authentication needed for public data
    
    def __init__(self):
        InputPlugin.__init__(self)
        self.description = "Extract location data from TikTok videos"
        self.searchOffline = False
        
        # Load configuration
        self._config_path = os.path.join(os.path.expanduser("~"), ".creepy", "tiktok.conf")
        self._cache_path = os.path.join(os.path.expanduser("~"), ".creepy", "tiktok_cache")
        os.makedirs(self._cache_path, exist_ok=True)
        self._load_config()
        
        # Load labels
        try:
            labels_file = os.path.join(os.path.dirname(__file__), 'tiktok.labels')
            labels_config = ConfigObj(infile=labels_file)
            self.labels = labels_config.get('labels', {})
        except Exception as e:
            logger.error(f"Error loading labels: {str(e)}")
            self.labels = {}
            
    def _load_config(self):
        """Load configuration from file"""
        self.configured = True  # TikTok doesn't require specific auth
        self.config = {
            'max_videos': 200,
            'use_cache': True
        }
        
        config_dir = os.path.dirname(self._config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {str(e)}")
                
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self._config_path, 'w') as f:
                json.dump(self.config, f)
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")
        
    def activate(self):
        logger.info("TikTokPlugin activated")
        
    def deactivate(self):
        logger.info("TikTokPlugin deactivated")
    
    def isConfigured(self):
        """Check if the plugin is properly configured"""
        return (True, "Plugin is ready to use (no special configuration required)")
    
    def searchForTargets(self, search_term):
        """Search for targets matching the search term"""
        logger.info(f"Searching for TikTok users matching: {search_term}")
        
        targets = []
        
        try:
            # For TikTok, just create a target with the username
            targets.append({
                'targetUsername': search_term,
                'targetUserid': search_term,
                'targetFullname': f"TikTok user: {search_term}",
                'targetPicture': '',
                'pluginName': self.name
            })
        except Exception as e:
            logger.error(f"Error searching for targets: {str(e)}")
            
        return targets
    
    def returnLocations(self, target, search_params):
        """Return location data for the target"""
        logger.info(f"Getting locations for TikTok user {target['targetUsername']}")
        
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
            dialog.setWindowTitle("TikTok Data Fetch")
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
            api = {'base_url': 'https://www.tiktok.com/api'}
            fetch_thread = TikTokDataFetchThread(api, username, self.config.get('max_videos', 200))
            
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
    
    def getConfigurationParameters(self):
        """Return configuration parameters for the plugin"""
        return [
            {'name': 'max_videos', 'type': 'integer', 'default': 200},
            {'name': 'use_cache', 'type': 'boolean', 'default': True}
        ]
        
    def setConfigurationParameters(self, params):
        """Set configuration parameters for the plugin"""
        if 'max_videos' in params:
            self.config['max_videos'] = params.get('max_videos', 200)
            self.config['use_cache'] = params.get('use_cache', True)
            
            self._save_config()
            return (True, "Configuration saved successfully")
        else:
            return (False, "Required parameters missing")
            
    def getLabelForKey(self, key):
        """Return user-friendly labels for configuration keys"""
        labels = {
            "max_videos": "Maximum Videos to Retrieve",
            "use_cache": "Cache Results"
        }
        return labels.get(key, key)
