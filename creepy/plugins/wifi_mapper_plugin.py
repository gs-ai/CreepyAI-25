import os
import glob
import json
import csv
import re
import math
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from .base_plugin import BasePlugin, LocationPoint

class WifiMapperPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="WiFi Mapper",
            description="Extract location data from WiFi scanning data and exports"
        )
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "data_directory",
                "display_name": "WiFi Data Directory",
                "type": "directory",
                "default": "",
                "required": True,
                "description": "Directory containing WiFi scanning data (WiGLE exports, Kismet files, etc.)"
            },
            {
                "name": "data_format",
                "display_name": "Data Format",
                "type": "select",
                "options": ["auto_detect", "wigle", "kismet", "other"],
                "default": "auto_detect",
                "required": False,
                "description": "Format of WiFi data files"
            },
            {
                "name": "group_networks",
                "display_name": "Group Nearby Networks",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Group networks that appear to be at the same location"
            }
        ]
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None, 
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
        locations = []
        data_dir = self.config.get("data_directory", "")
        data_format = self.config.get("data_format", "auto_detect")
        group_networks = self.config.get("group_networks", True)
        
        if not data_dir or not os.path.exists(data_dir):
            return self._generate_mock_networks(target, 8)
            
        # Process WiFi data files
        networks = []
        
        # WiGLE CSV format
        if data_format in ["auto_detect", "wigle"]:
            wigle_networks = self._process_wigle_csv_files(data_dir)
            networks.extend(wigle_networks)
            
        # Kismet XML format
        if data_format in ["auto_detect", "kismet"]:
            kismet_networks = self._process_kismet_files(data_dir)
            networks.extend(kismet_networks)
            
        # Generic CSV format (might be exported from other tools)
        if data_format in ["auto_detect", "other"]:
            other_networks = self._process_generic_csv_files(data_dir)
            networks.extend(other_networks)
            
        # Filter networks by SSID/target
        filtered_networks = []
        for network in networks:
            ssid = network.get("ssid", "")
            if ssid == target:
                filtered_networks.append(network)
                
        # Group networks if configured
        if group_networks and filtered_networks:
            filtered_networks = self._group_networks_by_location(filtered_networks)
            
        # Convert to location points
        for network in filtered_networks:
            # Skip records without valid location
            if 'lat' not in network or 'lon' not in network:
                continue
                
            # Apply date filters
            if 'timestamp' in network:
                timestamp = network['timestamp']
                if date_from and timestamp < date_from:
                    continue
                if date_to and timestamp > date_to:
                    continue
            else:
                timestamp = datetime.now()
                
            # Determine encryption icon
            security = network.get('auth', '')
            if "WPA" in security or "WPA2" in security:
                security_icon = "🔒" # Locked
            elif "WEP" in security:
                security_icon = "🔓" # Somewhat secure
            elif "OPN" in security:
                security_icon = "⚠️" # Open network
            else:
                security_icon = "❓" # Unknown
                
            # Format context
            ssid = network.get('ssid', 'Unknown SSID')
            channel = network.get('channel', '0')
            count = network.get('count', 1)
            ap_text = "access point" if count == 1 else "access points"
                
            # Create location point
            locations.append(
                LocationPoint(
                    latitude=float(network['lat']),
                    longitude=float(network['lon']),
                    timestamp=timestamp,
                    source=f"WiFi Network - {network.get('source', 'Unknown')}",
                    context=f"WiFi network {ssid} ({security_icon}) on channel {channel}"
                )
            )
            
        return locations
    
    def _process_wigle_csv_files(self, data_dir: str) -> List[Dict]:
        """Process WiGLE CSV export files."""
        networks = []
        
        # Look for WiGLE CSV files
        csv_files = []
        for ext in ["*.csv"]:
            csv_files.extend(glob.glob(os.path.join(data_dir, ext)))
            csv_files.extend(glob.glob(os.path.join(data_dir, "**", ext), recursive=True))
            
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                    # Check if it's a WiGLE CSV file by reading first line
                    first_line = f.readline().strip()
                    if "WigleWifi" not in first_line and "MAC,SSID" not in first_line:
                        continue
                        
                    # Reset file pointer
                    f.seek(0)
                    
                    reader = csv.reader(f)
                    # Skip header row
                    next(reader, None)
                    
                    for row in reader:
                        try:
                            # WiGLE CSV format
                            # MAC,SSID,AuthMode,FirstSeen,Channel,RSSI,CurrentLatitude,CurrentLongitude,etc...
                            if len(row) < 8:
                                continue
                                
                            mac = row[0]
                            ssid = row[1] or "Hidden Network"
                            auth = row[2]
                            first_seen = row[3]
                            channel = row[4]
                            rssi = float(row[5]) if row[5] else -75.0
                            lat = float(row[6]) if row[6] else 0.0
                            lon = float(row[7]) if row[7] else 0.0
                            
                            if lat != 0.0 and lon != 0.0:
                                # Parse date
                                timestamp = datetime.now()
                                try:
                                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                                        try:
                                            timestamp = datetime.strptime(first_seen, fmt)
                                            break
                                        except ValueError:
                                            continue
                                except Exception:
                                    pass
                                    
                                networks.append({
                                    'mac': mac,
                                    'ssid': ssid,
                                    'auth': auth,
                                    'channel': channel,
                                    'rssi': rssi,
                                    'lat': lat,
                                    'lon': lon,
                                    'timestamp': timestamp,
                                    'source': 'wigle'
                                })
                        except Exception as e:
                            print(f"Error parsing WiGLE CSV row: {e}")
            except Exception as e:
                print(f"Error processing WiGLE CSV file {csv_file}: {e}")
                
        return networks
    
    def _process_kismet_files(self, data_dir: str) -> List[Dict]:
        """Process Kismet XML or netxml files."""
        networks = []
        
        # Look for Kismet files
        netxml_files = []
        for ext in ["*.netxml", "*.xml", "*.kismet"]:
            netxml_files.extend(glob.glob(os.path.join(data_dir, ext)))
            netxml_files.extend(glob.glob(os.path.join(data_dir, "**", ext), recursive=True))
            
        for netxml_file in netxml_files:
            try:
                with open(netxml_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Check if it's a Kismet XML file
                    if "<wireless-network" not in content:
                        continue
                        
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
                                
                                # Parse date
                                timestamp = datetime.now()
                                if first_seen != "Unknown":
                                    try:
                                        timestamp = datetime.fromtimestamp(float(first_seen))
                                    except:
                                        pass
                                
                                networks.append({
                                    'mac': mac,
                                    'ssid': ssid,
                                    'auth': auth,
                                    'channel': channel,
                                    'rssi': rssi,
                                    'lat': lat,
                                    'lon': lon,
                                    'timestamp': timestamp,
                                    'source': 'kismet'
                                })
                        except Exception as e:
                            print(f"Error processing Kismet network data: {e}")
            except Exception as e:
                print(f"Error processing Kismet file {netxml_file}: {e}")
                
        return networks
    
    def _process_generic_csv_files(self, data_dir: str) -> List[Dict]:
        """Process generic CSV files that might contain WiFi data."""
        networks = []
        
        # Look for CSV files
        csv_files = []
        for ext in ["*.csv"]:
            csv_files.extend(glob.glob(os.path.join(data_dir, ext)))
            csv_files.extend(glob.glob(os.path.join(data_dir, "**", ext), recursive=True))
        
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.reader(f)
                    headers = next(reader, None)
                    
                    # Skip if no headers
                    if not headers:
                        continue
                        
                    # Try to identify columns
                    ssid_col = None
                    mac_col = None
                    lat_col = None
                    lon_col = None
                    auth_col = None
                    channel_col = None
                    
                    for i, header in enumerate(headers):
                        header_lower = header.lower()
                        if 'ssid' in header_lower or 'network' in header_lower or 'name' in header_lower:
                            ssid_col = i
                        elif 'mac' in header_lower or 'bssid' in header_lower:
                            mac_col = i
                        elif 'lat' in header_lower:
                            lat_col = i
                        elif 'lon' in header_lower or 'lng' in header_lower:
                            lon_col = i
                        elif 'auth' in header_lower or 'security' in header_lower or 'encryption' in header_lower:
                            auth_col = i
                        elif 'channel' in header_lower or 'freq' in header_lower:
                            channel_col = i
                            
                    # Skip if we can't find the necessary columns
                    if lat_col is None or lon_col is None or ssid_col is None:
                        continue
                        
                    for row in reader:
                        try:
                            # Skip if row is too short
                            if len(row) <= max(lat_col, lon_col, ssid_col):
                                continue
                                
                            lat = float(row[lat_col]) if row[lat_col] else 0.0
                            lon = float(row[lon_col]) if row[lon_col] else 0.0
                            ssid = row[ssid_col] or "Unknown Network"
                            
                            if lat != 0.0 and lon != 0.0:
                                # Get optional fields
                                mac = row[mac_col] if mac_col is not None and len(row) > mac_col else "00:00:00:00:00:00"
                                auth = row[auth_col] if auth_col is not None and len(row) > auth_col else "Unknown"
                                channel = row[channel_col] if channel_col is not None and len(row) > channel_col else "0"
                                
                                networks.append({
                                    'mac': mac,
                                    'ssid': ssid,
                                    'auth': auth,
                                    'channel': channel,
                                    'rssi': -75.0,  # Default value
                                    'lat': lat,
                                    'lon': lon,
                                    'timestamp': datetime.now(),
                                    'source': 'csv'
                                })
                        except Exception as e:
                            print(f"Error parsing CSV row: {e}")
            except Exception as e:
                print(f"Error processing CSV file {csv_file}: {e}")
                
        return networks
    
    def _group_networks_by_location(self, networks: List[Dict], proximity_threshold: float = 0.001) -> List[Dict]:
        """Group networks that are close to each other."""
        if not networks:
            return []
            
        # Sort by SSID to prioritize grouping same networks together
        networks = sorted(networks, key=lambda x: x.get('ssid', ''))
        
        groups = []
        added = set()
        
        for i, network in enumerate(networks):
            if i in added:
                continue
                
            group = [network]
            added.add(i)
            
            # Find other networks of the same SSID that are nearby
            for j, other in enumerate(networks):
                if j not in added and network.get('ssid', '') == other.get('ssid', ''):
                    distance = math.sqrt(
                        (network.get('lat', 0) - other.get('lat', 0))**2 + 
                        (network.get('lon', 0) - other.get('lon', 0))**2
                    )
                    if distance < proximity_threshold:
                        group.append(other)
                        added.add(j)
            
            # Average the location if multiple points
            if len(group) > 1:
                avg_lat = sum(n.get('lat', 0) for n in group) / len(group)
                avg_lon = sum(n.get('lon', 0) for n in group) / len(group)
                avg_rssi = sum(n.get('rssi', -75) for n in group) / len(group)
                
                # Use the most recent observation for other details
                best_network = max(group, key=lambda x: x.get('timestamp', datetime.min))
                result = best_network.copy()
                result['lat'] = avg_lat
                result['lon'] = avg_lon
                result['rssi'] = avg_rssi
                result['count'] = len(group)
                
                groups.append(result)
            else:
                result = network.copy()
                result['count'] = 1
                groups.append(result)
                
        return groups
    
    def _generate_mock_networks(self, ssid: str, count: int = 8) -> List[LocationPoint]:
        """Generate mock WiFi network data for demo purposes."""
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
            
            # Date within the last year
            date = datetime.now() - datetime.timedelta(days=random.randint(0, 365))
            
            # Determine security icon
            if "WPA" in security:
                security_icon = "🔒" # Locked
            elif security == "OPN":
                security_icon = "⚠️" # Open network
            else:
                security_icon = "❓" # Unknown
            
            location = LocationPoint(
                latitude=lat,
                longitude=lon,
                timestamp=date,
                source="WiFi Network - Simulated",
                context=f"WiFi network {ssid} ({security_icon}) on channel {channel}"
            )
            locations.append(location)
            
        return locations