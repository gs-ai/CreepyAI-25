#!/usr/bin/python
# -*- coding: utf-8 -*-
from creepy.models.InputPlugin import InputPlugin
import os
import logging
import urllib.request
from urllib.parse import urlparse, parse_qs
from configobj import ConfigObj
import traceback

# Set up logging without file handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Make flickrapi import conditional
try:
    import flickrapi
    FLICKR_API_AVAILABLE = True
except ImportError:
    logger.warning("Flickrapi module not available. Please install using 'pip install flickrapi'")
    FLICKR_API_AVAILABLE = False

class FlickrPlugin(InputPlugin):
    name = "flickr"
    hasWizard = True

    def __init__(self):
        InputPlugin.__init__(self)
        self.configured = False
        
        # Only attempt to load config and authenticate if the module is available
        if FLICKR_API_AVAILABLE:
            try:
                self.config, self.options_string = self.readConfiguration("string_options")
                self.api = self.getAuthenticatedAPI()
            except Exception as err:
                logger.error("Error initializing Flickr plugin")
                logger.debug(traceback.format_exc())
                self.api = None
        else:
            self.api = None

    def searchForTargets(self, search_term):
        possibleTargets = []
        try:
            if re.match(r"[\w\-\.+]+@(\w[\w\-]+\.)+[\w\-]+", search_term):
                results = self.api.people_findByEmail(find_email=search_term)
            else:
                results = self.api.people_findByUsername(username=search_term)

            for userid in results.find('user').items():
                possibleTargets.append(self.getUserInfo(userid[1]))

        except FlickrError as e:
            logger.error(e)
            if 'User not found' in str(e):
                logger.info(f"No results for search query {search_term} from Flickr Plugin")
        logger.debug(f"{len(possibleTargets)} possible targets were found matching the search query")
        return [dict(t) for t in set([tuple(d.items()) for d in possibleTargets])] if possibleTargets else []

    def getUserInfo(self, userId):
        try:
            results = self.api.people_getInfo(user_id=userId)
            if results.attrib['stat'] == 'ok':
                target = {'pluginName': 'Flickr Plugin'}
                res = results.find('person')
                target['targetUserid'] = userId
                target['targetUsername'] = res.find('username').text
                target['targetPicture'] = "d"
                target['targetFullname'] = res.find('realname').text if res.find('realname') else 'Unavailable'
                return target
            else:
                return None
        except FlickrError as err:
            logger.error(f"Error getting target info from Flickr for target {userId}")
            logger.error(err)
            return None

    def isConfigured(self):
        if not FLICKR_API_AVAILABLE:
            return (False, "Flickrapi module not installed. Please install using 'pip install flickrapi'")
            
        try:
            if not self.options_string:
                self.options_string = self.readConfiguration("string_options")[1]
            api = flickrapi.FlickrAPI(self.options_string["hidden_api_key"])
            api.people_findByUsername(username="testAPIKey")
            return (True, "")
        except FlickrError as e:
            logger.error("Error establishing connection to Flickr API.")
            logger.error(e)
            return (False, "Error establishing connection to Flickr API.")

    def getPhotosByPage(self, userid, page_nr):
        try:
            results = self.api.people_getPublicPhotos(user_id=userid, extras="geo, date_taken", per_page=500, page=page_nr)
            if results.attrib['stat'] == 'ok':
                return results.find('photos').findall('photo')
        except FlickrError as err:
            logger.error("Error getting photos per page from Flickr")
            logger.error(err)

    def getLocationsFromPhotos(self, photos):
        locations = []
        if photos:
            for photo in photos:
                try:
                    if photo.attrib['latitude'] != '0':
                        loc = {
                            'plugin': "flickr",
                            'context': f"Photo from flickr\nTitle: {photo.attrib['title']}",
                            'date': datetime.datetime.strptime(photo.attrib['datetaken'], "%Y-%m-%d %H:%M:%S"),
                            'lat': photo.attrib['latitude'],
                            'lon': photo.attrib['longitude'],
                            'shortName': "Unavailable",
                            'infowindow': self.constructContextInfoWindow(
                                f"http://www.flickr.com/photos/{photo.attrib['owner']}/{photo.attrib['id']}",
                                datetime.datetime.strptime(photo.attrib['datetaken'], "%Y-%m-%d %H:%M:%S")
                            )
                        }
                        locations.append(loc)
                except Exception as err:
                    logger.error(err)
        return locations

    def returnLocations(self, target, search_params):
        photosList = []
        locationsList = []
        try:
            results = self.api.people_getPublicPhotos(user_id=target['targetUserid'], extras="geo, date_taken", per_page=500)
            if results.attrib['stat'] == 'ok':
                res = results.find('photos')
                total_photos = res.attrib['total']
                pages = int(res.attrib['pages'])
                logger.debug(f"Photo results from Flickr were {pages} pages and {total_photos} photos.")
                if pages > 1:
                    for i in range(1, pages + 1):
                        photosList.extend(self.getPhotosByPage(target['targetUserid'], i))
                else:
                    photosList = results.find('photos').findall('photo')
                locationsList = self.getLocationsFromPhotos(photosList)
                return locationsList
        except FlickrError as err:
            logger.error("Error getting locations from Flickr")
            logger.error(err)

    def constructContextInfoWindow(self, link, date):
        html = self.options_string['infowindow_html']
        return html.replace("@LINK@", link).replace("@DATE@", date.strftime("%Y-%m-%d %H:%M:%S %z")).replace("@PLUGIN@", "flickr")

    def getLabelForKey(self, key):
        if not self.labels or key not in self.labels:
            return key
        return self.labels[key]

