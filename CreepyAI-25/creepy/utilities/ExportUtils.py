#!/usr/bin/python
# -*- coding: utf-8 -*-
import csv
import json
import os
import logging
from utilities import GeneralUtilities

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(os.getcwd(), 'creepy_export.log'))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

class ExportUtils:
    @staticmethod
    def export_to_csv(locations, filename, filtering=False):
        """
        Export locations to CSV format
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as fileobj:
                writer = csv.writer(fileobj, quoting=csv.QUOTE_ALL)
                writer.writerow(('Timestamp', 'Latitude', 'Longitude', 'Location Name', 'Retrieved from', 'Context'))
                for loc in locations:
                    if (filtering and loc.visible) or not filtering:
                        writer.writerow((loc.datetime.strftime('%Y-%m-%d %H:%M:%S %z'), 
                                        loc.latitude, 
                                        loc.longitude, 
                                        loc.shortName, 
                                        loc.plugin, 
                                        loc.context))
            return True
        except Exception as err:
            logger.error(f"Error exporting to CSV: {err}")
            return False

    @staticmethod
    def export_to_kml(locations, filename, filtering=False):
        """
        Export locations to KML format
        """
        try:
            with open(filename, 'w', encoding='utf-8') as fileobj:
                kml = []
                kml.append('<?xml version="1.0" encoding="UTF-8"?>')
                kml.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
                kml.append('<Document>')
                kml.append(f'  <name>{os.path.basename(filename)}</name>')
                
                for loc in locations:
                    if (filtering and loc.visible) or not filtering:
                        kml.append('  <Placemark>')
                        kml.append(f'  <name>{loc.datetime.strftime("%Y-%m-%d %H:%M:%S %z")}</name>')
                        kml.append(f'    <description>{GeneralUtilities.html_escape(loc.context)}</description>')
                        kml.append('    <Point>')
                        kml.append(f'       <coordinates>{loc.longitude}, {loc.latitude}, 0</coordinates>')
                        kml.append('    </Point>')
                        kml.append('  </Placemark>')
                
                kml.append('</Document>')
                kml.append('</kml>')
                
                kml_string = '\n'.join(kml)
                fileobj.write(kml_string)
            return True
        except Exception as err:
            logger.error(f"Error exporting to KML: {err}")
            return False

    @staticmethod
    def export_to_json(locations, filename, filtering=False):
        """
        Export locations to GeoJSON format
        """
        try:
            geo_json = {
                "type": "FeatureCollection",
                "features": []
            }
            
            for loc in locations:
                if (filtering and loc.visible) or not filtering:
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(loc.longitude), float(loc.latitude)]
                        },
                        "properties": {
                            "timestamp": loc.datetime.strftime('%Y-%m-%d %H:%M:%S %z'),
                            "name": loc.shortName,
                            "source": loc.plugin,
                            "context": loc.context
                        }
                    }
                    geo_json["features"].append(feature)
                    
            with open(filename, 'w', encoding='utf-8') as fileobj:
                json.dump(geo_json, fileobj, indent=2)
            return True
        except Exception as err:
            logger.error(f"Error exporting to GeoJSON: {err}")
            return False

    @staticmethod
    def export_to_html(locations, filename, filtering=False):
        """
        Export locations to standalone HTML with interactive map
        """
        try:
            locations_js = []
            for loc in locations:
                if (filtering and loc.visible) or not filtering:
                    loc_dict = {
                        "lat": float(loc.latitude),
                        "lng": float(loc.longitude),
                        "name": loc.shortName,
                        "date": loc.datetime.strftime('%Y-%m-%d %H:%M:%S %z'),
                        "context": loc.context,
                        "source": loc.plugin
                    }
                    locations_js.append(loc_dict)
            
            with open(os.path.join(os.getcwd(), 'include', 'export_template.html'), 'r') as template:
                html = template.read()
                
            html = html.replace('var LOCATIONS = [];', f'var LOCATIONS = {json.dumps(locations_js)};')
            
            with open(filename, 'w', encoding='utf-8') as fileobj:
                fileobj.write(html)
            return True
        except Exception as err:
            logger.error(f"Error exporting to HTML: {err}")
            return False
