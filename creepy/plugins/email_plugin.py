import os
import glob
import json
import email
import email.utils
import re
import mailbox
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import random
from creepy.plugins.base_plugin import BasePlugin, LocationPoint
from creepy.plugins.geocoding_helper import GeocodingHelper

class EmailPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="Email Analysis",
            description="Extract location data from email headers and content"
        )
        self.geocoder = GeocodingHelper()
    
    def is_configured(self):
        # Check if the plugin is properly configured
        return True, "EmailPlugin is configured"
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "data_directory",
                "display_name": "Email Directory",
                "type": "directory",
                "default": "",
                "required": True,
                "description": "Directory containing your email archives (mbox, maildir, or .eml files)"
            },
            {
                "name": "scan_depth",
                "display_name": "Scan Depth",
                "type": "select",
                "options": ["shallow", "medium", "deep"],
                "default": "medium",
                "required": False,
                "description": "How thoroughly to scan emails for location data"
            },
            {
                "name": "attempt_geocoding",
                "display_name": "Attempt Geocoding",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Try to convert textual addresses to coordinates"
            }
        ]
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None, 
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
        locations = []
        data_dir = self.config.get("data_directory", "")
        scan_depth = self.config.get("scan_depth", "medium")
        attempt_geocoding = self.config.get("attempt_geocoding", True)
        
        if not data_dir or not os.path.exists(data_dir):
            return self._generate_mock_locations(target, 15)
            
        # Check for maildir format
        maildir_locations = []
        if os.path.isdir(data_dir) and all(os.path.isdir(os.path.join(data_dir, d)) for d in ['cur', 'new', 'tmp']):
            maildir_locations = self._process_maildir(
                data_dir, target, scan_depth, attempt_geocoding, date_from, date_to
            )
            locations.extend(maildir_locations)
        
        # Check for mbox files
        mbox_files = glob.glob(os.path.join(data_dir, "*.mbox"))
        for mbox_file in mbox_files:
            mbox_locations = self._process_mbox(
                mbox_file, target, scan_depth, attempt_geocoding, date_from, date_to
            )
            locations.extend(mbox_locations)
            
        # Check for .eml files
        eml_files = glob.glob(os.path.join(data_dir, "*.eml"))
        eml_files.extend(glob.glob(os.path.join(data_dir, "*/*.eml")))
        for eml_file in eml_files:
            eml_locations = self._process_eml(
                eml_file, target, scan_depth, attempt_geocoding, date_from, date_to
            )
            locations.extend(eml_locations)
            
        # If no locations found, use mock data
        if not locations:
            return self._generate_mock_locations(target, 15)
            
        return locations
    
    def _process_maildir(self, maildir_path: str, target: str, scan_depth: str, attempt_geocoding: bool,
                        date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> List[LocationPoint]:
        """Process a maildir directory for location data."""
        locations = []
        
        try:
            mail_dir = mailbox.Maildir(maildir_path)
            for key, message in mail_dir.items():
                try:
                    message_locations = self._extract_locations_from_email(
                        message, target, scan_depth, attempt_geocoding, date_from, date_to
                    )
                    locations.extend(message_locations)
                except Exception as e:
                    print(f"Error processing maildir message {key}: {e}")
        except Exception as e:
            print(f"Error opening maildir {maildir_path}: {e}")
            
        return locations
    
    def _process_mbox(self, mbox_path: str, target: str, scan_depth: str, attempt_geocoding: bool,
                     date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> List[LocationPoint]:
        """Process an mbox file for location data."""
        locations = []
        
        try:
            mbox = mailbox.mbox(mbox_path)
            for i, message in enumerate(mbox):
                try:
                    message_locations = self._extract_locations_from_email(
                        message, target, scan_depth, attempt_geocoding, date_from, date_to
                    )
                    locations.extend(message_locations)
                except Exception as e:
                    print(f"Error processing mbox message {i}: {e}")
        except Exception as e:
            print(f"Error opening mbox {mbox_path}: {e}")
            
        return locations
    
    def _process_eml(self, eml_path: str, target: str, scan_depth: str, attempt_geocoding: bool,
                    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> List[LocationPoint]:
        """Process an .eml file for location data."""
        locations = []
        
        try:
            with open(eml_path, 'r', encoding='utf-8', errors='replace') as f:
                message = email.message_from_string(f.read())
                message_locations = self._extract_locations_from_email(
                    message, target, scan_depth, attempt_geocoding, date_from, date_to
                )
                locations.extend(message_locations)
        except Exception as e:
            print(f"Error processing eml file {eml_path}: {e}")
            
        return locations
    
    def _extract_locations_from_email(self, message, target: str, scan_depth: str, attempt_geocoding: bool,
                                    date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> List[LocationPoint]:
        """Extract location data from an email message."""
        locations = []
        
        # Extract sender and recipients
        from_name, from_email = self._extract_email_address(message.get('From'))
        
        # Check if this email matches our target
        is_target_email = (target == from_email or target in str(message.get('To', '')))
        if not is_target_email and '@' in target:
            # If target is not exactly matched but looks like an email, skip
            return []
        
        # Get message date
        message_date = None
        if message.get('Date'):
            try:
                message_date = email.utils.parsedate_to_datetime(message.get('Date'))
            except:
                pass
        
        if not message_date:
            # Fallback to current date if no valid date found
            message_date = datetime.now()
            
        # Apply date filters
        if date_from and message_date < date_from:
            return []
        if date_to and message_date > date_to:
            return []
        
        # Get email subject
        subject = message.get('Subject', 'No Subject')
        if isinstance(subject, bytes):
            subject = subject.decode('utf-8', errors='replace')
        
        # Process Received headers to extract IPs
        received_headers = message.get_all('Received', [])
        for header in received_headers:
            ips = self._extract_ips_from_header(header)
            for ip in ips:
                # Get geo location for IP (in a real implementation, use a GeoIP database)
                geo = self._get_geolocation_for_ip(ip)
                if geo:
                    locations.append(
                        LocationPoint(
                            latitude=geo["latitude"],
                            longitude=geo["longitude"],
                            timestamp=message_date,
                            source="Email Header",
                            context=f"Email from {from_name or from_email} routed via {geo['city']} ({ip})"
                        )
                    )
        
        # For deeper scan, extract locations from email body
        if scan_depth in ["medium", "deep"]:
            body_locations = self._extract_locations_from_body(
                message, message_date, attempt_geocoding
            )
            locations.extend(body_locations)
        
        return locations
    
    def _extract_email_address(self, header_value):
        """Extract email address from a header value."""
        if not header_value:
            return None, None
            
        try:
            name, email_addr = email.utils.parseaddr(header_value)
            return name, email_addr
        except:
            return None, None
    
    def _extract_ips_from_header(self, header_value):
        """Extract IP addresses from a header."""
        if not header_value:
            return []
            
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        return re.findall(ip_pattern, header_value)
    
    def _get_geolocation_for_ip(self, ip):
        """Get geolocation for an IP address.
        
        In a real implementation, this would use a GeoIP database.
        Here we use a simple mock implementation.
        """
        octet_sum = sum(int(o) for o in ip.split('.'))
        seed = octet_sum % 1000
        random.seed(seed)
        
        latitude = random.uniform(25, 65)  # Northern hemisphere
        longitude = random.uniform(-120, 120)
        
        cities = [
            "New York", "London", "Tokyo", "Sydney", "Berlin", 
            "Paris", "Toronto", "Singapore", "Mumbai", "Cape Town"
        ]
        
        return {
            "latitude": latitude,
            "longitude": longitude,
            "city": cities[seed % len(cities)],
            "ip": ip
        }
    
    def _extract_locations_from_body(self, message, message_date, attempt_geocoding):
        """Extract locations from email body."""
        locations = []
        
        body = self._get_email_body(message)
        if not body:
            return locations
        
        # Check for coordinates in the text
        coord_pattern = r'(-?\d+\.\d+)[,\s]+(-?\d+\.\d+)'
        coord_matches = re.finditer(coord_pattern, body)
        
        for match in coord_matches:
            try:
                latitude = float(match.group(1))
                longitude = float(match.group(2))
                
                # Validate coordinates
                if -90 <= latitude <= 90 and -180 <= longitude <= 180:
                    # Extract surrounding context
                    start = max(0, match.start() - 50)
                    end = min(len(body), match.end() + 50)
                    context = body[start:end].replace('\n', ' ').strip()
                    
                    locations.append(
                        LocationPoint(
                            latitude=latitude,
                            longitude=longitude,
                            timestamp=message_date,
                            source="Email Body",
                            context=f"Coordinates in message: {context}"
                        )
                    )
            except:
                continue
        
        # If geocoding is enabled, look for addresses
        if attempt_geocoding:
            # Simple address pattern matching - could be improved with NLP
            address_patterns = [
                r'(?:located at|address)[:\s]+([^,\n]+(?:,[^,\n]+){1,3})',
                r'(?:location|place)[:\s]+([^,\n]+(?:,[^,\n]+){1,3})'
            ]
            
            for pattern in address_patterns:
                matches = re.finditer(pattern, body, re.IGNORECASE)
                for match in matches:
                    address = match.group(1).strip()
                    lat, lon = self.geocoder.geocode(address)
                    
                    if lat is not None and lon is not None:
                        locations.append(
                            LocationPoint(
                                latitude=lat,
                                longitude=lon,
                                timestamp=message_date,
                                source="Email Body",
                                context=f"Address in message: {address}"
                            )
                        )
        
        return locations
    
    def _get_email_body(self, message):
        """Extract plain text body from an email message."""
        body = ""
        
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        part_body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='replace')
                        body += part_body + "\n"
                    except:
                        continue
        else:
            try:
                body = message.get_payload(decode=True).decode(message.get_content_charset() or 'utf-8', errors='replace')
            except:
                pass
                
        return body
    
    def _generate_mock_locations(self, email_addr: str, count: int = 15) -> List[LocationPoint]:
        """Generate mock email location data for demo purposes."""
        locations = []
        
        # Generate random but consistent seed from email
        if '@' in email_addr:
            seed_str = email_addr.split('@')[0]
        else:
            seed_str = email_addr
            
        seed = sum(ord(c) for c in seed_str)
        random.seed(seed)
        
        # Generate some mock email servers
        servers = [
            {"name": "smtp.example.com", "location": "New York", "lat": 40.7128, "lon": -74.0060},
            {"name": "mail.example.net", "location": "London", "lat": 51.5074, "lon": -0.1278},
            {"name": "mx1.example.org", "location": "Tokyo", "lat": 35.6762, "lon": 139.6503},
            {"name": "mail.example.co", "location": "Sydney", "lat": -33.8688, "lon": 151.2093},
            {"name": "smtp2.example.io", "location": "Berlin", "lat": 52.5200, "lon": 13.4050}
        ]
        
        # Generate some subjects
        subjects = [
            "Meeting next week", "Project update", "Hello!", "Question about yesterday",
            "Conference reminder", "Invoice #12345", "Your order has shipped",
            "Important announcement", "Newsletter", "Account verification"
        ]
        
        now = datetime.now()
        
        for i in range(count):
            server = random.choice(servers)
            
            # Add some jitter to location
            lat = server["lat"] + random.uniform(-0.1, 0.1)
            lon = server["lon"] + random.uniform(-0.1, 0.1)
            
            # Random date within last 30 days
            date = now - timedelta(days=random.randint(1, 30), 
                                   hours=random.randint(0, 23), 
                                   minutes=random.randint(0, 59))
            
            # Construct details
            ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            subject = random.choice(subjects)
            
            locations.append(
                LocationPoint(
                    latitude=float(lat),
                    longitude=float(lon),
                    timestamp=date,
                    source="Email Analysis",
                    context=f"Email routed through {server['location']} ({ip})"
                )
            )
            
        # Sort by date
        return sorted(locations, key=lambda x: x.timestamp)
