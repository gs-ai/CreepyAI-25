"""
KML Exporter for CreepyAI
Exports location data to KML format
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import xml.dom.minidom
import xml.etree.ElementTree as ET

from app.models.location_data import Location

logger = logging.getLogger(__name__)

def export_kml(locations: List[Location], output_path: str, 
              include_context: bool = True, pretty_print: bool = True) -> bool:
    """
    Export locations to a KML file
    
    Args:
        locations: List of Location objects to export
        output_path: Path to save the KML file
        include_context: Whether to include context information
        pretty_print: Whether to format the XML output
        
    Returns:
        True if export was successful, False otherwise
    """
    try:
        # Create the root KML element
        kml = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        
        # Create document
        document = ET.SubElement(kml, 'Document')
        
        # Add document name
        doc_name = ET.SubElement(document, 'name')
        doc_name.text = f"CreepyAI Export - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Add document description
        doc_desc = ET.SubElement(document, 'description')
        doc_desc.text = f"Location data exported from CreepyAI with {len(locations)} points"
        
        # Define styles for different sources
        styles = {}
        colors = {
            "Facebook": "7F0000FF", # Red
            "Instagram": "7F00FFFF", # Yellow
            "Twitter": "7F00FF00",  # Green
            "LinkedIn": "7FFF0000",  # Blue
            "Snapchat": "7FFF00FF",  # Purple
            "TikTok": "7F00FFFF",   # Yellow
            "Default": "7F0000FF"    # Red
        }
        
        # Create styles
        for source, color in colors.items():
            style = ET.SubElement(document, 'Style', id=f"{source.lower()}-style")
            
            # Icon style
            icon_style = ET.SubElement(style, 'IconStyle')
            icon_color = ET.SubElement(icon_style, 'color')
            icon_color.text = color
            icon_scale = ET.SubElement(icon_style, 'scale')
            icon_scale.text = "1.0"
            
            icon = ET.SubElement(icon_style, 'Icon')
            href = ET.SubElement(icon, 'href')
            href.text = "http://maps.google.com/mapfiles/kml/paddle/red-circle.png"
            
            # Label style
            label_style = ET.SubElement(style, 'LabelStyle')
            label_color = ET.SubElement(label_style, 'color')
            label_color.text = "FFFFFFFF"  # White
            label_scale = ET.SubElement(label_style, 'scale')
            label_scale.text = "0.8"
            
            styles[source] = f"{source.lower()}-style"
        
        # Add each location as a placemark
        for location in locations:
            placemark = ET.SubElement(document, 'Placemark')
            
            # Add name
            name = ET.SubElement(placemark, 'name')
            source_name = location.source or "Unknown Source"
            if hasattr(location, 'timestamp') and location.timestamp:
                if isinstance(location.timestamp, datetime):
                    name.text = f"{source_name} - {location.timestamp.strftime('%Y-%m-%d %H:%M')}"
                else:
                    name.text = f"{source_name} - {str(location.timestamp)}"
            else:
                name.text = source_name
            
            # Add description
            description = ET.SubElement(placemark, 'description')
            desc_text = ""
            
            if include_context and hasattr(location, 'context') and location.context:
                desc_text += f"<p>{location.context}</p>"
            
            if hasattr(location, 'address') and location.address:
                desc_text += f"<p>Address: {location.address}</p>"
            
            # Add any other metadata
            if hasattr(location, 'metadata') and location.metadata:
                for key, value in location.metadata.__dict__.items():
                    if value and key not in ['properties', 'tags'] and not key.startswith('_'):
                        desc_text += f"<p>{key.replace('_', ' ').title()}: {value}</p>"
            
            # Add tags if available
            if hasattr(location, 'metadata') and hasattr(location.metadata, 'tags') and location.metadata.tags:
                desc_text += f"<p>Tags: {', '.join(location.metadata.tags)}</p>"
            
            description.text = f"<![CDATA[{desc_text}]]>" if desc_text else ""
            
            # Add timestamp
            if hasattr(location, 'timestamp') and location.timestamp and isinstance(location.timestamp, datetime):
                timestamp = ET.SubElement(placemark, 'TimeStamp')
                when = ET.SubElement(timestamp, 'when')
                when.text = location.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Add style reference based on source
            source_key = location.source if location.source in styles else "Default"
            style_url = ET.SubElement(placemark, 'styleUrl')
            style_url.text = f"#{styles[source_key]}"
            
            # Add point geometry
            point = ET.SubElement(placemark, 'Point')
            coordinates = ET.SubElement(point, 'coordinates')
            coordinates.text = f"{location.longitude},{location.latitude},0"
        
        # Convert to string
        tree = ET.ElementTree(kml)
        xml_str = ET.tostring(kml, encoding='utf-8', method='xml')
        
        # Pretty print if requested
        if pretty_print:
            dom = xml.dom.minidom.parseString(xml_str)
            pretty_xml = dom.toprettyxml(indent='  ')
            
            # The xml.dom.minidom adds an XML declaration, which we want to keep
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
        else:
            with open(output_path, 'wb') as f:
                f.write(xml_str)
        
        logger.info(f"KML export completed successfully to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting to KML: {e}", exc_info=True)
        return False
