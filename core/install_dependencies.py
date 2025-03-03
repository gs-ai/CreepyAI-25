#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import logging
import platform
import argparse

logger = logging.getLogger(__name__)

# Define dependencies
REQUIRED_PACKAGES = [
    "PyQt5",
    "PyQt5-WebEngine",
    "beautifulsoup4",
    "requests",
    "yapsy",
    "folium",
    "Pillow",
    "geopy",
    "sqlite3"
]

OPTIONAL_PACKAGES = [
    "simplekml",
    "pandas",
    "matplotlib"
]

def check_package_installed(package):
    """Check if a package is installed."""
    try:
        __import__(package.split("==")[0])
        return True
    except ImportError:
        return False

def install_package(package):
    """Install a package using pip."""
    try:
        logger.info(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package}: {e}")
        return False

def install_missing_dependencies(include_optional=False):
    """Install missing dependencies."""
    packages_to_install = []
    
    # Check required packages
    for package in REQUIRED_PACKAGES:
        package_name = package.split("==")[0]
        if not check_package_installed(package_name):
            packages_to_install.append(package)
    
    # Check optional packages if requested
    if include_optional:
        for package in OPTIONAL_PACKAGES:
            package_name = package.split("==")[0]
            if not check_package_installed(package_name):
                packages_to_install.append(package)
    
    # Install missing packages
    if packages_to_install:
        logger.info(f"Installing {len(packages_to_install)} missing packages...")
        for package in packages_to_install:
            install_package(package)
        
        logger.info("Dependencies installed.")
        return True
    else:
        logger.info("All dependencies are already installed.")
        return True

def install_system_dependencies():
    """Install system-level dependencies."""
    system = platform.system()
    
    if system == "Linux":
        try:
            # Check for pip
            if not shutil.which("pip"):
                subprocess.check_call(["sudo", "apt-get", "update"])
                subprocess.check_call(["sudo", "apt-get", "install", "-y", "python3-pip"])
            
            # Install PyQt5 dependencies
            subprocess.check_call(["sudo", "apt-get", "install", "-y", "python3-pyqt5", "python3-pyqt5.qtwebengine"])
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install system dependencies: {e}")
            return False
            
    elif system == "Darwin":  # macOS
        try:
            # Check for Homebrew
            if not shutil.which("brew"):
                logger.info("Installing Homebrew...")
                subprocess.check_call(["/bin/bash", "-c", "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"])
            
            # Install PyQt5
            subprocess.check_call(["brew", "install", "pyqt5"])
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install system dependencies: {e}")
            return False
    
    # For Windows, we rely on pip to install everything
    return True

def create_virtual_environment(venv_path=None):
    """Create a virtual environment."""
    if not venv_path:
        venv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "creepyai25ENV")
    
    try:
        # Create virtual environment
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
        
        # Get paths
        if platform.system() == "Windows":
            pip_path = os.path.join(venv_path, "Scripts", "pip")
            python_path = os.path.join(venv_path, "Scripts", "python")
        else:
            pip_path = os.path.join(venv_path, "bin", "pip")
            python_path = os.path.join(venv_path, "bin", "python")
        
        # Upgrade pip
        subprocess.check_call([python_path, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install required packages
        for package in REQUIRED_PACKAGES:
            subprocess.check_call([pip_path, "install", package])
        
        logger.info(f"Virtual environment created at {venv_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create virtual environment: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Install dependencies for CreepyAI")
    parser.add_argument("--optional", action="store_true", help="Install optional dependencies")
    parser.add_argument("--system", action="store_true", help="Install system-level dependencies")
    parser.add_argument("--venv", action="store_true", help="Create a virtual environment")
    parser.add_argument("--venv-path", help="Path for the virtual environment")
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    if args.system:
        install_system_dependencies()
    
    if args.venv:
        create_virtual_environment(args.venv_path)
    else:
        install_missing_dependencies(args.optional)
    
    logger.info("Dependency installation complete.")

if __name__ == "__main__":
    main()
