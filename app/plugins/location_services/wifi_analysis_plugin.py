#!/usr/bin/python
# -*- coding: utf-8 -*-

""""""""""""
WiFi Analysis Plugin for CreepyAI""
""
This plugin extracts location data from WiFi scan data and logs.""
It supports various formats of WiFi scanner outputs and can correlate
WiFi networks with known locations.
""""""""""""
""
import os""
import re""
import csv
import json
import glob
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Set
import configparser
import sqlite3
from pathlib import Path

from app.plugins.base_plugin import BasePlugin, LocationPoint
from app.plugins.enhanced_geocoding_helper import EnhancedGeocodingHelper

logger = logging.getLogger(__name__)

class WiFiAnalysisPlugin(BasePlugin):
    """Plugin for extracting location data from WiFi scan data"""""""""""
    
    def __init__(self):
        super().__init__(
        name="WiFi Analysis",
        description="Extract location data from WiFi scan results and logs"
        )
        self.wifi_db = None
        self.geocoder = EnhancedGeocodingHelper()
        self._load_config_from_conf()
        self._connect_to_db()
        
    def _load_config_from_conf(self) -> None:
            """Load configuration from .conf file if available"""""""""""
            conf_path = os.path.join(os.path.dirname(__file__), 'WifiMonitor.conf')
        if os.path.exists(conf_path):
            try:
                    config = configparser.ConfigParser()
                    config.read(conf_path)
                
                # Convert the conf sections to our config format
                    new_config = {}
                
                if 'string_options' in config:
                    for key, value in config['string_options'].items():
                            new_config[key] = value
                
                if 'boolean_options' in config:
                    for key, value in config['boolean_options'].items():
                                    new_config[key] = value.lower() == 'true'
                
                if 'integer_options' in config:
                    for key, value in config['integer_options'].items():
                        try:
                                                new_config[key] = int(value)
                        except (ValueError, TypeError):
                                                pass
                
                if 'array_options' in config:
                    for key, value in config['array_options'].items():
                        try:
                            # Parse JSON arrays
                                                            new_config[key] = json.loads(value)
                        except:
                            # Fallback to comma-separated
                                                                new_config[key] = [item.strip() for item in value.split(',')]
                
                # Update config
                                                                self.config.update(new_config)
                                                                self._save_config()
                
            except Exception as e:
                                                                    logger.error(f"Error loading .conf file: {e}")
    
    def _connect_to_db(self) -> None:
                                                                        """Connect to WiFi database or create if it doesn't exist"""'""""""""
                                                                        db_path = self.config.get('wifi_db_path')
        if not db_path:
                                                                            db_path = os.path.join(self.data_dir, 'wifi_networks.db')
                                                                            self.config['wifi_db_path'] = db_path
                                                                            self._save_config()
        
        try:
                                                                                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                                                                                self.wifi_db = sqlite3.connect(db_path)
                                                                                self._create_tables()
        except Exception as e:
                                                                                    logger.error(f"Error connecting to WiFi database: {e}")
                                                                                    self.wifi_db = None
    
    def _create_tables(self) -> None:
                                                                                        """Create necessary tables in the database if they don't exist"""'""""""""
                                                                                        if not self.wifi_db:''
                                                                                    return''
                                                                                    ''
                                                                                    cursor = self.wifi_db.cursor()
        
        # WiFi networks table
                                                                                    cursor.execute(''''
                                                                                    CREATE TABLE IF NOT EXISTS wifi_networks (''
                                                                                    bssid TEXT PRIMARY KEY,''
                                                                                    ssid TEXT,''
                                                                                    last_seen TIMESTAMP,
                                                                                    first_seen TIMESTAMP,
                                                                                    channel INTEGER,
                                                                                    frequency INTEGER,
                                                                                    signal_strength INTEGER,
                                                                                    security TEXT,
                                                                                    latitude REAL,
                                                                                    longitude REAL,
                                                                                    accuracy REAL,
                                                                                    source TEXT
                                                                                    )
                                                                                    ''')'
                                                                                    ''
        # WiFi sightings table (for historical data)''
                                                                                    cursor.execute(''''
                                                                                    CREATE TABLE IF NOT EXISTS wifi_sightings (''
                                                                                    id INTEGER PRIMARY KEY AUTOINCREMENT,''
                                                                                    bssid TEXT,''
                                                                                    ssid TEXT,
                                                                                    timestamp TIMESTAMP,
                                                                                    signal_strength INTEGER,
                                                                                    latitude REAL,
                                                                                    longitude REAL,
                                                                                    accuracy REAL,
                                                                                    source TEXT,
                                                                                    FOREIGN KEY (bssid) REFERENCES wifi_networks (bssid)
                                                                                    )
                                                                                    ''')'
                                                                                    ''
        # Create indices for faster lookups''
                                                                                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_wifi_bssid ON wifi_networks (bssid)")''
                                                                                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_wifi_ssid ON wifi_networks (ssid)")
                                                                                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sightings_bssid ON wifi_sightings (bssid)")
                                                                                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sightings_timestamp ON wifi_sightings (timestamp)")
        
                                                                                    self.wifi_db.commit()
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
                                                                                        """Return configuration options for this plugin"""""""""""
                                                                                    return [
                                                                                    {
                                                                                    "name": "wifi_db_path",
                                                                                    "display_name": "WiFi Database Path",
                                                                                    "type": "file",
                                                                                    "default": os.path.join(self.data_dir, 'wifi_networks.db'),
                                                                                    "required": False,
                                                                                    "description": "Path to SQLite database for storing WiFi network data"
                                                                                    },
                                                                                    {
                                                                                    "name": "wigle_api_key",
                                                                                    "display_name": "WiGLE API Key",
                                                                                    "type": "string",
                                                                                    "default": "",
                                                                                    "required": False,
                                                                                    "description": "Optional API key for WiGLE WiFi database (for offline use, leave empty)"
                                                                                    },
                                                                                    {
                                                                                    "name": "data_directory",
                                                                                    "display_name": "Scan Data Directory",
                                                                                    "type": "directory",
                                                                                    "default": "",
                                                                                    "required": True,
                                                                                    "description": "Directory containing WiFi scan data to analyze"
                                                                                    },
                                                                                    {
                                                                                    "name": "use_trilateration",
                                                                                    "display_name": "Use Trilateration",
                                                                                    "type": "boolean",
                                                                                    "default": True,
                                                                                    "required": False,
                                                                                    "description": "Calculate position using WiFi signal strength"
                                                                                    },
                                                                                    {
                                                                                    "name": "min_networks_for_location",
                                                                                    "display_name": "Minimum Networks",
                                                                                    "type": "integer",
                                                                                    "default": 3,
                                                                                    "min": 1,
                                                                                    "max": 10,
                                                                                    "required": False,
                                                                                    "description": "Minimum number of networks needed for a location fix"
                                                                                    }
                                                                                    ]
    
    def is_configured(self) -> Tuple[bool, str]:
                                                                                        """Check if the plugin is properly configured"""""""""""
        # Check if data directory is set and exists
                                                                                        data_dir = self.config.get("data_directory", "")
        if not data_dir:
                                                                                        return False, "Scan data directory not configured"
        
        # Database connection
        if not self.wifi_db:
                                                                                        return False, "Could not connect to WiFi database"
        
                                                                                    return True, "WiFi Analysis plugin is configured"
    
                                                                                    def collect_locations(self, target: str, date_from: Optional[datetime] = None,
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
                                                                                        """"""""""""
                                                                                        Extract location data from WiFi scan data""
                                                                                        ""
                                                                                        Args:""
                                                                                        target: Directory containing WiFi scan data
                                                                                        date_from: Optional start date filter
                                                                                        date_to: Optional end date filter
            
        Returns:
                                                                                            List of location points
                                                                                            """"""""""""
                                                                                            locations = []""
                                                                                            ""
        # Use configured data directory if target is not specified""
                                                                                            data_dir = target
        if not os.path.exists(data_dir):
                                                                                                data_dir = self.config.get("data_directory", "")
            if not os.path.exists(data_dir):
                                                                                                    logger.warning(f"Data directory does not exist: {data_dir}")
                                                                                                return locations
        
        # Find all scan files in the directory
                                                                                                scan_files = []
                                                                                                scan_files.extend(glob.glob(os.path.join(data_dir, "**/*.csv"), recursive=True))
                                                                                                scan_files.extend(glob.glob(os.path.join(data_dir, "**/*.json"), recursive=True))
                                                                                                scan_files.extend(glob.glob(os.path.join(data_dir, "**/*.txt"), recursive=True))
                                                                                                scan_files.extend(glob.glob(os.path.join(data_dir, "**/*.xml"), recursive=True))
        
        # Process each file
        for scan_file in scan_files:
            try:
                                                                                                        file_ext = os.path.splitext(scan_file)[1].lower()
                
                # Process based on file type
                if file_ext == '.csv':
                                                                                                            file_locations = self._process_csv_file(scan_file, date_from, date_to)
                elif file_ext == '.json':
                                                                                                                file_locations = self._process_json_file(scan_file, date_from, date_to)
                elif file_ext == '.txt':
                                                                                                                    file_locations = self._process_text_file(scan_file, date_from, date_to)
                elif file_ext == '.xml':
                                                                                                                        file_locations = self._process_xml_file(scan_file, date_from, date_to)
                else:
                                                                                                                            logger.warning(f"Unsupported file type: {scan_file}")
                                                                                                                            file_locations = []
                
                                                                                                                            locations.extend(file_locations)
                
            except Exception as e:
                                                                                                                                logger.error(f"Error processing WiFi scan file {scan_file}: {e}")
        
        # Save the geocoder cache
                                                                                                                                self.geocoder.save_cache()
        
                                                                                                                            return locations
    
                                                                                                                            def _process_csv_file(self, file_path: str, date_from: Optional[datetime],
                         date_to: Optional[datetime]) -> List[LocationPoint]:
                                                                                                                                """Process a CSV format WiFi scan file"""""""""""
                                                                                                                                locations = []
        
        try:
            # Read the CSV file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Try to determine the CSV format
                                                                                                                                        first_line = f.readline().strip()
                                                                                                                                        f.seek(0)  # Reset file pointer
                
                # Detect CSV dialect
                                                                                                                                        dialect = csv.Sniffer().sniff(first_line)
                                                                                                                                        reader = csv.DictReader(f, dialect=dialect)
                
                # Get column names and map to standard fields
                                                                                                                                        fieldnames = reader.fieldnames
                if not fieldnames:
                                                                                                                                        return locations
                
                # Different CSV formats can have differently named columns
                # Try to map common column names
                                                                                                                                        bssid_fields = ['bssid', 'mac', 'mac_address', 'address', 'ap_mac']
                                                                                                                                        ssid_fields = ['ssid', 'name', 'network_name', 'ap_name']
                                                                                                                                        signal_fields = ['signal', 'rssi', 'signal_strength', 'signal_level', 'dbm']
                                                                                                                                        timestamp_fields = ['timestamp', 'time', 'date', 'seen', 'last_seen']
                                                                                                                                        lat_fields = ['latitude', 'lat', 'y', 'latitude_e7']
                                                                                                                                        lon_fields = ['longitude', 'lon', 'lng', 'x', 'longitude_e7']
                
                # Find matching field names
                                                                                                                                        bssid_field = next((f for f in bssid_fields if f in fieldnames), None)
                                                                                                                                        ssid_field = next((f for f in ssid_fields if f in fieldnames), None)
                                                                                                                                        signal_field = next((f for f in signal_fields if f in fieldnames), None)
                                                                                                                                        timestamp_field = next((f for f in timestamp_fields if f in fieldnames), None)
                                                                                                                                        lat_field = next((f for f in lat_fields if f in fieldnames), None)
                                                                                                                                        lon_field = next((f for f in lon_fields if f in fieldnames), None)
                
                                                                                                                                        scan_networks = []
                                                                                                                                        timestamp = None
                
                # Process each row in the CSV
                for row in reader:
                    # Skip empty rows
                    if not any(row.values()):
                                                                                                                                            continue
                        
                    # Extract network data
                                                                                                                                            network = {
                                                                                                                                            'bssid': row[bssid_field] if bssid_field and bssid_field in row else None,
                                                                                                                                            'ssid': row[ssid_field] if ssid_field and ssid_field in row else None,
                                                                                                                                            'signal': row[signal_field] if signal_field and signal_field in row else None,
                                                                                                                                            }
                    
                    # Skip rows without BSSID
                    if not network['bssid']:
                                                                                                                                            continue
                    
                    # Standardize BSSID format (lowercase, colon-separated)
                                                                                                                                            network['bssid'] = self._normalize_bssid(network['bssid'])
                    
                    # Try to parse signal strength
                    if network['signal']:
                        try:
                                                                                                                                                    network['signal'] = int(network['signal'])
                        except (ValueError, TypeError):
                                                                                                                                                        network['signal'] = None
                    
                    # Handle timestamp
                    if timestamp_field and timestamp_field in row and row[timestamp_field]:
                        try:
                            # Try to parse timestamp
                                                                                                                                                                ts_str = row[timestamp_field]
                                                                                                                                                                timestamp = self._parse_timestamp(ts_str)
                        except (ValueError, TypeError):
                                                                                                                                                                    timestamp = None
                    
                    # Add to scan networks
                                                                                                                                                                    scan_networks.append(network)
                    
                    # If this row has lat/lon directly, create a location point
                    if lat_field and lon_field and lat_field in row and lon_field in row:
                        try:
                                                                                                                                                                            lat_val = row[lat_field]
                                                                                                                                                                            lon_val = row[lon_field]
                            
                            if lat_val and lon_val:
                                                                                                                                                                                lat = float(lat_val)
                                                                                                                                                                                lon = float(lon_val)
                                
                                # Handle E7 format
                                if 'e7' in lat_field.lower() or abs(lat) > 180:
                                                                                                                                                                                    lat = lat / 1e7
                                if 'e7' in lon_field.lower() or abs(lon) > 180:
                                                                                                                                                                                        lon = lon / 1e7
                                
                                # Validate coordinates
                                if -90 <= lat <= 90 and -180 <= lon <= 180:
                                    # Create location point from direct coordinates
                                                                                                                                                                                            locations.append(
                                                                                                                                                                                            LocationPoint(
                                                                                                                                                                                            latitude=lat,
                                                                                                                                                                                            longitude=lon,
                                                                                                                                                                                            timestamp=timestamp or datetime.now(),
                                                                                                                                                                                            source="WiFi Scan",
                                                                                                                                                                                            context=f"Networks: {len(scan_networks)} | File: {os.path.basename(file_path)}"
                                                                                                                                                                                            )
                                                                                                                                                                                            )
                        except (ValueError, TypeError):
                                                                                                                                                                                            pass
                
                # If we have scan networks but no direct coordinates
                if scan_networks and not locations:
                    # Try to lookup locations for the networks
                                                                                                                                                                                                scan_location = self._get_location_from_networks(scan_networks, timestamp)
                    if scan_location:
                                                                                                                                                                                                    locations.append(scan_location)
                
                # Save networks to database
                                                                                                                                                                                                    self._save_networks_to_db(scan_networks, timestamp)
                
        except Exception as e:
                                                                                                                                                                                                        logger.error(f"Error processing CSV file {file_path}: {e}")
        
        # Apply date filters
        if date_from or date_to:
                                                                                                                                                                                                            locations = [
                                                                                                                                                                                                            loc for loc in locations 
                                                                                                                                                                                                            if (not date_from or loc.timestamp >= date_from) and
                                                                                                                                                                                                            (not date_to or loc.timestamp <= date_to)
                                                                                                                                                                                                            ]
        
                                                                                                                                                                                                        return locations
    
                                                                                                                                                                                                        def _process_json_file(self, file_path: str, date_from: Optional[datetime],
                          date_to: Optional[datetime]) -> List[LocationPoint]:
                                                                                                                                                                                                            """Process a JSON format WiFi scan file"""""""""""
                                                                                                                                                                                                            locations = []
        
        try:
            # Read the JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                                                                                                                                                                                                                    data = json.load(f)
            
            # Handle different JSON formats
            
            # Format 1: Array of networks
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                                                                                                                                                                                                                        scan_networks = []
                                                                                                                                                                                                                        timestamp = datetime.now()
                
                for item in data:
                                                                                                                                                                                                                            network = {}
                    
                    # Try different field names
                    for bssid_key in ['bssid', 'BSSID', 'mac', 'MAC', 'macAddress']:
                        if bssid_key in item:
                                                                                                                                                                                                                                    network['bssid'] = self._normalize_bssid(item[bssid_key])
                                                                                                                                                                                                                                break
                            
                    for ssid_key in ['ssid', 'SSID', 'name', 'essid', 'ESSID']:
                        if ssid_key in item:
                                                                                                                                                                                                                                        network['ssid'] = item[ssid_key]
                                                                                                                                                                                                                                    break
                            
                    for signal_key in ['signal', 'SIGNAL', 'rssi', 'RSSI', 'level', 'signalLevel']:
                        if signal_key in item:
                            try:
                                                                                                                                                                                                                                                network['signal'] = int(item[signal_key])
                            except (ValueError, TypeError):
                                                                                                                                                                                                                                                pass
                                                                                                                                                                                                                                            break
                    
                    # Skip entries without BSSID
                    if 'bssid' not in network:
                                                                                                                                                                                                                                            continue
                        
                    # Add to scan networks
                                                                                                                                                                                                                                            scan_networks.append(network)
                    
                    # Check for coordinates in this network
                                                                                                                                                                                                                                            lat = None
                                                                                                                                                                                                                                            lon = None
                    
                    for lat_key in ['latitude', 'lat', 'Latitude']:
                        if lat_key in item:
                            try:
                                                                                                                                                                                                                                                        lat = float(item[lat_key])
                                if lat_key.lower().endswith('e7') or abs(lat) > 180:
                                                                                                                                                                                                                                                            lat = lat / 1e7
                            except (ValueError, TypeError):
                                                                                                                                                                                                                                                                lat = None
                                                                                                                                                                                                                                                            break
                            
                    for lon_key in ['longitude', 'lon', 'lng', 'Longitude']:
                        if lon_key in item:
                            try:
                                                                                                                                                                                                                                                                        lon = float(item[lon_key])
                                if lon_key.lower().endswith('e7') or abs(lon) > 180:
                                                                                                                                                                                                                                                                            lon = lon / 1e7
                            except (ValueError, TypeError):
                                                                                                                                                                                                                                                                                lon = None
                                                                                                                                                                                                                                                                            break
                    
                    # Look for timestamp
                    for time_key in ['timestamp', 'time', 'date', 'scanTime']:
                        if time_key in item:
                                                                                                                                                                                                                                                                                    timestamp = self._parse_timestamp(item[time_key])
                            if timestamp:
                                                                                                                                                                                                                                                                                    break
                    
                    # If this network has direct coordinates, create a location
                    if lat is not None and lon is not None:
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                                                                                                                                                                                                                                                                                            locations.append(
                                                                                                                                                                                                                                                                                            LocationPoint(
                                                                                                                                                                                                                                                                                            latitude=lat,
                                                                                                                                                                                                                                                                                            longitude=lon,
                                                                                                                                                                                                                                                                                            timestamp=timestamp,
                                                                                                                                                                                                                                                                                            source="WiFi Network",
                                                                                                                                                                                                                                                                                            context=f"Network: {network.get('ssid', network.get('bssid', 'Unknown'))}"
                                                                                                                                                                                                                                                                                            )
                                                                                                                                                                                                                                                                                            )
                
                # If we have scan networks but no direct coordinates
                if scan_networks and not locations:
                    # Try to lookup locations for the networks
                                                                                                                                                                                                                                                                                                scan_location = self._get_location_from_networks(scan_networks, timestamp)
                    if scan_location:
                                                                                                                                                                                                                                                                                                    locations.append(scan_location)
                
                # Save networks to database
                                                                                                                                                                                                                                                                                                    self._save_networks_to_db(scan_networks, timestamp)
            
            # Format 2: Object with scan info and networks array
            elif isinstance(data, dict) and any(key in data for key in ['networks', 'access_points', 'wifiNetworks']):
                # Find the networks array
                                                                                                                                                                                                                                                                                                        networks_key = next((key for key in ['networks', 'access_points', 'wifiNetworks'] if key in data), None)
                
                if networks_key and isinstance(data[networks_key], list):
                    # Extract common metadata
                                                                                                                                                                                                                                                                                                            timestamp = datetime.now()
                    
                    # Try to find scan timestamp
                    for time_key in ['timestamp', 'scanTime', 'time', 'date']:
                        if time_key in data:
                                                                                                                                                                                                                                                                                                                    ts = self._parse_timestamp(data[time_key])
                            if ts:
                                                                                                                                                                                                                                                                                                                        timestamp = ts
                                                                                                                                                                                                                                                                                                                    break
                    
                    # Process the networks
                                                                                                                                                                                                                                                                                                                    scan_networks = []
                    for item in data[networks_key]:
                                                                                                                                                                                                                                                                                                                        network = {}
                        
                        # Extract fields (same as Format 1)
                        for bssid_key in ['bssid', 'BSSID', 'mac', 'MAC', 'macAddress']:
                            if bssid_key in item:
                                                                                                                                                                                                                                                                                                                                network['bssid'] = self._normalize_bssid(item[bssid_key])
                                                                                                                                                                                                                                                                                                                            break
                                
                        for ssid_key in ['ssid', 'SSID', 'name', 'essid', 'ESSID']:
                            if ssid_key in item:
                                                                                                                                                                                                                                                                                                                                    network['ssid'] = item[ssid_key]
                                                                                                                                                                                                                                                                                                                                break
                                
                        for signal_key in ['signal', 'SIGNAL', 'rssi', 'RSSI', 'level', 'signalLevel']:
                            if signal_key in item:
                                try:
                                                                                                                                                                                                                                                                                                                                            network['signal'] = int(item[signal_key])
                                except (ValueError, TypeError):
                                                                                                                                                                                                                                                                                                                                            pass
                                                                                                                                                                                                                                                                                                                                        break
                        
                        # Skip entries without BSSID
                        if 'bssid' not in network:
                                                                                                                                                                                                                                                                                                                                        continue
                            
                        # Add to scan networks
                                                                                                                                                                                                                                                                                                                                        scan_networks.append(network)
                    
                    # If scan has location data
                                                                                                                                                                                                                                                                                                                                        lat = None
                                                                                                                                                                                                                                                                                                                                        lon = None
                    
                    # Try to find location in main object
                    for lat_key in ['latitude', 'lat', 'Latitude']:
                        if lat_key in data:
                            try:
                                                                                                                                                                                                                                                                                                                                                    lat = float(data[lat_key])
                                if lat_key.lower().endswith('e7') or abs(lat) > 180:
                                                                                                                                                                                                                                                                                                                                                        lat = lat / 1e7
                            except (ValueError, TypeError):
                                                                                                                                                                                                                                                                                                                                                            lat = None
                                                                                                                                                                                                                                                                                                                                                        break
                            
                    for lon_key in ['longitude', 'lon', 'lng', 'Longitude']:
                        if lon_key in data:
                            try:
                                                                                                                                                                                                                                                                                                                                                                    lon = float(data[lon_key])
                                if lon_key.lower().endswith('e7') or abs(lon) > 180:
                                                                                                                                                                                                                                                                                                                                                                        lon = lon / 1e7
                            except (ValueError, TypeError):
                                                                                                                                                                                                                                                                                                                                                                            lon = None
                                                                                                                                                                                                                                                                                                                                                                        break
                    
                    # If this scan has direct coordinates, create a location
                    if lat is not None and lon is not None:
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                                                                                                                                                                                                                                                                                                                                                                                locations.append(
                                                                                                                                                                                                                                                                                                                                                                                LocationPoint(
                                                                                                                                                                                                                                                                                                                                                                                latitude=lat,
                                                                                                                                                                                                                                                                                                                                                                                longitude=lon,
                                                                                                                                                                                                                                                                                                                                                                                timestamp=timestamp,
                                                                                                                                                                                                                                                                                                                                                                                source="WiFi Scan",
                                                                                                                                                                                                                                                                                                                                                                                context=f"Networks: {len(scan_networks)} | File: {os.path.basename(file_path)}"
                                                                                                                                                                                                                                                                                                                                                                                )
                                                                                                                                                                                                                                                                                                                                                                                )
                    
                    # If we have scan networks but no direct coordinates
                    if scan_networks and not locations:
                        # Try to lookup locations for the networks
                                                                                                                                                                                                                                                                                                                                                                                    scan_location = self._get_location_from_networks(scan_networks, timestamp)
                        if scan_location:
                                                                                                                                                                                                                                                                                                                                                                                        locations.append(scan_location)
                    
                    # Save networks to database
                                                                                                                                                                                                                                                                                                                                                                                        self._save_networks_to_db(scan_networks, timestamp)
        
        except Exception as e:
                                                                                                                                                                                                                                                                                                                                                                                            logger.error(f"Error processing JSON file {file_path}: {e}")
        
        # Apply date filters
        if date_from or date_to:
                                                                                                                                                                                                                                                                                                                                                                                                locations = [
                                                                                                                                                                                                                                                                                                                                                                                                loc for loc in locations 
                                                                                                                                                                                                                                                                                                                                                                                                if (not date_from or loc.timestamp >= date_from) and
                                                                                                                                                                                                                                                                                                                                                                                                (not date_to or loc.timestamp <= date_to)
                                                                                                                                                                                                                                                                                                                                                                                                ]
        
                                                                                                                                                                                                                                                                                                                                                                                            return locations
    
                                                                                                                                                                                                                                                                                                                                                                                            def _process_text_file(self, file_path: str, date_from: Optional[datetime],
                          date_to: Optional[datetime]) -> List[LocationPoint]:
                                                                                                                                                                                                                                                                                                                                                                                                """Process a text format WiFi scan file"""""""""""
                                                                                                                                                                                                                                                                                                                                                                                                locations = []
        
        try:
            # Common text formats:
            # 1. iwlist scan output
            # 2. netsh wlan show networks mode=bssid (Windows)
            # 3. airport -s (macOS)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                                                                                                                                                                                                                                                                                                                                                                                        content = f.read()
            
            # Try to determine the format
                                                                                                                                                                                                                                                                                                                                                                                                        scan_networks = []
                                                                                                                                                                                                                                                                                                                                                                                                        timestamp = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            # Check for iwlist format
            if "Cell " in content and "ESSID:" in content:
                # Process iwlist format
                                                                                                                                                                                                                                                                                                                                                                                                            cells = re.split(r'Cell \d+ - ', content)[1:]  # Skip the first empty part
                
                for cell in cells:
                                                                                                                                                                                                                                                                                                                                                                                                                bssid_match = re.search(r'Address: ([0-9A-Fa-f:]{17})', cell)
                                                                                                                                                                                                                                                                                                                                                                                                                ssid_match = re.search(r'ESSID:"([^"]*)"', cell)"
                                                                                                                                                                                                                                                                                                                                                                                                                signal_match = re.search(r'Signal level=(-?\d+) dBm', cell)""
                                                                                                                                                                                                                                                                                                                                                                                                                ""
                                                                                                                                                                                                                                                                                                                                                                                                                if bssid_match:""
                                                                                                                                                                                                                                                                                                                                                                                                                bssid = self._normalize_bssid(bssid_match.group(1))
                                                                                                                                                                                                                                                                                                                                                                                                                ssid = ssid_match.group(1) if ssid_match else ""
                                                                                                                                                                                                                                                                                                                                                                                                                signal = int(signal_match.group(1)) if signal_match else None
                        
                                                                                                                                                                                                                                                                                                                                                                                                                scan_networks.append({
                                                                                                                                                                                                                                                                                                                                                                                                                'bssid': bssid,
                                                                                                                                                                                                                                                                                                                                                                                                                'ssid': ssid,
                                                                                                                                                                                                                                                                                                                                                                                                                'signal': signal
                                                                                                                                                                                                                                                                                                                                                                                                                })
            
            # Check for netsh format (Windows)
            elif "SSID" in content and "BSSID" in content and "Signal" in content:
                # Process netsh format
                                                                                                                                                                                                                                                                                                                                                                                                                    networks = re.split(r'SSID \d+ : ', content)[1:]  # Skip the first empty part
                
                for network in networks:
                                                                                                                                                                                                                                                                                                                                                                                                                        ssid_match = re.search(r'^([^\r\n]+)', network)
                                                                                                                                                                                                                                                                                                                                                                                                                        bssids = re.findall(r'BSSID \d+ : ([0-9A-Fa-f:]{17})[\r\n\s]+Signal : (\d+)%', network)
                    
                    if ssid_match and bssids:
                                                                                                                                                                                                                                                                                                                                                                                                                            ssid = ssid_match.group(1).strip()
                        
                        for bssid, signal_percent in bssids:
                            # Convert percentage to dBm (roughly)
                            # 0% ~ -100 dBm, 100% ~ -50 dBm
                                                                                                                                                                                                                                                                                                                                                                                                                                signal = -100 + int(signal_percent) / 2
                            
                                                                                                                                                                                                                                                                                                                                                                                                                                scan_networks.append({
                                                                                                                                                                                                                                                                                                                                                                                                                                'bssid': self._normalize_bssid(bssid),
                                                                                                                                                                                                                                                                                                                                                                                                                                'ssid': ssid,
                                                                                                                                                                                                                                                                                                                                                                                                                                'signal': int(signal)
                                                                                                                                                                                                                                                                                                                                                                                                                                })
            
            # Check for airport format (macOS)
            elif re.search(r'[\r\n]\s*SSID\s+BSSID\s+RSSI\s+CHANNEL\s+', content):
                # Process airport format
                                                                                                                                                                                                                                                                                                                                                                                                                                    lines = content.strip().split('\n')
                
                # Find the header line
                                                                                                                                                                                                                                                                                                                                                                                                                                    header_index = next((i for i, line in enumerate(lines) if re.match(r'\s*SSID\s+BSSID\s+RSSI\s+', line)), -1)
                
                if header_index >= 0 and len(lines) > header_index + 1:
                    # Process networks
                    for line in lines[header_index + 1:]: