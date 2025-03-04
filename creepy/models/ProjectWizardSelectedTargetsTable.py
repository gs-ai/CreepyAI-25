<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant

class ProjectWizardSelectedTargetsTable(QAbstractTableModel):
    """Model for displaying selected targets in the project wizard"""
    
    def __init__(self, parent=None):
        super(ProjectWizardSelectedTargetsTable, self).__init__(parent)
        
        self.targets = []  # List of target dictionaries
        self.headers = ["Name", "Username", "Platform"]
    
    def rowCount(self, parent=QModelIndex()):
        """Return number of rows in the model"""
        if parent.isValid():
            return 0
        return len(self.targets)
    
    def columnCount(self, parent=QModelIndex()):
        """Return number of columns in the model"""
        if parent.isValid():
            return 0
        return 3
    
    def data(self, index, role=Qt.DisplayRole):
        """Return data for the given role and index"""
        if not index.isValid() or index.row() >= len(self.targets):
            return QVariant()
        
        target = self.targets[index.row()]
        
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return target.get("name", "")
            elif index.column() == 1:
                return target.get("username", "")
            elif index.column() == 2:
                return target.get("platform", "")
        
        return QVariant()
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Return header data for the given role, section and orientation"""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if 0 <= section < len(self.headers):
                return self.headers[section]
        
        return QVariant()
=======
#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import QVariant, QAbstractTableModel, Qt
from PyQt4.Qt import QDataStream, QIODevice, QModelIndex


class ProjectWizardSelectedTargetsTable(QAbstractTableModel):
    def __init__(self, targets, parents=None):
        super(ProjectWizardSelectedTargetsTable, self).__init__()
        self.targets = targets
        
    def rowCount(self,index):
        return len(self.targets)
    
    def columnCount(self,index):
        return 5
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if section == 0:
                return QVariant('Plugin')
            elif section == 1:
                return QVariant('Picture')
            elif section == 2:
                return QVariant('Username')
            elif section == 3:
                return QVariant('Full Name')
            elif section == 4:
                return QVariant('User Id')
        return QVariant(int(section + 1))

    
    def data(self, index, role):
        target = self.targets[index.row()]
        
        if index.isValid() and target:
            column = index.column()
            if role == Qt.DecorationRole:
                if column == 1:
                    pixmap = target['targetPicture']
                    return pixmap
            if role == Qt.DisplayRole:
                if column == 0:
                    return QVariant(target['pluginName'])
                if column == 1:
                    return QVariant()
                elif column == 2:
                    return QVariant(target['targetUsername'])
                elif column == 3:
                    return QVariant(target['targetFullname'])
                elif column == 4:
                    return QVariant(target['targetUserid'])
                
                
            else: 
                return QVariant()

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
        return [ 'application/target.tableitem.creepy' ] 
        
    def dropMimeData(self, data, action, row, column, parent):
        if data.hasFormat('application/target.tableitem.creepy'):
            encodedData = data.data('application/target.tableitem.creepy')
            stream = QDataStream(encodedData, QIODevice.ReadOnly)
            columnsList = []
            qVariant = QVariant()
            while not stream.atEnd():
                stream >> qVariant
                columnsList.append(qVariant.toPyObject()) 
            draggedRows = [columnsList[x:x+5] for x in range(0,len(columnsList),5)]
            droppedRows = []
            for row in draggedRows:
                #Ensure we are not putting duplicates in the target list
                existed = False
                for target in self.targets:
                    if row[2] == target['targetUsername'] and row[0] == target['pluginName']:
                        existed = True
                if not existed:        
                    droppedRows.append({'targetUsername':row[2], 'targetFullname':row[3], 'targetPicture':row[1], 'targetUserid':row[4], 'pluginName':row[0]})
            self.insertRows(droppedRows, len(droppedRows), parent)
                
        return True
>>>>>>> gs-ai-patch-1
