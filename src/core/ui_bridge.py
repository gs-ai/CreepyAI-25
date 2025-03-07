"""
UI Bridge - Provides compatibility between PyQt5 and Tkinter UI implementations
"""
import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class UIBridge:
    """
    Bridge class to translate between PyQt5 and Tkinter implementations.
    Allows the core functionality to work with either UI.
    """
    
    def __init__(self):
        """Initialize the bridge"""
        self.ui_type = self._detect_ui_type()
        logger.info(f"Initialized UI Bridge with UI type: {self.ui_type}")
    
    def _detect_ui_type(self) -> str:
        """Detect which UI is being used"""
        try:
            import tkinter
            return "tkinter"
        except ImportError:
            try:
                from PyQt5 import QtCore
                return "pyqt5"
            except ImportError:
                logger.error("Neither PyQt5 nor Tkinter is available")
                return "unknown"
    
    def translate_project(self, project: Any) -> Dict:
        """
        Translate a PyQt5 project object to a format usable by Tkinter
        """
        if self.ui_type == "tkinter":
            # Convert from PyQt5 Project to dict for Tkinter
            project_dict = {
                "project_name": getattr(project, "projectName", ""),
                "project_keywords": getattr(project, "projectKeywords", []),
                "project_description": getattr(project, "projectDescription", ""),
                "date_created": getattr(project, "dateCreated", None),
                "date_edited": getattr(project, "dateEdited", None),
                "locations": []
            }
            
            # Convert locations
            locations = getattr(project, "locations", [])
            for loc in locations:
                location_dict = {
                    "plugin": getattr(loc, "plugin", ""),
                    "datetime": getattr(loc, "datetime", None),
                    "longitude": getattr(loc, "longitude", 0.0),
                    "latitude": getattr(loc, "latitude", 0.0),
                    "context": getattr(loc, "context", ""),
                    "infowindow": getattr(loc, "infowindow", ""),
                    "shortName": getattr(loc, "shortName", ""),
                    "visible": getattr(loc, "visible", True)
                }
                project_dict["locations"].append(location_dict)
                
            return project_dict
        else:
            # Already in PyQt5 format
            return project
    
    def translate_locations(self, locations: List) -> List[Dict]:
        """
        Translate locations from PyQt5 format to Tkinter-friendly format
        """
        location_list = []
        
        for loc in locations:
            if hasattr(loc, "latitude"):  # This is a PyQt5 location object
                location_dict = {
                    "plugin": getattr(loc, "plugin", ""),
                    "datetime": getattr(loc, "datetime", None),
                    "longitude": getattr(loc, "longitude", 0.0),
                    "latitude": getattr(loc, "latitude", 0.0),
                    "context": getattr(loc, "context", ""),
                    "infowindow": getattr(loc, "infowindow", ""),
                    "shortName": getattr(loc, "shortName", ""),
                    "visible": getattr(loc, "visible", True)
                }
                location_list.append(location_dict)
            else:  # Already a dict
                location_list.append(loc)
                
        return location_list
    
    def get_plugin_paths(self) -> List[str]:
        """
        Get the plugin paths for the current system
        """
        base_path = os.getcwd()
        plugin_paths = [
            os.path.join(base_path, 'plugins'),
        ]
        
        # Add user-specific plugin paths based on platform
        if sys.platform == 'darwin':  # macOS
            plugin_paths.append(os.path.expanduser("~/.config/creepyai/plugins"))
        elif sys.platform == 'win32':  # Windows
            plugin_paths.append(os.path.expanduser("~/AppData/Local/CreepyAI/plugins"))
        else:  # Linux and others
            plugin_paths.append(os.path.expanduser("~/.local/share/creepyai/plugins"))
            
        return plugin_paths
    
    def save_project_to_json(self, project: Any, file_path: str) -> bool:
        """
        Save a project to a JSON file that can be used by either UI
        """
        try:
            project_dict = self.translate_project(project)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Convert datetime objects to strings
            if "date_created" in project_dict and project_dict["date_created"]:
                project_dict["date_created"] = project_dict["date_created"].isoformat()
            if "date_edited" in project_dict and project_dict["date_edited"]:
                project_dict["date_edited"] = project_dict["date_edited"].isoformat()
                
            for loc in project_dict.get("locations", []):
                if "datetime" in loc and loc["datetime"]:
                    loc["datetime"] = loc["datetime"].isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_dict, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save project to JSON: {e}")
            return False
    
    def load_project_from_json(self, file_path: str) -> Optional[Dict]:
        """
        Load a project from a JSON file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                project_dict = json.load(f)
            
            return project_dict
        except Exception as e:
            logger.error(f"Failed to load project from JSON: {e}")
            return None
