#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import datetime
import logging
from typing import List, Dict, Optional
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant

logger = logging.getLogger(__name__)

class Location:
    """Simple location data class for compatibility"""
    def __init__(self):
        self.id = None
        self.latitude = 0.0
        self.longitude = 0.0
        self.datetime = datetime.datetime.now()
        self.plugin = ""
        self.shortName = ""
        self.context = ""
        self.infowindow = ""
        self.visible = True
    
    def updateId(self):
        """Update the location ID based on its properties"""
        import hashlib
        string_to_hash = f"{self.latitude}{self.longitude}{self.datetime}{self.plugin}"
        self.id = hashlib.md5(string_to_hash.encode()).hexdigest()

class LocationsTableModel(QAbstractTableModel):
    """
    Table model for displaying a list of locations.
    """

    def __init__(self, locations_list, parent=None):
        super(LocationsTableModel, self).__init__(parent)
        self.locations = locations_list
        self.headers = ['Date', 'Plugin', 'Location']

    def rowCount(self, parent=None):
        return len(self.locations)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.locations)):
            return QVariant()

        location = self.locations[index.row()]
        column = index.column()

        if role == Qt.DisplayRole:
            if column == 0:  # Date/time
                return location.datetime.strftime("%Y-%m-%d %H:%M:%S")
            elif column == 1:  # Plugin
                return location.plugin
            elif column == 2:  # Location name/description
                return location.shortName
        
        elif role == Qt.ToolTipRole:
            # Show more detailed information in a tooltip
            if column == 0:
                return location.datetime.strftime("%Y-%m-%d %H:%M:%S %z")
            elif column == 1:
                return f"Source: {location.plugin}"
            elif column == 2:
                return location.context or location.shortName
        
        elif role == Qt.UserRole:
            # For custom sorting/filtering
            if column == 0:
                return location.datetime
            elif column == 1:
                return location.plugin
            elif column == 2:
                return location.shortName

        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return QVariant()
    
    def sort(self, column, order):
        """Sort table by given column and order."""
        self.beginResetModel()
        if column == 0:
            self.locations.sort(key=lambda x: x.datetime, reverse=(order == Qt.DescendingOrder))
        elif column == 1:
            self.locations.sort(key=lambda x: x.plugin, reverse=(order == Qt.DescendingOrder))
        elif column == 2:
            self.locations.sort(key=lambda x: x.shortName, reverse=(order == Qt.DescendingOrder))
        self.endResetModel()
        
    def addLocation(self, location):
        """Add a location to the model."""
        self.beginInsertRows(QModelIndex(), len(self.locations), len(self.locations))
        self.locations.append(location)
        self.endInsertRows()
        
    def clear(self):
        """Clear all locations from the model."""
        self.beginResetModel()
        self.locations = []
        self.endResetModel()
        
    def getLocation(self, row):
        """Get location at specified row."""
        if 0 <= row < len(self.locations):
            return self.locations[row]
        return None

class LocationsList:
    """Class for managing a list of locations"""
    
    def __init__(self):
        """Initialize an empty locations list"""
        self._locations = []
    
    def add_location(self, location) -> bool:
        """Add a location to the list if it doesn't already exist"""
        # Make sure location has an ID
        if not hasattr(location, 'id') or not location.id:
            if hasattr(location, 'updateId'):
                location.updateId()
            else:
                # Generate a basic ID
                import hashlib
                string_to_hash = f"{location.latitude}{location.longitude}{location.datetime}{location.plugin}"
                location.id = hashlib.md5(string_to_hash.encode()).hexdigest()
        
        # Check for duplicates
        if location.id in [l.id for l in self._locations]:
            return False
        
        self._locations.append(location)
        return True
    
    def remove_location(self, location_id) -> bool:
        """Remove a location by ID"""
        for i, loc in enumerate(self._locations):
            if loc.id == location_id:
                self._locations.pop(i)
                return True
        return False
    
    def get_location(self, location_id):
        """Get a location by ID"""
        for loc in self._locations:
            if loc.id == location_id:
                return loc
        return None
    
    def count(self) -> int:
        """Get the number of locations"""
        return len(self._locations)
    
    def to_json(self, file_path=None):
        """Export locations to JSON"""
        data = []
        for loc in self._locations:
            # Convert location to dict
            loc_dict = {
                "id": loc.id,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "datetime": loc.datetime.isoformat() if hasattr(loc.datetime, 'isoformat') else str(loc.datetime),
                "plugin": loc.plugin,
                "shortName": loc.shortName,
                "context": loc.context,
                "infowindow": loc.infowindow,
                "visible": loc.visible
            }
            data.append(loc_dict)
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        
        return data
    
    @classmethod
    def from_json(cls, file_path=None, json_data=None):
        """Create a locations list from JSON"""
        locations_list = cls()
        
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif json_data:
            data = json_data
        else:
            return locations_list
        
        for loc_dict in data:
            loc = Location()
            loc.id = loc_dict.get("id", "")
            loc.latitude = loc_dict.get("latitude", 0.0)
            loc.longitude = loc_dict.get("longitude", 0.0)
            
            # Parse datetime
            dt_str = loc_dict.get("datetime", "")
            if dt_str:
                try:
                    loc.datetime = datetime.datetime.fromisoformat(dt_str)
                except ValueError:
                    loc.datetime = datetime.datetime.now()
            else:
                loc.datetime = datetime.datetime.now()
            
            loc.plugin = loc_dict.get("plugin", "")
            loc.shortName = loc_dict.get("shortName", "")
            loc.context = loc_dict.get("context", "")
            loc.infowindow = loc_dict.get("infowindow", "")
            loc.visible = loc_dict.get("visible", True)
            
            locations_list.add_location(loc)
        
        return locations_list
    
    def get_date_range(self):
        """Get the min and max dates in the locations list"""
        if not self._locations:
            return None, None
            
        # Find min and max dates
        min_date = min(self._locations, key=lambda x: x.datetime).datetime
        max_date = max(self._locations, key=lambda x: x.datetime).datetime
        
        return min_date, max_date
    
    def filter_by_date(self, start_date=None, end_date=None):
        """Filter locations by date range and return count of visible locations"""
        if not self._locations:
            return 0
            
        for loc in self._locations:
            if start_date and end_date:
                loc.visible = start_date <= loc.datetime <= end_date
            elif start_date:
                loc.visible = start_date <= loc.datetime
            elif end_date:
                loc.visible = loc.datetime <= end_date
            else:
                loc.visible = True
        
        return sum(1 for loc in self._locations if loc.visible)
    
    def filter_by_point(self, lat, lon, radius):
        """
        Filter locations by distance from a point
        Returns count of visible locations
        """
        if not self._locations:
            return 0
            
        from utilities import GeneralUtilities
        
        for loc in self._locations:
            distance = GeneralUtilities.calcDistance(lat, lon, loc.latitude, loc.longitude)
            loc.visible = distance <= radius
            
        return sum(1 for loc in self._locations if loc.visible)
    
    def clear_filters(self):
        """Clear all filters, making all locations visible"""
        for loc in self._locations:
            loc.visible = True
        return len(self._locations)
    
    def __iter__(self):
        return iter(self._locations)
    
    def __len__(self):
        return len(self._locations)
    
    def __getitem__(self, index):
        return self._locations[index]