    """
Data validation utilities for CreepyAI.
Provides functions to validate various types of data.
"""
import re
import ipaddress
import os
import json
import uuid
import logging
import datetime
from typing import Dict, List, Any, Union, Optional, Tuple

logger = logging.getLogger('creepyai.utilities.validation')

class ValidationError(Exception):
    """Exception raised for validation errors"""
    pass

def validate_email(email: str) -> bool:
    """Validate email address format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_ip(ip: str) -> bool:
    """Validate IP address (both IPv4 and IPv6)"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r'^(http|https)://([\w-]+(\.[\w-]+)+)(/[\w-./?%&=]*)?$'
    return bool(re.match(pattern, url))

def validate_coordinates(lat: float, lng: float) -> bool:
    """Validate geographic coordinates"""
    return -90 <= lat <= 90 and -180 <= lng <= 180

def validate_username(username: str) -> bool:
    """Validate username format (alphanumeric with underscores and hyphens)"""
    if not username or len(username) < 3:
        return False
    
    pattern = r'^[a-zA-Z0-9_-]{3,30}$'
    return bool(re.match(pattern, username))

def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number in international format
    Examples: +12025550149, +44 20 7946 0958
    """
    # Remove spaces and other formatting characters
    phone = re.sub(r'[\s\(\)\-]', '', phone)
    pattern = r'^\+?[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone))

def validate_json(json_str: str) -> Union[Dict, List, bool]:
    """
    Validate if a string is valid JSON
    Returns the parsed object if valid, False otherwise
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return False

def validate_date(date_str: str, formats: List[str] = None) -> Optional[datetime.datetime]:
    """
    Validate if a string is a valid date
    Returns datetime object if valid, None otherwise
    
    Args:
        date_str: Date string to validate
        formats: List of formats to try (e.g. ['%Y-%m-%d', '%m/%d/%Y'])
    """
    if formats is None:
        formats = ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y', 
                   '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']
    
    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def validate_project_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate project data structure
    Returns (is_valid, errors)
    """
    errors = []
    required_fields = ['name', 'created_at', 'version']
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    if 'name' in data and (not isinstance(data['name'], str) or len(data['name']) < 1):
        errors.append("Project name must be a non-empty string")
    
    if 'version' in data and not isinstance(data['version'], str):
        errors.append("Version must be a string")
    
    if 'created_at' in data:
        if isinstance(data['created_at'], str):
            if not validate_date(data['created_at']):
                errors.append("Invalid date format for created_at")
        elif not isinstance(data['created_at'], (int, float, datetime.datetime)):
            errors.append("created_at must be a date string, timestamp or datetime object")
    
    return len(errors) == 0, errors

def validate_plugin_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate plugin configuration
    Returns (is_valid, errors)
    """
    errors = []
    required_fields = ['name', 'version', 'description']
    
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    if 'name' in config and (not isinstance(config['name'], str) or len(config['name']) < 1):
        errors.append("Plugin name must be a non-empty string")
    
    if 'version' in config and not isinstance(config['version'], str):
        errors.append("Version must be a string")
    
    if 'description' in config and not isinstance(config['description'], str):
        errors.append("Description must be a string")
    
    return len(errors) == 0, errors

def validate_file_path(path: str, must_exist: bool = False) -> bool:
    """Validate if a path is a valid file path"""
    try:
        if os.path.isabs(path) or os.path.expanduser(path):
            if must_exist:
                return os.path.isfile(path)
            return True
        return False
    except Exception:
        return False

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    # Remove potentially dangerous characters and limit length
    return re.sub(r'[^\w\s\.,;:\-_\(\)@]', '', text)[:1000]
