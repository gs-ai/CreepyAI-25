#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import logging
import folium
import json
import datetime
from xml.dom import minidom
from PyQt5.QtCore import QObject
from .error_handling import ErrorTracker  # Fixed import path

# Handle simplekml import gracefully
try:
    import simplekml
    SIMPLEKML_AVAILABLE = True
except ImportError:
    SIMPLEKML_AVAILABLE = False
    logging.warning("simplekml module not found. KML export functionality will be disabled.")

logger = logging.getLogger('CreepyAI.ExportUtils')
error_tracker = ErrorTracker()

class ExportManager(QObject):
    """Class for managing location data exports"""
    
    def __init__(self):
        super(ExportManager, self).__init__()
        self.template_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'include'
        )
        
        # Check for simplekml and notify if missing
        if not SIMPLEKML_AVAILABLE:
            error_tracker.track_dependency_error(
                module_name="simplekml",
                feature_name="KML Export",
                error_message="Install using pip install simplekml"
            )
    
    def export_locations(self, locations_list, file_path, format_type):
        """
        Export locations to the specified format
        
        Args:
            locations_list: LocationsList object containing the locations
            file_path: Path to save the file
            format_type: Type of export (kml, csv, html, etc.)
        
        Returns:
            bool: True if export successful, False otherwise
        """
        if locations_list.count() == 0:
            logger.warning("No locations to export")
            return False
            
        try:
            # Call appropriate export method based on format
            if format_type.lower() == 'kml':
                return self.export_to_kml(locations_list, file_path)
            elif format_type.lower() == 'csv':
                return self.export_to_csv(locations_list, file_path)
            elif format_type.lower() == 'html':
                return self.export_to_html_map(locations_list, file_path)
            elif format_type.lower() == 'json':
                return self.export_to_json(locations_list, file_path)
            else:
                logger.error(f"Unsupported export format: {format_type}")
                return False
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    def export_to_kml(self, locations_list, file_path):
        """
        Export locations to KML format
        
        Args:
            locations_list: LocationsList object containing the locations
            file_path: Path to save the KML file
            
        Returns:
            bool: True if export successful, False otherwise
        """
        if not SIMPLEKML_AVAILABLE:
            logger.error("Cannot export to KML: simplekml module not installed")
            error_tracker.track_dependency_error(
                module_name="simplekml",
                feature_name="KML Export",
                error_message="Export attempted but simplekml is not available"
            )
            return False

        try:
            # Create KML object
            kml = simplekml.Kml()
            
            # Create folders for different sources
            source_folders = {}
            
            # Process locations by source
            for location in locations_list.locations:
                if not location.is_valid():
                    continue
                
                # Get or create folder for this source
                if location.source not in source_folders:
                    source_folders[location.source] = kml.newfolder(name=location.source)
                
                folder = source_folders[location.source]
                
                # Create placemark
                placemark = folder.newpoint(
                    name=location.get_context('title', f"Location from {location.source}"),
                    coords=[(location.longitude, location.latitude, location.get_context('altitude', 0))],
                    description=self._format_location_description(location)
                )
                
                # Add timestamp if available
                if location.datetime:
                    placemark.timestamp.when = location.datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
                
                # Style the placemark based on source
                self._style_kml_placemark(placemark, location.source)
            
            # Save KML file
            kml.save(file_path)
            
            logger.info(f"Exported {locations_list.count()} locations to KML file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"KML export failed: {e}")
            return False
            
    def _style_kml_placemark(self, placemark, source):
        """
        Apply styling to a KML placemark based on its source
        
        Args:
            placemark: simplekml placemark object
            source: Source name string
        """
        # Color mapping for different sources
        source_colors = {
            'twitter': 'blue',
            'facebook': 'blue',
            'instagram': 'purple',
            'flickr': 'pink',
            'foursquare': 'green',
            'google': 'yellow',
            'linkedin': 'blue',
            'pinterest': 'red',
            'snapchat': 'yellow',
            'tiktok': 'cyan'
        }
        
        # Find matching color
        color = 'red'  # Default color
        for key, value in source_colors.items():
            if key.lower() in source.lower():
                color = value
                break
                
        # Map color name to KML color code
        color_map = {
            'red': 'ff0000ff',
            'blue': 'ffff0000',
            'green': 'ff00ff00',
            'yellow': 'ff00ffff',
            'purple': 'ffff00ff',
            'pink': 'ffff6666',
            'cyan': 'ffffff00'
        }
        
        # Apply style
        placemark.style.iconstyle.color = color_map.get(color, 'ff0000ff')
        placemark.style.iconstyle.scale = 1.0
        
        # Use standard placemark icons
        placemark.style.iconstyle.icon.href = f"http://maps.google.com/mapfiles/kml/pushpin/{color[0]}.png"
    
    def export_to_csv(self, locations_list, file_path):
        """Export locations to CSV format"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Latitude', 'Longitude', 'Date/Time', 'Source', 'Title', 'Description', 'Accuracy']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                for location in locations_list.locations:
                    if not location.is_valid():
                        continue
                        
                    writer.writerow({
                        'Latitude': location.latitude,
                        'Longitude': location.longitude,
                        'Date/Time': location.datetime.isoformat() if location.datetime else '',
                        'Source': location.source,
                        'Title': location.get_context('title', ''),
                        'Description': location.get_context('description', ''),
                        'Accuracy': location.accuracy
                    })
            
            logger.info(f"Exported {locations_list.count()} locations to CSV file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            return False
    
    def export_to_html_map(self, locations_list, file_path):
        """Export locations to interactive HTML map"""
        try:
            # Get center coordinates for the map
            valid_locations = [loc for loc in locations_list.locations if loc.is_valid()]
            if not valid_locations:
                logger.error("No valid locations to export")
                return False
                
            # Calculate center point
            avg_lat = sum(loc.latitude for loc in valid_locations) / len(valid_locations)
            avg_lon = sum(loc.longitude for loc in valid_locations) / len(valid_locations)
            
            # Create map centered on average coordinates
            m = folium.Map(location=[avg_lat, avg_lon], zoom_start=10)
            
            # Create feature groups for different sources
            source_groups = {}
            
            # Add locations to map
            for location in valid_locations:
                # Get or create feature group for this source
                if location.source not in source_groups:
                    source_groups[location.source] = folium.FeatureGroup(name=location.source)
                
                # Create popup content
                popup_content = self._format_location_description(location, html=True)
                
                # Create marker
                folium.Marker(
                    [location.latitude, location.longitude],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=f"{location.source}: {location.get_context('title', 'Location')}"
                ).add_to(source_groups[location.source])
            
            # Add all feature groups to the map
            for group in source_groups.values():
                group.add_to(m)
            
            # Add layer control
            folium.LayerControl().add_to(m)
            
            # Save map to HTML file
            m.save(file_path)
            
            logger.info(f"Exported {len(valid_locations)} locations to HTML map: {file_path}")
            return True
        except Exception as e:
            logger.error(f"HTML map export failed: {e}")
            return False
    
    def export_to_json(self, locations_list, file_path):
        """Export locations to JSON format"""
        try:
            locations_data = []
            
            for location in locations_list.locations:
                if not location.is_valid():
                    continue
                    
                # Convert location to dictionary
                loc_dict = location.to_dict()
                locations_data.append(loc_dict)
            
            # Write to JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(locations_data, f, indent=4, default=self._json_serializer)
            
            logger.info(f"Exported {len(locations_data)} locations to JSON file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            return False
    
    def _json_serializer(self, obj):
        """Helper method to serialize objects to JSON"""
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    def _format_location_description(self, location, html=False):
        """Format location description for export"""
        if html:
            desc = "<div style='font-family: Arial, sans-serif;'>"
            
            # Source and time
            desc += f"<p><strong>Source:</strong> {location.source}</p>"
            if location.datetime:
                desc += f"<p><strong>Time:</strong> {location.datetime.strftime('%Y-%m-%d %H:%M:%S')}</p>"
            
            # Context information
            for key, value in location.context.items():
                if key not in ('title', 'description') and value:
                    desc += f"<p><strong>{key.capitalize()}:</strong> {value}</p>"
            
            # Main description if available
            if 'description' in location.context and location.context['description']:
                desc += f"<p>{location.context['description']}</p>"
                
            desc += "</div>"
            return desc
        else:
            # Plain text format for KML descriptions
            desc = f"Source: {location.source}\n"
            if location.datetime:
                desc += f"Time: {location.datetime.strftime('%Y-%m-%d %H:%M:%S')}\n"
                
            # Context information
            for key, value in location.context.items():
                if key not in ('title', 'description') and value:
                    desc += f"{key.capitalize()}: {value}\n"
            
            # Main description if available
            if 'description' in location.context and location.context['description']:
                desc += f"\n{location.context['description']}"
                
            return desc

"""
Export Utilities for CreepyAI

This module handles exporting data to various formats, supporting both
the PyQt5 and Tkinter UIs.
"""
import os
import csv
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import xml.dom.minidom

logger = logging.getLogger(__name__)

class ExportUtils:
    """
    Utilities for exporting data from CreepyAI
    """
    
    @staticmethod
    def export_csv(locations: List[Any], filename: str, filtering: bool = False) -> bool:
        """
        Export locations to CSV
        
        Args:
            locations: List of location objects or dictionaries
            filename: Output filename
            filtering: Whether to apply filtering
            
        Returns:
            bool: Success or failure
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as fileobj:
                writer = csv.writer(fileobj, quoting=csv.QUOTE_ALL)
                writer.writerow(('Timestamp', 'Latitude', 'Longitude', 'Location Name', 'Retrieved from', 'Context'))
                
                for loc in locations:
                    # Check if this is a Location object or dictionary
                    if hasattr(loc, 'latitude'):  # It's a Location object
                        if (filtering and loc.visible) or not filtering:
                            writer.writerow((
                                loc.datetime.strftime('%Y-%m-%d %H:%M:%S %z'), 
                                loc.latitude, 
                                loc.longitude, 
                                loc.shortName, 
                                loc.plugin, 
                                loc.context
                            ))
                    else:  # It's a dictionary
                        if (filtering and loc.get('visible', True)) or not filtering:
                            datetime_val = loc.get('datetime', datetime.now())
                            if isinstance(datetime_val, str):
                                datetime_str = datetime_val
                            else:
                                datetime_str = datetime_val.strftime('%Y-%m-%d %H:%M:%S %z')
                                
                            writer.writerow((
                                datetime_str,
                                loc.get('latitude', 0.0),
                                loc.get('longitude', 0.0),
                                loc.get('shortName', ''),
                                loc.get('plugin', ''),
                                loc.get('context', '')
                            ))
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def export_kml(locations: List[Any], filename: str, filtering: bool = False) -> bool:
        """
        Export locations to KML
        
        Args:
            locations: List of location objects or dictionaries
            filename: Output filename
            filtering: Whether to apply filtering
            
        Returns:
            bool: Success or failure
        """
        try:
            with open(filename, 'w', encoding='utf-8') as fileobj:
                kml = []
                kml.append('<?xml version="1.0" encoding="UTF-8"?>')
                kml.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
                kml.append('<Document>')
                kml.append(f'  <name>{os.path.basename(filename)}</name>')
                
                for loc in locations:
                    # Check if this is a Location object or dictionary
                    if hasattr(loc, 'latitude'):  # It's a Location object
                        if (filtering and loc.visible) or not filtering:
                            kml.append('  <Placemark>')
                            kml.append(f'  <name>{loc.datetime.strftime("%Y-%m-%d %H:%M:%S %z")}</name>')
                            kml.append(f'    <description>{ExportUtils.html_escape(loc.context)}</description>')
                            kml.append('    <Point>')
                            kml.append(f'       <coordinates>{loc.longitude}, {loc.latitude}, 0</coordinates>')
                            kml.append('    </Point>')
                            kml.append('  </Placemark>')
                    else:  # It's a dictionary
                        if (filtering and loc.get('visible', True)) or not filtering:
                            datetime_val = loc.get('datetime', datetime.now())
                            if isinstance(datetime_val, str):
                                datetime_str = datetime_val
                            else:
                                datetime_str = datetime_val.strftime('%Y-%m-%d %H:%M:%S %z')
                                
                            kml.append('  <Placemark>')
                            kml.append(f'  <name>{datetime_str}</name>')
                            kml.append(f'    <description>{ExportUtils.html_escape(loc.get("context", ""))}</description>')
                            kml.append('    <Point>')
                            kml.append(f'       <coordinates>{loc.get("longitude", 0.0)}, {loc.get("latitude", 0.0)}, 0</coordinates>')
                            kml.append('    </Point>')
                            kml.append('  </Placemark>')
                
                kml.append('</Document>')
                kml.append('</kml>')
                
                kml_string = '\n'.join(kml)
                fileobj.write(kml_string)
                
            return True
        except Exception as e:
            logger.error(f"Error exporting to KML: {e}")
            return False
    
    @staticmethod
    def export_json(locations: List[Any], filename: str, filtering: bool = False) -> bool:
        """
        Export locations to JSON
        
        Args:
            locations: List of location objects or dictionaries
            filename: Output filename
            filtering: Whether to apply filtering
            
        Returns:
            bool: Success or failure
        """
        try:
            export_data = []
            
            for loc in locations:
                # Check if this is a Location object or dictionary
                if hasattr(loc, 'latitude'):  # It's a Location object
                    if (filtering and loc.visible) or not filtering:
                        export_data.append({
                            'timestamp': loc.datetime.isoformat(),
                            'latitude': loc.latitude,
                            'longitude': loc.longitude,
                            'name': loc.shortName,
                            'source': loc.plugin,
                            'context': loc.context
                        })
                else:  # It's a dictionary
                    if (filtering and loc.get('visible', True)) or not filtering:
                        datetime_val = loc.get('datetime', datetime.now())
                        if isinstance(datetime_val, str):
                            datetime_str = datetime_val
                        else:
                            datetime_str = datetime_val.isoformat()
                            
                        export_data.append({
                            'timestamp': datetime_str,
                            'latitude': loc.get('latitude', 0.0),
                            'longitude': loc.get('longitude', 0.0),
                            'name': loc.get('shortName', ''),
                            'source': loc.get('plugin', ''),
                            'context': loc.get('context', '')
                        })
            
            with open(filename, 'w', encoding='utf-8') as fileobj:
                json.dump(export_data, fileobj, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False
    
    @staticmethod
    def html_escape(text: str) -> str:
        """
        Escape HTML special characters
        
        Args:
            text: Text to escape
            
        Returns:
            str: Escaped text
        """
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
