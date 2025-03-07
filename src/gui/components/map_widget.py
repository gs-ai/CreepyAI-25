#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Map widget for CreepyAI.

This module provides a reusable map widget for displaying
geographical data using PyQtWebEngine and Leaflet.
"""

import os
import json
import logging
from PyQt5.QtCore import QUrl, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEnginePage
from PyQt5.QtWidgets import QVBoxLayout, QWidget

logger = logging.getLogger('CreepyAI.UI.MapWidget')

class MapBridge(QObject):
    """Bridge between JavaScript and Python for the map widget."""
    
    locationSelected = pyqtSignal(float, float, str)
    markersUpdated = pyqtSignal(str)
    
    @pyqtSlot(float, float, str)
    def on_location_selected(self, lat, lng, name):
        """Handle location selection from the map."""
        logger.debug(f"Location selected: {lat}, {lng} ({name})")
        self.locationSelected.emit(lat, lng, name)
    
    @pyqtSlot(str)
    def on_markers_updated(self, markers_json):
        """Handle markers update from the map."""
        logger.debug("Markers updated")
        self.markersUpdated.emit(markers_json)

class MapWidget(QWidget):
    """
    Map widget for displaying geographical data.
    
    This widget uses Leaflet.js with a PyQt5 QWebEngineView to display
    interactive maps and location data.
    """
    
    locationSelected = pyqtSignal(float, float, str)
    
    def __init__(self, parent=None):
        """
        Initialize the map widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create web engine view
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(
            QWebEngineSettings.JavascriptEnabled, True)
        self.web_view.settings().setAttribute(
            QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        
        # Create bridge between JavaScript and Python
        self.bridge = MapBridge()
        self.bridge.locationSelected.connect(self.on_location_selected)
        
        # Add web view to layout
        self.layout.addWidget(self.web_view)
        
        # Initialize map
        self.initialize_map()
    
    def initialize_map(self):
        """Initialize the map with Leaflet."""
        # Get path to HTML template
        html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                 'resources', 'html', 'map_template.html')
        
        # Check if the file exists
        if os.path.exists(html_path):
            self.web_view.load(QUrl.fromLocalFile(html_path))
            logger.info(f"Loaded map template from: {html_path}")
        else:
            # Use default HTML if template doesn't exist
            logger.warning(f"Map template not found at {html_path}, using default")
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>CreepyAI Map</title>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
                <style>
                    html, body, #map {
                        width: 100%;
                        height: 100%;
                        margin: 0;
                        padding: 0;
                    }
                </style>
                <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            </head>
            <body>
                <div id="map"></div>
                <script>
                    var map = L.map('map').setView([0, 0], 2);
                    
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    }).addTo(map);
                    
                    var markers = [];
                    
                    function addMarker(lat, lng, name, popupContent) {
                        var marker = L.marker([lat, lng]).addTo(map);
                        if (popupContent) {
                            marker.bindPopup(popupContent);
                        } else {
                            marker.bindPopup(name);
                        }
                        markers.push({
                            id: markers.length,
                            lat: lat,
                            lng: lng,
                            name: name
                        });
                        return marker;
                    }
                    
                    function clearMarkers() {
                        markers.forEach(function(marker) {
                            map.removeLayer(marker);
                        });
                        markers = [];
                    }
                    
                    map.on('click', function(e) {
                        var lat = e.latlng.lat;
                        var lng = e.latlng.lng;
                        var name = "Selected Location";
                        window.pybridge.on_location_selected(lat, lng, name);
                    });
                </script>
            </body>
            </html>
            """
            self.web_view.setHtml(html)
    
    def on_location_selected(self, lat, lng, name):
        """Handle location selection from the map."""
        self.locationSelected.emit(lat, lng, name)
    
    def add_marker(self, lat, lng, name, popup_content=None):
        """
        Add a marker to the map.
        
        Args:
            lat: Latitude
            lng: Longitude
            name: Marker name
            popup_content: Custom popup content (HTML)
        """
        script = f"addMarker({lat}, {lng}, '{name}', "
        if popup_content:
            script += f"'{popup_content}'"
        else:
            script += "null"
        script += ");"
        
        self.web_view.page().runJavaScript(script)
    
    def clear_markers(self):
        """Clear all markers from the map."""
        self.web_view.page().runJavaScript("clearMarkers();")
    
    def center_map(self, lat, lng, zoom=12):
        """
        Center the map on a specific location.
        
        Args:
            lat: Latitude
            lng: Longitude
            zoom: Zoom level
        """
        self.web_view.page().runJavaScript(f"map.setView([{lat}, {lng}], {zoom});")
