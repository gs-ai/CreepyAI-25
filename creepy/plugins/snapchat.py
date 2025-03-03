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
                           QProgressBar, QCheckBox, QFileDialog)
from PyQt5.QtCore import QUrl, pyqtSignal, QObject, QThread
import webbrowser
from bs4 import BeautifulSoup

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class SnapchatMapExtractor:
    """Helper class to extract data from the Snapchat Map"""
    
    def __init__(self):
        self.base_url = "https://map.snapchat.com"
        self.api_url = "https://ms.sc-jpl.com/web/getSnap"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://map.snapchat.com/'
        }
        
    def extract_stories_from_coordinates(self, lat, lon, radius_meters=1000):
        """Extract stories from coordinates"""
        try:
            params = {
                'lat': lat,
                'lng': lon,
                'radius': radius_meters,
                'limit': 50
            }
            
            response = requests.get(
                self.api_url,
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('elements', [])
            else:
                logger.error(f"Failed to extract stories: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting stories: {str(e)}")
            return []
            
    def extract_story_details(self, story_id):
        """Extract details for a specific story"""
        try:
            params = {
                'id': story_id
            }
            
            response = requests.get(
                f"{self.api_url}/{story_id}",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to extract story details: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting story details: {str(e)}")
            return None

class SnapchatMemoriesParser:
    """Helper class to parse Snapchat memories data export"""
    
    def parse_memories_json(self, file_path):
        """Parse Snapchat memories JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            memories = []
            for entry in data.get('Saved Media', []):
                try:
                    # Extract location if available
                    location = None
                    if 'Location' in entry and entry['Location'] and 'Latitude' in entry['Location'] and 'Longitude' in entry['Location']:
                        location = {
                            'latitude': float(entry['Location']['Latitude']),
                            'longitude': float(entry['Location']['Longitude'])
                        }
                        
                    if location:
                        # Parse date
                        date = None
                        if 'Date' in entry:
                            try:
                                date = datetime.datetime.strptime(entry['Date'], '%Y-%m-%d %H:%M:%S %Z')
                            except:
                                try:
                                    date = datetime.datetime.strptime(entry['Date'], '%Y-%m-%d %H:%M:%S')
                                except:
                                    date = datetime.datetime.now()
                        
                        # Create memory object
                        memory = {
                            'id': entry.get('Media ID', ''),
                            'date': date,
                            'location': location,
                            'type': entry.get('Media Type', 'Unknown'),
                            'file_path': entry.get('Download Link', '')
                        }
                        memories.append(memory)
                except Exception as e:
                    logger.error(f"Error parsing memory entry: {str(e)}")
                    
            return memories
            
        except Exception as e:
            logger.error(f"Error parsing memories file: {str(e)}")
            return []

class SnapchatDataFetchThread(QThread):
    """Thread to fetch data from Snapchat"""
    progress_signal = pyqtSignal(int, str)
    complete_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, config, search_params=None):
        super().__init__()
        self.config = config
        self.search_params = search_params or {}
        self.should_stop = False
        
    def run(self):
        """Main thread execution to fetch Snapchat data"""
        try:
            locations = []
            self.progress_signal.emit(10, "Processing Snapchat data...")
            
            # There are three modes of operation:
            # 1. Parse memories JSON export
            # 2. Extract from coordinates (search all spots)
            # 3. Extract from custom coordinates (search specific spots)
            
            # Mode 1: Parse memories export
            if self.config.get('memories_file') and os.path.exists(self.config.get('memories_file')):
                self.progress_signal.emit(20, "Parsing Snapchat memories export...")
                parser = SnapchatMemoriesParser()
                memories = parser.parse_memories_json(self.config.get('memories_file'))
                
                if memories:
                    self.progress_signal.emit(50, f"Found {len(memories)} memories with location data")
                    
                    # Convert memories to location format
                    for i, memory in enumerate(memories):
                        if self.should_stop:
                            return
                            
                        progress = 50 + min(40, int(40 * i / len(memories)))
                        self.progress_signal.emit(progress, f"Processing memory {i+1} of {len(memories)}")
                        
                        loc = {
                            'plugin': 'snapchat',
                            'lat': memory['location']['latitude'],
                            'lon': memory['location']['longitude'],
                            'date': memory['date'],
                            'context': f"Snapchat Memory ({memory['type']})",
                            'infowindow': self._create_memory_infowindow(memory),
                            'shortName': "Snapchat Memory",
                        }
                        locations.append(loc)
                else:
                    self.progress_signal.emit(60, "No memories with location data found")
            
            # Mode 2 & 3: Extract from coordinates
            search_coordinates = []
            
            # Add predefined coordinates from configuration
            for coord in self.config.get('search_coordinates', []):
                search_coordinates.append(coord)
                
            # Add custom coordinates from search parameters
            if self.search_params.get('search_coordinates'):
                for coord in self.search_params.get('search_coordinates'):
                    search_coordinates.append(coord)
                    
            if search_coordinates:
                self.progress_signal.emit(70, f"Searching Snapchat Map at {len(search_coordinates)} locations")
                
                map_extractor = SnapchatMapExtractor()
                for i, coord in enumerate(search_coordinates):
                    if self.should_stop:
                        return
                        
                    progress = 70 + min(20, int(20 * i / len(search_coordinates)))
                    self.progress_signal.emit(progress, f"Searching location {i+1} of {len(search_coordinates)}")
                    
                    stories = map_extractor.extract_stories_from_coordinates(
                        coord['lat'], 
                        coord['lon'],
                        radius_meters=coord.get('radius', 1000)
                    )
                    
                    if stories:
                        for story in stories:
                            try:
                                if ('lat' in story and 'lng' in story and 
                                    story['lat'] is not None and story['lng'] is not None):
                                    
                                    # Parse date
                                    try:
                                        timestamp = story.get('timestamp', 0) / 1000  # Convert from milliseconds
                                        date = datetime.datetime.fromtimestamp(timestamp)
                                    except:
                                        date = datetime.datetime.now()
                                    
                                    # Create location object
                                    loc = {
                                        'plugin': 'snapchat',
                                        'lat': story['lat'],
                                        'lon': story['lng'],
                                        'date': date,
                                        'context': story.get('venue', {}).get('name', 'Snapchat Story'),
                                        'infowindow': self._create_story_infowindow(story),
                                        'shortName': story.get('venue', {}).get('name', 'Snapchat Location'),
                                    }
                                    locations.append(loc)
                            except Exception as e:
                                logger.error(f"Error processing story: {str(e)}")
            
            self.progress_signal.emit(100, f"Completed! Found {len(locations)} locations from Snapchat")
            self.complete_signal.emit(locations)
            
        except Exception as e:
            logger.error(f"Error in Snapchat data fetch: {str(e)}")
            logger.debug(traceback.format_exc())
            self.error_signal.emit(str(e))
    
    def _create_memory_infowindow(self, memory):
        """Create info window HTML for a Snapchat memory"""
        date_str = memory['date'].strftime('%Y-%m-%d %H:%M') if memory['date'] else 'Unknown date'
        
        html = f"""<div class="snapchat-memory">
            <h3>Snapchat Memory</h3>
            <div class="memory-details">
                <p><strong>Date:</strong> {date_str}</p>
                <p><strong>Type:</strong> {memory['type']}</p>
                <p><strong>ID:</strong> {memory['id']}</p>
            </div>
        </div>"""
        
        return html
    
    def _create_story_infowindow(self, story):
        """Create info window HTML for a Snapchat story"""
        # Parse timestamp
        try:
            timestamp = story.get('timestamp', 0) / 1000  # Convert from milliseconds
            date = datetime.datetime.fromtimestamp(timestamp)
            date_str = date.strftime('%Y-%m-%d %H:%M')
        except:
            date_str = 'Unknown date'
            
        venue_name = story.get('venue', {}).get('name', 'Unknown Location')
        
        # Get preview image if available
        preview_url = story.get('snapInfo', {}).get('previewUrl', '')
        image_html = f'<img src="{preview_url}" alt="Story preview" class="thumbnail">' if preview_url else ''
        
        html = f"""<div class="snapchat-story">
            <h3>Snapchat Story at {venue_name}</h3>
            {image_html}
            <div class="story-details">
                <p><strong>Date:</strong> {date_str}</p>
                <p><strong>Location:</strong> {venue_name}</p>
            </div>
        </div>"""
        
        return html
    
    def stop(self):
        """Stop the thread"""
        self.should_stop = True

class SnapchatPlugin(InputPlugin):
    name = "snapchat"
    hasWizard = True
    
    def __init__(self):
        InputPlugin.__init__(self)
        self.description = "Extract location data from Snapchat memories and map"
        self.searchOffline = False
        
        # Load configuration
        self._config_path = os.path.join(os.path.expanduser("~"), ".creepy", "snapchat.conf")
        self._cache_path = os.path.join(os.path.expanduser("~"), ".creepy", "snapchat_cache")
        os.makedirs(self._cache_path, exist_ok=True)
        self._load_config()
        
        # Load labels
        try:
            labels_file = os.path.join(os.path.dirname(__file__), 'snapchat.labels')
            labels_config = ConfigObj(infile=labels_file)
            self.labels = labels_config.get('labels', {})
        except Exception as e:
            logger.error(f"Error loading labels: {str(e)}")
            self.labels = {}
            
    def _load_config(self):
        """Load configuration from file"""
        self.configured = False
        self.config = {
            'memories_file': '',
            'search_coordinates': [],
            'use_cache': True
        }
        
        config_dir = os.path.dirname(self._config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r') as f:
                    self.config = json.load(f)
                
                # Check if we have valid configuration
                if self.config.get('memories_file') or self.config.get('search_coordinates'):
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
        
    def activate(self):
        logger.info("SnapchatPlugin activated")
        if not self.configured:
            logger.warning("Snapchat plugin is not configured yet")
        
    def deactivate(self):
        logger.info("SnapchatPlugin deactivated")
    
    def isConfigured(self):
        """Check if the plugin is properly configured"""
        if not self.configured:
            return (False, "Please configure Snapchat plugin")
            
        if self.config.get('memories_file') and os.path.exists(self.config.get('memories_file')):
            return (True, "Snapchat memories file configured")
        elif self.config.get('search_coordinates'):
            return (True, f"{len(self.config.get('search_coordinates'))} search locations configured")
        else:
            return (False, "No valid data sources configured")
    
    def searchForTargets(self, search_term):
        """Search for targets matching the search term"""
        logger.info(f"Searching for Snapchat data sources")
        
        targets = []
        
        # Add target for Snapchat memories file if configured
        if self.config.get('memories_file') and os.path.exists(self.config.get('memories_file')):
            targets.append({
                'targetUsername': 'memories',
                'targetUserid': 'snapchat_memories',
                'targetFullname': 'Snapchat Memories',
                'targetPicture': '',
                'pluginName': self.name
            })
            
        # Add target for map search coordinates
        if self.config.get('search_coordinates'):
            targets.append({
                'targetUsername': 'map',
                'targetUserid': 'snapchat_map',
                'targetFullname': 'Snapchat Map',
                'targetPicture': '',
                'pluginName': self.name
            })
            
        # If search term is a coordinate pair, add it as custom search
        coord_match = re.search(r'(-?\d+\.\d+)[,\s]+(-?\d+\.\d+)', search_term)
        if coord_match:
            try:
                lat = float(coord_match.group(1))
                lon = float(coord_match.group(2))
                
                targets.append({
                    'targetUsername': f"{lat},{lon}",
                    'targetUserid': 'snapchat_custom_location',
                    'targetFullname': f"Snapchat Custom Location ({lat}, {lon})",
                    'targetPicture': '',
                    'pluginName': self.name,
                    'coordinates': {'lat': lat, 'lon': lon, 'radius': 1000}
                })
            except:
                pass
                
        # If no targets found, suggest configuration
        if not targets:
            targets.append({
                'targetUsername': 'setup',
                'targetUserid': 'snapchat_setup',
                'targetFullname': 'Configure Snapchat Plugin',
                'targetPicture': '',
                'pluginName': self.name
            })
            
        return targets
    
    def returnLocations(self, target, search_params):
        """Return location data for the target"""
        logger.info(f"Getting locations from Snapchat for {target.get('targetFullname')}")
        
        # Check if target is the configuration target
        if target.get('targetUserid') == 'snapchat_setup':
            self.runConfigWizard()
            return []
            
        # Determine search parameters based on target type
        params = {}
        if target.get('targetUserid') == 'snapchat_custom_location' and target.get('coordinates'):
            params['search_coordinates'] = [{
                'lat': target['coordinates']['lat'],
                'lon': target['coordinates']['lon'],
                'radius': target['coordinates'].get('radius', 1000)
            }]
            
        # Check if we already have cached results for this target
        cache_key = target.get('targetUserid')
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
        
        # Show progress dialog and start data fetch thread
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
            from PyQt5.QtCore import Qt
            
            # Create progress dialog
            dialog = QDialog()
            dialog.setWindowTitle("Snapchat Data Fetch")
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
            fetch_thread = SnapchatDataFetchThread(self.config, params)
            
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
        """Run configuration wizard to set up Snapchat plugin"""
        from PyQt5.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QLabel, QPushButton,
                                    QTextBrowser, QMessageBox, QTableWidget, QTableWidgetItem,
                                    QHeaderView, QHBoxLayout, QGroupBox, QDoubleSpinBox)
        
        wizard = QWizard()
        wizard.setWindowTitle("Snapchat Plugin Configuration")
        wizard.setMinimumSize(600, 500)
        
        # Welcome page
        welcome_page = QWizardPage()
        welcome_page.setTitle("Snapchat Plugin Setup")
        
        welcome_layout = QVBoxLayout()
        welcome_text = QTextBrowser()
        welcome_text.setOpenExternalLinks(True)
        welcome_text.setHtml("""
        <h2>Welcome to Snapchat Plugin Setup</h2>
        <p>This wizard will help you set up the Snapchat plugin for CreepyAI.</p>
        <p>There are two ways to extract location data from Snapchat:</p>
        <ol>
            <li>Upload your Snapchat memories data export (contains location metadata)</li>
            <li>Configure specific locations to search on the Snapchat Map</li>
        </ol>
        <p>You can set up either or both methods.</p>
        """)
        welcome_layout.addWidget(welcome_text)
        welcome_page.setLayout(welcome_layout)
        wizard.addPage(welcome_page)
        
        # Memories configuration page
        memories_page = QWizardPage()
        memories_page.setTitle("Snapchat Memories Configuration")
        
        memories_layout = QVBoxLayout()
        memories_text = QTextBrowser()
        memories_text.setHtml("""
        <h3>Snapchat Memories Export</h3>
        <p>You can request your Snapchat data export from the Snapchat app:</p>
        <ol>
            <li>Open Snapchat and go to your profile</li>
            <li>Tap the gear icon to access Settings</li>
            <li>Scroll down to 'Privacy' and select 'My Data'</li>
            <li>Follow the instructions to request and download your data</li>
        </ol>
        <p>Once you have your data, select the memories.json file below:</p>
        """)
        memories_layout.addWidget(memories_text)
        
        # File selection
        file_group = QGroupBox("Memories File")
        file_layout = QHBoxLayout()
        
        file_label = QLabel("Selected file:")
        file_layout.addWidget(file_label)
        
        file_path_label = QLabel(self.config.get('memories_file', 'No file selected'))
        file_layout.addWidget(file_path_label, 1)
        
        browse_button = QPushButton("Browse...")
        file_layout.addWidget(browse_button)
        
        file_group.setLayout(file_layout)
        memories_layout.addWidget(file_group)
        
        # Status label
        status_label = QLabel("")
        memories_layout.addWidget(status_label)
        
        memories_page.setLayout(memories_layout)
        wizard.addPage(memories_page)
        
        # Browse button handler
        def browse_file():
            file_path, _ = QFileDialog.getOpenFileName(
                None, "Select Snapchat Memories JSON File", "", "JSON Files (*.json);;All Files (*)"
            )
            if file_path:
                file_path_label.setText(file_path)
                
                # Validate file
                try:
                    parser = SnapchatMemoriesParser()
                    memories = parser.parse_memories_json(file_path)
                    if memories:
                        status_label.setText(f"<span style='color:green;'>Found {len(memories)} memories with location data</span>")
                    else:
                        status_label.setText("<span style='color:orange;'>No memories with location data found in this file</span>")
                except Exception as e:
                    status_label.setText(f"<span style='color:red;'>Error parsing file: {str(e)}</span>")
                    
        browse_button.clicked.connect(browse_file)
        
        # Map locations configuration page
        map_page = QWizardPage()
        map_page.setTitle("Snapchat Map Configuration")
        
        map_layout = QVBoxLayout()
        map_text = QTextBrowser()
        map_text.setHtml("""
        <h3>Snapchat Map Locations</h3>
        <p>You can add specific locations to search for content on the Snapchat Map.</p>
        <p>For each location, specify the latitude, longitude, and search radius in meters.</p>
        <p>Popular locations like tourist attractions, public events, and landmarks often have public stories.</p>
        """)
        map_layout.addWidget(map_text)
        
        # Locations table
        locations_table = QTableWidget()
        locations_table.setColumnCount(3)
        locations_table.setHorizontalHeaderLabels(["Latitude", "Longitude", "Radius (m)"])
        locations_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Load existing locations
        existing_locations = self.config.get('search_coordinates', [])
        locations_table.setRowCount(max(1, len(existing_locations)))
        
        for i, loc in enumerate(existing_locations):
            locations_table.setItem(i, 0, QTableWidgetItem(str(loc['lat'])))
            locations_table.setItem(i, 1, QTableWidgetItem(str(loc['lon'])))
            locations_table.setItem(i, 2, QTableWidgetItem(str(loc.get('radius', 1000))))
            
        map_layout.addWidget(locations_table)
        
        # Buttons for table manipulation
        btn_layout = QHBoxLayout()
        add_row_btn = QPushButton("Add Row")
        delete_row_btn = QPushButton("Delete Selected Row")
        
        btn_layout.addWidget(add_row_btn)
        btn_layout.addWidget(delete_row_btn)
        map_layout.addLayout(btn_layout)
        
        # Add a row handler
        def add_row():
            current_rows = locations_table.rowCount()
            locations_table.setRowCount(current_rows + 1)
            # Set default values
            locations_table.setItem(current_rows, 0, QTableWidgetItem("0.0"))
            locations_table.setItem(current_rows, 1, QTableWidgetItem("0.0"))
            locations_table.setItem(current_rows, 2, QTableWidgetItem("1000"))
            
        add_row_btn.clicked.connect(add_row)
        
        # Delete row handler
        def delete_row():
            selected_rows = locations_table.selectedIndexes()
            if selected_rows:
                row = selected_rows[0].row()
                locations_table.removeRow(row)
                # Ensure we always have at least one row
                if locations_table.rowCount() == 0:
                    add_row()
                    
        delete_row_btn.clicked.connect(delete_row)
        
        # Cache option
        cache_group = QGroupBox("Caching Options")
        cache_layout = QVBoxLayout()
        
        use_cache_checkbox = QCheckBox("Cache results to improve performance")
        use_cache_checkbox.setChecked(self.config.get('use_cache', True))
        cache_layout.addWidget(use_cache_checkbox)
        
        cache_group.setLayout(cache_layout)
        map_layout.addWidget(cache_group)
        
        map_page.setLayout(map_layout)
        wizard.addPage(map_page)
        
        # Final page
        final_page = QWizardPage()
        final_page.setTitle("Setup Complete")
        
        final_layout = QVBoxLayout()
        final_text = QTextBrowser()
        final_text.setHtml("""
        <h3>Configuration Complete!</h3>
        <p>Your Snapchat plugin is now configured and ready to use.</p>
        <p>You can now search for Snapchat data and extract location information.</p>
        <p>To get started, use the search function and enter:</p>
        <ul>
            <li>"memories" to analyze your Snapchat memories</li>
            <li>"map" to search your configured locations</li>
            <li>Or enter coordinates like "40.7128, -74.0060" to search a custom location</li>
        </ul>
        """)
        final_layout.addWidget(final_text)
        final_page.setLayout(final_layout)
        wizard.addPage(final_page)
        
        # Process results
        if wizard.exec_():
            # Save memories file path
            self.config['memories_file'] = file_path_label.text()
            if self.config['memories_file'] == 'No file selected':
                self.config['memories_file'] = ''
                
            # Save locations
            search_coordinates = []
            for row in range(locations_table.rowCount()):
                try:
                    lat_item = locations_table.item(row, 0)
                    lon_item = locations_table.item(row, 1)
                    radius_item = locations_table.item(row, 2)
                    
                    if lat_item and lon_item and radius_item:
                        lat = float(lat_item.text())
                        lon = float(lon_item.text())
                        radius = int(float(radius_item.text()))
                        
                        if -90 <= lat <= 90 and -180 <= lon <= 180 and radius > 0:
                            search_coordinates.append({
                                'lat': lat,
                                'lon': lon,
                                'radius': radius
                            })
                except Exception as e:
                    logger.error(f"Error parsing coordinates at row {row}: {str(e)}")
                    
            self.config['search_coordinates'] = search_coordinates
            self.config['use_cache'] = use_cache_checkbox.isChecked()
            
            # Save configuration
            self._save_config()
            self.configured = bool(self.config['memories_file'] or self.config['search_coordinates'])
            
            QMessageBox.information(None, "Configuration Saved", 
                                  "Snapchat plugin configuration has been saved successfully.")
            return True
        else:
            return False
    
    def getConfigurationParameters(self):
        """Return configuration parameters for the plugin"""
        return [
            {'name': 'memories_file', 'type': 'string', 'default': ''},
            {'name': 'search_coordinates', 'type': 'list', 'default': []},
            {'name': 'use_cache', 'type': 'boolean', 'default': True}
        ]
        
    def setConfigurationParameters(self, params):
        """Set configuration parameters for the plugin"""
        if 'memories_file' in params or 'search_coordinates' in params:
            self.config['memories_file'] = params.get('memories_file', '')
            self.config['search_coordinates'] = params.get('search_coordinates', [])
            self.config['use_cache'] = params.get('use_cache', True)
            
            self._save_config()
            self.configured = bool(self.config['memories_file'] or self.config['search_coordinates'])
            return (True, "Configuration saved successfully")
        else:
            return (False, "No valid configuration parameters provided")
            
    def getLabelForKey(self, key):
        """Return user-friendly labels for configuration keys"""
        labels = {
            "memories_file": "Snapchat Memories File",
            "search_coordinates": "Map Search Locations",
            "use_cache": "Cache Results"
        }
        return labels.get(key, key)
