#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Location Exporter for CreepyAI
Exports location data to various formats
"""

import os
import sys
import argparse
import logging
import json
import csv
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent directory to path so we can import plugins
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(SCRIPT_DIR)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import required modules
try:
    from plugins.base_plugin import LocationPoint
except ImportError:
    # If we can't import directly, define a minimal version
    class LocationPoint:
        def __init__(self, latitude, longitude, timestamp=None, source="", context="", accuracy=0.0):
            self.latitude = latitude
            self.longitude = longitude
            self.timestamp = timestamp if timestamp else datetime.now()
            self.source = source
            self.context = context
            self.accuracy = accuracy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("location_exporter")

def get_locations_from_db(db_path: str, plugin_name: Optional[str] = None, 
                         target_id: Optional[str] = None) -> List[LocationPoint]:
    """
    Get locations from the CreepyAI database
    
    Args:
        db_path: Path to the database file
        plugin_name: Optional plugin name filter
        target_id: Optional target ID filter
        
    Returns:
        List of LocationPoint objects
    """
    locations = []
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query based on filters
        query = 'SELECT * FROM locations WHERE 1=1'
        params = []
        
        if plugin_name:
            query += ' AND plugin_name = ?'
            params.append(plugin_name)
            
        if target_id:
            query += ' AND target_id = ?'
            params.append(target_id)
            
        # Execute query
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert rows to LocationPoint objects
        for row in rows:
            try:
                timestamp = datetime.fromisoformat(row['timestamp']) if row['timestamp'] else None
            except ValueError:
                timestamp = None
                
            loc = LocationPoint(
                latitude=row['latitude'],
                longitude=row['longitude'],
                timestamp=timestamp,
                source=row['source'],
                context=row['context'],
                accuracy=row['accuracy'] if row['accuracy'] is not None else 0.0
            )
            locations.append(loc)
            
        conn.close()
        return locations
        
    except Exception as e:
        logger.error(f"Error getting locations from database: {e}")
        return []

def export_to_json(locations: List[LocationPoint], output_file: str) -> bool:
    """
    Export locations to JSON format
    
    Args:
        locations: List of LocationPoint objects
        output_file: Path to the output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert locations to dictionaries
        location_dicts = []
        for loc in locations:
            location_dict = {
                'latitude': loc.latitude,
                'longitude': loc.longitude,
                'timestamp': loc.timestamp.isoformat() if loc.timestamp else None,
                'source': loc.source,
                'context': loc.context,
                'accuracy': loc.accuracy
            }
            location_dicts.append(location_dict)
            
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(location_dicts, f, indent=2)
            
        logger.info(f"Exported {len(locations)} locations to JSON file: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        return False

def export_to_csv(locations: List[LocationPoint], output_file: str) -> bool:
    """
    Export locations to CSV format
    
    Args:
        locations: List of LocationPoint objects
        output_file: Path to the output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Define CSV columns
        fieldnames = ['latitude', 'longitude', 'timestamp', 'source', 'context', 'accuracy']
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for loc in locations:
                writer.writerow({
                    'latitude': loc.latitude,
                    'longitude': loc.longitude,
                    'timestamp': loc.timestamp.isoformat() if loc.timestamp else '',
                    'source': loc.source,
                    'context': loc.context,
                    'accuracy': loc.accuracy
                })
                
        logger.info(f"Exported {len(locations)} locations to CSV file: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return False

def export_to_kml(locations: List[LocationPoint], output_file: str) -> bool:
    """
    Export locations to KML format for Google Earth/Maps
    
    Args:
        locations: List of LocationPoint objects
        output_file: Path to the output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create KML document
        kml = ['<?xml version="1.0" encoding="UTF-8"?>']
        kml.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
        kml.append('<Document>')
        kml.append(f'<name>CreepyAI Locations ({len(locations)})</name>')
        kml.append('<description>Exported from CreepyAI</description>')
        
        # Define styles
        kml.append('<Style id="creepyStyle">')
        kml.append('  <IconStyle>')
        kml.append('    <Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href></Icon>')
        kml.append('  </IconStyle>')
        kml.append('</Style>')
        
        # Add placemarks for each location
        for i, loc in enumerate(locations):
            kml.append('<Placemark>')
            kml.append(f'  <name>Location {i+1}</name>')
            
            # Add description with details
            description = f"Time: {loc.timestamp.strftime('%Y-%m-%d %H:%M:%S') if loc.timestamp else 'Unknown'}<br/>"
            description += f"Source: {loc.source}<br/>"
            if loc.context:
                description += f"Context: {loc.context}<br/>"
            if loc.accuracy:
                description += f"Accuracy: {loc.accuracy} meters<br/>"
                
            kml.append(f'  <description><![CDATA[{description}]]></description>')
            kml.append('  <styleUrl>#creepyStyle</styleUrl>')
            kml.append('  <Point>')
            kml.append(f'    <coordinates>{loc.longitude},{loc.latitude},0</coordinates>')
            kml.append('  </Point>')
            kml.append('</Placemark>')
        
        # Close KML document
        kml.append('</Document>')
        kml.append('</kml>')
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(kml))
            
        logger.info(f"Exported {len(locations)} locations to KML file: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting to KML: {e}")
        return False

def export_to_geojson(locations: List[LocationPoint], output_file: str) -> bool:
    """
    Export locations to GeoJSON format
    
    Args:
        locations: List of LocationPoint objects
        output_file: Path to the output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create GeoJSON structure
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        
        # Add features for each location
        for loc in locations:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [loc.longitude, loc.latitude]
                },
                "properties": {
                    "timestamp": loc.timestamp.isoformat() if loc.timestamp else None,
                    "source": loc.source,
                    "context": loc.context,
                    "accuracy": loc.accuracy
                }
            }
            geojson["features"].append(feature)
            
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2)
            
        logger.info(f"Exported {len(locations)} locations to GeoJSON file: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting to GeoJSON: {e}")
        return False

def export_to_gpx(locations: List[LocationPoint], output_file: str) -> bool:
    """
    Export locations to GPX format
    
    Args:
        locations: List of LocationPoint objects
        output_file: Path to the output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create GPX document
        gpx = ['<?xml version="1.0" encoding="UTF-8"?>']
        gpx.append('<gpx version="1.1" creator="CreepyAI" xmlns="http://www.topografix.com/GPX/1/1">')
        
        # Add metadata
        gpx.append('  <metadata>')
        gpx.append(f'    <name>CreepyAI Export ({len(locations)} locations)</name>')
        gpx.append(f'    <time>{datetime.now().isoformat()}</time>')
        gpx.append('  </metadata>')
        
        # Add waypoints for each location
        for loc in locations:
            gpx.append(f'  <wpt lat="{loc.latitude}" lon="{loc.longitude}">')
            
            # Add optional elements
            if loc.timestamp:
                gpx.append(f'    <time>{loc.timestamp.isoformat()}</time>')
                
            name = loc.source or "Waypoint"
            gpx.append(f'    <name>{name}</name>')
            
            if loc.context:
                gpx.append(f'    <desc>{loc.context}</desc>')
                
            gpx.append('  </wpt>')
        
        # Close GPX document
        gpx.append('</gpx>')
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(gpx))
            
        logger.info(f"Exported {len(locations)} locations to GPX file: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting to GPX: {e}")
        return False

def main():
    """Main function for the location exporter"""
    parser = argparse.ArgumentParser(description="Export location data from CreepyAI")
    parser.add_argument("-d", "--database", help="Path to the CreepyAI database", required=True)
    parser.add_argument("-o", "--output", help="Output file path", required=True)
    parser.add_argument("-f", "--format", choices=["json", "csv", "kml", "geojson", "gpx"], default="json",
                       help="Output format (default: json)")
    parser.add_argument("-p", "--plugin", help="Filter by plugin name")
    parser.add_argument("-t", "--target", help="Filter by target ID")
    args = parser.parse_args()
    
    # Get locations from database
    logger.info(f"Getting locations from database: {args.database}")
    locations = get_locations_from_db(args.database, args.plugin, args.target)
    
    if not locations:
        logger.warning("No locations found matching the criteria")
        return 1
        
    logger.info(f"Found {len(locations)} locations")
    
    # Export to the specified format
    if args.format == "json":
        success = export_to_json(locations, args.output)
    elif args.format == "csv":
        success = export_to_csv(locations, args.output)
    elif args.format == "kml":
        success = export_to_kml(locations, args.output)
    elif args.format == "geojson":
        success = export_to_geojson(locations, args.output)
    elif args.format == "gpx":
        success = export_to_gpx(locations, args.output)
    else:
        logger.error(f"Unsupported format: {args.format}")
        return 1
        
    if success:
        logger.info(f"Successfully exported locations to {args.output}")
        return 0
    else:
        logger.error(f"Failed to export locations")
        return 1

if __name__ == "__main__":
    sys.exit(main())