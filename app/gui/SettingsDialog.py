#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import logging
from typing import Dict, List, Optional

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QDoubleSpinBox,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.analysis import DEFAULT_PROMPT_TEMPLATE, SUPPORTED_LOCAL_LLM_MODELS

logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """Settings dialog for the CreepyAI application."""
    
    def __init__(self, config_manager, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("CreepyAI Settings")
        self.resize(600, 400)
        self.config_manager = config_manager
        
        # Set up UI
        self._setup_ui()
        
        # Load current settings
        self._load_settings()
        
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # General settings tab
        self.general_tab = QWidget()
        general_layout = QFormLayout()
        
        # General settings
        self.data_dir = QLineEdit()
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_data_dir)
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.data_dir)
        dir_layout.addWidget(browse_button)
        
        general_layout.addRow("Data Directory:", dir_layout)
        
        self.remember_recent = QCheckBox("Remember recent projects")
        general_layout.addRow("", self.remember_recent)
        
        self.max_recent = QSpinBox()
        self.max_recent.setMinimum(1)
        self.max_recent.setMaximum(20)
        general_layout.addRow("Maximum recent projects:", self.max_recent)
        
        self.general_tab.setLayout(general_layout)
        
        # Map settings tab
        self.map_tab = QWidget()
        map_layout = QFormLayout()
        
        self.map_provider = QComboBox()
        self.map_provider.addItems(["OpenStreetMap (offline friendly)"])
        self.map_provider.setCurrentIndex(0)
        self.map_provider.setEnabled(False)
        map_layout.addRow("Map Provider:", self.map_provider)
        
        self.map_info = QLabel(
            "CreepyAI ships with offline-friendly OpenStreetMap tiles and does not "
            "require map API keys."
        )
        self.map_info.setWordWrap(True)
        map_layout.addRow("", self.map_info)

        self.cache_maps = QCheckBox("Cache map tiles")
        self.cache_maps.setChecked(True)
        self.cache_maps.setEnabled(False)
        map_layout.addRow("", self.cache_maps)

        self.map_tab.setLayout(map_layout)

        # Analysis settings tab
        self.analysis_tab = QWidget()
        analysis_layout = QVBoxLayout()

        defaults_group = QGroupBox("Default Analysis Behaviour")
        defaults_form = QFormLayout()

        self.analysis_temperature = QDoubleSpinBox()
        self.analysis_temperature.setRange(0.0, 2.0)
        self.analysis_temperature.setSingleStep(0.05)
        self.analysis_temperature.setDecimals(2)
        defaults_form.addRow("Base temperature:", self.analysis_temperature)

        self.analysis_tone = QLineEdit()
        defaults_form.addRow("Default tone:", self.analysis_tone)

        self.analysis_depth = QLineEdit()
        defaults_form.addRow("Default depth:", self.analysis_depth)

        self.prompt_template_edit = QPlainTextEdit()
        self.prompt_template_edit.setPlaceholderText("Enter the JSON-orientated prompt instructions shared with the LLM.")
        self.prompt_template_edit.setTabChangesFocus(True)
        defaults_form.addRow("Prompt template:", self.prompt_template_edit)

        defaults_group.setLayout(defaults_form)
        analysis_layout.addWidget(defaults_group)

        overrides_group = QGroupBox("Per-model overrides")
        overrides_layout = QVBoxLayout()

        self.model_table = QTableWidget(0, 5)
        self.model_table.setHorizontalHeaderLabels(
            ["Model", "Temperature", "Tone", "Depth", "Prompt override"]
        )
        self.model_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.model_table.verticalHeader().setVisible(False)
        self.model_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.model_table.setSelectionMode(QTableWidget.SingleSelection)
        overrides_layout.addWidget(self.model_table)

        button_row = QHBoxLayout()
        self.add_model_button = QPushButton("Add Model")
        self.add_model_button.clicked.connect(self._add_model_override_row)
        self.remove_model_button = QPushButton("Remove Selected")
        self.remove_model_button.clicked.connect(self._remove_selected_override_row)
        button_row.addWidget(self.add_model_button)
        button_row.addWidget(self.remove_model_button)
        button_row.addStretch()
        overrides_layout.addLayout(button_row)

        overrides_group.setLayout(overrides_layout)
        analysis_layout.addWidget(overrides_group)
        analysis_layout.addStretch(1)
        self.analysis_tab.setLayout(analysis_layout)

        # Add tabs
        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.map_tab, "Map")
        self.tabs.addTab(self.analysis_tab, "Analysis")

        layout.addWidget(self.tabs)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def _add_model_override_row(
        self,
        model: str = "",
        temperature: Optional[float] = None,
        tone: str = "",
        depth: str = "",
        prompt_override: str = "",
    ) -> None:
        row = self.model_table.rowCount()
        self.model_table.insertRow(row)

        model_item = QTableWidgetItem(model)
        self.model_table.setItem(row, 0, model_item)

        spin = QDoubleSpinBox()
        spin.setRange(0.0, 2.0)
        spin.setSingleStep(0.05)
        spin.setDecimals(2)
        base_value = temperature if temperature is not None else self.analysis_temperature.value()
        spin.setValue(base_value)
        self.model_table.setCellWidget(row, 1, spin)

        for column, value in enumerate([tone, depth, prompt_override], start=2):
            item = QTableWidgetItem(value)
            self.model_table.setItem(row, column, item)

    def _remove_selected_override_row(self) -> None:
        current_row = self.model_table.currentRow()
        if current_row >= 0:
            self.model_table.removeRow(current_row)

    def _load_model_overrides(self, overrides: List[Dict[str, object]]) -> None:
        self.model_table.setRowCount(0)
        if overrides:
            for entry in overrides:
                model = str(entry.get("model", ""))
                temperature = entry.get("temperature")
                try:
                    temperature = float(temperature) if temperature is not None else None
                except (TypeError, ValueError):
                    temperature = None
                tone = str(entry.get("tone", "") or "")
                depth = str(entry.get("depth", "") or "")
                prompt_override = str(entry.get("prompt_override", "") or "")
                self._add_model_override_row(
                    model=model,
                    temperature=temperature,
                    tone=tone,
                    depth=depth,
                    prompt_override=prompt_override,
                )
        else:
            for candidate in SUPPORTED_LOCAL_LLM_MODELS[:3]:
                self._add_model_override_row(model=str(candidate.get("name", "")))

    def _collect_model_overrides(self) -> List[Dict[str, object]]:
        overrides: List[Dict[str, object]] = []
        for row in range(self.model_table.rowCount()):
            model_item = self.model_table.item(row, 0)
            model = model_item.text().strip() if model_item else ""
            if not model:
                continue

            temperature_widget = self.model_table.cellWidget(row, 1)
            if isinstance(temperature_widget, QDoubleSpinBox):
                temperature = float(temperature_widget.value())
            else:
                temperature = float(self.analysis_temperature.value())

            entry: Dict[str, object] = {"model": model, "temperature": round(temperature, 2)}

            tone_item = self.model_table.item(row, 2)
            tone_text = tone_item.text().strip() if tone_item else ""
            if tone_text:
                entry["tone"] = tone_text

            depth_item = self.model_table.item(row, 3)
            depth_text = depth_item.text().strip() if depth_item else ""
            if depth_text:
                entry["depth"] = depth_text

            prompt_item = self.model_table.item(row, 4)
            prompt_text = prompt_item.text().strip() if prompt_item else ""
            if prompt_text:
                entry["prompt_override"] = prompt_text

            overrides.append(entry)

        return overrides

    def _load_settings(self):
        """Load current settings."""
        try:
            self.analysis_temperature.setValue(0.2)
            self.analysis_tone.setText("objective")
            self.analysis_depth.setText("balanced")
            self.prompt_template_edit.setPlainText(DEFAULT_PROMPT_TEMPLATE)
            overrides: List[Dict[str, object]] = []

            # Load from config manager
            if self.config_manager:
                data_dir = self.config_manager.get('data_dir', os.path.expanduser("~/.creepyai/data"))
                remember_recent = self.config_manager.get('remember_recent', True)
                max_recent = self.config_manager.get('max_recent', 10)
                map_provider = self.config_manager.get('map_provider', "OpenStreetMap")
                cache_maps = self.config_manager.get('cache_maps', True)
                
                # Set values in UI
                self.data_dir.setText(data_dir)
                self.remember_recent.setChecked(remember_recent)
                self.max_recent.setValue(max_recent)
                index = self.map_provider.findText(map_provider)
                if index >= 0:
                    self.map_provider.setCurrentIndex(index)
                self.cache_maps.setChecked(cache_maps)

                analysis_temp = self.config_manager.get('analysis.default_temperature', 0.2)
                try:
                    self.analysis_temperature.setValue(float(analysis_temp))
                except (TypeError, ValueError):
                    self.analysis_temperature.setValue(0.2)

                tone = self.config_manager.get('analysis.default_tone', "objective") or "objective"
                depth = self.config_manager.get('analysis.default_depth', "balanced") or "balanced"
                self.analysis_tone.setText(str(tone))
                self.analysis_depth.setText(str(depth))

                template = self.config_manager.get('analysis.prompt_template', DEFAULT_PROMPT_TEMPLATE) or DEFAULT_PROMPT_TEMPLATE
                self.prompt_template_edit.setPlainText(str(template))

                overrides_config = self.config_manager.get('analysis.model_overrides', [])
                if isinstance(overrides_config, list):
                    overrides = overrides_config

        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
            QMessageBox.warning(self, "Settings Error", f"Failed to load settings: {str(e)}")
            overrides = []
        self._load_model_overrides(overrides or [])

    def _save_settings(self):
        """Save settings and close dialog."""
        try:
            # Save to config manager
            if self.config_manager:
                self.config_manager.set('data_dir', self.data_dir.text())
                self.config_manager.set('remember_recent', self.remember_recent.isChecked())
                self.config_manager.set('max_recent', self.max_recent.value())
                self.config_manager.set('map_provider', self.map_provider.currentText())
                self.config_manager.set('cache_maps', self.cache_maps.isChecked())

                template_text = self.prompt_template_edit.toPlainText().strip()
                if not template_text:
                    template_text = DEFAULT_PROMPT_TEMPLATE

                self.config_manager.set('analysis.default_temperature', float(self.analysis_temperature.value()))
                self.config_manager.set('analysis.default_tone', self.analysis_tone.text().strip() or "objective")
                self.config_manager.set('analysis.default_depth', self.analysis_depth.text().strip() or "balanced")
                self.config_manager.set('analysis.prompt_template', template_text)
                self.config_manager.set('analysis.model_overrides', self._collect_model_overrides())

                # Save config to disk
                self.config_manager.save()

            self.accept()
            
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            QMessageBox.critical(self, "Settings Error", f"Failed to save settings: {str(e)}")
    
    def _browse_data_dir(self):
        """Browse for data directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Data Directory", self.data_dir.text())
            
        if directory:
            self.data_dir.setText(directory)
