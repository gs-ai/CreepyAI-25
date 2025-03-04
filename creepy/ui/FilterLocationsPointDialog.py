<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QGroupBox, QFormLayout, QSlider
)
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)

class FilterLocationsPointDialog(QDialog):
    """Dialog for filtering locations by distance from a point."""
    
    def __init__(self, project, parent=None):
        super(FilterLocationsPointDialog, self).__init__(parent)
        
        self.setWindowTitle("Filter Locations by Distance")
        self.setFixedWidth(400)
        
        self.project = project
        
        # Create layout
        layout = QVBoxLayout()
        
        # Information label
        info_label = QLabel(
            "Filter locations based on their distance from a specific point. "
            "Only locations within the specified radius will be displayed."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Point group
        point_group = QGroupBox("Center Point")
        point_form = QFormLayout()
        
        # Latitude control
        self.lat_spin = QDoubleSpinBox()
        self.lat_spin.setRange(-90, 90)
        self.lat_spin.setDecimals(6)
        self.lat_spin.setValue(0)
        point_form.addRow("Latitude:", self.lat_spin)
        
        # Longitude control
        self.lon_spin = QDoubleSpinBox()
        self.lon_spin.setRange(-180, 180)
        self.lon_spin.setDecimals(6)
        self.lon_spin.setValue(0)
        point_form.addRow("Longitude:", self.lon_spin)
        
        point_group.setLayout(point_form)
        layout.addWidget(point_group)
        
        # Radius group
        radius_group = QGroupBox("Search Radius")
        radius_layout = QVBoxLayout()
        
        # Radius slider and value display
        slider_layout = QHBoxLayout()
        self.radius_slider = QSlider(Qt.Horizontal)
        self.radius_slider.setRange(1, 500)
        self.radius_slider.setValue(10)
        self.radius_slider.setTickInterval(50)
        self.radius_slider.setTickPosition(QSlider.TicksBelow)
        slider_layout.addWidget(self.radius_slider)
        
        self.radius_label = QLabel("10 km")
        slider_layout.addWidget(self.radius_label)
        
        radius_layout.addLayout(slider_layout)
        
        # Connect slider to label update
        self.radius_slider.valueChanged.connect(self._update_radius_label)
        
        radius_group.setLayout(radius_layout)
        layout.addWidget(radius_group)
        
        # Stats label - show how many locations are in the full dataset
        self.stats_label = QLabel()
        self._update_stats_label()
        layout.addWidget(self.stats_label)
        
        # Use current center button
        center_button = QPushButton("Use Current Map Center")
        center_button.clicked.connect(self._use_current_center)
        layout.addWidget(center_button)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply Filter")
        self.apply_button.clicked.connect(self.apply_filter)
        button_layout.addWidget(self.apply_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Set default center point to the center of all locations
        self._set_default_center()
    
    def _set_default_center(self):
        """Set the default center point to the center of all locations."""
        if self.project and hasattr(self.project, 'locations'):
            center_lat, center_lon = self.project.locations.get_center_point()
            
            self.lat_spin.setValue(center_lat)
            self.lon_spin.setValue(center_lon)
    
    def _update_radius_label(self, value):
        """Update the radius label with the slider value."""
        self.radius_label.setText(f"{value} km")
    
    def _update_stats_label(self):
        """Update the stats label with location counts."""
        if not self.project or not hasattr(self.project, 'locations'):
            self.stats_label.setText("No locations available")
            return
            
        total_count = self.project.locations.count()
        self.stats_label.setText(f"Total locations in project: {total_count}")
    
    def _use_current_center(self):
        """Use the current map center as the filter point."""
        # This would normally get the current center from the map view
        # For now, we'll just keep the current values
        pass
    
    def apply_filter(self):
        """Apply the distance filter to the project's locations."""
        if not self.project or not hasattr(self.project, 'locations'):
            self.reject()
            return
            
        # Get filter parameters
        latitude = self.lat_spin.value()
        longitude = self.lon_spin.value()
        radius_km = self.radius_slider.value()
        
        # Apply filter
        try:
            filtered_count = self.project.locations.filter_by_distance(latitude, longitude, radius_km)
            logger.info(f"Applied distance filter: {filtered_count} locations match")
            self.accept()
        except Exception as e:
            logger.error(f"Error applying distance filter: {str(e)}")
            self.reject()

=======
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\filterLocationsPointDialog.ui'
#
# Created: Fri Jan 31 15:33:25 2014
#      by: PyQt5 UI code generator 5.15.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

try:
    _fromUtf8 = lambda s: s
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FilteLocationsPointDialog(object):
    def setupUi(self, FilteLocationsPointDialog):
        FilteLocationsPointDialog.setObjectName(_fromUtf8("FilteLocationsPointDialog"))
        FilteLocationsPointDialog.resize(758, 565)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/creepy/marker")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FilteLocationsPointDialog.setWindowIcon(icon)
        self.buttonBox = QtWidgets.QDialogButtonBox(FilteLocationsPointDialog)
        self.buttonBox.setGeometry(QtCore.QRect(390, 520, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayoutWidget = QtWidgets.QWidget(FilteLocationsPointDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 731, 501))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.containerLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.containerLayout.setContentsMargins(0, 0, 0, 0)
        self.containerLayout.setObjectName(_fromUtf8("containerLayout"))
        self.titleLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLabel.sizePolicy().hasHeightForWidth())
        self.titleLabel.setSizePolicy(sizePolicy)
        self.titleLabel.setTextFormat(QtCore.Qt.RichText)
        self.titleLabel.setObjectName(_fromUtf8("titleLabel"))
        self.containerLayout.addWidget(self.titleLabel)
        self.webView = QtWebEngineWidgets.QWebEngineView(self.verticalLayoutWidget)
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.containerLayout.addWidget(self.webView)
        self.controlsContainerLayout = QtWidgets.QHBoxLayout()
        self.controlsContainerLayout.setObjectName(_fromUtf8("controlsContainerLayout"))
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.controlsContainerLayout.addItem(spacerItem)
        self.radiusLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radiusLabel.sizePolicy().hasHeightForWidth())
        self.radiusLabel.setSizePolicy(sizePolicy)
        self.radiusLabel.setTextFormat(QtCore.Qt.RichText)
        self.radiusLabel.setObjectName(_fromUtf8("radiusLabel"))
        self.controlsContainerLayout.addWidget(self.radiusLabel)
        self.radiusSpinBox = QtWidgets.QSpinBox(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radiusSpinBox.sizePolicy().hasHeightForWidth())
        self.radiusSpinBox.setSizePolicy(sizePolicy)
        self.radiusSpinBox.setMaximum(1000)
        self.radiusSpinBox.setObjectName(_fromUtf8("radiusSpinBox"))
        self.controlsContainerLayout.addWidget(self.radiusSpinBox)
        self.radiusUnitComboBox = QtWidgets.QComboBox(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radiusUnitComboBox.sizePolicy().hasHeightForWidth())
        self.radiusUnitComboBox.setSizePolicy(sizePolicy)
        self.radiusUnitComboBox.setObjectName(_fromUtf8("radiusUnitComboBox"))
        self.controlsContainerLayout.addWidget(self.radiusUnitComboBox)
        self.containerLayout.addLayout(self.controlsContainerLayout)

        self.retranslateUi(FilteLocationsPointDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FilteLocationsPointDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FilteLocationsPointDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FilteLocationsPointDialog)

    def retranslateUi(self, FilteLocationsPointDialog):
        FilteLocationsPointDialog.setWindowTitle(QtWidgets.QApplication.translate("FilteLocationsPointDialog", "Filter Locations By Place", None))
        self.titleLabel.setText(QtWidgets.QApplication.translate("FilteLocationsPointDialog", "<html><head/><body><p><span style=\" font-size:9pt;\">Drop a </span><span style=\" font-size:9pt; font-weight:600; color:#ff0000;\">pin</span><span style=\" font-size:9pt;\"> on the map for your point of interest</span></p></body></html>", None))
        self.radiusLabel.setText(QtWidgets.QApplication.translate("FilteLocationsPointDialog", "<html><head/><body><p><span style=\" font-size:9pt;\">Distance from the POI :</span></p></body></html>", None))

import creepy_resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    FilteLocationsPointDialog = QtWidgets.QDialog()
    ui = Ui_FilteLocationsPointDialog()
    ui.setupUi(FilteLocationsPointDialog)
    FilteLocationsPointDialog.show()
    sys.exit(app.exec_())
>>>>>>> gs-ai-patch-1
