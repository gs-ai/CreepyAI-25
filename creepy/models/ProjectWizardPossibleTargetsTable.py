#!/usr/bin/python
# -*- coding: utf-8 -*-
<<<<<<< HEAD
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtCore import QMimeData, QByteArray, QDataStream, QIODevice
from PyQt5.QtGui import QPixmap, QIcon
import os
import logging

# Setup logging
logger = logging.getLogger(__name__)

class ProjectWizardPossibleTargetsTable(QAbstractTableModel):
    """Table model for displaying available targets from various plugins"""
    
    def __init__(self, targets, parents=None):
        super(ProjectWizardPossibleTargetsTable, self).__init__()
        self.targets = targets
        self.column_headers = ['Plugin', 'Picture', 'Username', 'Full Name', 'User Id']
=======
from PyQt4.QtCore import QVariant, QAbstractTableModel, Qt
from PyQt4.Qt import QPixmap, QIcon, QMimeData, QByteArray, QDataStream, QIODevice
import os
class ProjectWizardPossibleTargetsTable(QAbstractTableModel):
    def __init__(self, targets, parents=None):
        super(ProjectWizardPossibleTargetsTable, self).__init__()
        self.targets = targets
>>>>>>> gs-ai-patch-1
        
    def rowCount(self, index):
        return len(self.targets)
    
    def columnCount(self, index):
<<<<<<< HEAD
        return len(self.column_headers)
=======
        return 5
>>>>>>> gs-ai-patch-1
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
<<<<<<< HEAD
                return int(Qt.AlignLeft|Qt.AlignVCenter)
            return int(Qt.AlignRight|Qt.AlignVCenter)
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if 0 <= section < len(self.column_headers):
                return self.column_headers[section]
        return int(section + 1)
    
    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self.targets)):
            return None
            
        target = self.targets[index.row()]
        column = index.column()
        
        try:
            if role == Qt.DecorationRole:
                if column == 1:
                    picturePath = os.path.join(os.getcwd(), 'temp', target['targetPicture']) if 'targetPicture' in target else None
                    if picturePath and os.path.exists(picturePath):
                        pixmap = QPixmap(picturePath)
                        return QIcon(pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    else:
                        pixmap = QPixmap(':/creepy/user')
                        return QIcon(pixmap.scaled(20, 20, Qt.KeepAspectRatio))
            elif role == Qt.DisplayRole:
                if column == 0:
                    return target.get('pluginName', 'Unknown')
                elif column == 1:
                    return None  # No text for image column
                elif column == 2:
                    return target.get('targetUsername', 'N/A')
                elif column == 3:
                    return target.get('targetFullname', 'N/A')
                elif column == 4:
                    return target.get('targetUserid', 'N/A')
            elif role == Qt.ToolTipRole:
                if column == 0:
                    return f"Plugin: {target.get('pluginName', 'Unknown')}"
                elif column == 2:
                    return f"Username: {target.get('targetUsername', 'N/A')}"
                elif column == 3:
                    return f"Full Name: {target.get('targetFullname', 'N/A')}"
                elif column == 4:
                    return f"User ID: {target.get('targetUserid', 'N/A')}"
        except Exception as e:
            logger.error(f"Error retrieving data for index {index.row()},{index.column()}: {str(e)}")
                
        return None
=======
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
        if index.isValid() and (0 <= index.row() < len(self.targets)) and target: 
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
            if role == Qt.DisplayRole:
                if column == 0:
                    return QVariant(target['pluginName'])
                elif column == 1:
                    return QVariant()
                elif column == 2:
                    return QVariant(target['targetUsername'])
                elif column == 3:
                    return QVariant(target['targetFullname'])
                elif column == 4:
                    return QVariant(target['targetUserid'])
        return QVariant()
>>>>>>> gs-ai-patch-1

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled)
        
    def mimeTypes(self):
<<<<<<< HEAD
        return ['application/target.tableitem.creepy']
=======
        return [ 'application/target.tableitem.creepy' ] 
>>>>>>> gs-ai-patch-1
    
    def mimeData(self, indices):
        mimeData = QMimeData()
        encodedData = QByteArray()
        stream = QDataStream(encodedData, QIODevice.WriteOnly)
<<<<<<< HEAD
        
        try:
            for index in indices:
                if index.row() >= len(self.targets):
                    continue
                    
                if index.column() == 1:
                    stream.writeQVariant(self.data(index, Qt.DecorationRole))
                else:
                    stream.writeQVariant(self.data(index, Qt.DisplayRole))
                    
            mimeData.setData('application/target.tableitem.creepy', encodedData)
        except Exception as e:
            logger.error(f"Error creating mime data: {str(e)}")
            
=======
        for index in indices:
            if index.column() == 1:
                d = QVariant(self.data(index, Qt.DecorationRole))
            else:
                d = QVariant(self.data(index, Qt.DisplayRole).toString())
            stream << d
        mimeData.setData('application/target.tableitem.creepy', encodedData)
>>>>>>> gs-ai-patch-1
        return mimeData