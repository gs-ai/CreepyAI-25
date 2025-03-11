"""
Dashboard View for CreepyAI
Provides a summary view showing key statistics and recent activities
"""

import logging
from typing import Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QGroupBox, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt

from app.models.location_data import LocationDataModel

logger = logging.getLogger(__name__)

class DashboardView(QWidget):
    """Widget for displaying a dashboard with key statistics and recent activities"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.location_model = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Summary statistics
        summary_group = QGroupBox("Summary Statistics")
        summary_layout = QGridLayout(summary_group)
        
        self.total_locations_label = QLabel("0")
        self.total_locations_label.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(QLabel("Total Locations:"), 0, 0)
        summary_layout.addWidget(self.total_locations_label, 0, 1)
        
        self.unique_sources_label = QLabel("0")
        self.unique_sources_label.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(QLabel("Unique Sources:"), 1, 0)
        summary_layout.addWidget(self.unique_sources_label, 1, 1)
        
        self.date_range_label = QLabel("N/A")
        self.date_range_label.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(QLabel("Date Range:"), 2, 0)
        summary_layout.addWidget(self.date_range_label, 2, 1)
        
        self.address_coverage_label = QLabel("0%")
        self.address_coverage_label.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(QLabel("Address Coverage:"), 3, 0)
        summary_layout.addWidget(self.address_coverage_label, 3, 1)
        
        layout.addWidget(summary_group)
        
        # Recent activities
        recent_group = QGroupBox("Recent Activities")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_activities_list = QLabel("No recent activities")
        self.recent_activities_list.setAlignment(Qt.AlignCenter)
        recent_layout.addWidget(self.recent_activities_list)
        
        layout.addWidget(recent_group)
        
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
            model.dataChanged.connect(self.update_dashboard)
        
        # Update UI
        self.update_dashboard()
    
    def update_dashboard(self):
        """Update dashboard display"""
        if not self.location_model:
            return
        
        # Get locations
        locations = self.location_model.get_all_locations()
        location_count = len(locations)
        
        # Update summary statistics
        self.total_locations_label.setText(str(location_count))
        
        unique_sources = self.location_model.get_all_sources()
        self.unique_sources_label.setText(str(len(unique_sources)))
        
        # Calculate date range
        if location_count > 0:
            timestamps = [loc.timestamp for loc in locations if loc.timestamp]
            if timestamps:
                min_date = min(timestamps).strftime("%Y-%m-%d")
                max_date = max(timestamps).strftime("%Y-%m-%d")
                self.date_range_label.setText(f"{min_date} to {max_date}")
            else:
                self.date_range_label.setText("N/A")
        else:
            self.date_range_label.setText("N/A")
        
        # Calculate address coverage
        addresses = [loc for loc in locations if loc.address]
        if location_count > 0:
            coverage = (len(addresses) / location_count) * 100
            self.address_coverage_label.setText(f"{coverage:.1f}%")
        else:
            self.address_coverage_label.setText("0%")
        
        # Update recent activities
        recent_activities = "\n".join(
            f"{loc.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {loc.source}: {loc.context}"
            for loc in sorted(locations, key=lambda x: x.timestamp, reverse=True)[:5]
        )
        self.recent_activities_list.setText(recent_activities or "No recent activities")
