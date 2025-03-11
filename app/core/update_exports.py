#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This script updates the CreepyAI main application to include the new export functions.
Run this script to patch the main application file.
"""

import os
import re
from utilities.PluginManager import PluginManager

def update_main_app():
    main_file = '/Users/mbaosint/Desktop/Projects/CreepyAI/CreepyAI-25/creepy/CreepyMain.py'
    
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add import for ExportUtils
    import_pattern = r'from utilities import GeneralUtilities'
    import_replacement = 'from utilities import GeneralUtilities\nfrom utilities.ExportUtils import ExportUtils'
    content = re.sub(import_pattern, import_replacement, content)
    
    # Update the menu creation to add the new export formats
    menu_pattern = r'self\.ui\.actionExportFilteredKML\.triggered\.connect\(functools\.partial\(self\.exportProjectKML, filtering=True\)\)'
    menu_replacement = '''self.ui.actionExportFilteredKML.triggered.connect(functools.partial(self.exportProjectKML, filtering=True))
        self.ui.actionExportJSON = self.ui.menuExport.addAction("Export as GeoJSON...")
        self.ui.actionExportJSON.triggered.connect(self.exportProjectJSON)
        self.ui.actionExportHTML = self.ui.menuExport.addAction("Export as Interactive HTML...")
        self.ui.actionExportHTML.triggered.connect(self.exportProjectHTML)
        self.ui.actionExportFilteredJSON = self.ui.menuExportFiltered.addAction("Export as GeoJSON...")
        self.ui.actionExportFilteredJSON.triggered.connect(functools.partial(self.exportProjectJSON, filtering=True))
        self.ui.actionExportFilteredHTML = self.ui.menuExportFiltered.addAction("Export as Interactive HTML...")
        self.ui.actionExportFilteredHTML.triggered.connect(functools.partial(self.exportProjectHTML, filtering=True))'''
    
    content = re.sub(menu_pattern, menu_replacement, content)
    
    # Add new export functions
    export_kml_pattern = r'def exportProjectKML\(.*?\):\s+.*?self\.ui\.statusbar\.showMessage\(self\.tr\(\'Error saving the export\.\'\)\)'
    export_kml_pattern = re.compile(export_kml_pattern, re.DOTALL)
    
    new_export_functions = '''
    def exportProjectJSON(self, project=None, filtering=False):
        """Export project locations to GeoJSON format"""
        # If the project was not provided explicitly, analyze the currently selected one
        if not project:
            project = self.currentProject
        if not project:
            self.showWarning(self.tr('No project selected'), self.tr('Please select a project first'))
            self.ui.statusbar.showMessage(self.tr('Please select a project first'))
            return
        if not project.locations:
            self.showWarning(self.tr('No locations found'), self.tr('The selected project has no locations to be exported'))
            self.ui.statusbar.showMessage(self.tr('The selected project has no locations to be exported'))
            return

        fileName, _ = QFileDialog.getSaveFileName(None, self.tr('Save GeoJSON export as...'), 
                                              os.getcwd(), 'GeoJSON Files (*.json);;All files (*.*)')
        if fileName:
            if ExportUtils.export_to_json(project.locations, fileName, filtering):
                self.ui.statusbar.showMessage(self.tr('Project Locations have been exported successfully'))
            else:
                self.ui.statusbar.showMessage(self.tr('Error saving the export.'))
                
    def exportProjectHTML(self, project=None, filtering=False):
        """Export project locations to interactive HTML map"""
        # If the project was not provided explicitly, analyze the currently selected one
        if not project:
            project = self.currentProject
        if not project:
            self.showWarning(self.tr('No project selected'), self.tr('Please select a project first'))
            self.ui.statusbar.showMessage(self.tr('Please select a project first'))
            return
        if not project.locations:
            self.showWarning(self.tr('No locations found'), self.tr('The selected project has no locations to be exported'))
            self.ui.statusbar.showMessage(self.tr('The selected project has no locations to be exported'))
            return

        fileName, _ = QFileDialog.getSaveFileName(None, self.tr('Save HTML export as...'), 
                                              os.getcwd(), 'HTML Files (*.html);;All files (*.*)')
        if fileName:
            if ExportUtils.export_to_html(project.locations, fileName, filtering):
                self.ui.statusbar.showMessage(self.tr('Project Locations have been exported successfully'))
                # Ask if the user wants to open the HTML file in a browser
                reply = QMessageBox.question(self, 'Open HTML Map', 
                                          'Would you like to open the HTML map in your browser?',
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    import webbrowser
                    webbrowser.open('file://' + os.path.abspath(fileName))
            else:
                self.ui.statusbar.showMessage(self.tr('Error saving the export.'))
    
    def exportProjectCSV(self, project=None, filtering=False):
        # If the project was not provided explicitly, analyze the currently selected one
        if not project:
            project = self.currentProject
        if not project:
            self.showWarning(self.tr('No project selected'), self.tr('Please select a project first'))
            self.ui.statusbar.showMessage(self.tr('Please select a project first'))
            return
        if not project.locations:
            self.showWarning(self.tr('No locations found'), self.tr('The selected project has no locations to be exported'))
            self.ui.statusbar.showMessage(self.tr('The selected project has no locations to be exported'))
            return
        
        fileName, _ = QFileDialog.getSaveFileName(None, self.tr('Save CSV export as...'), os.getcwd(), 'CSV Files (*.csv);;All files (*.*)')
        if fileName:
            if ExportUtils.export_to_csv(project.locations, fileName, filtering):
                self.ui.statusbar.showMessage(self.tr('Project Locations have been exported successfully'))
            else:
                self.ui.statusbar.showMessage(self.tr('Error saving the export.'))

    def exportProjectKML(self, project=None, filtering=False):
        # If the project was not provided explicitly, analyze the currently selected one
        if not project:
            project = self.currentProject
        if not project:
            self.showWarning(self.tr('No project selected'), self.tr('Please select a project first'))
            self.ui.statusbar.showMessage(self.tr('Please select a project first'))
            return
        if not project.locations:
            self.showWarning(self.tr('No locations found'), self.tr('The selected project has no locations to be exported'))
            self.ui.statusbar.showMessage(self.tr('The selected project has no locations to be exported'))
            return
        
        fileName, _ = QFileDialog.getSaveFileName(None, self.tr('Save KML export as...'), os.getcwd(), 'KML Files (*.kml);;All files (*.*)')
        if fileName:
            if ExportUtils.export_to_kml(project.locations, fileName, filtering):
                self.ui.statusbar.showMessage(self.tr('Project Locations have been exported successfully'))
            else:
                self.ui.statusbar.showMessage(self.tr('Error saving the export.'))'''
    
    content = export_kml_pattern.sub(new_export_functions, content)
    
    plugin_manager = PluginManager()
    plugin_manager.load_plugins()

    # Example of updating exports for a specific plugin
    plugin = plugin_manager.get_plugin('example_plugin')
    if plugin:
        plugin.update_exports()
    
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Successfully updated {main_file} with new export functionality")

if __name__ == "__main__":
    update_main_app()
