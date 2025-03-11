"""
Data Import/Export Pipeline for CreepyAI
Handles data import and export operations
"""

import os
import logging
from typing import List, Dict, Any, Optional

from app.models.location_data import LocationDataModel, Location
from app.exporters.gpx_exporter import export_gpx
from app.exporters.kml_exporter import export_kml

logger = logging.getLogger(__name__)

class DataPipeline:
    """Manages data import and export operations"""
    
    def __init__(self, location_model: LocationDataModel):
        self.location_model = location_model
    
    def import_data(self, file_path: str, format_type: str) -> bool:
        """Import data from a file"""
        try:
            if format_type.lower() == 'json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for loc_data in data:
                    location = Location.from_dict(loc_data)
                    self.location_model.add_location(location)
                return True
            elif format_type.lower() == 'csv':
                import csv
                with open(file_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        location = Location(
                            latitude=float(row['latitude']),
                            longitude=float(row['longitude']),
                            timestamp=datetime.fromisoformat(row['timestamp']),
                            source=row['source'],
                            context=row['context']
                        )
                        self.location_model.add_location(location)
                return True
            else:
                logger.error(f"Unsupported import format: {format_type}")
                return False
        except Exception as e:
            logger.error(f"Error importing data from {file_path}: {e}")
            return False
    
    def export_data(self, file_path: str, format_type: str) -> bool:
        """Export data to a file"""
        try:
            if format_type.lower() == 'json':
                locations = self.location_model.get_all_locations()
                data = [loc.to_dict() for loc in locations]
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                return True
            elif format_type.lower() == 'csv':
                import csv
                locations = self.location_model.get_all_locations()
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['id', 'latitude', 'longitude', 'timestamp', 'source', 'context', 'address'])
                    for loc in locations:
                        writer.writerow([
                            loc.id, loc.latitude, loc.longitude,
                            loc.timestamp.isoformat() if loc.timestamp else '',
                            loc.source, loc.context, loc.address
                        ])
                return True
            elif format_type.lower() == 'kml':
                return export_kml(self.location_model.get_all_locations(), file_path)
            elif format_type.lower() == 'gpx':
                return export_gpx(self.location_model.get_all_locations(), file_path)
            else:
                logger.error(f"Unsupported export format: {format_type}")
                return False
        except Exception as e:
            logger.error(f"Error exporting data to {file_path}: {e}")
            return False
