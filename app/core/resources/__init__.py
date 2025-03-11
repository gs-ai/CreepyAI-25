"""
CreepyAI resources package.
Provides centralized access to application resources.
"""
import os
import sys
import logging

# Ensure proper import paths
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.core.path_utils import get_app_root, normalize_path

# Define common resource paths
APP_ROOT = get_app_root()
RESOURCES_DIR = os.path.dirname(os.path.abspath(__file__))

# Resource subdirectories
ASSETS_DIR = os.path.join(RESOURCES_DIR, 'assets')
TEMPLATES_DIR = os.path.join(RESOURCES_DIR, 'templates')
STYLES_DIR = os.path.join(RESOURCES_DIR, 'styles')
HTML_DIR = os.path.join(RESOURCES_DIR, 'html')
DATA_DIR = os.path.join(RESOURCES_DIR, 'data')

__all__ = ['RESOURCES_DIR', 'ASSETS_DIR', 'TEMPLATES_DIR', 'STYLES_DIR', 'HTML_DIR', 'DATA_DIR']
