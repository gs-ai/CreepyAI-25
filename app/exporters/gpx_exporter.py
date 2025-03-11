"""
GPX Exporter for CreepyAI
Exports location data to GPX format
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import xml.dom.minidom
import xml.etree.ElementTree as ET

from app.models.location_data import Location

logger = logging.getLogger(__name__)

def export_gpx(locations: List[Location], output_path: str, 
              include_context: bool = True, pretty_print: bool = True) -> bool:
    """
    Export locations to a GPX file
    
    Args:
        locations: List of Location objects to export
        output_path: Path to save the GPX file
        include_context: Whether to include context information
        pretty_print: Whether to format the XML output
        
    Returns:
        True if export was successful, False otherwise
    """
    try:
        # Create the root GPX element with namespaces
        gpx = ET.Element('gpx', 
                        version="1.1", 
                        creator="CreepyAI", 
                        xmlns="http://www.topografix.com/GPX/1/1",
                        xmlns_xsi="http://www.w3.org/2001/XMLSchema-instance",
                        xsi_schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd")
        
        # Add metadata
        metadata = ET.SubElement(gpx, 'metadata')
        
        name = ET.SubElement(metadata, 'name')
        name.text = f"CreepyAI Export"
        
        desc = ET.SubElement(metadata, 'desc')
        desc.text = f"Location data exported from CreepyAI with {len(locations)} points"
        
        author = ET.SubElement(metadata, 'author')
        author_name = ET.SubElement(author, 'name')
        author_name.text = "CreepyAI"
        
        time = ET.SubElement(metadata, 'time')
        time.text = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Sort locations by timestamp if available
        sorted_locations = sorted(
            locations,
            key=lambda loc: loc.timestamp if hasattr(loc, 'timestamp') and loc.timestamp else datetime.min
        )
        
        # Group locations by source
        source_locations = {}
        for location in sorted_locations:
            source = location.source if hasattr(location, 'source') and location.source else "Unknown"
            if source not in source_locations:
                source_locations[source] = []
            source_locations[source].append(location)
        
        # Add individual waypoints for each location
        for location in sorted_locations:
            wpt = ET.SubElement(gpx, 'wpt',
                               lat=str(location.latitude),
                               lon=str(location.longitude))
            
            # Add name based on source and timestamp
            wpt_name = ET.SubElement(wpt, 'name')
            name_text = location.source if hasattr(location, 'source') and location.source else "Unknown"
            
            # Add timestamp to name if available
            if hasattr(location, 'timestamp') and location.timestamp and isinstance(location.timestamp, datetime):
                name_text += f" - {location.timestamp.strftime('%Y-%m-%d %H:%M')}"
            
            wpt_name.text = name_text
            
            # Add timestamp if available
            if hasattr(location, 'timestamp') and location.timestamp and isinstance(location.timestamp, datetime):
                time_elem = ET.SubElement(wpt, 'time')
                time_elem.text = location.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Add source as symbol
            symbol = ET.SubElement(wpt, 'sym')
            symbol.text = location.source if hasattr(location, 'source') and location.source else "Waypoint"
            
            # Add elevation if available
            if hasattr(location, 'metadata') and hasattr(location.metadata, 'altitude') and location.metadata.altitude is not None:
                ele = ET.SubElement(wpt, 'ele')
                ele.text = str(location.metadata.altitude)
            
            # Add context as description if requested
            if include_context and hasattr(location, 'context') and location.context:
                desc_elem = ET.SubElement(wpt, 'desc')
                desc_elem.text = location.context
                
            # Add address as comment if available
            if hasattr(location, 'address') and location.address:
                cmt = ET.SubElement(wpt, 'cmt')
                cmt.text = location.address
        
        # Create track segments by source
        trk = ET.SubElement(gpx, 'trk')
        trk_name = ET.SubElement(trk, 'name')
        trk_name.text = "CreepyAI Track"
        
        # Create track segments for each source
        for source, locs in source_locations.items():
            # Only create a track segment if there are multiple locations from the same source
            if len(locs) > 1:
                trkseg = ET.SubElement(trk, 'trkseg')
                
                # Sort locations by timestamp
                sorted_source_locs = sorted(
                    locs,
                    key=lambda loc: loc.timestamp if hasattr(loc, 'timestamp') and loc.timestamp else datetime.min
                )
                
                # Add track points
                for location in sorted_source_locs:
                    trkpt = ET.SubElement(trkseg, 'trkpt',
                                        lat=str(location.latitude),
                                        lon=str(location.longitude))
                    
                    # Add timestamp if available
                    if hasattr(location, 'timestamp') and location.timestamp and isinstance(location.timestamp, datetime):
                        time_elem = ET.SubElement(trkpt, 'time')
                        time_elem.text = location.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
                    
                    # Add elevation if available
                    if hasattr(location, 'metadata') and hasattr(location.metadata, 'altitude') and location.metadata.altitude is not None:
                        ele = ET.SubElement(trkpt, 'ele')
                        ele.text = str(location.metadata.altitude)
        
        # Convert to string
        xml_str = ET.tostring(gpx, encoding='utf-8', method='xml')
        
        # Pretty print if requested
        if pretty_print:
            dom = xml.dom.minidom.parseString(xml_str)
            pretty_xml = dom.toprettyxml(indent='  ')
            
            # Remove the xml declaration (as it's added by toprettyxml)
            pretty_xml_lines = pretty_xml.splitlines()[1:]
            clean_pretty_xml = "\n".join(pretty_xml_lines)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(clean_pretty_xml)
        else:
            with open(output_path, 'wb') as f:
                f.write(xml_str)
        
        logger.info(f"GPX export completed successfully to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting to GPX: {e}", exc_info=True)
        return False
