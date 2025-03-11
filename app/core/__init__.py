"""
Core components for CreepyAI
"""
import os
import sys
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Ensure core package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

__all__ = []

# Import core utilities safely
try:
    from app.core.path_utils import (
        get_app_root,
        normalize_path,
        ensure_app_dirs,
        get_dir,
        find_file
    )
    __all__.extend([
        'get_app_root',
        'normalize_path',
        'ensure_app_dirs',
        'get_dir',
        'find_file',
    ])
except ImportError as e:
    logger.debug(f"Could not import path_utils: {repr(e)}")

try:
    from app.core.import_helper import (
        import_module_from_path,
        dynamic_import,
        ensure_imports
    )
    __all__.extend([
        'import_module_from_path',
        'dynamic_import',
        'ensure_imports',
    ])
except ImportError as e:
    logger.debug(f"Could not import import_helper: {repr(e)}")

try:
    from app.core.engine import CreepyAIEngine
    __all__.append('CreepyAIEngine')
except ImportError as e:
    logger.debug(f"Could not import engine: {repr(e)}")

try:
    from app.core.config import Configuration
    __all__.append('Configuration')
except ImportError as e:
    logger.debug(f"Could not import config: {repr(e)}")