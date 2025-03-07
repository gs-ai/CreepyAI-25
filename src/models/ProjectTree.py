#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QAbstractItemModel, Qt, QModelIndex
from PyQt5.QtGui import QIcon
import logging

logger = logging.getLogger(__name__)

class ProjectTreeNode(object):
    """Base class for all nodes in the project tree."""
    
    def __init__(self, name, parent=None):
        self.parentNode = parent
        self.nodeName = name
        self.childNodes = []
        
    def appendChild(self, child):
        self.childNodes.append(child)
        
    def child(self, row):
        if 0 <= row < len(self.childNodes):
            return self.childNodes[row]
        return None
        
    def childCount(self):
        return len(self.childNodes)
        
    def row(self):
        if self.parentNode:
            return self.parentNode.childNodes.index(self)
        return 0
        
    def columnCount(self):
        return 1
        
    def data(self, column):
        if column == 0:
            return self.nodeName
        return None
        
    def parent(self):
        return self.parentNode
        
    def nodeType(self):
        return "BASE"
    
    def addChild(self, child):
        self.appendChild(child)

class ProjectNode(ProjectTreeNode):
    """Node representing a project in the tree."""
    
    def __init__(self, name, project, parent=None):
        super(ProjectNode, self).__init__(name, parent)
        self.project = project
        
    def nodeType(self):
        return "PROJECT"
        
    def data(self, column):
        if column == 0:
            return self.project.projectName
        return None

class LocationsNode(ProjectTreeNode):
    """Node representing the locations section of a project."""
    
    def __init__(self, name, parent=None):
        super(LocationsNode, self).__init__(name, parent)
        
    def nodeType(self):
        return "LOCATIONS"

class AnalysisNode(ProjectTreeNode):
    """Node representing the analysis section of a project."""
    
    def __init__(self, name, parent=None):
        super(AnalysisNode, self).__init__(name, parent)
        
    def nodeType(self):
        return "ANALYSIS"

class ProjectTreeModel(QAbstractItemModel):
    """Tree model for projects, locations, and analysis results."""
    
    def __init__(self, root, parent=None):
        super(ProjectTreeModel, self).__init__(parent)
        self.rootNode = root
        
    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
            
        if not parent.isValid():
            parentNode = self.rootNode
        else:
            parentNode = parent.internalPointer()
            
        childNode = parentNode.child(row)
        if childNode:
            return self.createIndex(row, column, childNode)
        return QModelIndex()
        
    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
            
        childNode = index.internalPointer()
        parentNode = childNode.parent()
        
        if parentNode == self.rootNode:
            return QModelIndex()
            
        return self.createIndex(parentNode.row(), 0, parentNode)
        
    def rowCount(self, parent):
        if parent.column() > 0:
            return 0
            
        if not parent.isValid():
            parentNode = self.rootNode
        else:
            parentNode = parent.internalPointer()
            
        return parentNode.childCount()
        
    def columnCount(self, parent):
        return 1
        
    def data(self, index, role):
        if not index.isValid():
            return None
            
        node = index.internalPointer()
        
        if role == Qt.DisplayRole:
            return node.data(index.column())
        elif role == Qt.DecorationRole:
            if node.nodeType() == "PROJECT":
                return QIcon(":/creepy/project")
            elif node.nodeType() == "LOCATIONS":
                return QIcon(":/creepy/locations")
            elif node.nodeType() == "ANALYSIS":
                return QIcon(":/creepy/analysis")
        
        return None
        
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootNode.data(section)
        return None


