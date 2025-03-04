#!/usr/bin/python
# -*- coding: utf-8 -*-
from models.InputPlugin import InputPlugin
import os
import datetime
import random
import logging
import json
import math
import numpy as np
from pathlib import Path

# set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class LocationHistoryPlugin(InputPlugin):
    name = "location_history"
    
    def __init__(self):
        InputPlugin.__init__(self)
        self.description = "Extract and analyze location history data"
        self.searchOffline = True
        self.hasWizard = True
        self._config_path = os.path.join(os.path.expanduser("~"), ".creepy", "location_history.conf")
        self._default_paths = {
            'google': os.path.join(os.path.expanduser("~"), "Downloads", "Takeout", "Location History"),
            'apple': os.path.join(os.path.expanduser("~"), "Downloads", "apple_location_history"),
        }
        self._load_config()
        
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
                    if self.config.get('data_path'):
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
        logger.info("LocationHistoryPlugin activated")
        
    def deactivate(self):
        logger.info("LocationHistoryPlugin deactivated")
    
    def isConfigured(self):
        if self.configured:
            return (True, "Plugin is configured.")
        else:
            return (False, "Please configure data path in plugin settings.")
    
    def _get_possible_users(self):
        """Scan for available location history data files"""
        users = []
        data_path = self.config.get('data_path', '')
        
        if not data_path or not os.path.exists(data_path):
            return users
            
        # Google location history format
        if os.path.exists(os.path.join(data_path, "Location History.json")):
            users.append({
                'targetUsername': 'google_user',
                'targetUserid': 'google_location_history',
                'targetFullname': 'Google Location History',
                'targetPicture': 'google.png',
                'pluginName': self.name
            })
            
        # Apple location history format
        if list(Path(data_path).glob("*.csv")):
            users.append({
                'targetUsername': 'apple_user',
                'targetUserid': 'apple_location_history',
                'targetFullname': 'Apple Location History',
                'targetPicture': 'apple.png',
                'pluginName': self.name
            })
            
        return users
    
    def _parse_google_location(self, filename):
        """Parse Google location history data"""
        locations = []
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            if 'locations' in data:
                for loc in data['locations'][:1000]:  # Limit to 1000 points for performance
                    try:
                        lat = float(loc['latitudeE7']) / 1e7
                        lon = float(loc['longitudeE7']) / 1e7
                        timestamp = int(loc['timestampMs']) / 1000
                        date = datetime.datetime.fromtimestamp(timestamp)
                        
                        accuracy = loc.get('accuracy', 0)
                        activity = ', '.join(a['activity'] for a in loc.get('activity', [])[:3]) if 'activity' in loc else 'Unknown'
                        
                        location = {
                            "plugin": self.name,
                            "lat": lat,
                            "lon": lon,
                            "date": date,
                            "context": f"Location recorded with {accuracy}m accuracy",
                            "infowindow": f"""<div class="location-history">
                                <h3>Location History</h3>
                                <p>Date: {date.strftime('%Y-%m-%d %H:%M:%S')}</p>
                                <p>Accuracy: {accuracy}m</p>
                                <p>Activity: {activity}</p>
                                <p>Coordinates: {lat:.6f}, {lon:.6f}</p>
                            </div>""",
                            "shortName": date.strftime("%Y-%m-%d %H:%M")
                        }
                        locations.append(location)
                    except (KeyError, ValueError) as e:
                        logger.warning(f"Error parsing location entry: {str(e)}")
                        continue
        except Exception as e:
            logger.error(f"Failed to parse Google location data: {str(e)}")
            
        return locations
    
    def _parse_apple_location(self, directory):
        """Parse Apple location history data"""
        locations = []
        
        try:
            csv_files = list(Path(directory).glob("*.csv"))
            for csv_file in csv_files:
                with open(csv_file, 'r') as f:
                    # Skip header
                    next(f)
                    for line in f:
                        try:
                            parts = line.strip().split(',')
                            if len(parts) >= 5:
                                date_str, time_str, lat_str, lon_str, accuracy_str = parts[:5]
                                date_obj = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                                lat = float(lat_str)
                                lon = float(lon_str)
                                accuracy = float(accuracy_str) if accuracy_str else 0
                                
                                location = {
                                    "plugin": self.name,
                                    "lat": lat,
                                    "lon": lon,
                                    "date": date_obj,
                                    "context": f"Apple location history at {date_obj.strftime('%Y-%m-%d %H:%M')}",
                                    "infowindow": f"""<div class="location-history">
                                        <h3>Apple Location History</h3>
                                        <p>Date: {date_obj.strftime('%Y-%m-%d %H:%M:%S')}</p>
                                        <p>Accuracy: {accuracy}m</p>
                                        <p>Coordinates: {lat:.6f}, {lon:.6f}</p>
                                    </div>""",
                                    "shortName": date_obj.strftime("%Y-%m-%d %H:%M")
                                }
                                locations.append(location)
                        except Exception as e:
                            logger.warning(f"Error parsing line in Apple data: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to parse Apple location data: {str(e)}")
            
        return locations
    
    def searchForTargets(self, search_term):
        """Return available users based on search term"""
        users = self._get_possible_users()
        if not users:
            # Use search term as user if no local data found
            return [{
                'targetUsername': search_term,
                'targetUserid': f"user_{search_term}",
                'targetFullname': search_term,
                'targetPicture': 'default.png',
                'pluginName': self.name
            }]
        return users
    
    def returnLocations(self, target, search_params):
        """Return location data for the target"""
        locations = []
        data_path = self.config.get('data_path', '')
        
        if not data_path or not os.path.exists(data_path):
            return locations
            
        if target['targetUserid'] == 'google_location_history':
            google_file = os.path.join(data_path, "Location History.json")
            if os.path.exists(google_file):
                locations = self._parse_google_location(google_file)
        elif target['targetUserid'] == 'apple_location_history':
            locations = self._parse_apple_location(data_path)
        else:
            # Generate some mock data for demo purposes
            locations = self._generate_mock_locations(target['targetUsername'], 50)
            
        return locations
    
    def _generate_mock_locations(self, username, count=50):
        """Generate mock location history data for demo purposes"""
        locations = []
        
        # Define some common locations/routes
        home = (random.uniform(40.0, 42.0), random.uniform(-74.0, -72.0))  # NYC area
        work = (home[0] + random.uniform(-0.05, 0.05), home[1] + random.uniform(-0.05, 0.05))
        
        # Generate patterns: home->work->lunch->work->home
        now = datetime.datetime.now()
        
        for day in range(14):  # 2 weeks of history
            base_date = now - datetime.timedelta(days=day)
            
            # Morning at home (6-8 AM)
            home_morning = base_date.replace(hour=random.randint(6, 8), minute=random.randint(0, 59))
            locations.append(self._create_mock_location(home[0], home[1], home_morning, "Home"))
            
            # Commute to work
            commute_time = home_morning + datetime.timedelta(minutes=random.randint(20, 60))
            # Create a few points along the commute route
            for i in range(3):
                t = (i + 1) / 4  # Interpolation factor
                lat = home[0] * (1-t) + work[0] * t
                lon = home[1] * (1-t) + work[1] * t
                jitter = random.uniform(-0.001, 0.001)  # Add some randomness
                locations.append(self._create_mock_location(
                    lat + jitter, lon + jitter, 
                    commute_time + datetime.timedelta(minutes=random.randint(5, 15) * i),
                    "Commuting"
                ))
            
            # At work (9 AM - 5 PM)
            work_time = base_date.replace(hour=9, minute=random.randint(0, 30))
            locations.append(self._create_mock_location(work[0], work[1], work_time, "Work"))
            
            # Lunch break
            lunch_place = (work[0] + random.uniform(-0.01, 0.01), work[1] + random.uniform(-0.01, 0.01))
            lunch_time = base_date.replace(hour=random.randint(12, 13), minute=random.randint(0, 59))
            locations.append(self._create_mock_location(lunch_place[0], lunch_place[1], lunch_time, "Lunch"))
            
            # Back to work
            after_lunch = lunch_time + datetime.timedelta(hours=random.uniform(0.5, 1.5))
            locations.append(self._create_mock_location(work[0], work[1], after_lunch, "Work"))
            
            # Commute home
            leave_work = base_date.replace(hour=random.randint(17, 19), minute=random.randint(0, 59))
            # Create a few points along the return commute route
            for i in range(3):
                t = (i + 1) / 4  # Interpolation factor
                lat = work[0] * (1-t) + home[0] * t
                lon = work[1] * (1-t) + home[1] * t
                jitter = random.uniform(-0.001, 0.001)  # Add some randomness
                locations.append(self._create_mock_location(
                    lat + jitter, lon + jitter, 
                    leave_work + datetime.timedelta(minutes=random.randint(5, 15) * i),
                    "Commuting"
                ))
            
            # Evening at home
            home_evening = leave_work + datetime.timedelta(hours=random.uniform(0.5, 1.0))
            locations.append(self._create_mock_location(home[0], home[1], home_evening, "Home"))
        
        # Sort by date and limit to count
        locations = sorted(locations, key=lambda x: x['date'])
        if len(locations) > count:
            locations = locations[:count]
            
        return locations
    
    def _create_mock_location(self, lat, lon, date, label):
        """Helper to create a mock location entry"""
        accuracy = random.randint(5, 100)  # Accuracy in meters
        
        return {
            "plugin": self.name,
            "lat": lat,
            "lon": lon,
            "date": date,
            "context": f"Location recorded: {label}",
            "infowindow": f"""<div class="location-history">
                <h3>Location: {label}</h3>
                <p>Date: {date.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Accuracy: {accuracy}m</p>
                <p>Coordinates: {lat:.6f}, {lon:.6f}</p>
            </div>""",
            "shortName": f"{label} - {date.strftime('%H:%M')}"
        }
    
    def getConfigurationParameters(self):
        """Return configuration parameters for the plugin"""
        return [
            {'name': 'data_path', 'type': 'path', 'default': self._default_paths['google']},
            {'name': 'source_type', 'type': 'option', 'values': ['google', 'apple', 'other'], 'default': 'google'}
        ]
        
    def setConfigurationParameters(self, params):
        """Set configuration parameters for the plugin"""
        if 'data_path' in params and os.path.exists(params['data_path']):
            self.config['data_path'] = params['data_path']
            self.config['source_type'] = params.get('source_type', 'google')
            self._save_config()
            self.configured = True
            return (True, "Configuration saved successfully")
        else:
            return (False, "Invalid data path specified")
            
    def getLabelForKey(self, key):
        """Return user-friendly labels for configuration keys"""
        labels = {
            "data_path": "Location History Data Path",
            "source_type": "Source Type (Google/Apple)"
        }
        return labels.get(key, key)
