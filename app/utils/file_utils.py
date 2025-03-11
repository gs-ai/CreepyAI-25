"""
File utilities for CreepyAI.
"""
import os
import sys
import shutil
import logging
import tempfile
import mimetypes
import hashlib
from pathlib import Path
from typing import List, Optional, Set, Tuple, Union, Dict, Any

# Add core to path so we can import path utilities
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'core')))
try:
    from path_utils import normalize_path, get_app_root
except ImportError:
    # Fallback if import fails
    def normalize_path(path):
        if not path:
            return path
        return os.path.normpath(os.path.expanduser(path))
        
    def get_app_root():
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

def ensure_directory(directory: str) -> bool:
    """Ensure directory exists.
    
    Args:
        directory: Directory to ensure exists
        
    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        return False

def copy_file(source: str, destination: str, overwrite: bool = False) -> bool:
    """Copy file with error handling.
    
    Args:
        source: Source file path
        destination: Destination file path
        overwrite: Whether to overwrite if destination exists
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Normalize paths
        source = normalize_path(source)
        destination = normalize_path(destination)
        
        if not os.path.exists(source):
            logger.error(f"Source file doesn't exist: {source}")
            return False
            
        if os.path.exists(destination) and not overwrite:
            logger.warning(f"Destination file exists and overwrite is False: {destination}")
            return False
            
        # Create destination directory if it doesn't exist
        dest_dir = os.path.dirname(destination)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
            
        shutil.copy2(source, destination)
        logger.debug(f"File copied from {source} to {destination}")
        return True
    except Exception as e:
        logger.error(f"Error copying file from {source} to {destination}: {e}")
        return False

def safe_delete(path: str) -> bool:
    """Delete file or directory safely.
    
    Args:
        path: Path to delete
        
    Returns:
        True if deleted or didn't exist, False on error
    """
    try:
        if not os.path.exists(path):
            return True
            
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
            
        logger.debug(f"Deleted: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete {path}: {e}")
        return False

def get_file_hash(filepath: str, algorithm: str = 'md5') -> Optional[str]:
    """Get hash of file contents.
    
    Args:
        filepath: Path to file
        algorithm: Hash algorithm (md5, sha1, sha256)
        
    Returns:
        Hex digest hash string or None if error
    """
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        logger.error(f"File doesn't exist: {filepath}")
        return None
        
    try:
        hash_obj = getattr(hashlib, algorithm)()
        
        with open(filepath, 'rb') as f:
            # Read file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
                
        return hash_obj.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {filepath}: {e}")
        return None

def find_files(directory: str, extensions: List[str] = None, recursive: bool = True) -> List[str]:
    """Find files with specific extensions.
    
    Args:
        directory: Directory to search
        extensions: List of file extensions to find (e.g. ['.jpg', '.png'])
        recursive: Whether to search recursively
        
    Returns:
        List of absolute paths to matching files
    """
    if not os.path.exists(directory) or not os.path.isdir(directory):
        logger.error(f"Directory doesn't exist: {directory}")
        return []
        
    matching_files = []
    
    try:
        if recursive:
            for root, _, files in os.walk(directory):
                for filename in files:
                    if not extensions or any(filename.lower().endswith(ext.lower()) for ext in extensions):
                        matching_files.append(os.path.join(root, filename))
        else:
            for entry in os.scandir(directory):
                if entry.is_file() and (not extensions or any(entry.name.lower().endswith(ext.lower()) for ext in extensions)):
                    matching_files.append(entry.path)
                    
        return matching_files
    except Exception as e:
        logger.error(f"Error finding files in {directory}: {e}")
        return []

def get_mime_type(filepath: str) -> Optional[str]:
    """Get MIME type of file.
    
    Args:
        filepath: Path to file
        
    Returns:
        MIME type string or None if error
    """
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        return None
        
    # Ensure MIME types are initialized
    if not mimetypes.inited:
        mimetypes.init()
        
    mime_type, _ = mimetypes.guess_type(filepath)
    return mime_type
