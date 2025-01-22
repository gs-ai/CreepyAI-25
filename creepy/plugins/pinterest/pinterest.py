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

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(os.getcwd(), 'creepy_main.log'))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

class Pinterest(InputPlugin):
    name = "pinterest"
    hasWizard = True

    def __init__(self):
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
        self.config, self.options_string = self.readConfiguration("string_options")
        self.api = self.getAuthenticatedAPI()

    def getAuthenticatedAPI(self):
        try:
            # Replace with actual Pinterest API authentication
            return None
        except Exception as err:
            logger.error("Error authenticating with Pinterest API.")
            logger.debug(traceback.format_exc())
            return None

    def isConfigured(self):
        if not self.api:
            self.api = self.getAuthenticatedAPI()
        try:
            # Replace with actual Pinterest API check
            return (True, "")
        except Exception as err:
            logger.error("Pinterest API is not configured properly.")
            logger.debug(traceback.format_exc())
            return (False, str(err))

    def searchForTargets(self, search_term):
        logger.debug(f"Attempting to search for targets. Search term was: {search_term}")
        possibleTargets = []
        try:
            if not self.api:
                self.api = self.getAuthenticatedAPI()
            # Replace with actual Pinterest API search
            results = []
            for i in results:
                target = {
                    'pluginName': 'Pinterest Plugin',
                    'targetUserid': i.id,
                    'targetUsername': i.username,
                    'targetPicture': f'profile_pic_{i.id}',
                    'targetFullname': i.full_name
                }
                filename = f'profile_pic_{i.id}'
                temp_file = os.path.join(os.getcwd(), "temp", filename)
                if not os.path.exists(temp_file):
                    urllib.request.urlretrieve(i.profile_picture, temp_file)
                possibleTargets.append(target)
            logger.debug(f"{len(possibleTargets)} possible targets were found matching the search query.")
        except Exception as err:
            logger.error("Error searching for targets with Pinterest plugin.")
            logger.debug(traceback.format_exc())
        return possibleTargets

    def getAllPhotos(self, uid, count, max_id, photos):
        logger.debug(f"Attempting to retrieve all photos for user {uid}")
        if not self.api:
            self.api = self.getAuthenticatedAPI()
        try:
            # Replace with actual Pinterest API call
            new_photos = []
            next1 = None
            if new_photos:
                logger.debug(f"Found {len(new_photos)} photos")
                photos.extend(new_photos)
                logger.debug(f"We now have {len(photos)} photos")
            if not next1:
                logger.debug("Finished, got all photos")
                return photos
            else:
                a = parse_qs(urlparse(next1).query)
                logger.debug(f"Found more, max_id will now be {a['max_id'][0]}")
                return self.getAllPhotos(uid, count, a['max_id'][0], photos)
        except Exception as err:
            logger.error(f"Error retrieving photos for user {uid}")
            logger.debug(traceback.format_exc())
            return photos

    def returnLocations(self, target, search_params):
        logger.debug(f"Attempting to retrieve all photos for user {target['targetUserid']}")
        locations_list = []
        try:
            if not self.api:
                self.api = self.getAuthenticatedAPI()
            photos_list = self.getAllPhotos(target['targetUserid'], 33, None, [])
            for i in photos_list:
                if hasattr(i, 'location'):
                    loc = {
                        'plugin': "pinterest",
                        'context': i.caption.text if i.caption else 'No Caption',
                        'infowindow': self.constructContextInfoWindow(i),
                        'date': i.created_time,
                        'lat': i.location.point.latitude,
                        'lon': i.location.point.longitude,
                        'shortName': i.location.name
                    }
                    locations_list.append(loc)
            logger.debug(f"{len(locations_list)} locations have been retrieved")
        except Exception as err:
            logger.error("Error getting locations from Pinterest plugin")
            logger.debug(traceback.format_exc())
        return locations_list

    def runConfigWizard(self):
        try:
            # Replace with actual Pinterest API configuration
            url = "https://api.pinterest.com/oauth/"
            self.wizard = QWizard()
            page1 = QWizardPage()
            layout1 = QVBoxLayout()
            txtArea = QTextEdit()
            txtArea.setReadOnly(True)
            txtArea.setText(f"Please copy the following link to your browser window. \n\n{url}\n\nOnce you authenticate with Pinterest you will be redirected to a link that looks like \n")
            # ...existing code...
        except Exception as err:
            logger.error("Error running configuration wizard for Pinterest plugin.")
            logger.debug(traceback.format_exc())
