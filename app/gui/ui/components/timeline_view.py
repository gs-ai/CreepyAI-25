"""
Timeline View for CreepyAI
Visualizes location data chronologically
"""

import logging
from typing import Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QPushButton, QFrame
)
from PyQt5.QtCore import Qt

from app.models.location_data import LocationDataModel

logger = logging.getLogger(__name__)

class TimelineView(QWidget):
    """Widget for visualizing location data chronologically"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.location_model = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Group By:"))
        
        self.group_by_combo = QComboBox()
        self.group_by_combo.addItems(["Day", "Week", "Month", "Year", "Hour of Day", "Day of Week"])
        self.group_by_combo.currentIndexChanged.connect(self.update_timeline)
        controls_layout.addWidget(self.group_by_combo)
        
        controls_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.update_timeline)
        controls_layout.addWidget(refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Timeline visualization
        self.timeline_view = QLabel("Timeline visualization will be here")
        self.timeline_view.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.timeline_view)
        
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
            model.dataChanged.connect(self.update_timeline)
        
        # Update UI
        self.update_timeline()
    
    def update_timeline(self):
        """Update the timeline visualization"""
        if not self.location_model:
            return
        
        # Get locations
        locations = self.location_model.get_all_locations()
        
        if not locations:
            self.timeline_view.setText("No locations available for timeline")
            return
        
        # Extract timestamps
        timestamps = [loc.timestamp for loc in locations if loc.timestamp]
        
        if not timestamps:
            self.timeline_view.setText("No timestamps available for timeline")
            return
        
        # Get grouping method
        group_method = self.group_by_combo.currentText()
        
        # Create a simple text-based timeline
        data = {}
        
        if group_method == "Hour of Day":
            for ts in timestamps:
                hour = ts.hour
                data[hour] = data.get(hour, 0) + 1
            text = "Distribution by Hour of Day:\n\n"
            for hour in range(24):
                count = data.get(hour, 0)
                bar = "#" * int(count / max(data.values(), 1) * 20)
                text += f"{hour:02d}:00 | {bar} ({count})\n"
        
        elif group_method == "Day of Week":
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for ts in timestamps:
                day = ts.weekday()
                data[day] = data.get(day, 0) + 1
            text = "Distribution by Day of Week:\n\n"
            for day in range(7):
                count = data.get(day, 0)
                bar = "#" * int(count / max(data.values(), 1) * 20)
                text += f"{day_names[day]:<10} | {bar} ({count})\n"
        
        elif group_method == "Day":
            for ts in timestamps:
                day = ts.date()
                data[day] = data.get(day, 0) + 1
            text = "Daily Location Count:\n\n"
            for day in sorted(data.keys()):
                count = data[day]
                bar = "#" * min(count, 50)
                text += f"{day.strftime('%Y-%m-%d')}: {bar} ({count})\n"
        
        elif group_method == "Week":
            for ts in timestamps:
                year, week, _ = ts.isocalendar()
                key = f"{year}-W{week:02d}"
                data[key] = data.get(key, 0) + 1
            text = "Weekly Location Count:\n\n"
            for week_key in sorted(data.keys()):
                count = data[week_key]
                bar = "#" * min(count, 50)
                text += f"{week_key}: {bar} ({count})\n"
        
        elif group_method == "Month":
            for ts in timestamps:
                month_key = ts.strftime("%Y-%m")
                data[month_key] = data.get(month_key, 0) + 1
            text = "Monthly Location Count:\n\n"
            for month_key in sorted(data.keys()):
                count = data[month_key]
                bar = "#" * min(count, 50)
                text += f"{month_key}: {bar} ({count})\n"
        
        elif group_method == "Year":
            for ts in timestamps:
                year = ts.year
                data[year] = data.get(year, 0) + 1
            text = "Yearly Location Count:\n\n"
            for year in sorted(data.keys()):
                count = data[year]
                bar = "#" * min(count, 50)
                text += f"{year}: {bar} ({count})\n"
        
        self.timeline_view.setText(text)
