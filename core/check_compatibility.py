#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CreepyAI Compatibility Checker
------------------------------
This script checks the compatibility of dependencies with the current Python version
and suggests compatible versions.
"""

import os
import sys
import platform
import logging
import subprocess
import re
import pkg_resources
from packaging.version import parse
import importlib

logger = logging.getLogger('CreepyAI.Compatibility')

def get_python_version():
    """Get the current Python version"""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def get_max_compatible_version(package_name, python_version):
    """Find the maximum compatible version of a package for the current Python version"""
    try:
        # Get all available versions
        result = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", package_name],
            capture_output=True,
            text=True
        )
        
        output = result.stdout
        
        # Parse output to find available versions
        available_versions = re.findall(r'Available versions: (.*)', output)
        if not available_versions:
            return None
            
        version_list = available_versions[0].split(", ")
        compatible_versions = []
        
        # Check each version for compatibility
        for version_str in version_list:
            try:
                # Try to find version in PyPI without installing
                metadata = subprocess.run(
                    [sys.executable, "-m", "pip", "install", f"{package_name}=={version_str}", "--dry-run"],
                    capture_output=True,
                    text=True
                )
                
                # If no Python version error, it's compatible
                if "Requires-Python" not in metadata.stderr:
                    compatible_versions.append(version_str)
            except Exception:
                continue
                
        if compatible_versions:
            # Sort versions and return the highest
            sorted_versions = sorted(compatible_versions, key=parse)
            return sorted_versions[-1]
        
        return None
    
    except Exception as e:
        print(f"Error checking {package_name}: {e}")
        return None

def check_requirements_file(file_path):
    """Check and suggest fixes for requirements file"""
    python_version = get_python_version()
    print(f"Checking compatibility with Python {python_version}")
    
    with open(file_path, 'r') as f:
        requirements = f.readlines()
    
    new_requirements = []
    incompatible_found = False
    
    for req in requirements:
        req = req.strip()
        if not req or req.startswith('#'):
            new_requirements.append(req)
            continue
            
        # Parse requirement
        try:
            package_req = pkg_resources.Requirement.parse(req)
            package_name = package_req.name
            
            # Check if already installed
            try:
                pkg_resources.get_distribution(req)
                print(f"✓ {req} - Already installed and compatible")
                new_requirements.append(req)
            except pkg_resources.DistributionNotFound:
                print(f"! {req} - Not installed, checking compatibility...")
                compatible_version = get_max_compatible_version(package_name, python_version)
                
                if compatible_version:
                    new_req = f"{package_name}=={compatible_version}"
                    print(f"  Suggested replacement: {new_req}")
                    new_requirements.append(new_req)
                    incompatible_found = True
                else:
                    print(f"  No compatible version found for {package_name}")
                    new_requirements.append(f"# {req} - No compatible version found for Python {python_version}")
                    incompatible_found = True
            except pkg_resources.VersionConflict:
                print(f"! {req} - Version conflict, checking compatibility...")
                compatible_version = get_max_compatible_version(package_name, python_version)
                
                if compatible_version:
                    new_req = f"{package_name}=={compatible_version}"
                    print(f"  Suggested replacement: {new_req}")
                    new_requirements.append(new_req)
                    incompatible_found = True
                else:
                    print(f"  No compatible version found for {package_name}")
                    new_requirements.append(f"# {req} - No compatible version found for Python {python_version}")
                    incompatible_found = True
        except Exception as e:
            print(f"Error parsing requirement {req}: {e}")
            new_requirements.append(req)
    
    if incompatible_found:
        backup_path = file_path + ".bak"
        with open(backup_path, 'w') as f:
            f.write("\n".join(requirements))
        
        response = input("Would you like to update your requirements.txt with compatible versions? (y/N): ")
        if response.lower() == 'y':
            with open(file_path, 'w') as f:
                f.write("\n".join(new_requirements))
            print(f"Updated {file_path} with compatible versions. Original backed up to {backup_path}")
        else:
            print("No changes made to requirements.txt")
    else:
        print("All requirements are compatible. No changes needed.")

def check_system_compatibility():
    """
    Check if the system is compatible with CreepyAI requirements
    
    Returns:
        bool: True if system is compatible, False otherwise
    """
    logger.info("Checking system compatibility...")
    
    # Check Python version
    python_version = sys.version_info
    if (python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6)):
        logger.error(f"Incompatible Python version: {platform.python_version()}")
        logger.error("CreepyAI requires Python 3.6 or higher")
        return False
    
    # Check required packages
    required_packages = [
        'PyQt5', 'yapsy', 'configobj', 'folium', 'geopy', 'requests',
        'pillow', 'matplotlib', 'pandas', 'numpy'
    ]
    
    # Optional packages that enhance functionality but aren't required
    optional_packages = [
        'simplekml',   # For KML export
        'packaging',   # For version parsing
        'openpyxl',    # For Excel export
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)
    
    missing_optional = []
    for package in optional_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_optional.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install missing packages using: pip install -r requirements.txt")
        return False
    
    if missing_optional:
        logger.warning(f"Missing optional packages: {', '.join(missing_optional)}")
        logger.warning("Some features may be limited. Install these packages for full functionality.")
    
    # Check for plugins directory
    plugins_dir = os.path.join(os.getcwd(), 'plugins')
    if not os.path.exists(plugins_dir) or not os.path.isdir(plugins_dir):
        logger.error(f"Plugins directory not found at: {plugins_dir}")
        return False
    
    # Check for essential files
    essential_files = [
        os.path.join('creepy', 'include', 'creepy_resources.qrc'),
        os.path.join('creepy', 'include', 'map.html'),
        os.path.join('creepy', 'include', 'style.qss'),
    ]
    
    for file_path in essential_files:
        full_path = os.path.join(os.getcwd(), file_path)
        if not os.path.exists(full_path):
            logger.error(f"Essential file not found: {full_path}")
            return False
    
    logger.info("System compatibility check passed")
    return True

def get_incompatibility_details():
    """
    Get detailed information about incompatibilities
    
    Returns:
        list: List of incompatibility details
    """
    incompatibilities = []
    
    # Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        incompatibilities.append({
            'type': 'Python Version',
            'issue': f"Incompatible Python version: {platform.python_version()}",
            'resolution': 'Install Python 3.6 or higher',
            'critical': True
        })
    
    # Check packages
    required_packages = [
        'PyQt5', 'yapsy', 'configobj', 'folium', 'geopy', 'requests',
        'pillow', 'matplotlib', 'pandas', 'numpy'
    ]
    
    optional_packages = [
        'simplekml',   # For KML export
        'packaging',   # For version parsing
        'openpyxl',    # For Excel export
    ]
    
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            incompatibilities.append({
                'type': 'Missing Package',
                'issue': f"Package '{package}' is not installed",
                'resolution': f"Install using: pip install {package}",
                'critical': True
            })
    
    for package in optional_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            incompatibilities.append({
                'type': 'Missing Optional Package',
                'issue': f"Optional package '{package}' is not installed",
                'resolution': f"Install using: pip install {package}",
                'critical': False
            })
    
    # Check plugins directory
    plugins_dir = os.path.join(os.getcwd(), 'plugins')
    if not os.path.exists(plugins_dir):
        incompatibilities.append({
            'type': 'Missing Directory',
            'issue': f"Plugins directory not found at: {plugins_dir}",
            'resolution': 'Create plugins directory and install plugins',
            'critical': True
        })
    
    return incompatibilities

def check_compatibility():
    """
    Check system compatibility for running CreepyAI.
    
    Returns:
        bool: True if system is compatible, False otherwise
    """
    compatibility_issues = []
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        compatibility_issues.append(f"Python version {python_version.major}.{python_version.minor} is not supported. Minimum required is 3.7")
    
    # Check for required modules
    required_modules = [
        "PyQt5",
        "PyQt5.QtWebEngineWidgets",
        "requests",
        "bs4",
        "yapsy"
    ]
    
    for module in required_modules:
        if not importlib.util.find_spec(module):
            compatibility_issues.append(f"Required module '{module}' is not installed")
    
    # Platform-specific checks
    system = platform.system()
    if system == "Windows":
        # Check Windows-specific requirements
        pass
    elif system == "Linux":
        # Check Linux-specific requirements
        pass
    elif system == "Darwin":
        # Check macOS-specific requirements
        pass
    else:
        compatibility_issues.append(f"Unsupported operating system: {system}")
    
    # Log compatibility issues
    if compatibility_issues:
        for issue in compatibility_issues:
            logger.warning(f"Compatibility issue: {issue}")
        return False
    
    logger.info("System compatibility check passed")
    return True

def get_compatibility_status():
    """
    Get detailed compatibility status.
    
    Returns:
        dict: Compatibility status information
    """
    status = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": platform.system(),
        "platform_version": platform.version(),
        "modules": {}
    }
    
    # Check modules
    modules_to_check = [
        "PyQt5", "PyQt5.QtWebEngineWidgets", "requests", "bs4", 
        "yapsy", "folium", "PIL", "simplekml"
    ]
    
    for module in modules_to_check:
        try:
            imported_module = importlib.import_module(module)
            version = getattr(imported_module, "__version__", "Unknown")
            status["modules"][module] = {
                "installed": True,
                "version": version
            }
        except ImportError:
            status["modules"][module] = {
                "installed": False,
                "version": None
            }
    
    return status

if __name__ == "__main__":
    # Configure logging when run directly
    logging.basicConfig(level=logging.INFO)
    
    # Run compatibility check
    is_compatible = check_system_compatibility()
    
    if not is_compatible:
        print("System compatibility check failed. See above for details.")
        sys.exit(1)
    else:
        print("System is compatible with CreepyAI.")
        sys.exit(0)
