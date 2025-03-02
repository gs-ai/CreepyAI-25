#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtCore import QDataStream, QIODevice, QModelIndex


class ProjectWizardSelectedTargetsTable(QAbstractTableModel):
    def __init__(self, targets, parents=None):
        super(ProjectWizardSelectedTargetsTable, self).__init__()
        self.targets = targets
        
    def rowCount(self, index):
        return len(self.targets)
    
    def columnCount(self, index):
        return 5
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignLeft|Qt.AlignVCenter)
            return int(Qt.AlignRight|Qt.AlignVCenter)
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if section == 0:
                return 'Plugin'
            elif section == 1:
                return 'Picture'
            elif section == 2:
                return 'Username'
            elif section == 3:
                return 'Full Name'
            elif section == 4:
                return 'User Id'
        return int(section + 1)

    
    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self.targets):
            return None
            
        target = self.targets[index.row()]
        column = index.column()
        
        if role == Qt.DecorationRole:
            if column == 1:
                return target['targetPicture']
        elif role == Qt.DisplayRole:
            if column == 0:
                return target['pluginName']
            if column == 1:
                return None
            elif column == 2:
                return target['targetUsername']
            elif column == 3:
                return target['targetFullname']
            elif column == 4:
                return target['targetUserid']
                
        return None

    def removeRows(self, rows, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, min(rows), max(rows))
        for row in sorted(rows, reverse=True):
            if 0 <= row < len(self.targets):
                del self.targets[row]
        self.endRemoveRows()
        return True

    def insertRow(self, row, parent=QModelIndex()):
        self.insertRows(row, 1, parent)

    def insertRows(self, rows, count, parent=QModelIndex()):
        self.beginInsertRows(parent, len(self.targets), len(self.targets) + count - 1)
        self.targets.extend(rows)
        self.endInsertRows()
        return True
    
    def flags(self, index):
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|Qt.ItemIsDropEnabled)
        
    def mimeTypes(self):
        return ['application/target.tableitem.creepy']
        
    def dropMimeData(self, data, action, row, column, parent):
        if data.hasFormat('application/target.tableitem.creepy'):
            encodedData = data.data('application/target.tableitem.creepy')
            stream = QDataStream(encodedData, QIODevice.ReadOnly)
            columnsList = []
            while not stream.atEnd():
                value = stream.readQVariant()
                columnsList.append(value)
                
            draggedRows = [columnsList[x:x+5] for x in range(0, len(columnsList), 5)]
            droppedRows = []
            for row in draggedRows:
                # Ensure we are not putting duplicates in the target list
                existed = False
                for target in self.targets:
                    if row[2] == target['targetUsername'] and row[0] == target['pluginName']:
                        existed = True
                if not existed:        
                    droppedRows.append({
                        'targetUsername': row[2], 
                        'targetFullname': row[3], 
                        'targetPicture': row[1], 
                        'targetUserid': row[4], 
                        'pluginName': row[0]
                    })
            self.insertRows(droppedRows, len(droppedRows), parent)
                
        return True