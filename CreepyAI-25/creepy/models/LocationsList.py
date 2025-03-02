#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import Qt

class LocationsTableModel(QAbstractTableModel):
    def __init__(self, locations, parent=None):
        self.locations = locations
        super(LocationsTableModel,self).__init__()
        
    def rowCount(self, index):
        return len(self.locations)
    
    def columnCount(self, index):
        return 2
    
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
        location = self.locations[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            if column == 0:
                return location.datetime.isoformat()
            if column == 1:
                return location.shortName
        return None
    
    def getLocationFromIndex(self, index):
        try:
            if index.isValid() and (0 <= index.row() < len(self.locations)):
                return self.locations[index.row()]
        except Exception as e:
            print(f"Error getting location from index: {e}")
        return None
        
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable