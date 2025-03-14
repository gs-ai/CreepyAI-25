"""
Map Controller for CreepyAI
Manages interactions between UI map view and location data
"""

import os
import sys
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal, QUrl, QVariant, QJsonValue, QJsonDocument
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel

from app.models.location_data import LocationDataModel, Location
from app.core.path_utils import get_resource_path

logger = logging.getLogger(__name__)

class MapController(QObject):
    """
    Controller for map operations
    
    Manages interactions between the map view and location data model
    """
    
    # Signals
    locationSelected = pyqtSignal(str)  # Emits location ID when selected on map
    mapLoaded = pyqtSignal(bool)  # Emits True when map loaded successfully, False otherwise
    clusterSelected = pyqtSignal(list)  # Emits list of location IDs when a cluster is selected
    mapMoved = pyqtSignal(float, float, float)  # Emits lat, lng, zoom when map is moved
    mapError = pyqtSignal(str)  # Emits error message when map encounters an error
    
    def __init__(self, web_view: QWebEngineView):
        """
        Initialize the map controller
        
        Args:
            web_view: QWebEngineView to display the map
        """
        super().__init__()
        self.web_view = web_view
        self.location_model = None
        self.markers = {}  # Dictionary of marker IDs to location IDs
        self.selected_marker_id = None
        self.marker_counter = 0
        self.web_channel = QWebChannel()
        
        # Set up web channel
        self.web_view.page().setWebChannel(self.web_channel)
        self.web_channel.registerObject("mapController", self)
        
        # Set up map
        self.setup_map()
        
        # Flag to track if map is ready
        self.map_ready = False
        
        # Default view settings
        self.default_lat = 0
        self.default_lng = 0
        self.default_zoom = 4
    
    def setup_map(self) -> None:
        """Set up the map view"""
        try:
            # Find map HTML file
            map_path = get_resource_path("map/index.html")
            if not map_path:
                logger.error("Map HTML file not found")
                self.mapError.emit("Map HTML file not found")
                self.mapLoaded.emit(False)
                return
                
            # Load map HTML file
            self.web_view.load(QUrl.fromLocalFile(str(map_path)))
            
            # Connect signals
            self.web_view.loadFinished.connect(self._on_map_loaded)
            
            # Connect JavaScript callbacks
            page = self.web_view.page()
            page.javaScriptConsoleMessage = self._handle_js_console
            
            logger.info("Map setup complete")
            
        except Exception as e:
            logger.error(f"Error setting up map: {e}")
            self.mapError.emit(f"Error setting up map: {str(e)}")
            self.mapLoaded.emit(False)
    
    def _on_map_loaded(self, success: bool) -> None:
        """
        Handle map loaded event
        
        Args:
            success: Whether the map loaded successfully
        """
        if success:
            logger.info("Map loaded successfully")
            self.map_ready = True
            self.mapLoaded.emit(True)
            
            # Set up custom JS handler for map events
            self._setup_js_handlers()
            
            # Set map default location
            self.set_view(self.default_lat, self.default_lng, self.default_zoom)
        else:
            logger.error("Failed to load map")
            self.map_ready = False
            self.mapLoaded.emit(False)
    
    def _setup_js_handlers(self) -> None:
        """Set up JavaScript handlers for map events"""
        js_code = """
        // Map click handler
        map.on('click', function(e) {
            // Check if a marker was clicked
            if (e.originalEvent.target && e.originalEvent.target.className === 'leaflet-marker-icon') {
                // Don't handle marker clicks here
                return;
            }
            
            // Handle click on map
            var lat = e.latlng.lat;
            var lng = e.latlng.lng;
            mapController.handleMapClick(lat, lng);
        });
        
        // Map move handler
        map.on('moveend', function() {
            var center = map.getCenter();
            var lat = center.lat;
            var lng = center.lng;
            var zoom = map.getZoom();
            mapController.handleMapMove(lat, lng, zoom);
        });
        
        // Marker click handler - set globally for access from creepyAI object
        window.onMarkerClick = function(markerId) {
            mapController.handleMarkerClick(markerId);
        };
        
        // Cluster click handler
        window.onClusterClick = function(markerIds) {
            mapController.handleClusterClick(markerIds);
        };
        
        // Set map as ready
        window.creepyAI = window.creepyAI || {};
        window.creepyAI.mapReady = true;
        """
        
        self.web_view.page().runJavaScript(js_code)
    
    def set_location_model(self, model: LocationDataModel) -> None:
        """
        Set the location data model
        
        Args:
            model: Location data model to use
        """
        if self.location_model:
            # Disconnect old model signals
            self.location_model.locationAdded.disconnect(self.add_location_marker)
            self.location_model.locationRemoved.disconnect(self.remove_location_marker)
            self.location_model.locationUpdated.disconnect(self.update_location_marker)
            self.location_model.locationsCleared.disconnect(self.clear_markers)
        
        self.location_model = model
        
        if model:
            # Connect to model signals
            model.locationAdded.connect(self.add_location_marker)
            model.locationRemoved.connect(self.remove_location_marker)
            model.locationUpdated.connect(self.update_location_marker)
            model.locationsCleared.connect(self.clear_markers)
            
            # Add markers for all locations in the model
            self.display_all_locations()
    
    def display_all_locations(self) -> None:
        """Display all locations from the model on the map"""
        if not self.map_ready or not self.location_model:
            return
        
        # Clear existing markers
        self.clear_markers()
        
        # Add markers for all locations
        for location in self.location_model.get_all_locations():
            self.add_location_marker(location)
        
        # Fit map to show all markers
        self.fit_bounds()
    
    def add_location_marker(self, location: Location) -> None:
        """
        Add a marker for a location
        
        Args:
            location: Location to add marker for
        """
        if not self.map_ready:
            return
        
        marker_id = f"marker_{self.marker_counter}"
        self.marker_counter += 1
        
        # Save mapping from marker ID to location ID
        self.markers[marker_id] = location.id
        
        # Create marker options
        marker_options = {
            "id": marker_id,
            "lat": location.latitude,
            "lng": location.longitude,
            "title": f"{location.source} - {location.timestamp.strftime('%Y-%m-%d %H:%M:%S') if hasattr(location.timestamp, 'strftime') else ''}",
            "popup": f"<strong>{location.source}</strong><br>{location.address or ''}<br>{location.context or ''}",
            "source": location.source,
            "timestamp": location.timestamp.isoformat() if hasattr(location.timestamp, 'isoformat') else None
        }
        
        # Set icon based on source
        if location.source:
            source_lower = location.source.lower()
            for social_media in ["facebook", "twitter", "instagram", "linkedin", "snapchat", "tiktok", "pinterest"]:
                if social_media in source_lower:
                    marker_options["icon"] = social_media
                    break
        
        # Add marker to map
        js_code = f"""
        window.creepyAI = window.creepyAI || {{}};
        if (window.creepyAI.addMarker) {{
            window.creepyAI.addMarker({json.dumps(marker_options)});
        }}
        """
        self.web_view.page().runJavaScript(js_code)
    
    def remove_location_marker(self, location_id: str) -> None:
        """
        Remove a marker for a location
        
        Args:
            location_id: ID of location to remove marker for
        """
        if not self.map_ready:
            return
        
        # Find marker ID for this location
        marker_id = None
        for m_id, loc_id in self.markers.items():
            if loc_id == location_id:
                marker_id = m_id
                break
        
        if marker_id:
            # Remove marker from map
            js_code = f"""
            window.creepyAI = window.creepyAI || {{}};
            if (window.creepyAI.removeMarker) {{
                window.creepyAI.removeMarker("{marker_id}");
            }}
            """
            self.web_view.page().runJavaScript(js_code)
            
            # Remove from our markers dictionary
            del self.markers[marker_id]
    
    def update_location_marker(self, location: Location) -> None:
        """
        Update a marker for a location
        
        Args:
            location: Updated location
        """
        if not self.map_ready:
            return
        
        # Find marker ID for this location
        marker_id = None
        for m_id, loc_id in self.markers.items():
            if loc_id == location.id:
                marker_id = m_id
                break
        
        if marker_id:
            # Update marker on map
            marker_options = {
                "id": marker_id,
                "lat": location.latitude,
                "lng": location.longitude,
                "title": f"{location.source} - {location.timestamp.strftime('%Y-%m-%d %H:%M:%S') if hasattr(location.timestamp, 'strftime') else ''}",
                "popup": f"<strong>{location.source}</strong><br>{location.address or ''}<br>{location.context or ''}",
                "source": location.source
            }
            
            js_code = f"""
            window.creepyAI = window.creepyAI || {{}};
            if (window.creepyAI.updateMarker) {{
                window.creepyAI.updateMarker({json.dumps(marker_options)});
            }}
            """
            self.web_view.page().runJavaScript(js_code)
    
    def clear_markers(self) -> None:
        """Clear all markers from the map"""
        if not self.map_ready:
            return
        
        js_code = """
        window.creepyAI = window.creepyAI || {};
        if (window.creepyAI.clearMarkers) {
            window.creepyAI.clearMarkers();
        }
        """
        self.web_view.page().runJavaScript(js_code)
        
        # Clear our markers dictionary
        self.markers = {}
        self.marker_counter = 0
    
    def set_view(self, lat: float, lng: float, zoom: int = 14) -> None:
        """
        Set the map view
        
        Args:
            lat: Latitude
            lng: Longitude
            zoom: Zoom level (1-18)
        """
        if not self.map_ready:
            return
        
        js_code = f"""
        window.creepyAI = window.creepyAI || {{}};
        if (window.creepyAI.setView) {{
            window.creepyAI.setView({lat}, {lng}, {zoom});
        }}
        """
        self.web_view.page().runJavaScript(js_code)
    
    def fit_bounds(self) -> None:
        """Fit the map to show all markers"""
        if not self.map_ready:
            return
        
        js_code = """
        window.creepyAI = window.creepyAI || {};
        if (window.creepyAI.fitBounds) {
            window.creepyAI.fitBounds();
        }
        """
        self.web_view.page().runJavaScript(js_code)
    
    def select_marker(self, location_id: str) -> None:
        """
        Select a marker on the map
        
        Args:
            location_id: ID of location to select
        """
        if not self.map_ready:
            return
        
        # Find marker ID for this location
        marker_id = None
        for m_id, loc_id in self.markers.items():
            if loc_id == location_id:
                marker_id = m_id
                break
        
        if marker_id:
            # Select marker on map
            js_code = f"""
            window.creepyAI = window.creepyAI || {{}};
            if (window.creepyAI.selectMarker) {{
                window.creepyAI.selectMarker("{marker_id}");
            }}
            """
            self.web_view.page().runJavaScript(js_code)
            
            # Store selected marker ID
            self.selected_marker_id = marker_id
    
    def deselect_marker(self) -> None:
        """Deselect any selected marker"""
        if not self.map_ready:
            return
        
        js_code = """
        window.creepyAI = window.creepyAI || {};
        if (window.creepyAI.deselectMarker) {
            window.creepyAI.deselectMarker();
        }
        """
        self.web_view.page().runJavaScript(js_code)
        
        # Clear selected marker ID
        self.selected_marker_id = None
    
    def set_map_layer(self, layer_name: str) -> None:
        """
        Set the map layer
        
        Args:
            layer_name: Name of the layer to set
        """
        if not self.map_ready:
            return
        
        js_code = f"""
        window.creepyAI = window.creepyAI || {{}};
        if (window.creepyAI.setMapLayer) {{
            window.creepyAI.setMapLayer("{layer_name}");
        }}
        """
        self.web_view.page().runJavaScript(js_code)
    
    def toggle_heatmap(self, enabled: bool) -> None:
        """
        Toggle heatmap display
        
        Args:
            enabled: Whether to enable heatmap
        """
        if not self.map_ready:
            return
        
        js_code = f"""
        window.creepyAI = window.creepyAI || {{}};
        if (window.creepyAI.toggleHeatmap) {{
            window.creepyAI.toggleHeatmap({str(enabled).lower()});
        }}
        """
        self.web_view.page().runJavaScript(js_code)
    
    def toggle_clustering(self, enabled: bool) -> None:
        """
        Toggle marker clustering
        
        Args:
            enabled: Whether to enable clustering
        """
        if not self.map_ready:
            return
        
        js_code = f"""
        window.creepyAI = window.creepyAI || {{}};
        if (window.creepyAI.toggleClustering) {{
            window.creepyAI.toggleClustering({str(enabled).lower()});
        }}
        """
        self.web_view.page().runJavaScript(js_code)
    
    def show_path(self, show: bool = True, 
                 location_ids: Optional[List[str]] = None,
                 color: str = "#3388ff") -> None:
        """
        Show or hide path between locations
        
        Args:
            show: Whether to show path
            location_ids: Optional list of location IDs to include (if None, use all)
            color: Path color
        """
        if not self.map_ready:
            return
        
        if not show:
            # Hide path
            js_code = """
            window.creepyAI = window.creepyAI || {};
            if (window.creepyAI.hidePath) {
                window.creepyAI.hidePath();
            }
            """
            self.web_view.page().runJavaScript(js_code)
            return
        
        # Get locations to include in path
        locations = []
        if location_ids:
            for location_id in location_ids:
                location = self.location_model.get_location(location_id)
                if location:
                    locations.append(location)
        else:
            locations = self.location_model.get_all_locations()
        
        # Sort locations by timestamp (if available)
        locations = sorted(
            locations,
            key=lambda loc: loc.timestamp if loc.timestamp else datetime.min
        )
        
        # Create path data
        path_data = []
        for location in locations:
            path_data.append({
                "lat": location.latitude,
                "lng": location.longitude,
                "timestamp": location.timestamp.isoformat() if hasattr(location.timestamp, 'isoformat') else None
            })
        
        # Show path
        js_code = f"""
        window.creepyAI = window.creepyAI || {{}};
        if (window.creepyAI.showPath) {{
            window.creepyAI.showPath({json.dumps(path_data)}, "{color}");
        }}
        """
        self.web_view.page().runJavaScript(js_code)
    
    # JavaScript callable slots
    
    @pyqtSlot(str)
    def handleMarkerClick(self, marker_id: str) -> None:
        """
        Handle marker click event from JavaScript
        
        Args:
            marker_id: ID of the clicked marker
        """
        if marker_id in self.markers:
            location_id = self.markers[marker_id]
            logger.debug(f"Marker clicked: {marker_id} (location {location_id})")
            self.locationSelected.emit(location_id)
    
    @pyqtSlot(list)
    def handleClusterClick(self, marker_ids: List[str]) -> None:
        """
        Handle cluster click event from JavaScript
        
        Args:
            marker_ids: List of IDs of markers in the cluster
        """
        location_ids = []
        for marker_id in marker_ids:
            if marker_id in self.markers:
                location_ids.append(self.markers[marker_id])
        
        if location_ids:
            logger.debug(f"Cluster clicked with {len(location_ids)} locations")
            self.clusterSelected.emit(location_ids)
    
    @pyqtSlot(float, float)
    def handleMapClick(self, lat: float, lng: float) -> None:
        """
        Handle map click event from JavaScript
        
        Args:
            lat: Latitude of clicked point
            lng: Longitude of clicked point
        """
        # This could be used to add new locations or perform other actions
        logger.debug(f"Map clicked at {lat}, {lng}")
    
    @pyqtSlot(float, float, int)
    def handleMapMove(self, lat: float, lng: float, zoom: int) -> None:
        """
        Handle map move event from JavaScript
        
        Args:
            lat: New center latitude
            lng: New center longitude
            zoom: New zoom level
        """
        logger.debug(f"Map moved to {lat}, {lng} (zoom {zoom})")
        self.mapMoved.emit(lat, lng, zoom)
    
    def _handle_js_console(self, level: int, message: str, line_number: int, source_id: str) -> None:
        """
        Handle JavaScript console messages
        
        Args:
            level: Message level (0=info, 1=warning, 2=error)
            message: Console message
            line_number: Line number
            source_id: Source ID
        """
        prefix = "JavaScript"
        if level == 0:
            logger.debug(f"{prefix}: {message}")
        elif level == 1:
            logger.warning(f"{prefix}: {message}")
        else:
            logger.error(f"{prefix}: {message}")
