#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Utility functions and classes for CreepyAI plugins
"""

import os
import sys
import logging
import tempfile
import shutil
import zipfile
import json
import csv
import re
import glob
import hashlib
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Generator

logger = logging.getLogger(__name__)

class TemporaryDirectory:
    """
    Context manager for creating and cleaning up temporary directories.
    More robust than tempfile.TemporaryDirectory, with better error handling.
    """
    
    def __init__(self, suffix=None, prefix=None, dir=None, keep_on_error=False):
        self.suffix = suffix
        self.prefix = prefix
        self.dir = dir
        self.keep_on_error = keep_on_error
        self.path = None
        self.clean = True
        
    def __enter__(self):
        try:
            self.path = tempfile.mkdtemp(suffix=self.suffix, prefix=self.prefix, dir=self.dir)
            return self.path
        except Exception as e:
            self.clean = False
            logger.error(f"Error creating temporary directory: {e}")
            raise
            
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.path:
            return
            
        # Check if we should keep the directory
        if exc_type is not None and self.keep_on_error:
            logger.warning(f"Error occurred but keeping temporary directory: {self.path}")
            self.clean = False
            
        if self.clean:
            try:
                shutil.rmtree(self.path)
            except Exception as e:
                logger.warning(f"Error removing temporary directory {self.path}: {e}")


def extract_archive(archive_path: str, extract_to: Optional[str] = None, 
                   password: Optional[str] = None) -> str:
    """
    Extract an archive (zip, tar, etc.) to a directory
    
    Args:
        archive_path: Path to the archive file
        extract_to: Directory to extract to (if None, creates temp dir)
        password: Optional password for encrypted archives
        
    Returns:
        Path to the directory containing extracted files
    """
    # Determine if we need to create a temp dir
    created_temp_dir = False
    if not extract_to:
        extract_to = tempfile.mkdtemp(prefix="creepyai_extract_")
        created_temp_dir = True
    
    try:
        # Make sure the target directory exists
        os.makedirs(extract_to, exist_ok=True)
        
        # Check if it's a ZIP file
        if zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                # Check if password is needed
                if password and any(zipinfo.flag_bits & 0x1 for zipinfo in zip_ref.infolist()):
                    # Extract each file with password
                    for zipinfo in zip_ref.infolist():
                        target_path = os.path.join(extract_to, zipinfo.filename)
                        
                        # Create directories if needed
                        if zipinfo.filename.endswith('/'):
                            os.makedirs(target_path, exist_ok=True)
                            continue
                            
                        # Create parent directories if needed
                        parent_dir = os.path.dirname(target_path)
                        if parent_dir and not os.path.exists(parent_dir):
                            os.makedirs(parent_dir, exist_ok=True)
                            
                        # Extract the file with password
                        with zip_ref.open(zipinfo.filename, pwd=password.encode() if password else None) as source, \
                             open(target_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                else:
                    # Extract all without password
                    zip_ref.extractall(extract_to)
        else:
            # Try using shutil.unpack_archive for other archive types
            shutil.unpack_archive(archive_path, extract_to)
            
        return extract_to
        
    except Exception as e:
        # Clean up temp dir if we created it and there was an error
        if created_temp_dir and os.path.exists(extract_to):
            try:
                shutil.rmtree(extract_to)
            except:
                pass
        logger.error(f"Error extracting archive {archive_path}: {e}")
        raise


def find_files(directory: str, patterns: List[str], recursive: bool = True,
              exclude_patterns: Optional[List[str]] = None) -> List[str]:
    """
    Find files in a directory matching specified patterns
    
    Args:
        directory: Directory to search in
        patterns: List of glob patterns to match
        recursive: Whether to search recursively
        exclude_patterns: List of patterns to exclude
        
    Returns:
        List of matching file paths
    """
    result = []
    if not os.path.exists(directory):
        return result
        
    # Normalize exclude patterns
    if exclude_patterns is None:
        exclude_patterns = []
    exclude_regexes = [re.compile(p) for p in exclude_patterns]
    
    # Find files matching the patterns
    for pattern in patterns:
        if recursive:
            pattern_paths = glob.glob(os.path.join(directory, "**", pattern), recursive=True)
        else:
            pattern_paths = glob.glob(os.path.join(directory, pattern))
            
        # Apply exclusions
        for path in pattern_paths:
            rel_path = os.path.relpath(path, directory)
            excluded = False
            
            for regex in exclude_regexes:
                if regex.search(rel_path):
                    excluded = True
                    break
                    
            if not excluded:
                result.append(path)
    
    return result


def compute_file_hash(file_path: str, hash_type: str = 'sha256', block_size: int = 65536) -> str:
    """
    Compute the hash of a file
    
    Args:
        file_path: Path to the file
        hash_type: Hash algorithm to use ('md5', 'sha1', 'sha256', etc.)
        block_size: Size of blocks to read (affects memory usage)
        
    Returns:
        Hash string in hexadecimal format
    """
    if not os.path.isfile(file_path):
        raise ValueError(f"File not found: {file_path}")
        
    hash_obj = getattr(hashlib, hash_type)()
    
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            hash_obj.update(data)
            
    return hash_obj.hexdigest()


def detect_file_type(file_path: str) -> Dict[str, Any]:
    """
    Detect file type and metadata without relying on external libraries
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dict containing file type information and basic metadata
    """
    result = {
        'path': file_path,
        'name': os.path.basename(file_path),
        'extension': os.path.splitext(file_path)[1].lower(),
        'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)) if os.path.exists(file_path) else None,
        'created': datetime.fromtimestamp(os.path.getctime(file_path)) if os.path.exists(file_path) else None,
        'type': 'unknown',
        'mime_type': None,
    }
    
    # Try to determine the MIME type
    import mimetypes
    mime_type, encoding = mimetypes.guess_type(file_path)
    if mime_type:
        result['mime_type'] = mime_type
        
        # Categorize by MIME type
        if mime_type.startswith('image/'):
            result['type'] = 'image'
        elif mime_type.startswith('video/'):
            result['type'] = 'video'
        elif mime_type.startswith('audio/'):
            result['type'] = 'audio'
        elif mime_type.startswith('text/'):
            result['type'] = 'text'
        elif mime_type == 'application/pdf':
            result['type'] = 'pdf'
        elif 'officedocument' in mime_type:
            result['type'] = 'office'
        elif mime_type in ['application/zip', 'application/x-tar', 'application/gzip']:
            result['type'] = 'archive'
            
    # If we couldn't determine by MIME type, try by extension
    if result['type'] == 'unknown':
        ext = result['extension']
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff']:
            result['type'] = 'image'
        elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']:
            result['type'] = 'video'
        elif ext in ['.mp3', '.wav', '.aac', '.ogg', '.flac']:
            result['type'] = 'audio'
        elif ext in ['.txt', '.log', '.md', '.json', '.xml', '.html', '.csv']:
            result['type'] = 'text'
        elif ext == '.pdf':
            result['type'] = 'pdf'
        elif ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
            result['type'] = 'office'
        elif ext in ['.zip', '.tar', '.gz', '.bz2', '.7z', '.rar']:
            result['type'] = 'archive'
            
    return result


def safe_convert_to_csv(data: List[Dict[str, Any]], output_file: str, 
                       field_names: Optional[List[str]] = None) -> bool:
    """
    Safely convert a list of dictionaries to CSV file
    
    Args:
        data: List of dictionaries to convert
        output_file: Path to output CSV file
        field_names: List of field names to include (if None, uses all fields)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Make sure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        # Determine field names if not provided
        if not field_names and data:
            # Use keys from all dictionaries to ensure we capture all fields
            field_set = set()
            for item in data:
                field_set.update(item.keys())
            field_names = sorted(list(field_set))
            
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(data)
            
        return True
        
    except Exception as e:
        logger.error(f"Error converting data to CSV: {e}")
        return False


def safe_json_serialize(obj: Any) -> Any:
    """
    Safely serialize objects to JSON, handling non-serializable types
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON-serializable version of the object
    """
    if isinstance(obj, dict):
        return {k: safe_json_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [safe_json_serialize(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    elif hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
        return safe_json_serialize(obj.to_dict())
    else:
        # Try to convert to string for unserializable types
        try:
            return str(obj)
        except:
            return None


class DataChunker:
    """
    Helper class for processing large datasets in manageable chunks
    with memory efficiency and progress tracking.
    """
    
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
        self.total_processed = 0
        self.start_time = None
        
    def chunk_file(self, file_path: str, skip_header: bool = False) -> Generator[List[str], None, None]:
        """
        Yield chunks of lines from a file
        
        Args:
            file_path: Path to the file to chunk
            skip_header: Whether to skip the first line (header)
            
        Yields:
            Lists of lines from the file
        """
        self.start_time = datetime.now()
        self.total_processed = 0
        
        chunk = []
        header = None
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Handle header if needed
            if skip_header:
                header = f.readline().strip()
                
            # Process file in chunks
            for line in f:
                chunk.append(line.strip())
                
                if len(chunk) >= self.chunk_size:
                    self.total_processed += len(chunk)
                    yield chunk
                    chunk = []
                    
            # Don't forget the last chunk
            if chunk:
                self.total_processed += len(chunk)
                yield chunk
                
    def chunk_json_array(self, json_file: str) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Yield chunks of items from a JSON array
        
        Args:
            json_file: Path to JSON file containing an array
            
        Yields:
            Lists of dictionaries from the JSON array
        """
        self.start_time = datetime.now()
        self.total_processed = 0
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not isinstance(data, list):
            logger.warning(f"JSON file {json_file} does not contain an array")
            return
            
        # Process in chunks
        for i in range(0, len(data), self.chunk_size):
            chunk = data[i:i + self.chunk_size]
            self.total_processed += len(chunk)
            yield chunk
            
    def chunk_iterable(self, iterable) -> Generator[List[Any], None, None]:
        """
        Yield chunks of items from any iterable
        
        Args:
            iterable: Any iterable object
            
        Yields:
            Lists of items from the iterable
        """
        self.start_time = datetime.now()
        self.total_processed = 0
        
        chunk = []
        for item in iterable:
            chunk.append(item)
            
            if len(chunk) >= self.chunk_size:
                self.total_processed += len(chunk)
                yield chunk
                chunk = []
                
        # Don't forget the last chunk
        if chunk:
            self.total_processed += len(chunk)
            yield chunk
            
    def get_progress(self) -> Dict[str, Any]:
        """
        Get progress statistics
        
        Returns:
            Dictionary containing progress information
        """
        now = datetime.now()
        elapsed = (now - self.start_time).total_seconds() if self.start_time else 0
        
        return {
            'processed': self.total_processed,
            'elapsed_seconds': elapsed,
            'items_per_second': self.total_processed / elapsed if elapsed > 0 else 0,
            'start_time': self.start_time,
            'current_time': now
        }
