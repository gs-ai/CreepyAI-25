#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, pyqtSlot

# Try to import QtWebEngineWidgets (preferred) or fall back to older QtWebKit
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
    USE_WEBENGINE = True
except ImportError:
    try:
        from PyQt5.QtWebKitWidgets import QWebView
        from PyQt5.QtWebKit import QWebSettings
        USE_WEBENGINE = False
        logging.warning("Using deprecated QtWebKit. Consider upgrading to PyQt5 with QtWebEngine.")
    except ImportError:
        logging.error("Neither QtWebEngine nor QtWebKit is available. Map functionality will be disabled.")
        USE_WEBENGINE = None

logger = logging.getLogger(__name__)

class MapView(QWidget):
    """
    A widget that displays a map using either QtWebEngine or QtWebKit.
    It can load map data from various sources including Leaflet, OpenStreetMap, etc.
    """
    locationClicked = pyqtSignal(float, float, str)  # lat, lon, info
    mapLoaded = pyqtSignal(bool)  # success

    def __init__(self, parent=None):
        super(MapView, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        self.web_view = None
        self.initialize_web_view()

    def initialize_web_view(self):
        """Initialize the web view with appropriate backend"""
        if USE_WEBENGINE is None:
            logger.error("No web view backend available. Map will not be displayed.")
            return
            
        if USE_WEBENGINE:
            self.web_view = QWebEngineView(self)
            # Set up web engine specific settings
            page = self.web_view.page()
            # Fix the attributes to use the correct names available in your PyQt5 version
            try:
                # Modern PyQt5 versions
                page.settings().setAttribute(QWebEnginePage.WebAttribute.WebGLEnabled, True)
                page.settings().setAttribute(QWebEnginePage.WebAttribute.LocalContentCanAccessRemoteUrls, True)
                page.settings().setAttribute(QWebEnginePage.WebAttribute.LocalContentCanAccessFileUrls, True)
            except (AttributeError, TypeError):
                try:
                    # Older PyQt5 versions
                    page.settings().setAttribute(QWebEnginePage.WebGLEnabled, True)
                    page.settings().setAttribute(QWebEnginePage.LocalContentCanAccessRemoteUrls, True)
                    page.settings().setAttribute(QWebEnginePage.LocalContentCanAccessFileUrls, True)
                except (AttributeError, TypeError):
                    # Last resort - numeric values directly
                    logger.warning("Using numeric values for QWebEnginePage settings")
                    page.settings().setAttribute(11, True)  # WebGLEnabled
                    page.settings().setAttribute(6, True)   # LocalContentCanAccessRemoteUrls
                    page.settings().setAttribute(7, True)   # LocalContentCanAccessFileUrls
        else:
            self.web_view = QWebView(self)
            # Set up WebKit specific settings
            settings = self.web_view.settings()
            settings.setAttribute(QWebSettings.JavascriptEnabled, True)
            settings.setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
            
        self.layout.addWidget(self.web_view)
        self.web_view.loadFinished.connect(self._on_load_finished)
        logger.info(f"Map view initialized with {'WebEngine' if USE_WEBENGINE else 'WebKit'} backend")
        
    def _on_load_finished(self, success):
        """Called when the web page has finished loading"""
        self.mapLoaded.emit(success)
        if success:
            logger.info("Map loaded successfully")
        else:
            logger.error("Failed to load map")

    def load_leaflet_map(self):
        """Load a Leaflet map"""
        html_path = os.path.join(os.path.dirname(__file__), 'resources', 'map.html')
        
        if not os.path.exists(html_path):
            # Create a basic Leaflet map HTML file if it doesn't exist
            map_html_dir = os.path.dirname(html_path)
            os.makedirs(map_html_dir, exist_ok=True)
            
            with open(html_path, 'w') as f:
                f.write('''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CreepyAI Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <style>
        body, html, #map {
            height: 100%;
            width: 100%;
            margin: 0;
            padding: 0;
        }
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([0, 0], 2);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19
        }).addTo(map);
        
        // Function to add a marker that can be called from Python
        function addMarker(lat, lng, title, info) {
            var marker = L.marker([lat, lng]).addTo(map);
            if (title || info) {
                marker.bindPopup("<b>" + title + "</b><br>" + info);
            }
            return marker;
        }
        
        // Function to center map at a location
        function centerMap(lat, lng, zoom) {
            map.setView([lat, lng], zoom);
        }
        
        // Function to clear all markers
        function clearMarkers() {
            map.eachLayer(function(layer) {
                if (layer instanceof L.Marker) {
                    map.removeLayer(layer);
                }
            });
        }
        
        // Function to handle clicks and send coordinates back to Python
        map.on('click', function(e) {
            var lat = e.latlng.lat;
            var lng = e.latlng.lng;
            // This will be caught by the Python code
            if (window.pyQtBridge) {
                window.pyQtBridge.handleMapClick(lat, lng);
            } else {
                console.log("Map clicked at: " + lat + ", " + lng);
            }
        });
    </script>
</body>
</html>''')
                
        url = QUrl.fromLocalFile(html_path)
        self.web_view.load(url)
        return True

    def add_marker(self, lat, lon, title="", info=""):
        """Add a marker to the map"""
        if not self.web_view:
            return False
        
        # Sanitize the title and info for JavaScript
        safe_title = title.replace("'", "\\'").replace("\n", " ")
        safe_info = info.replace("'", "\\'").replace("\n", "<br>")
        
        js = f"addMarker({lat}, {lon}, '{safe_title}', '{safe_info}');"
        
        if USE_WEBENGINE:
            self.web_view.page().runJavaScript(js)
        else:
            self.web_view.page().mainFrame().evaluateJavaScript(js)
        
        return True

    def center_map(self, lat, lon, zoom=13):
        """Center the map on the given coordinates"""
        if not self.web_view:
            return False
            
        js = f"centerMap({lat}, {lon}, {zoom});"
        
        if USE_WEBENGINE:
            self.web_view.page().runJavaScript(js)
        else:
            self.web_view.page().mainFrame().evaluateJavaScript(js)
            
        return True
        
    def clear_markers(self):
        """Clear all markers from the map"""
        if not self.web_view:
            return False
            
        js = "clearMarkers();"
        
        if USE_WEBENGINE:
            self.web_view.page().runJavaScript(js)
        else:
            self.web_view.page().mainFrame().evaluateJavaScript(js)
            
        return True
