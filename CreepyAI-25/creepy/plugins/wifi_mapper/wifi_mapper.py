#!/usr/bin/python
# -*- coding: utf-8 -*-
from models.InputPlugin import InputPlugin
import os
import datetime
import random
import logging
import json
import re
import csv
from pathlib import Path
import math

# set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class WifiMapperPlugin(InputPlugin):
    name = "wifi_mapper"
    
    def __init__(self):
        InputPlugin.__init__(self)
        self.description = "Map wireless networks from exports and war-driving data"
        self.searchOffline = True
        self.hasWizard = True
        self._config_path = os.path.join(os.path.expanduser("~"), ".creepy", "wifi_mapper.conf")
        self._default_paths = {
            'wigle': os.path.join(os.path.expanduser("~"), "Downloads", "WigleWifi"),
            'kismet': os.path.join(os.path.expanduser("~"), "Downloads", "Kismet"),
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
        logger.info("WifiMapperPlugin activated")
        
    def deactivate(self):
        logger.info("WifiMapperPlugin deactivated")
    
    def isConfigured(self):
        if self.configured:
            return (True, "Plugin is configured.")
        else:
            return (False, "Please configure WiFi data path in plugin settings.")
    
    def _calculate_signal_coverage(self, lat, lon, rssi):
        """Calculate an approximate coverage radius based on signal strength"""
        # Convert RSSI to a rough distance estimate
        # RSSI typically ranges from -30 (very close) to -100 (very far)
        if rssi >= -50:  # Strong signal
            radius = 0.05  # ~50m
        elif rssi >= -65:  # Good signal
            radius = 0.1   # ~100m
        elif rssi >= -75:  # Fair signal
            radius = 0.2   # ~200m
        else:  # Weak signal
            radius = 0.3   # ~300m
            
        return radius
        
    def _parse_wigle_csv(self, filename):
        """Parse WiFi networks from a WiGLE CSV export"""
        networks = []
        
        try:
            with open(filename, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.reader(f)
                # Skip header
                next(reader, None)
                
                for row in reader:
                    try:
                        # WiGLE CSV format
                        # MAC,SSID,AuthMode,FirstSeen,Channel,RSSI,CurrentLatitude,CurrentLongitude,etc...
                        if len(row) >= 8:
                            mac = row[0]
                            ssid = row[1] or "Hidden Network"
                            auth = row[2]
                            first_seen = row[3]
                            channel = row[4]
                            rssi = float(row[5]) if row[5] else -75.0
                            lat = float(row[6]) if row[6] else 0.0
                            lon = float(row[7]) if row[7] else 0.0
                            
                            if lat != 0.0 and lon != 0.0:
                                networks.append({
                                    'mac': mac,
                                    'ssid': ssid,
                                    'auth': auth,
                                    'channel': channel,
                                    'rssi': rssi,
                                    'lat': lat,
                                    'lon': lon,
                                    'first_seen': first_seen,
                                    'source': 'wigle'
                                })
                    except Exception as e:
                        logger.warning(f"Error parsing WiGLE CSV row: {str(e)}")
                        continue
        except Exception as e:
            logger.error(f"Failed to parse WiGLE file {filename}: {str(e)}")
            
        return networks
    
    def _parse_kismet_netxml(self, filename):
        """Parse WiFi networks from a Kismet NetXML file"""
        networks = []
        
        # In a real implementation, you'd use an XML parser
        # This is a simplified mock parser for demonstration
        try:
            with open(filename, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
                # Very basic regex extraction - not recommended for production
                network_blocks = re.findall(r'<wireless-network[^>]*>(.*?)</wireless-network>', 
                                           content, re.DOTALL)
                
                for block in network_blocks:
                    try:
                        ssid_match = re.search(r'<essid[^>]*>(.*?)</essid>', block, re.DOTALL)
                        ssid = ssid_match.group(1).strip() if ssid_match else "Hidden Network"
                        
                        mac_match = re.search(r'<BSSID>(.*?)</BSSID>', block, re.DOTALL)
                        mac = mac_match.group(1).strip() if mac_match else "00:00:00:00:00:00"
                        
                        lat_match = re.search(r'<gps-info>.*?<lat>(.*?)</lat>', block, re.DOTALL)
                        lat = float(lat_match.group(1)) if lat_match else 0.0
                        
                        lon_match = re.search(r'<gps-info>.*?<lon>(.*?)</lon>', block, re.DOTALL)
                        lon = float(lon_match.group(1)) if lon_match else 0.0
                        
                        if lat != 0.0 and lon != 0.0:
                            # Extract other info
                            channel_match = re.search(r'<channel>(.*?)</channel>', block, re.DOTALL)
                            channel = channel_match.group(1) if channel_match else "0"
                            
                            encryption_match = re.search(r'<encryption>(.*?)</encryption>', block, re.DOTALL)
                            auth = encryption_match.group(1) if encryption_match else "Unknown"
                            
                            signal_match = re.search(r'<signal_dbm>(.*?)</signal_dbm>', block, re.DOTALL)
                            rssi = float(signal_match.group(1)) if signal_match else -75.0
                            
                            first_seen_match = re.search(r'<first-time>(.*?)</first-time>', block, re.DOTALL)
                            first_seen = first_seen_match.group(1) if first_seen_match else "Unknown"
                            
                            networks.append({
                                'mac': mac,
                                'ssid': ssid,
                                'auth': auth,
                                'channel': channel,
                                'rssi': rssi,
                                'lat': lat,
                                'lon': lon,
                                'first_seen': first_seen,
                                'source': 'kismet'
                            })
                    except Exception as e:
                        logger.warning(f"Error parsing network block: {str(e)}")
                        continue
        except Exception as e:
            logger.error(f"Failed to parse Kismet file {filename}: {str(e)}")
            
        return networks
    
    def _scan_wifi_directory(self):
        """Scan configured directory for WiFi network data"""
        data_path = self.config.get('data_path', '')
        if not data_path or not os.path.exists(data_path):
            return []
            
        networks = []
        
        # Look for WiGLE CSV exports
        csv_files = list(Path(data_path).glob("*.csv"))
        for csv_file in csv_files:
            networks.extend(self._parse_wigle_csv(csv_file))
            
        # Look for Kismet NetXML files
        netxml_files = list(Path(data_path).glob("*.netxml"))
        for netxml_file in netxml_files:
            networks.extend(self._parse_kismet_netxml(netxml_file))
            
        return networks
    
    def _group_networks_by_location(self, networks, proximity_threshold=0.001):
        """Group networks that are close to each other"""
        if not networks:
            return []
            
        # Sort by SSID to prioritize grouping same networks together
        networks = sorted(networks, key=lambda x: x['ssid'])
        
        groups = []
        added = set()
        
        for i, network in enumerate(networks):
            if i in added:
                continue
                
            group = [network]
            added.add(i)
            
            # Find other networks of the same SSID that are nearby
            for j, other in enumerate(networks):
                if j not in added and network['ssid'] == other['ssid']:
                    distance = math.sqrt((network['lat'] - other['lat'])**2 + 
                                         (network['lon'] - other['lon'])**2)
                    if distance < proximity_threshold:
                        group.append(other)
                        added.add(j)
            
            # Average the location if multiple points
            if len(group) > 1:
                avg_lat = sum(n['lat'] for n in group) / len(group)
                avg_lon = sum(n['lon'] for n in group) / len(group)
                avg_rssi = sum(n['rssi'] for n in group) / len(group)
                # Use the most recent observation for other details
                network = max(group, key=lambda x: x.get('first_seen', ''))
                network['lat'] = avg_lat
                network['lon'] = avg_lon
                network['rssi'] = avg_rssi
                network['count'] = len(group)
            else:
                network['count'] = 1
                
            groups.append(network)
            
        return groups
    
    def searchForTargets(self, search_term):
        """Return available targets based on search term (SSIDs)"""
        networks = self._scan_wifi_directory()
        if not networks:
            # Return search term as an SSID if no networks found
            return [{
                'targetUsername': search_term,
                'targetUserid': f"ssid_{search_term}",
                'targetFullname': f"Network: {search_term}",
                'targetPicture': 'wifi.png',
                'pluginName': self.name
            }]
            
        # Group networks by SSID
        ssids = {}
        for network in networks:
            ssid = network['ssid']
            if ssid not in ssids:
                ssids[ssid] = 0
            ssids[ssid] += 1
            
        # Filter SSIDs matching search term
        matches = []
        for ssid, count in ssids.items():
            if search_term.lower() in ssid.lower():
                matches.append({
                    'targetUsername': ssid,
                    'targetUserid': f"ssid_{ssid.replace(' ', '_')}",
                    'targetFullname': f"Network: {ssid} ({count} APs)",
                    'targetPicture': 'wifi.png',
                    'pluginName': self.name
                })
                
        return sorted(matches, key=lambda x: x['targetFullname'])[:20]  # Limit to 20 matches
    
    def returnLocations(self, target, search_params):
        """Return location data for the target SSID"""
        networks = self._scan_wifi_directory()
        
        if not networks:
            # Generate mock data if no networks found
            return self._generate_mock_networks(target['targetUsername'], 8)
            
        # Find networks matching the target SSID
        ssid = target['targetUsername']
        matching_networks = [n for n in networks if n['ssid'] == ssid]
        
        # Group nearby APs
        grouped_networks = self._group_networks_by_location(matching_networks)
        
        # Convert to CreepyAI location format
        locations = []
        for network in grouped_networks:
            # Determine encryption icon
            if "WPA" in network['auth'] or "WPA2" in network['auth']:
                security = "🔒" # Locked
            elif "WEP" in network['auth']:
                security = "🔓" # Somewhat secure
            elif "OPN" in network['auth']:
                security = "⚠️" # Open network
            else:
                security = "❓" # Unknown
                
            # Format date if available
            date_str = network.get('first_seen', 'Unknown')
            try:
                if date_str != 'Unknown':
                    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                else:
                    date_obj = datetime.datetime.now()
            except:
                date_obj = datetime.datetime.now()
                
            count = network.get('count', 1)
            ap_text = "access point" if count == 1 else "access points"
                
            location = {
                "plugin": self.name,
                "lat": network['lat'],
                "lon": network['lon'],
                "date": date_obj,
                "context": f"WiFi network {ssid} ({security}) on channel {network['channel']}",
                "infowindow": f"""<div class="wifi-network">
                    <h3>{security} {ssid}</h3>
                    <p><strong>MAC Address:</strong> {network['mac']}</p>
                    <p><strong>Channel:</strong> {network['channel']}</p>
                    <p><strong>Security:</strong> {network['auth']}</p>
                    <p><strong>Signal:</strong> {network['rssi']} dBm</p>
                    <p><strong>First Seen:</strong> {date_str}</p>
                    <p><strong>Source:</strong> {network['source'].upper()}</p>
                    <p>{count} {ap_text} observed at this location</p>
                </div>""",
                "shortName": f"{ssid} ({network['channel']})"
            }
            locations.append(location)
                
        return locations
    
    def _generate_mock_networks(self, ssid, count=8):
        """Generate mock WiFi network data for demo purposes"""
        locations = []
        
        # Generate a consistent base location based on the SSID
        # This ensures the same SSID will always generate the same locations
        seed = sum(ord(c) for c in ssid) % 1000
        random.seed(seed)
        
        base_lat = random.uniform(30, 50)  # Northern hemisphere
        base_lon = random.uniform(-100, 0)  # Western hemisphere
        
        channels = [1, 6, 11, 36, 40]  # Common channels
        securities = ["WPA2-PSK", "WPA2-PSK", "WPA2-PSK", "WPA-PSK", "WPA3-PSK", "OPN"]
        
        # Generate a realistic deployment - multiple APs of the same network
        for i in range(count):
            # Create variance in locations
            lat = base_lat + random.uniform(-0.05, 0.05)
            lon = base_lon + random.uniform(-0.05, 0.05)
            
            # Create a random MAC address with a consistent vendor prefix
            mac = f"00:11:22:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}"
            
            # Select technical details
            channel = random.choice(channels)
            security = random.choice(securities)
            rssi = random.uniform(-85, -45)
            
            # Date within the last year
            date = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365))
            date_str = date.strftime("%Y-%m-%d %H:%M:%S")
            
            # Determine security icon
            if "WPA" in security:
                security_icon = "🔒" # Locked
            elif security == "OPN":
                security_icon = "⚠️" # Open network
            else:
                security_icon = "❓" # Unknown
            
            location = {
                "plugin": self.name,
                "lat": lat,
                "lon": lon,
                "date": date,
                "context": f"WiFi network {ssid} ({security_icon}) on channel {channel}",
                "infowindow": f"""<div class="wifi-network">
                    <h3>{security_icon} {ssid}</h3>
                    <p><strong>MAC Address:</strong> {mac}</p>
                    <p><strong>Channel:</strong> {channel}</p>
                    <p><strong>Security:</strong> {security}</p>
                    <p><strong>Signal:</strong> {rssi:.1f} dBm</p>
                    <p><strong>First Seen:</strong> {date_str}</p>
                    <p><strong>Source:</strong> SIMULATED</p>
                    <p>1 access point observed at this location</p>
                </div>""",
                "shortName": f"{ssid} ({channel})"
            }
            locations.append(location)
            
        return locations
    
    def getConfigurationParameters(self):
        """Return configuration parameters for the plugin"""
        return [
            {'name': 'data_path', 'type': 'path', 'default': self._default_paths['wigle']},
            {'name': 'data_source', 'type': 'option', 'values': ['wigle', 'kismet', 'other'], 'default': 'wigle'}
        ]
        
    def setConfigurationParameters(self, params):
        """Set configuration parameters for the plugin"""
        if 'data_path' in params:
            path = params['data_path']
            if not os.path.exists(path):
                # Try to create the directory if it doesn't exist
                try:
                    os.makedirs(path)
                except Exception as e:
                    return (False, f"Could not create directory: {str(e)}")
                    
            self.config['data_path'] = path
            self.config['data_source'] = params.get('data_source', 'wigle')
            self._save_config()
            self.configured = True
            return (True, "Configuration saved successfully")
        else:
            return (False, "Data path not specified")
            
    def getLabelForKey(self, key):
        """Return user-friendly labels for configuration keys"""
        labels = {
            "data_path": "WiFi Data Directory",
            "data_source": "Data Source Type"
        }
        return labels.get(key, key)
