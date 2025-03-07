#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import json
import glob
import logging
import time
import shutil
import subprocess
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set
import traceback
import mimetypes
import configparser
import re

try:
    from PIL import Image, ExifTags
    from PIL.ExifTags import TAGS, GPSTAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    pass  # Auto-added by plugin_fixer.py

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    pass  # Auto-added by plugin_fixer.py

try:
    import exifread
    EXIFREAD_AVAILABLE = True
except ImportError:
    EXIFREAD_AVAILABLE = False
    pass  # Auto-added by plugin_fixer.py

from plugins.base_plugin import BasePlugin, LocationPoint
from plugins.enhanced_geocoding_helper import EnhancedGeocodingHelper

logger = logging.getLogger(__name__)

class MetadataExtractor(BasePlugin):
    """Plugin for extracting metadata from various file types"""
    
    def __init__(self):
        super().__init__(
            name="Metadata Extractor",
            description="Extract metadata including location data from various file formats"
        )
        self.geocoder = EnhancedGeocodingHelper()
        self._load_config_from_conf()
        
    def _load_config_from_conf(self) -> None:
        """Load configuration from .conf file if available"""
        conf_path = os.path.join(os.path.dirname(__file__), 'MetadataExtractor.conf')
        if os.path.exists(conf_path):
            try:
                config = configparser.ConfigParser()
                config.read(conf_path)
                
                # Convert the conf sections to our config format
                new_config = {}
                
                if 'string_options' in config:
                    for key, value in config['string_options'].items():
                        new_config[key] = value
                
                if 'boolean_options' in config:
                    for key, value in config['boolean_options'].items():
                        new_config[key] = value.lower() == 'true'
                
                if 'integer_options' in config:
                    for key, value in config['integer_options'].items():
                        try:
                            new_config[key] = int(value)
                        except (ValueError, TypeError):
                            pass
                
                if 'array_options' in config:
                    for key, value in config['array_options'].items():
                        try:
                            # Parse JSON arrays
                            new_config[key] = json.loads(value)
                        except:
                            # Fallback to comma-separated
                            new_config[key] = [item.strip() for item in value.split(',')]
                
                # Update config
                self.config.update(new_config)
                self._save_config()
                
            except Exception as e:
                logger.error(f"Error loading .conf file: {e}")
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        """Return configuration options for this plugin"""
        return [
            {
                "name": "output_directory",
                "display_name": "Output Directory",
                "type": "directory",
                "default": os.path.join(os.path.expanduser('~'), ".creepyai", "extracted_metadata"),
                "required": True,
                "description": "Directory to store extracted metadata"
            },
            {
                "name": "temp_directory",
                "display_name": "Temporary Directory",
                "type": "directory",
                "default": tempfile.gettempdir(),
                "required": False,
                "description": "Directory for temporary files"
            },
            {
                "name": "extract_gps",
                "display_name": "Extract GPS Data",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Extract GPS coordinates from files"
            },
            {
                "name": "extract_author",
                "display_name": "Extract Author Data",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Extract author/creator information"
            },
            {
                "name": "extract_creation_date",
                "display_name": "Extract Creation Date",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Extract creation dates"
            },
            {
                "name": "clean_temp_files",
                "display_name": "Clean Temporary Files",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Remove temporary files after processing"
            },
            {
                "name": "max_file_size",
                "display_name": "Maximum File Size",
                "type": "integer",
                "default": 104857600,  # 100MB
                "required": False,
                "description": "Maximum file size to process in bytes"
            },
            {
                "name": "thread_count",
                "display_name": "Thread Count",
                "type": "integer",
                "default": 4,
                "min": 1,
                "max": 16,
                "required": False,
                "description": "Number of threads to use for processing"
            },
            {
                "name": "supported_formats",
                "display_name": "Supported File Formats",
                "type": "string",
                "default": "jpg,jpeg,png,pdf,docx,xlsx,mp3,mp4",
                "required": False,
                "description": "Comma-separated list of file extensions to process"
            }
        ]
    
    def is_configured(self) -> Tuple[bool, str]:
        """Check if the plugin is properly configured"""
        # Check if output directory is set and exists/can be created
        output_dir = self.config.get('output_directory')
        if not output_dir:
            return False, "Output directory not configured"
            
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            return False, f"Cannot create output directory: {str(e)}"
            
        # Check if the plugin is enabled
        if not self.config.get('enabled', True):
            return False, "Plugin is disabled"
            
        # Check for required dependencies
        if not PIL_AVAILABLE and not EXIFREAD_AVAILABLE:
            return False, "Missing required dependencies: PIL or ExifRead for image processing"
            
        return True, "Metadata Extractor plugin is configured"
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None, 
                          date_to: Optional[datetime] = None) -> List[LocationPoint]:
        """"
        Collect location data from files in the target directory
        
        Args:
            target: Target directory or file to process
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            List of location points
        """"
        locations = []
        
        # If target is not a directory or file, return empty
        if not target or (not os.path.isdir(target) and not os.path.isfile(target)):
            logger.warning(f"Target is not a valid directory or file: {target}")
            return locations
            
        # Get list of supported formats
        supported_formats = self._get_supported_formats()
        
        # Find all matching files
        files_to_process = []
        
        if os.path.isfile(target):
            # Single file target
            if self._is_supported_format(target, supported_formats):
                files_to_process.append(target)
        else:
            # Directory target
            for format in supported_formats:
                pattern = f"*.{format}"
                recursive = self.config.get('recursive_search', True)
                
                if recursive:
                    files_to_process.extend(glob.glob(os.path.join(target, "**", pattern), recursive=True))
                else:
                    files_to_process.extend(glob.glob(os.path.join(target, pattern)))
        
        # Process each file
        for file_path in files_to_process:
            try:
                # Check file size limit
                if os.path.getsize(file_path) > self.config.get('max_file_size', 104857600):
                    logger.info(f"Skipping large file: {file_path}")
                    continue
                    
                # Extract metadata based on file type
                file_type = self._get_file_type(file_path)
                
                if file_type == "image":
                    locations.extend(self._process_image(file_path, date_from, date_to))
                elif file_type == "pdf":
                    locations.extend(self._process_pdf(file_path, date_from, date_to))
                elif file_type == "office":
                    locations.extend(self._process_office_document(file_path, date_from, date_to))
                elif file_type == "audio" or file_type == "video":
                    locations.extend(self._process_media_file(file_path, date_from, date_to))
                    
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                logger.debug(traceback.format_exc())
        
        # Save the cache after processing all files
        self.geocoder.save_cache()
        
        return locations
    
    def _get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        # Get from config
        formats = self.config.get('supported_formats')
        
        if isinstance(formats, list):
            # Already a list
            return [fmt.lower().lstrip('.') for fmt in formats if fmt]
        elif isinstance(formats, str):
            # Parse comma-separated string
            return [fmt.lower().lstrip('.').strip() for fmt in formats.split(',') if fmt.strip()]
        
        # Default formats if not configured
        return ['jpg', 'jpeg', 'png', 'pdf', 'docx', 'xlsx', 'mp3', 'mp4']
    
    def _is_supported_format(self, file_path: str, supported_formats: Optional[List[str]] = None) -> bool:
        """Check if a file is in a supported format"""
        if supported_formats is None:
            supported_formats = self._get_supported_formats()
            
        ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        return ext in supported_formats
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine the type of file based on extension or content"""
        ext = os.path.splitext(file_path)[1].lower()
        
        # Check by extension
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
            return "image"
        elif ext == '.pdf':
            return "pdf"
        elif ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
            return "office"
        elif ext in ['.mp3', '.wav', '.ogg', '.flac', '.aac']:
            return "audio"
        elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            return "video"
            
        # Try to determine by mimetype
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if mime_type.startswith('image/'):
                return "image"
            elif mime_type == 'application/pdf':
                return "pdf"
            elif 'officedocument' in mime_type or 'ms-' in mime_type:
                return "office"
            elif mime_type.startswith('audio/'):
                return "audio"
            elif mime_type.startswith('video/'):
                return "video"
                
        # Default unknown
        return "unknown"
    
    def _convert_to_degrees(self, value) -> float:
        """Convert GPS coordinates stored as rational numbers to degrees"""
        try:
            d = float(value[0])
            m = float(value[1]) / 60.0
            s = float(value[2]) / 3600.0
            return d + m + s
        except (TypeError, ValueError, ZeroDivisionError, IndexError):
            return 0.0
    
    def _process_image(self, file_path: str, date_from: Optional[datetime], 
                      date_to: Optional[datetime]) -> List[LocationPoint]:
        """Extract metadata from image files"""
        locations = []
        
        if not self.config.get('extract_gps', True):
            return locations
            
        # Try using PIL first
        if PIL_AVAILABLE:
            try:
                with Image.open(file_path) as img:
                    # Get EXIF data
                    exif_data = None
                    
                    if hasattr(img, '_getexif') and callable(getattr(img, '_getexif')):
                        raw_exif = img._getexif()
                        if raw_exif:
                            exif_data = {
                                TAGS.get(tag, tag): value
                                for tag, value in raw_exif.items():
                            }
                    
                    if exif_data and 'GPSInfo' in exif_data:
                        gps_info = {}
                        
                        for key, value in exif_data['GPSInfo'].items():
                            tag_name = GPSTAGS.get(key, key)
                            gps_info[tag_name] = value
                        
                        if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
                            lat = self._convert_to_degrees(gps_info['GPSLatitude'])
                            lng = self._convert_to_degrees(gps_info['GPSLongitude'])
                            
                            # Adjust for reference direction
                            if 'GPSLatitudeRef' in gps_info and gps_info['GPSLatitudeRef'] == 'S':
                                lat = -lat
                            if 'GPSLongitudeRef' in gps_info and gps_info['GPSLongitudeRef'] == 'W':
                                lng = -lng
                                
                            # Get timestamp
                            timestamp = None
                            
                            # Try to get date from EXIF
                            if 'DateTimeOriginal' in exif_data:
                                try:
                                    timestamp = datetime.strptime(
                                        exif_data['DateTimeOriginal'], 
                                        '%Y:%m:%d %H:%M:%S'
                                    )
                                except (ValueError, TypeError):
                                    pass
                            
                            # Fall back to file modification time
                            if timestamp is None:
                                timestamp = datetime.fromtimestamp(os.path.getmtime(file_path))
                                
                            # Apply date filters
                            if date_from and timestamp < date_from:
                                return locations
                            if date_to and timestamp > date_to:
                                return locations
                                
                            # Create location point
                            context_info = f"Image: {os.path.basename(file_path)}"
                            
                            # Add camera info if available
                            if 'Make' in exif_data or 'Model' in exif_data:
                                context_info += f" | Camera: {exif_data.get('Make', '')} {exif_data.get('Model', '')}"
                            
                            locations.append(
                                LocationPoint(
                                    latitude=lat,
                                    longitude=lng,
                                    timestamp=timestamp,
                                    source="Image Metadata",
                                    context=context_info
                                )
                            )
                            
            except Exception as e:
                logger.debug(f"Error extracting EXIF with PIL from {file_path}: {e}")
        
        # Try using exifread if available and PIL failed
        if not locations and EXIFREAD_AVAILABLE:
            try:
                with open(file_path, 'rb') as f:
                    tags = exifread.process_file(f, details=False)
                    
                    # Check for GPS tags
                    if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                        lat_ref = tags.get('GPS GPSLatitudeRef', 'N').values
                        lng_ref = tags.get('GPS GPSLongitudeRef', 'E').values
                        
                        # Parse latitude
                        lat_parts = tags['GPS GPSLatitude'].values
                        lat = float(lat_parts[0].num) / float(lat_parts[0].den) + \
                              float(lat_parts[1].num) / float(lat_parts[1].den) / 60.0 + \
                              float(lat_parts[2].num) / float(lat_parts[2].den) / 3600.0
                              
                        if lat_ref == 'S':
                            lat = -lat
                            
                        # Parse longitude
                        lng_parts = tags['GPS GPSLongitude'].values
                        lng = float(lng_parts[0].num) / float(lng_parts[0].den) + \
                              float(lng_parts[1].num) / float(lng_parts[1].den) / 60.0 + \
                              float(lng_parts[2].num) / float(lng_parts[2].den) / 3600.0
                              
                        if lng_ref == 'W':
                            lng = -lng
                            
                        # Get timestamp
                        timestamp = None
                        
                        if 'EXIF DateTimeOriginal' in tags:
                            try:
                                timestamp = datetime.strptime(
                                    str(tags['EXIF DateTimeOriginal']), 
                                    '%Y:%m:%d %H:%M:%S'
                                )
                            except (ValueError, TypeError):
                                pass
                        
                        # Fall back to file modification time
                        if timestamp is None:
                            timestamp = datetime.fromtimestamp(os.path.getmtime(file_path))
                            
                        # Apply date filters
                        if date_from and timestamp < date_from:
                            return locations
                        if date_to and timestamp > date_to:
                            return locations
                            
                        # Get camera info
                        make = str(tags.get('Image Make', ''))
                        model = str(tags.get('Image Model', ''))
                        
                        # Create location point
                        context_info = f"Image: {os.path.basename(file_path)}"
                        if make or model:
                            context_info += f" | Camera: {make} {model}"
                            
                        locations.append(
                            LocationPoint(
                                latitude=lat,
                                longitude=lng,
                                timestamp=timestamp,
                                source="Image Metadata",
                                context=context_info
                            )
                        )
            except Exception as e:
                logger.debug(f"Error extracting EXIF with exifread from {file_path}: {e}")
                
        return locations
    
    def _process_pdf(self, file_path: str, date_from: Optional[datetime],
                    date_to: Optional[datetime]) -> List[LocationPoint]:
        """Extract metadata from PDF files"""
        locations = []
        
        if PYPDF2_AVAILABLE:
            try:
                pdf = PyPDF2.PdfReader(file_path)
                info = pdf.metadata
                
                if info:
                    # Look for location in metadata
                    location_text = None
                    
                    # Check various metadata fields that might contain location
                    for key in ['/Location', '/GeoLocation', '/Address', '/Place']:
                        if key in info and info[key]:
                            location_text = info[key]
                            break
                    
                    # Try to extract from document info
                    if not location_text and info.get('/Subject'):
                        # Look for GPS coordinates in the subject
                        subject = info['/Subject']
                        coords = re.search(r'(\d+\.\d+)[,\s]+(-?\d+\.\d+)', subject)
                        if coords:
                            lat = float(coords.group(1))
                            lng = float(coords.group(2))
                            
                            # Get timestamp
                            timestamp = None
                            
                            if info.get('/CreationDate'):
                                date_str = info['/CreationDate']
                                # PDF dates are often in this format: D:20190415093821Z
                                date_match = re.match(r'D:(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})', date_str)
                                if date_match:
                                    year, month, day, hour, minute, second = map(int, date_match.groups())
                                    timestamp = datetime(year, month, day, hour, minute, second)
                            
                            # Fall back to file modification time
                            if timestamp is None:
                                timestamp = datetime.fromtimestamp(os.path.getmtime(file_path))
                                
                            # Apply date filters
                            if date_from and timestamp < date_from:
                                return locations
                            if date_to and timestamp > date_to:
                                return locations
                                
                            # Create location point
                            locations.append(
                                LocationPoint(
                                    latitude=lat,
                                    longitude=lng,
                                    timestamp=timestamp,
                                    source="PDF Metadata",
                                    context=f"PDF: {os.path.basename(file_path)}"
                                )
                            )
                    
                    # If no direct coordinates, try to geocode any location text
                    if not locations and location_text and self.geocoder:
                        lat, lng = self.geocoder.geocode(location_text)
                        
                        if lat is not None and lng is not None:
                            # Get timestamp
                            timestamp = None
                            
                            if info.get('/CreationDate:'
