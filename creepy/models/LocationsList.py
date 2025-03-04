<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import datetime
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import Qt

from creepy.models.Location import Location

logger = logging.getLogger('CreepyAI.LocationsList')

class LocationsList(QObject):
    """Class for managing a list of locations"""
    
    # Signals
    locations_changed = pyqtSignal()
    
    def __init__(self):
        super(LocationsList, self).__init__()
        self.locations = []
        self.filtered_locations = []
        self.filter_active = False
        self.metadata = {
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat(),
            'stats': {}
        }
    
    def add_location(self, location):
        """Add a location to the list"""
        if not isinstance(location, Location):
            logger.warning("Attempted to add a non-Location object to LocationsList")
            return False
        
        # Check if location already exists (by exact coordinates and time)
        for existing_loc in self.locations:
            if (existing_loc.latitude == location.latitude and
                existing_loc.longitude == location.longitude and
                existing_loc.datetime == location.datetime):
                return False  # Skip duplicate
        
        self.locations.append(location)
        self.locations_changed.emit()
        
        # Update metadata
        self.metadata['updated_at'] = datetime.datetime.now().isoformat()
        self._update_stats()
        
        # If filter is active, also check if it should be added to filtered list
        if self.filter_active and self._location_passes_filter(location):
            self.filtered_locations.append(location)
        
        return True
    
    def remove_location(self, location):
        """Remove a location from the list"""
        if location in self.locations:
            self.locations.remove(location)
            
            if location in self.filtered_locations:
                self.filtered_locations.remove(location)
                
            # Update metadata
            self.metadata['updated_at'] = datetime.datetime.now().isoformat()
            self._update_stats()
            
            self.locations_changed.emit()
            return True
        return False
    
    def count(self):
        """Return the number of locations in the list"""
        if self.filter_active:
            return len(self.filtered_locations)
        return len(self.locations)
    
    def clear(self):
        """Clear all locations from the list"""
        self.locations.clear()
        self.filtered_locations.clear()
        self.filter_active = False
        self.metadata['updated_at'] = datetime.datetime.now().isoformat()
        self._update_stats()
        self.locations_changed.emit()
    
    def get_date_range(self):
        """Get the date range of the locations"""
        if not self.locations:
            return None, None
            
        dates = [loc.datetime for loc in self.locations if loc.datetime]
        if not dates:
            return None, None
            
        return min(dates), max(dates)
    
    def filter_by_date_range(self, start_date, end_date):
        """Return locations within a date range"""
        filtered = []
        for location in self.locations:
            if location.datetime and start_date <= location.datetime <= end_date:
                filtered.append(location)
        return filtered
    
    def filter_by_distance(self, latitude, longitude, distance_km):
        """Return locations within a certain distance of a point"""
        from geopy.distance import geodesic
        
        filtered = []
        point = (latitude, longitude)
        
        for location in self.locations:
            loc_point = (location.latitude, location.longitude)
            distance = geodesic(point, loc_point).kilometers
            
            if distance <= distance_km:
                filtered.append(location)
        
        return filtered
    
    def save_to_file(self, filepath):
        """Save locations to a JSON file"""
        locations_data = []
        
        for location in self.locations:
            loc_data = {
                'latitude': location.latitude,
                'longitude': location.longitude,
                'datetime': location.datetime.isoformat() if location.datetime else None,
                'context': location.context,
                'source': location.source,
                'accuracy': location.accuracy
            }
            locations_data.append(loc_data)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(locations_data, f, indent=4)
            logger.info(f"Saved {len(locations_data)} locations to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save locations: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath):
        """Load locations from a JSON file"""
        locations_list = cls()
        
        try:
            with open(filepath, 'r') as f:
                locations_data = json.load(f)
            
            for loc_data in locations_data:
                location = Location()
                location.latitude = loc_data.get('latitude')
                location.longitude = loc_data.get('longitude')
                
                # Parse datetime if available
                dt_str = loc_data.get('datetime')
                if dt_str:
                    try:
                        location.datetime = datetime.datetime.fromisoformat(dt_str)
                    except ValueError:
                        location.datetime = None
                
                location.context = loc_data.get('context', {})
                location.source = loc_data.get('source', '')
                location.accuracy = loc_data.get('accuracy', 0)
                
                locations_list.add_location(location)
            
            logger.info(f"Loaded {locations_list.count()} locations from {filepath}")
            return locations_list
        except Exception as e:
            logger.error(f"Failed to load locations: {e}")
            return cls()
    
    def filter_by_date(self, start_date=None, end_date=None):
        """
        Filter locations by date.
        
        Args:
            start_date: Start date for filter (datetime object)
            end_date: End date for filter (datetime object)
            
        Returns:
            int: Number of locations that match the filter
        """
        self.filtered_locations = []
        
        if not start_date and not end_date:
            self.filter_active = False
            return len(self.locations)
            
        for location in self.locations:
            if location.datetime:
                if start_date and end_date:
                    if start_date <= location.datetime <= end_date:
                        self.filtered_locations.append(location)
                elif start_date:
                    if location.datetime >= start_date:
                        self.filtered_locations.append(location)
                elif end_date:
                    if location.datetime <= end_date:
                        self.filtered_locations.append(location)
                        
        self.filter_active = True
        return len(self.filtered_locations)
    
    def filter_by_source(self, sources):
        """
        Filter locations by source.
        
        Args:
            sources: List of source strings to include
            
        Returns:
            int: Number of locations that match the filter
        """
        if not sources:
            self.filter_active = False
            return len(self.locations)
            
        self.filtered_locations = []
        
        for location in self.locations:
            if location.source:
                for source in sources:
                    if source.lower() in location.source.lower():
                        self.filtered_locations.append(location)
                        break
                        
        self.filter_active = True
        return len(self.filtered_locations)
    
    def filter_by_distance(self, lat, lon, max_distance_km):
        """
        Filter locations by distance from a point.
        
        Args:
            lat: Latitude of center point
            lon: Longitude of center point
            max_distance_km: Maximum distance in kilometers
            
        Returns:
            int: Number of locations that match the filter
        """
        if not max_distance_km:
            self.filter_active = False
            return len(self.locations)
            
        self.filtered_locations = []
        
        # Create reference location for distance calculation
        ref_location = Location(lat, lon)
        
        for location in self.locations:
            distance = location.get_distance(ref_location)
            if distance <= max_distance_km:
                self.filtered_locations.append(location)
                
        self.filter_active = True
        return len(self.filtered_locations)
    
    def clear_filter(self):
        """Clear any active filters."""
        self.filter_active = False
        self.filtered_locations = []
        return len(self.locations)
    
    def get_locations(self):
        """
        Get current locations list (filtered or all).
        
        Returns:
            list: Current list of locations (filtered or all)
        """
        if self.filter_active:
            return self.filtered_locations
        return self.locations
    
    def to_dict_list(self):
        """
        Convert locations to a list of dictionaries.
        
        Returns:
            list: List of location dictionaries
        """
        locations = self.get_locations()
        return [loc.to_dict() for loc in locations]
    
    def to_json(self, file_path=None):
        """
        Convert to JSON string or save to file.
        
        Args:
            file_path: Optional file path to save JSON data
            
        Returns:
            str: JSON string if file_path is None
        """
        data = {
            'metadata': self.metadata,
            'locations': self.to_dict_list()
        }
        
        json_data = json.dumps(data, indent=2)
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(json_data)
            except Exception as e:
                logger.error(f"Error saving locations to JSON file: {str(e)}")
                
        return json_data
    
    @classmethod
    def from_json(cls, json_data=None, file_path=None):
        """
        Create LocationsList from JSON string or file.
        
        Args:
            json_data: JSON string
            file_path: Path to JSON file
            
        Returns:
            LocationsList: New instance with loaded data
        """
        if not json_data and not file_path:
            logger.error("Either json_data or file_path must be provided")
            return None
            
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = f.read()
            except Exception as e:
                logger.error(f"Error reading locations from JSON file: {str(e)}")
                return None
                
        try:
            data = json.loads(json_data)
            locations_list = cls()
            
            # Load metadata
            if 'metadata' in data:
                locations_list.metadata = data['metadata']
                
            # Load locations
            if 'locations' in data:
                for loc_dict in data['locations']:
                    location = Location.from_dict(loc_dict)
                    locations_list.add_location(location)
                    
            return locations_list
            
        except Exception as e:
            logger.error(f"Error parsing locations JSON data: {str(e)}")
            return None
    
    def get_center_point(self):
        """
        Calculate the center point of all locations.
        
        Returns:
            tuple: (latitude, longitude) of center point
        """
        if not self.locations:
            return 0, 0
            
        valid_locations = [loc for loc in self.locations if loc.is_valid]
        if not valid_locations:
            return 0, 0
            
        avg_lat = sum(loc.latitude for loc in valid_locations) / len(valid_locations)
        avg_lon = sum(loc.longitude for loc in valid_locations) / len(valid_locations)
        
        return avg_lat, avg_lon
    
    def _update_stats(self):
        """Update metadata statistics."""
        self.metadata['stats'] = {
            'total_locations': len(self.locations),
            'unique_sources': len(set(loc.source for loc in self.locations if loc.source)),
            'date_range': self.get_date_range(),
            'center_point': self.get_center_point()
        }
    
    def _location_passes_filter(self, location):
        """Check if a location passes the current filter."""
        # This is a placeholder since the actual filter logic would depend on what filter is active
        # In a real implementation, we would store filter parameters and check against them
        return True
=======
#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import QAbstractTableModel
from PyQt4.QtCore import Qt, QVariant
>>>>>>> gs-ai-patch-1

class LocationsTableModel(QAbstractTableModel):
    def __init__(self, locations, parent=None):
        self.locations = locations
        super(LocationsTableModel,self).__init__()
        
<<<<<<< HEAD
=======
        
>>>>>>> gs-ai-patch-1
    def rowCount(self, index):
        return len(self.locations)
    
    def columnCount(self, index):
        return 2
    
<<<<<<< HEAD
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignLeft|Qt.AlignVCenter)
            return int(Qt.AlignRight|Qt.AlignVCenter)
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if section == 0:
                return 'Date'
            elif section == 1:
                return 'Location'
        return int(section + 1)
    
    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self.locations)):
            return None
=======
        
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if section == 0:
                return QVariant('Date')
            elif section == 1:
                return QVariant('Location')
        return QVariant(int(section + 1))
    
    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self.locations)):
            return QVariant()
>>>>>>> gs-ai-patch-1
        location = self.locations[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            if column == 0:
<<<<<<< HEAD
                return location.datetime.isoformat()
            if column == 1:
                return location.shortName
        return None
=======
                return QVariant(location.datetime.isoformat())
            if column == 1:
                return QVariant(location.shortName)
        return QVariant()
>>>>>>> gs-ai-patch-1
    
    def getLocationFromIndex(self, index):
        try:
            if index.isValid() and (0 <= index.row() < len(self.locations)):
                return self.locations[index.row()]
        except Exception as e:
            print(f"Error getting location from index: {e}")
        return None
        
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable