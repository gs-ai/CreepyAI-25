#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Map view widget for displaying location data.
"""

import os
import sys
import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QMessageBox
from PyQt5.QtCore import QUrl, QTimer, QObject, pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel

from app.resources.icons import Icons

logger = logging.getLogger(__name__)

class CreepyMapView(QWidget):
    """
    Map view component for displaying location data.
    Uses Leaflet.js for mapping without relying on external APIs.
    """
    
    def __init__(self, parent=None):
        super(CreepyMapView, self).__init__(parent)
        
        # Debug icon loading
        self.logger = logging.getLogger(__name__)
        self.logger.info('Map view initialized, checking icons...')
        icon_names = ['add_24dp_000000', 'remove_24dp_000000', 'map_32dp_000000', 'person_24dp_000000']
        for name in icon_names:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources', f'{name}.png')
            if os.path.exists(icon_path):
                self.logger.info(f'Icon {name} found at {icon_path}')
            else:
                self.logger.warning(f'Icon {name} NOT found at {icon_path}')
        
        self.parent = parent
        self.locations = []
        self.markers = []
        self.map_loaded = False

        self._setup_ui()

        # Create a timer to retry loading if the map doesn't load initially
        self.load_retry_timer = QTimer()
        self.load_retry_timer.timeout.connect(self._reload_map)
        self.load_retry_timer.setSingleShot(True)
        self.load_retry_count = 0
    
    def _setup_ui(self):
        """Set up the map view UI."""
        try:
            # Create layout
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # Create web view for the map
            self.web_view = QWebEngineView(self)
            layout.addWidget(self.web_view)
            
            # Define slot for map_ready - IMPORTANT: This must be defined as a Python slot
            # to be properly exposed to JavaScript
            # Create web channel and explicitly add the slot method
            self.web_channel = QWebChannel()
            
            # Fix: Make map_ready available to JavaScript
            class WebBridge(QObject):
                @pyqtSlot()
                def map_ready(self_bridge):
                    self.map_ready()
            
            self.bridge = WebBridge()
            self.web_channel.registerObject("pyHandler", self.bridge)
            self.web_view.page().setWebChannel(self.web_channel)
            
            # Load HTML template
            self._load_map_template()
            
            # Connect signals
            self.web_view.loadFinished.connect(self._on_load_finished)
            
            # Message when map is not available
            self.error_label = QLabel("Map loading... If the map doesn't appear, check your internet connection.", self)
            self.error_label.setStyleSheet("color: red; background-color: white; padding: 10px;")
            self.error_label.setVisible(False)
            
            logger.info("Map view UI setup complete")
            
        except Exception as e:
            logger.error(f"Error setting up map view: {str(e)}")
            QMessageBox.critical(self.parent, "Map Error", f"Failed to set up map view: {str(e)}")
    
    def _load_map_template(self):
        """Load the map HTML template."""
        try:
            # Get the path to the HTML template
            template_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'include', 'map.html'
            )
            
            # If template exists, load it
            if (os.path.exists(template_path)):
                logger.debug(f"Loading map template from: {template_path}")
                map_url = QUrl.fromLocalFile(template_path)
                self.web_view.load(map_url)
            else:
                # If template doesn't exist, create a basic HTML content with Leaflet
                logger.warning(f"Map template not found at {template_path}. Creating basic template.")
                html_content = self._generate_basic_map_html()
                self.web_view.setHtml(html_content)
                
        except Exception as e:
            logger.error(f"Error loading map template: {str(e)}")
            self.error_label.setVisible(True)
    
    def _generate_basic_map_html(self):
        """Generate basic HTML for the map if the template isn't available."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>CreepyAI Map</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <style>
                html, body, #map {
                    height: 100%;
                    width: 100%;
                    margin: 0;
                    padding: 0;
                }
            </style>
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        </head>
        <body>
            <div id="map"></div>
            <script>
                // Initialize map
                var map = L.map('map').setView([0, 0], 2);
                
                // Add OpenStreetMap layer (no API key required)
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                    maxZoom: 19
                }).addTo(map);
                
                // Set up Qt web channel
                new QWebChannel(qt.webChannelTransport, function (channel) {
                    window.pyHandler = channel.objects.pyHandler;
                    
                    // Notify Python that the map is ready
                    if (window.pyHandler) {
                        window.pyHandler.map_ready();
                    }
                });
                
                // Markers array
                var markers = [];
                
                // Add marker function
                function addMarker(latitude, longitude, title, description, color) {
                    var marker = L.marker([latitude, longitude]).addTo(map);
                    if (title) {
                        marker.bindTooltip(title);
                    }
                    if (description) {
                        marker.bindPopup(description);
                    }
                    markers.push(marker);
                    return markers.length - 1;
                }
                
                // Clear markers
                function clearMarkers() {
                    for (var i = 0; i < markers.length; i++) {
                        map.removeLayer(markers[i]);
                    }
                    markers = [];
                }
                
                // Fit bounds to markers
                function fitMapToMarkers() {
                    if (markers.length > 0) {
                        var group = new L.featureGroup(markers);
                        map.fitBounds(group.getBounds().pad(0.1));
                    }
                }
            </script>
        </body>
        </html>
        """
    
    def _on_load_finished(self, success):
        """Handle map load completion."""
        if success:
            logger.info("Map loaded successfully")
            self.map_loaded = True
            self.error_label.setVisible(False)
        else:
            logger.error("Failed to load map")
            self.error_label.setVisible(True)
            
            # Try to reload if we haven't reached the retry limit
            if self.load_retry_count < 3:  # Limit retries
                self.load_retry_count += 1
                self.load_retry_timer.start(2000)  # Retry after 2 seconds
    
    def _reload_map(self):
        """Attempt to reload the map."""
        logger.info(f"Retrying map load (attempt {self.load_retry_count})")
        self._load_map_template()
    
    def map_ready(self):
        """Called from JavaScript when the map is ready."""
        logger.info("Map is ready for interaction")
        self.map_loaded = True
        
        # If we have locations waiting to be displayed, show them now
        if self.locations:
            self.display_locations(self.locations)
    
    def display_locations(self, locations):
        """
        Display locations on the map.
        
        Args:
            locations: List of Location objects to display
        """
        # Store locations in case we need to redisplay later
        self.locations = locations
        
        if not self.map_loaded:
            logger.warning("Map not loaded yet. Locations will be displayed when the map is ready.")
            return
            
        try:
            # First clear existing markers
            self.web_view.page().runJavaScript("clearMarkers();")
            
            # Add new markers
            self.markers = []
            
            for location in locations:
                if location.is_valid:
                    # Escape HTML in description to prevent script injection
                    description = f"""
                    <div>
                        <h4>{location.source}</h4>
                        <p>Date: {location.datetime_friendly}</p>
                        <p>{location.context}</p>
                    </div>
                    """
                    
                    # Create marker
                    js_code = f"addMarker({location.latitude}, {location.longitude}, '{location.source}', '{description}', 'red');"
                    self.web_view.page().runJavaScript(js_code)
                    self.markers.append(location)
            
            # Fit map to markers
            if self.markers:
                self.web_view.page().runJavaScript("fitMapToMarkers();")
                
            logger.info(f"Displayed {len(self.markers)} locations on map")
            
        except Exception as e:
            logger.error(f"Error displaying locations on map: {str(e)}")
    
    def clear_map(self):
        """Clear all markers from the map."""
        if not self.map_loaded:
            return
            
        self.web_view.page().runJavaScript("clearMarkers();")
        self.markers = []
        self.locations = []
        logger.info("Cleared all markers from map")
    
    def center_map(self, latitude, longitude, zoom=12):
        """
        Center the map on specific coordinates.
        
        Args:
            latitude: Latitude to center on
            longitude: Longitude to center on
            zoom: Zoom level (1-19)
        """
        if not self.map_loaded:
            return
            
        js_code = f"map.setView([{latitude}, {longitude}], {zoom});"
        self.web_view.page().runJavaScript(js_code)
    
    def fit_to_markers(self):
        """Fit the map view to include all markers."""
        if not self.map_loaded or not self.markers:
            return
            
        self.web_view.page().runJavaScript("fitMapToMarkers();")
