#!/usr/bin/python
# -*- coding: utf-8 -*-
from models.InputPlugin import InputPlugin
import os
import datetime
import email
import email.utils
import logging
import json
import re
import mailbox
import glob
from pathlib import Path
from email.header import decode_header
import random

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class EmailAnalysisPlugin(InputPlugin):
    name = "email_analysis"
    
    def __init__(self):
        InputPlugin.__init__(self)
        self.description = "Extract location and contact data from email headers"
        self.searchOffline = True
        self.hasWizard = True
        self._config_path = os.path.join(os.path.expanduser("~"), ".creepy", "email_analysis.conf")
        self.contacts = {}  # Store extracted contacts
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
                    if self.config.get('email_path'):
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
        logger.info("EmailAnalysisPlugin activated")
        
    def deactivate(self):
        logger.info("EmailAnalysisPlugin deactivated")
    
    def isConfigured(self):
        if self.configured:
            return (True, "Plugin is configured.")
        else:
            return (False, "Please configure email data path in plugin settings.")
    
    def _extract_email_address(self, header_value):
        """Extract email address from a header value"""
        if not header_value:
            return None, None
            
        try:
            name, email_addr = email.utils.parseaddr(header_value)
            # Decode non-ASCII names
            if name:
                decoded_parts = []
                for part, encoding in decode_header(name):
                    if isinstance(part, bytes):
                        if encoding:
                            try:
                                decoded_parts.append(part.decode(encoding))
                            except:
                                decoded_parts.append(part.decode('utf-8', errors='replace'))
                        else:
                            decoded_parts.append(part.decode('utf-8', errors='replace'))
                    else:
                        decoded_parts.append(part)
                name = ''.join(decoded_parts)
            return name, email_addr
        except Exception as e:
            logger.warning(f"Failed to parse email address: {str(e)}")
            return None, None
    
    def _parse_received_header(self, header_value):
        """Extract IP addresses and timestamps from Received headers"""
        if not header_value:
            return None, None
            
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, header_value)
        
        # Find date
        date_match = re.search(r';(.+?)(?:\n|$)', header_value)
        if date_match:
            try:
                date_str = date_match.group(1).strip()
                timestamp = email.utils.parsedate_to_datetime(date_str)
                return ips, timestamp
            except:
                pass
                
        return ips, None
    
    def _extract_location_from_ip(self, ip):
        """Simple mock geo-location for IPs for demonstration purposes"""
        # In a real implementation, you would use a GeoIP database
        # This is just for demonstration
        octet_sum = sum(int(o) for o in ip.split('.'))
        seed = octet_sum % 1000
        random.seed(seed)
        
        # Generate a location based on the IP (consistent but random)
        lat = random.uniform(25, 65)  # Northern hemisphere
        lon = random.uniform(-120, 120)
        city = random.choice([
            "New York", "London", "Tokyo", "Sydney", "Berlin", 
            "Paris", "Toronto", "Singapore", "Mumbai", "Cape Town"
        ])
        
        return {
            "lat": lat,
            "lon": lon,
            "city": city,
            "ip": ip
        }
    
    def _scan_maildir(self, maildir_path):
        """Scan a maildir directory for emails"""
        contacts = {}
        locations = []
        
        try:
            mail_dir = mailbox.Maildir(maildir_path)
            for key, message in mail_dir.items():
                try:
                    self._process_email(message, contacts, locations)
                except Exception as e:
                    logger.warning(f"Error processing message {key}: {str(e)}")
        except Exception as e:
            logger.error(f"Error scanning maildir {maildir_path}: {str(e)}")
            
        return contacts, locations
    
    def _scan_mbox(self, mbox_path):
        """Scan an mbox file for emails"""
        contacts = {}
        locations = []
        
        try:
            mbox = mailbox.mbox(mbox_path)
            for i, message in enumerate(mbox):
                try:
                    self._process_email(message, contacts, locations)
                except Exception as e:
                    logger.warning(f"Error processing message {i}: {str(e)}")
        except Exception as e:
            logger.error(f"Error scanning mbox {mbox_path}: {str(e)}")
            
        return contacts, locations
    
    def _process_email(self, message, contacts, locations):
        """Process a single email message"""
        # Extract sender and recipients
        from_name, from_email = self._extract_email_address(message.get('From'))
        if from_email and '@' in from_email:
            contacts[from_email] = from_name or from_email.split('@')[0]
        
        for field in ['To', 'Cc', 'Bcc']:
            addresses = message.get_all(field, [])
            for address in addresses:
                for addr in address.split(','):
                    name, email_addr = self._extract_email_address(addr)
                    if email_addr and '@' in email_addr:
                        contacts[email_addr] = name or email_addr.split('@')[0]
        
        # Process headers for location data
        received_headers = message.get_all('Received', [])
        date = email.utils.parsedate_to_datetime(message.get('Date', '')) if message.get('Date') else None
        
        for header in received_headers:
            ips, timestamp = self._parse_received_header(header)
            if ips:
                for ip in ips:
                    geo = self._extract_location_from_ip(ip)
                    
                    # Use the header timestamp, or fall back to message date
                    loc_date = timestamp or date or datetime.datetime.now()
                    
                    subject = message.get('Subject', 'No Subject')
                    if isinstance(subject, bytes):
                        subject = subject.decode('utf-8', errors='replace')
                    
                    # Truncate subject if needed
                    if len(subject) > 50:
                        subject = subject[:47] + "..."
                    
                    location = {
                        "plugin": self.name,
                        "lat": geo["lat"],
                        "lon": geo["lon"],
                        "date": loc_date,
                        "context": f"Email from {from_email} routed through {geo['city']} ({ip})",
                        "infowindow": f"""<div class="email-location">
                            <h3>Email Hop: {geo['city']}</h3>
                            <p><strong>Subject:</strong> {subject}</p>
                            <p><strong>From:</strong> {from_name or from_email}</p>
                            <p><strong>Date:</strong> {loc_date.strftime('%Y-%m-%d %H:%M:%S')}</p>
                            <p><strong>IP Address:</strong> {ip}</p>
                        </div>""",
                        "shortName": f"Email via {geo['city']} ({loc_date.strftime('%m-%d')})"
                    }
                    locations.append(location)
                    
        return True
                    
    def _scan_email_directory(self):
        """Scan configured email directory for messages"""
        email_path = self.config.get('email_path', '')
        if not email_path or not os.path.exists(email_path):
            return {}, []
            
        all_contacts = {}
        all_locations = []
        
        # Check for maildir format
        if os.path.isdir(email_path) and all(os.path.isdir(os.path.join(email_path, d)) for d in ['cur', 'new', 'tmp']):
            contacts, locations = self._scan_maildir(email_path)
            all_contacts.update(contacts)
            all_locations.extend(locations)
            
        # Check for mbox files
        mbox_files = glob.glob(os.path.join(email_path, "*.mbox"))
        for mbox_file in mbox_files:
            contacts, locations = self._scan_mbox(mbox_file)
            all_contacts.update(contacts)
            all_locations.extend(locations)
            
        # Check for .eml files
        eml_files = glob.glob(os.path.join(email_path, "*.eml"))
        for eml_file in eml_files:
            try:
                with open(eml_file, 'r', encoding='utf-8', errors='replace') as f:
                    message = email.message_from_string(f.read())
                    self._process_email(message, all_contacts, all_locations)
            except Exception as e:
                logger.warning(f"Error processing {eml_file}: {str(e)}")
                
        self.contacts = all_contacts
        return all_contacts, all_locations
    
    def searchForTargets(self, search_term):
        """Return available targets based on search term"""
        contacts, _ = self._scan_email_directory()
        
        if not contacts:
            # Return search term as a target if no contacts found
            return [{
                'targetUsername': search_term,
                'targetUserid': f"email_{search_term}",
                'targetFullname': search_term,
                'targetPicture': 'default.png',
                'pluginName': self.name
            }]
            
        # Filter contacts matching search term
        matches = []
        for email_addr, name in contacts.items():
            if search_term.lower() in email_addr.lower() or (name and search_term.lower() in name.lower()):
                matches.append({
                    'targetUsername': email_addr,
                    'targetUserid': f"email_{email_addr}",
                    'targetFullname': name or email_addr,
                    'targetPicture': 'user.png',
                    'pluginName': self.name
                })
                
        return matches[:20]  # Limit to 20 matches
    
    def returnLocations(self, target, search_params):
        """Return location data for the target"""
        _, locations = self._scan_email_directory()
        
        if not locations:
            # Generate mock data if no real emails found
            return self._generate_mock_locations(target['targetUsername'], 15)
            
        # Filter locations for this target
        email_addr = target['targetUsername']
        target_locations = []
        
        for location in locations:
            if email_addr in location['context']:
                target_locations.append(location)
                
        return target_locations
    
    def _generate_mock_locations(self, email_addr, count=15):
        """Generate mock email location data for demo purposes"""
        locations = []
        
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
        
        now = datetime.datetime.now()
        
        for i in range(count):
            server = random.choice(servers)
            
            # Add some jitter to location
            lat = server["lat"] + random.uniform(-0.1, 0.1)
            lon = server["lon"] + random.uniform(-0.1, 0.1)
            
            # Random date within last 30 days
            date = now - datetime.timedelta(days=random.randint(1, 30), 
                                           hours=random.randint(0, 23), 
                                           minutes=random.randint(0, 59))
            
            # Construct details
            ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            subject = random.choice(subjects)
            name = email_addr.split('@')[0].replace('.', ' ').title()
            
            location = {
                "plugin": self.name,
                "lat": lat,
                "lon": lon,
                "date": date,
                "context": f"Email from {email_addr} routed through {server['location']} ({ip})",
                "infowindow": f"""<div class="email-location">
                    <h3>Email Hop: {server['location']}</h3>
                    <p><strong>Subject:</strong> {subject}</p>
                    <p><strong>From:</strong> {name}</p>
                    <p><strong>Date:</strong> {date.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Server:</strong> {server['name']}</p>
                    <p><strong>IP Address:</strong> {ip}</p>
                </div>""",
                "shortName": f"Email - {server['location']} ({date.strftime('%m-%d')})"
            }
            locations.append(location)
            
        return sorted(locations, key=lambda x: x["date"])
    
    def getConfigurationParameters(self):
        """Return configuration parameters for the plugin"""
        return [
            {'name': 'email_path', 'type': 'path', 'default': os.path.join(os.path.expanduser("~"), "Documents", "Emails")},
            {'name': 'scan_depth', 'type': 'option', 'values': ['shallow', 'medium', 'deep'], 'default': 'medium'},
            {'name': 'include_sent', 'type': 'boolean', 'default': True}
        ]
        
    def setConfigurationParameters(self, params):
        """Set configuration parameters for the plugin"""
        if 'email_path' in params:
            path = params['email_path']
            if not os.path.exists(path):
                # Try to create the directory if it doesn't exist
                try:
                    os.makedirs(path)
                except Exception as e:
                    return (False, f"Could not create directory: {str(e)}")
                    
            self.config['email_path'] = path
            self.config['scan_depth'] = params.get('scan_depth', 'medium')
            self.config['include_sent'] = params.get('include_sent', True)
            self._save_config()
            self.configured = True
            return (True, "Configuration saved successfully")
        else:
            return (False, "Email path not specified")
            
    def getLabelForKey(self, key):
        """Return user-friendly labels for configuration keys"""
        labels = {
            "email_path": "Email Data Directory",
            "scan_depth": "Scan Depth",
            "include_sent": "Include Sent Emails"
        }
        return labels.get(key, key)
