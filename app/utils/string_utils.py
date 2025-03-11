    """
String utility functions for CreepyAI.
"""
import re
import base64
import hashlib
import random
import string
import unicodedata
from typing import Optional, Dict, Any, List, Union


def snake_to_camel(text: str) -> str:
    """
    Convert snake_case to CamelCase
    
    Args:
        text: Text in snake_case
        
    Returns:
        Text in CamelCase
    """
    return ''.join(word.title() for word in text.split('_'))


def camel_to_snake(text: str) -> str:
    """
    Convert CamelCase to snake_case
    
    Args:
        text: Text in CamelCase
        
    Returns:
        Text in snake_case
    """
    # Insert underscore before uppercase letters and convert to lowercase
    result = re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()
    return result


def truncate(text: str, max_length: int, suffix: str = '...') -> str:
    """
    Truncate text to a maximum length, adding a suffix if truncated
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """
    Convert a string to a URL-friendly slug.
    Example: "Hello World!" -> "hello-world"
    """
    # Convert to lowercase and normalize unicode characters
    text = unicodedata.normalize('NFKD', text.lower())
    
    # Remove non-alphanumeric characters and replace spaces with hyphens
    text = re.sub(r'[^\w\s-]', '', text).strip()
    text = re.sub(r'[-\s]+', '-', text)
    
    return text


def extract_between(text: str, start: str, end: str) -> List[str]:
    """
    Extract all substrings between start and end markers
    
    Args:
        text: Text to search in
        start: Start marker
        end: End marker
        
    Returns:
        List of extracted substrings
    """
    pattern = f'{re.escape(start)}(.*?){re.escape(end)}'
    return re.findall(pattern, text, re.DOTALL)


def format_table(data: List[Dict[str, Any]], columns: Optional[List[str]] = None) -> str:
    """
    Format tabular data as a text table
    
    Args:
        data: List of dictionaries containing the data
        columns: List of column names to include (default: all keys in the first row)
        
    Returns:
        Formatted table as a string
    """
    if not data:
        return ""
        
    # Determine columns if not provided
    if columns is None:
        columns = list(data[0].keys())
    
    # Calculate column widths
    widths = {col: len(col) for col in columns}
    for row in data:
        for col in columns:
            if col in row:
                widths[col] = max(widths[col], len(str(row.get(col, ''))))
    
    # Build the table
    header = ' | '.join(col.ljust(widths[col]) for col in columns)
    separator = '-+-'.join('-' * widths[col] for col in columns)
    rows = [' | '.join(str(row.get(col, '')).ljust(widths[col]) for col in columns) for row in data]
    
    return '\n'.join([header, separator] + rows)


def parse_key_value_string(text: str, item_separator: str = ',', key_value_separator: str = '=') -> Dict[str, str]:
    """
    Parse a string of key-value pairs
    
    Args:
        text: String to parse (e.g. "key1=value1,key2=value2")
        item_separator: Separator between items
        key_value_separator: Separator between keys and values
        
    Returns:
        Dictionary of key-value pairs
    """
    result = {}
    
    if not text:
        return result
        
    items = text.split(item_separator)
    for item in items:
        item = item.strip()
        if not item or key_value_separator not in item:
            continue
            
        key, value = item.split(key_value_separator, 1)
        result[key.strip()] = value.strip()
    
    return result


def generate_random_string(length: int = 8) -> str:
    """Generate a random string of specified length"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate a string to a specified maximum length"""
    if len(text) <= max_length:
        return text
    
    # Truncate at a word boundary if possible
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return truncated + suffix


def extract_urls(text: str) -> List[str]:
    """Extract all URLs from a string"""
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?[\w=&]*)?'
    return re.findall(url_pattern, text)


def extract_emails(text: str) -> List[str]:
    """Extract all email addresses from a string"""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)


def extract_usernames(text: str, platform: str = None) -> List[str]:
    """
    Extract usernames from text based on platform-specific patterns
    
    Args:
        text: The text to search
        platform: Platform identifier ('twitter', 'instagram', etc.)
    """
    if not platform:
        # General username pattern (alphanumeric with underscore)
        pattern = r'@([a-zA-Z0-9_]{3,30})'
    elif platform.lower() == 'twitter':
        pattern = r'@([a-zA-Z0-9_]{1,15})'
    elif platform.lower() == 'instagram':
        pattern = r'@([a-zA-Z0-9._]{1,30})'
    else:
        # Default for other platforms
        pattern = r'@([a-zA-Z0-9._-]{3,30})'
    
    return re.findall(pattern, text)


def hash_string(text: str, algorithm: str = 'sha256') -> str:
    """
    Create a hash of a string using the specified algorithm
    
    Args:
        text: Text to hash
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256', 'sha512')
    """
    if algorithm.lower() == 'md5':
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm.lower() == 'sha1':
        return hashlib.sha1(text.encode()).hexdigest()
    elif algorithm.lower() == 'sha512':
        return hashlib.sha512(text.encode()).hexdigest()
    else:
        # default to sha256
        return hashlib.sha256(text.encode()).hexdigest()


def base64_encode(text: str) -> str:
    """Encode a string as Base64"""
    return base64.b64encode(text.encode()).decode()


def base64_decode(encoded: str) -> str:
    """Decode a Base64 string"""
    try:
        return base64.b64decode(encoded).decode()
    except Exception:
        return ""


def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text"""
    # Multiple patterns for different phone number formats
    patterns = [
        r'\+\d{1,3}[\s-]?\d{1,3}[\s-]?\d{3,5}[\s-]?\d{3,5}',  # International
        r'\(\d{3}\)\s*\d{3}[-\s]?\d{4}',  # US format (123) 456-7890
        r'\d{3}[-\s]?\d{3}[-\s]?\d{4}'     # US format 123-456-7890
    ]
    
    numbers = []
    for pattern in patterns:
        numbers.extend(re.findall(pattern, text))
    
    return numbers


def redact_sensitive_info(text: str) -> str:
    """
    Redact sensitive information from text 
    (emails, phone numbers, credit cards, etc.)
    """
    # Redact emails
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL REDACTED]', text)
    
    # Redact phone numbers - various patterns
    for pattern in [r'\+\d{1,3}[\s-]?\d{1,3}[\s-]?\d{3,5}[\s-]?\d{3,5}',
                   r'\(\d{3}\)\s*\d{3}[-\s]?\d{4}',
                   r'\d{3}[-\s]?\d{3}[-\s]?\d{4}']:
        text = re.sub(pattern, '[PHONE REDACTED]', text)
    
    # Redact credit card numbers
    text = re.sub(r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}', '[CREDIT CARD REDACTED]', text)
    
    # Redact SSN
    text = re.sub(r'\d{3}[-\s]?\d{2}[-\s]?\d{4}', '[SSN REDACTED]', text)
    
    return text
