#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
UI Mapping Generator for CreepyAI Plugins
Generates HTML/JavaScript for displaying location data on various mapping providers
"""

import os
import json
import base64
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import colorsys
import random

from plugins.base_plugin import LocationPoint

logger = logging.getLogger(__name__)

class PluginUIMap:
    """
    Utility class for generating interactive maps from plugin location data
    """
    
    MAP_PROVIDERS = {
        'leaflet': {
            'name': 'Leaflet',
            'url': 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
            'css': 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
            'attribution': '© OpenStreetMap contributors'
        },
        'google': {
            'name': 'Google Maps',
            'url': 'https://maps.googleapis.com/maps/api/js?key={api_key}&callback=initMap',
            'attribution': '© Google'
        },
        'mapbox': {
            'name': 'Mapbox',
            'url': 'https://api.mapbox.com/mapbox-gl-js/v2.14.1/mapbox-gl.js',
            'css': 'https://api.mapbox.com/mapbox-gl-js/v2.14.1/mapbox-gl.css',
            'attribution': '© Mapbox © OpenStreetMap'
        }
    }
    
    def __init__(self, provider: str = 'leaflet', api_key: Optional[str] = None):
        """
        Initialize the UI map generator
        
        Args:
            provider: Map provider to use ('leaflet', 'google', or 'mapbox')
            api_key: API key for the selected map provider (if required)
        """
        self.provider = provider.lower()
        if self.provider not in self.MAP_PROVIDERS:
            logger.warning(f"Unknown map provider '{provider}', falling back to leaflet")
            self.provider = 'leaflet'
            
        self.api_key = api_key
        self.map_id = "creepyai-map"
        
    def generate_map_html(self, locations: List[LocationPoint], 
                         title: str = "CreepyAI Location Map",
                         group_by_source: bool = True,
                         include_timeline: bool = True) -> str:
        """
        Generate HTML with an interactive map displaying the provided location points
        
        Args:
            locations: List of LocationPoint objects to display
            title: Title for the map page
            group_by_source: Whether to group markers by source
            include_timeline: Whether to include a timeline control
            
        Returns:
            HTML string with map
        """
        if not locations:
            return self._generate_empty_map_html(title)
            
        if self.provider == 'leaflet':
            return self._generate_leaflet_map(locations, title, group_by_source, include_timeline)
        elif self.provider == 'google':
            return self._generate_google_map(locations, title, group_by_source, include_timeline)
        elif self.provider == 'mapbox':
            return self._generate_mapbox_map(locations, title, group_by_source, include_timeline)
        else:
            # Fallback to leaflet
            return self._generate_leaflet_map(locations, title, group_by_source, include_timeline)
    
    def _generate_empty_map_html(self, title: str) -> str:
        """Generate HTML for an empty map (no locations)"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        .container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }}
        .message {{ text-align: center; padding: 2rem; background-color: #f8f9fa; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        p {{ color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="message">
            <h1>{title}</h1>
            <p>No location data available to display.</p>
        </div>
    </div>
</body>
</html>"""
    
    def _generate_leaflet_map(self, locations: List[LocationPoint], title: str,
                             group_by_source: bool, include_timeline: bool) -> str:
        """Generate HTML with a Leaflet map"""
        # Group locations by source if needed
        source_groups = {}
        if group_by_source:
            for loc in locations:
                source = loc.source or "Unknown"
                if source not in source_groups:
                    source_groups[source] = []
                source_groups[source].append(loc)
        else:
            source_groups = {"Locations": locations}
            
        # Assign a unique color for each source
        source_colors = self._generate_colors(len(source_groups))
        source_color_map = {}
        for i, source in enumerate(source_groups.keys()):
            source_color_map[source] = source_colors[i]
            
        # Create marker data for JavaScript
        marker_data_js = []
        
        for source, locs in source_groups.items():
            color = source_color_map[source]
            
            for loc in locs:
                popup_content = self._create_popup_content(loc)
                popup_content_js = popup_content.replace("'", "\\'").replace("\n", "\\n")
                
                # Format the timestamp
                timestamp_str = loc.timestamp.strftime('%Y-%m-%dT%H:%M:%S') if loc.timestamp else ""
                
                marker_data = {
                    'lat': loc.latitude,
                    'lng': loc.longitude,
                    'popup': popup_content_js,
                    'source': source,
                    'color': color,
                    'timestamp': timestamp_str
                }
                
                marker_data_js.append(json.dumps(marker_data))
                
        # Calculate center point for the map
        center_lat = sum(loc.latitude for loc in locations) / len(locations)
        center_lng = sum(loc.longitude for loc in locations) / len(locations)
        
        # Generate HTML with embedde