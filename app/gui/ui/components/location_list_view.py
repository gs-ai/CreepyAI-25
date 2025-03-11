"""
Location List View for CreepyAI
Provides a filterable list view for browsing location data
"""

import logging
from typing import Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QComboBox, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt

from app.models.location_data import LocationDataModel, Location

logger = logging.getLogger(__name__)

class LocationListView(QWidget):
    """Widget for displaying a filterable list of locations"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.location_model = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Filter controls
        filter_group = QGroupBox("Filter Locations")
        filter_layout = QFormLayout(filter_group)
        
        self.source_filter_combo = QComboBox()
        self.source_filter_combo.addItem("All Sources")
        self.source_filter_combo.currentIndexChanged.connect(self.update_location_list)
        filter_layout.addRow("Source:", self.source_filter_combo)
        
        self.tag_filter_combo = QComboBox()
        self.tag_filter_combo.addItem("All Tags")
        self.tag_filter_combo.currentIndexChanged.connect(self.update_location_list)
        filter_layout.addRow("Tag:", self.tag_filter_combo)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by context or address")
        self.search_edit.textChanged.connect(self.update_location_list)
        filter_layout.addRow("Search:", self.search_edit)
        
        layout.addWidget(filter_group)
        
        # Location list
        self.location_list = QListWidget()
        self.location_list.itemClicked.connect(self.on_location_selected)
        layout.addWidget(self.location_list)
        
        # Add stretching space
        layout.addStretch()
    
    def set_location_model(self, model: LocationDataModel):
        """
        Set the location data model
        
        Args:
            model: Location data model
        """
        self.location_model = model
        
        # Connect to model signals
        if model:
            model.dataChanged.connect(self.update_location_list)
            
            # Update filters
            self.source_filter_combo.clear()
            self.source_filter_combo.addItem("All Sources")
            self.source_filter_combo.addItems(model.get_all_sources())
            
            self.tag_filter_combo.clear()
            self.tag_filter_combo.addItem("All Tags")
            self.tag_filter_combo.addItems(model.get_all_tags())
        
        # Update UI
        self.update_location_list()
    
    def update_location_list(self):
        """Update the location list display"""
        if not self.location_model:
            return
        
        # Get filter values
        selected_source = self.source_filter_combo.currentText()
        selected_tag = self.tag_filter_combo.currentText()
        search_text = self.search_edit.text().lower()
        
        # Filter locations
        locations = self.location_model.get_all_locations()
        
        if selected_source != "All Sources":
            locations = [loc for loc in locations if loc.source == selected_source]
        
        if selected_tag != "All Tags":
            locations = [loc for loc in locations if selected_tag in loc.metadata.tags]
        
        if search_text:
            locations = [
                loc for loc in locations 
                if search_text in (loc.context or "").lower() or search_text in (loc.address or "").lower()
            ]
        
        # Update list widget
        self.location_list.clear()
        
        for location in locations:
            item = QListWidgetItem(f"{location.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {location.source}: {location.context}")
            item.setData(Qt.UserRole, location.id)
            self.location_list.addItem(item)
    
    def on_location_selected(self, item: QListWidgetItem):
        """Handle location selection"""
        location_id = item.data(Qt.UserRole)
        location = self.location_model.get_location(location_id)
        
        if location:
            logger.info(f"Selected location: {location.context}")
