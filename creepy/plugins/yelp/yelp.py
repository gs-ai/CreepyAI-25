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
from yelpapi import YelpAPI

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(os.getcwd(), 'creepy_main.log'))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

class Yelp(InputPlugin):
    name = "yelp"
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
            return YelpAPI(self.options_string['hidden_api_key'])
        except Exception as err:
            logger.error("Error authenticating with Yelp API.")
            logger.debug(traceback.format_exc())
            return None

    def isConfigured(self):
        if not self.api:
            self.api = self.getAuthenticatedAPI()
        try:
            self.api.search_query(term="test", location="San Francisco")
            return (True, "")
        except Exception as err:
            logger.error("Yelp API is not configured properly.")
            logger.debug(traceback.format_exc())
            return (False, str(err))

    def searchForTargets(self, search_term):
        logger.debug(f"Attempting to search for targets. Search term was: {search_term}")
        possibleTargets = []
        try:
            if not self.api:
                self.api = self.getAuthenticatedAPI()
            results = self.api.search_query(term=search_term, location="San Francisco")
            for i in results['businesses']:
                target = {
                    'pluginName': 'Yelp Plugin',
                    'targetUserid': i['id'],
                    'targetUsername': i['name'],
                    'targetPicture': f'profile_pic_{i["id"]}',
                    'targetFullname': i['name']
                }
                filename = f'profile_pic_{i["id"]}'
                temp_file = os.path.join(os.getcwd(), "temp", filename)
                if not os.path.exists(temp_file):
                    urllib.request.urlretrieve(i['image_url'], temp_file)
                possibleTargets.append(target)
            logger.debug(f"{len(possibleTargets)} possible targets were found matching the search query.")
        except Exception as err:
            logger.error("Error searching for targets with Yelp plugin.")
            logger.debug(traceback.format_exc())
        return possibleTargets

    def getAllPhotos(self, uid, count, max_id, photos):
        logger.debug(f"Attempting to retrieve all photos for business {uid}")
        if not self.api:
            self.api = self.getAuthenticatedAPI()
        try:
            # Yelp API does not provide a method to get all photos directly, this is a placeholder
            new_photos = []  # Placeholder for actual photo retrieval logic
            if new_photos:
                logger.debug(f"Found {len(new_photos)} photos")
                photos.extend(new_photos)
                logger.debug(f"We now have {len(photos)} photos")
            logger.debug("Finished, got all photos")
            return photos
        except Exception as err:
            logger.error(f"Error retrieving photos for business {uid}")
            logger.debug(traceback.format_exc())
            return photos

    def returnLocations(self, target, search_params):
        logger.debug(f"Attempting to retrieve all photos for business {target['targetUserid']}")
        locations_list = []
        try:
            if not self.api:
                self.api = self.getAuthenticatedAPI()
            photos_list = self.getAllPhotos(target['targetUserid'], 33, None, [])
            for i in photos_list:
                if hasattr(i, 'location'):
                    loc = {
                        'plugin': "yelp",
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
            logger.error("Error getting locations from Yelp plugin")
            logger.debug(traceback.format_exc())
        return locations_list

    def runConfigWizard(self):
        try:
            self.wizard = QWizard()
            page1 = QWizardPage()
            layout1 = QVBoxLayout()
            txtArea = QTextEdit()
            txtArea.setReadOnly(True)
            txtArea.setText("Please enter your Yelp API key in the next step.")
            layout1.addWidget(txtArea)
            page1.setLayout(layout1)
            self.wizard.addPage(page1)
            self.wizard.exec_()
        except Exception as err:
            logger.error("Error running configuration wizard for Yelp plugin.")
            logger.debug(traceback.format_exc())
