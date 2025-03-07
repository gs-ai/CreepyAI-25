#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Plugin Requirements Manager for CreepyAI
Checks and installs missing dependencies for plugins
"""

import os
import sys
import subprocess
import logging
import importlib
import pkg_resources
from typing import Dict, List, Tuple, Any, Optional, Set

logger = logging.getLogger(__name__)

class PluginRequirements:
    """
    Utility class for managing plugin dependencies
    """
    
    def __init__(self, auto_install: bool = False):
        """
        Initialize the requirements manager
        
        Args:
            auto_install: Whether to automatically install missing dependencies
        """
        self.auto_install = auto_install
        self._installed_packages = self._get_installed_packages()
    
    def _get_installed_packages(self) -> Dict[str, str]:
        """Return a dictionary of installed Python packages and their versions"""
        installed = {}
        
        try:
            for pkg in pkg_resources.working_set:
                installed[pkg.project_name.lower()] = pkg.version
        except Exception as e:
            logger.error(f"Error getting installed packages: {e}")
        
        return installed
    
    def check_requirement(self, package_name: str, version: Optional[str] = None) -> Tuple[bool, str]:
        """
        Check if a Python package requirement is met
        
        Args:
            package_name: Name of the package to check
            version: Required version string (e.g. '>=1.0.0')
            
        Returns:
            (is_satisfied, message) tuple
        """
        package_name = package_name.lower()
        
        # First check if the package is installed
        if package_name not in self._installed_packages:
            return False, f"Package '{package_name}' is not installed"
        
        # If no version requirement, consider it satisfied
        if not version:
            return True, f"Package '{package_name}' is installed"
        
        installed_version = self._installed_packages[package_name]
        
        # Parse version requirement
        try:
            requirement = pkg_resources.Requirement.parse(f"{package_name}{version}")
            if pkg_resources.parse_version(installed_version) in requirement:
                return True, f"Package '{package_name}' version {installed_version} meets requirement {version}"
            else:
                return False, f"Package '{package_name}' version {installed_version} does not meet requirement {version}"
        except Exception as e:
            logger.error(f"Error checking version requirement: {e}")
            # Fall back to simple string comparison if parsing fails
            if version.startswith(">=") and installed_version >= version[2:]:
                return True, f"Package '{package_name}' version {installed_version} meets requirement {version}"
            elif version.startswith(">") and installed_version > version[1:]:
                return True, f"Package '{package_name}' version {installed_version} meets requirement {version}"
            elif version.startswith("<=") and installed_version <= version[2:]:
                return True, f"Package '{package_name}' version {installed_version} meets requirement {version}"
            elif version.startswith("<") and installed_version < version[1:]:
                return True, f"Package '{package_name}' version {installed_version} meets requirement {version}"
            elif version.startswith("==") and installed_version == version[2:]:
                return True, f"Package '{package_name}' version {installed_version} meets requirement {version}"
            else:
                return False, f"Package '{package_name}' version {installed_version} does not meet requirement {version}"
    
    def install_requirement(self, package_name: str, version: Optional[str] = None) -> Tuple[bool, str]:
        """
        Install a Python package requirement
        
        Args:
            package_name: Name of the package to install
            version: Required version string (e.g. '>=1.0.0')
            
        Returns:
            (is_successful, message) tuple
        """
        if not package_name:
            return False, "No package name provided"
            
        # Construct the installation target
        if version:
            if version.startswith("==") or version.startswith(">=") or \
               version.startswith("<=") or version.startswith(">") or version.startswith("<"):
                target = f"{package_name}{version}"
            else:
                target = f"{package_name}=={version}"
        else:
            target = package_name
            
        # Execute pip install
        try:
            logger.info(f"Installing Python package: {target}")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", target],
                capture_output=True,
                text=True,
                check=False  # Don't raise exception on error
            )
            
            if result.returncode == 0:
                # Update installed packages cache
                self._installed_packages = self._get_installed_packages()
                return True, f"Successfully installed {target}"
            else:
                error_msg = result.stderr.strip()
                logger.error(f"Error installing {target}: {error_msg}")
                return False, f"Failed to install {target}: {error_msg}"
                
        except Exception as e:
            logger.error(f"Error installing {target}: {e}")
            return False, f"Failed to install {target}: {str(e)}"
    
    def check_requirements(self, requirements: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Check a list of requirements and optionally install missing ones
        
        Args:
            requirements: List of requirement dictionaries with 'package' and optional 'version' keys
            
        Returns:
            List of dictionaries containing check results
        """
        results = []
        
        for req in requirements:
            package = req.get('package', '').strip()
            version = req.get('version', '').strip() or None
            
            if not package:
                continue
                
            # Check if requirement is satisfied
            satisfied, message = self.check_requirement(package, version)
            result = {
                'package': package,
                'version': version,
                'satisfied': satisfied,
                'message': message,
                'installed': False
            }
            
            # If not satisfied and auto_install is True, try to install it
            if not satisfied and self.auto_install:
                success, install_message = self.install_requirement(package, version)
                result['installed'] = success
                result['install_message'] = install_message
                
                # Re-check after installation
                if success:
                    satisfied, message = self.check_requirement(package, version)
                    result['satisfied'] = satisfied
                    result['message'] = message
            
            results.append(result)
            
        return results
    
    def check_module_exists(self, module_name: str) -> bool:
        """
        Check if a Python module can be imported
        
        Args:
            module_name: Name of the module to check
            
        Returns:
            True if the module exists, False otherwise
        """
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False
    
    @staticmethod
    def get_common_plugin_requirements() -> Dict[str, List[Dict[str, str]]]:
        """
        Return common requirements for various plugin types
        
        Returns:
            Dictionary mapping plugin type to list of requirement dictionaries
        """
        return {
            'social_media': [
                {'package': 'requests'},
                {'package': 'beautifulsoup4'},
                {'package': 'html5lib'},
                {'package': 'lxml', 'version': '>=4.0.0'}
            ],
            'image_processing': [
                {'package': 'pillow', 'version': '>=7.0.0'},
                {'package': 'exifread'},
                {'package': 'opencv-python-headless'}
            ],
            'geocoding': [
                {'package': 'geopy'},
                {'package': 'reverse_geocoder'},
                {'package': 'shapely'}
            ],
            'network': [
                {'package': 'requests'},
                {'package': 'urllib3'},
                {'package': 'scapy'}
            ],
            'document_processing': [
                {'package': 'pdfminer.six'},
                {'package': 'python-docx'},
                {'package': 'openpyxl'}
            ],
            'data_analysis': [
                {'package': 'pandas'},
                {'package': 'numpy'},
                {'package': 'matplotlib'}
            ]
        }
