#!/usr/bin/python
# -*- coding: utf-8 -*-
from creepy.models.InputPlugin import InputPlugin
import os
from PyQt5.QtWidgets import QLabel, QLineEdit, QWizard, QWizardPage, QVBoxLayout, QTextEdit, QMessageBox
import logging
import urllib.request
from urllib.parse import urlparse, parse_qs
from configobj import ConfigObj
import traceback

# Set up logging without file handler (we'll use the main app's logger)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Make foursquare import conditional
try:
    from foursquare import Foursquare
    FOURSQUARE_AVAILABLE = True
except ImportError:
    logger.warning("Foursquare module not available. Please install using 'pip install foursquare'")
    FOURSQUARE_AVAILABLE = False

class FoursquarePlugin(InputPlugin):
    name = "foursquare"
    hasWizard = True

    def __init__(self):
        InputPlugin.__init__(self)
        self.configured = False
        
        labels_filename = self.name + ".labels"
        labels_file = os.path.join(os.getcwd(), 'plugins', self.name, labels_filename)
        labels_config = ConfigObj(infile=labels_file)
        labels_config.create_empty = False
        try:
            logger.debug(f"Trying to load the labels file for the {self.name} plugin.")
            self.labels = labels_config['labels']
        except Exception as err:
            self.labels = None
            logger.error(f"Could not load the labels file for the {self.name} plugin.")
            logger.debug(traceback.format_exc())
            
        # Only attempt to load config and authenticate if the module is available
        if FOURSQUARE_AVAILABLE:
            try:
                self.config, self.options_string = self.readConfiguration("string_options")
                self.api = self.getAuthenticatedAPI()
            except Exception as err:
                logger.error("Error initializing Foursquare plugin")
                logger.debug(traceback.format_exc())
                self.api = None
        else:
            self.api = None

    def getAuthenticatedAPI(self):
        if not FOURSQUARE_AVAILABLE:
            return None
        try:
            return Foursquare(access_token=self.options_string['hidden_access_token'])
        except Exception as err:
            logger.error("Error authenticating with Foursquare API.")
            logger.debug(traceback.format_exc())
            return None

    def isConfigured(self):
        if not FOURSQUARE_AVAILABLE:
            return (False, "Foursquare module not installed. Please install using 'pip install foursquare'")
        if not self.api:
            self.api = self.getAuthenticatedAPI()
        try:
            self.api.users()
            return (True, "")
        except Exception as err:
            logger.error("Foursquare API is not configured properly.")
            logger.debug(traceback.format_exc())
            return (False, str(err))

    def searchForTargets(self, search_term):
        if not FOURSQUARE_AVAILABLE:
            logger.error("Foursquare module not available. Cannot search for targets.")
            return []
        logger.debug(f"Attempting to search for targets. Search term was: {search_term}")
        possibleTargets = []
        try:
            if not self.api:
                self.api = self.getAuthenticatedAPI()
            results = self.api.users.search(params={'query': search_term})
            for i in results['results']:
                target = {
                    'pluginName': 'Foursquare Plugin',
                    'targetUserid': i['id'],
                    'targetUsername': i['firstName'] + ' ' + i['lastName'],
                    'targetPicture': f'profile_pic_{i["id"]}',
                    'targetFullname': i['firstName'] + ' ' + i['lastName']
                }
                filename = f'profile_pic_{i["id"]}'
                temp_file = os.path.join(os.getcwd(), "temp", filename)
                if not os.path.exists(temp_file):
                    urllib.request.urlretrieve(i['photo']['prefix'] + 'original' + i['photo']['suffix'], temp_file)
                possibleTargets.append(target)
            logger.debug(f"{len(possibleTargets)} possible targets were found matching the search query.")
        except Exception as err:
            logger.error("Error searching for targets with Foursquare plugin.")
            logger.debug(traceback.format_exc())
        return possibleTargets

    def getAllCheckins(self, uid, count, max_id, checkins):
        if not FOURSQUARE_AVAILABLE:
            logger.error("Foursquare module not available. Cannot retrieve check-ins.")
            return []
        logger.debug(f"Attempting to retrieve all check-ins for user {uid}")
        if not self.api:
            self.api = self.getAuthenticatedAPI()
        try:
            new_checkins = self.api.users.checkins(params={'limit': count, 'offset': max_id})
            if new_checkins:
                logger.debug(f"Found {len(new_checkins['items'])} check-ins")
                checkins.extend(new_checkins['items'])
                logger.debug(f"We now have {len(checkins)} check-ins")
            if len(new_checkins['items']) < count:
                logger.debug("Finished, got all check-ins")
                return checkins
            else:
                max_id += count
                logger.debug(f"Found more, max_id will now be {max_id}")
                return self.getAllCheckins(uid, count, max_id, checkins)
        except Exception as err:
            logger.error(f"Error retrieving check-ins for user {uid}")
            logger.debug(traceback.format_exc())
            return checkins

    def returnLocations(self, target, search_params):
        if not FOURSQUARE_AVAILABLE:
            logger.error("Foursquare module not available. Cannot retrieve locations.")
            return []
        logger.debug(f"Attempting to retrieve all check-ins for user {target['targetUserid']}")
        locations_list = []
        try:
            if not self.api:
                self.api = self.getAuthenticatedAPI()
            checkins_list = self.getAllCheckins(target['targetUserid'], 33, 0, [])
            for i in checkins_list:
                if 'venue' in i:
                    loc = {
                        'plugin': "foursquare",
                        'context': i['shout'] if 'shout' in i else 'No Shout',
                        'infowindow': self.constructContextInfoWindow(i),
                        'date': i['createdAt'],
                        'lat': i['venue']['location']['lat'],
                        'lon': i['venue']['location']['lng'],
                        'shortName': i['venue']['name']
                    }
                    locations_list.append(loc)
            logger.debug(f"{len(locations_list)} locations have been retrieved")
        except Exception as err:
            logger.error("Error getting locations from Foursquare plugin")
            logger.debug(traceback.format_exc())
        return locations_list

    def runConfigWizard(self):
        if not FOURSQUARE_AVAILABLE:
            logger.error("Foursquare module not available. Cannot run configuration wizard.")
            return
        try:
            api = Foursquare(client_id=self.options_string['hidden_client_id'], client_secret=self.options_string['hidden_client_secret'], redirect_uri=self.options_string['redirect_uri'])
            url = api.oauth.auth_url()
            self.wizard = QWizard()
            page1 = QWizardPage()
            layout1 = QVBoxLayout()
            txtArea = QTextEdit()
            txtArea.setReadOnly(True)
            txtArea.setText(f"Please copy the following link to your browser window. \n\n{url}\n\nOnce you authenticate with Foursquare you will be redirected to a link that looks like \ncreepyai://callback. Copy the FULL URL and paste it below.")
        except Exception as err:
            logger.error("Error running configuration wizard for Foursquare plugin.")
            logger.debug(traceback.format_exc())
