#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtCore import QMimeData, QByteArray, QDataStream, QIODevice
from PyQt5.QtGui import QPixmap, QIcon
import os

class ProjectWizardPossibleTargetsTable(QAbstractTableModel):
    def __init__(self, targets, parents=None):
        super(ProjectWizardPossibleTargetsTable, self).__init__()
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
        if not index.isValid() or not (0 <= index.row() < len(self.targets)):
            return None
            
        target = self.targets[index.row()]
        column = index.column()
        
        if role == Qt.DecorationRole:
            if column == 1:
                picturePath = os.path.join(os.getcwd(), 'temp', target['targetPicture'])
                if picturePath and os.path.exists(picturePath):
                    pixmap = QPixmap(picturePath)
                    return QIcon(pixmap.scaled(30, 30, Qt.IgnoreAspectRatio, Qt.FastTransformation))
                else:
                    pixmap = QPixmap(':/creepy/user')
                    return QIcon(pixmap.scaled(20, 20, Qt.IgnoreAspectRatio))
        elif role == Qt.DisplayRole:
            if column == 0:
                return target['pluginName']
            elif column == 1:
                return None
            elif column == 2:
                return target['targetUsername']
            elif column == 3:
                return target['targetFullname']
            elif column == 4:
                return target['targetUserid']
                
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled)
        
    def mimeTypes(self):
        return ['application/target.tableitem.creepy']
    
    def mimeData(self, indices):
        mimeData = QMimeData()
        encodedData = QByteArray()
        stream = QDataStream(encodedData, QIODevice.WriteOnly)
        for index in indices:
            if index.column() == 1:
                stream.writeQVariant(self.data(index, Qt.DecorationRole))
            else:
                stream.writeQVariant(self.data(index, Qt.DisplayRole))
        mimeData.setData('application/target.tableitem.creepy', encodedData)
        return mimeData