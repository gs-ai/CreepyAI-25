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

class Facebook(InputPlugin):
    name = "facebook"
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
            # Replace with actual Facebook API authentication
            return None
        except Exception as err:
            logger.error("Error authenticating with Facebook API.")
            logger.debug(traceback.format_exc())
            return None

    def isConfigured(self):
        if not self.api:
            self.api = self.getAuthenticatedAPI()
        try:
            # Replace with actual Facebook API check
            return (True, "")
        except Exception as err:
            logger.error("Facebook API is not configured properly.")
            logger.debug(traceback.format_exc())
            return (False, str(err))

    def searchForTargets(self, search_term):
        logger.debug(f"Attempting to search for targets. Search term was: {search_term}")
        possibleTargets = []
        try:
            if not self.api:
                self.api = self.getAuthenticatedAPI()
            # Replace with actual Facebook API search
            results = []
            for i in results:
                target = {
                    'pluginName': 'Facebook Plugin',
                    'targetUserid': i['id'],
                    'targetUsername': i['name'],
                    'targetPicture': f'profile_pic_{i["id"]}',
                    'targetFullname': i['name']
                }
                filename = f'profile_pic_{i["id"]}'
                temp_file = os.path.join(os.getcwd(), "temp", filename)
                if not os.path.exists(temp_file):
                    urllib.request.urlretrieve(i['profile_picture'], temp_file)
                possibleTargets.append(target)
            logger.debug(f"{len(possibleTargets)} possible targets were found matching the search query.")
        except Exception as err:
            logger.error("Error searching for targets with Facebook plugin.")
            logger.debug(traceback.format_exc())
        return possibleTargets

    def getAllPhotos(self, uid, count, max_id, photos):
        logger.debug(f"Attempting to retrieve all photos for user {uid}")
        if not self.api:
            self.api = self.getAuthenticatedAPI()
        try:
            # Replace with actual Facebook API call to get photos
            new_photos = []
            if new_photos:
                logger.debug(f"Found {len(new_photos)} photos")
                photos.extend(new_photos)
                logger.debug(f"We now have {len(photos)} photos")
            # Replace with actual logic to check for more photos
            more_photos = False
            if not more_photos:
                logger.debug("Finished, got all photos")
                return photos
            else:
                # Replace with actual logic to get next max_id
                next_max_id = None
                logger.debug(f"Found more, max_id will now be {next_max_id}")
                return self.getAllPhotos(uid, count, next_max_id, photos)
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
                if 'location' in i:
                    loc = {
                        'plugin': "facebook",
                        'context': i['caption'] if 'caption' in i else 'No Caption',
                        'infowindow': self.constructContextInfoWindow(i),
                        'date': i['created_time'],
                        'lat': i['location']['latitude'],
                        'lon': i['location']['longitude'],
                        'shortName': i['location']['name']
                    }
                    locations_list.append(loc)
            logger.debug(f"{len(locations_list)} locations have been retrieved")
        except Exception as err:
            logger.error("Error getting locations from Facebook plugin")
            logger.debug(traceback.format_exc())
        return locations_list

    def runConfigWizard(self):
        try:
            # Replace with actual Facebook API configuration wizard
            self.wizard = QWizard()
            page1 = QWizardPage()
            layout1 = QVBoxLayout()
            txtArea = QTextEdit()
            txtArea.setReadOnly(True)
            txtArea.setText("Please configure the Facebook plugin.")
            layout1.addWidget(txtArea)
            page1.setLayout(layout1)
            self.wizard.addPage(page1)
            self.wizard.exec_()
        except Exception as err:
            logger.error("Error running configuration wizard for Facebook plugin.")
            logger.debug(traceback.format_exc())
