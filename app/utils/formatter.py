# Description: Formatting utilities for CreepyAI."""
Formatting utilities for CreepyAI.
"""
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union


def format_bytes(bytes_value: int, precision: int = 2) -> str:
    """
    Format bytes as a human-readable string
    
    Args:
        bytes_value: Number of bytes
        precision: Number of decimal places
        
    Returns:
        Formatted string (e.g. "2.5 MB")
    """
    if bytes_value < 0:
        raise ValueError("Bytes value cannot be negative")
        
    if bytes_value == 0:
        return "0 B"
        
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    unit_index = 0
    value = bytes_value
    
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024.0
        unit_index += 1
        
    return f"{value:.{precision}f} {units[unit_index]}"


def format_timedelta(td: timedelta, compact: bool = False) -> str:
    """
    Format a timedelta object as a readable string
    
    Args:
        td: Timedelta object
        compact: Whether to use compact format
        
    Returns:
        Formatted string (e.g. "2d 5h 3m 20s" or "2 days, 5 hours, 3 minutes, 20 seconds")
    """
    total_seconds = int(td.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if compact:
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if seconds or not parts:
            parts.append(f"{seconds}s")
        return " ".join(parts)
    else:
        parts = []
        if days:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds or not parts:
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        return ", ".join(parts)


def format_timestamp(timestamp: Union[int, float], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a timestamp as a date string
    
    Args:
        timestamp: Unix timestamp
        format_str: Format string for datetime.strftime
        
    Returns:
        Formatted date string
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime(format_str)


def format_json(obj: Any, indent: int = 2) -> str:
    """
    Format an object as a JSON string
    
    Args:
        obj: Object to format
        indent: Indentation level
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(obj, indent=indent, sort_keys=True)


def format_duration(seconds: float, precision: int = 2) -> str:
    """
    Format a duration in seconds into an appropriate unit
    
    Args:
        seconds: Duration in seconds
        precision: Number of decimal places
        
    Returns:
        Formatted duration string with appropriate unit
    """
    if seconds < 0.001:
        # Microseconds
        return f"{seconds * 1_000_000:.{precision}f} µs"
    elif seconds < 1.0:
        # Milliseconds
        return f"{seconds * 1_000:.{precision}f} ms"
    elif seconds < 60:
        # Seconds
        return f"{seconds:.{precision}f} s"
    elif seconds < 3600:
        # Minutes and seconds
        m, s = divmod(seconds, 60)
        return f"{int(m)}m {int(s)}s"
    else:
        # Hours, minutes, and seconds
        h, remainder = divmod(seconds, 3600)
        m, s = divmod(remainder, 60)
        return f"{int(h)}h {int(m)}m {int(s)}s"


def format_percentage(value: float, total: float, precision: int = 2) -> str:
    """
    Format a value as a percentage of total
    
    Args:
        value: Value to format
        total: Total value
        precision: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if total == 0:
        return "0.00%"
    
    percentage = (value / total) * 100
    return f"{percentage:.{precision}f}%"


def format_list(items: List[str], conjunction: str = 'and') -> str:
    """
    Format a list of items as a string
    
    Args:
        items: List of items to format
        conjunction: Conjunction to use for the last item
        
    Returns:
        Formatted string (e.g. "item1, item2, and item3")
    """
    if not items:
        return ""
    elif len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    else:
        return f"{', '.join(items[:-1])}, {conjunction} {items[-1]}"


def format_table_text(data: List[List[Any]], headers: Optional[List[str]] = None) -> str:
    """
    Format a table as text with aligned columns
    
    Args:
        data: Table data as list of rows
        headers: Column headers
        
    Returns:
        Text table with aligned columns
    """
    if not data:
        return ""
    
    # Prepare all rows (including header if present)
    all_rows = []
    if headers:
        all_rows.append(headers)
    all_rows.extend(data)
    
    # Convert all values to strings
    str_rows = [[str(cell) for cell in row] for row in all_rows]
    
    # Calculate column widths
    col_count = max(len(row) for row in str_rows)
    col_widths = [0] * col_count
    for row in str_rows:
        for i, cell in enumerate(row):
            if i < col_count:
                col_widths[i] = max(col_widths[i], len(cell))
    
    # Build the table
    result = []
    if headers:
        # Header row
        header_row = "| " + " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(str_rows[0])) + " |"
        result.append(header_row)
        
        # Separator row
        sep_row = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
        result.append(sep_row)
        
        # Data rows
        for row in str_rows[1:]:
            padded_row = [row[i].ljust(col_widths[i]) if i < len(row) else " " * col_widths[i] for i in range(col_count)]
            result.append("| " + " | ".join(padded_row) + " |")
    else:
        # No headers, just data rows
        for row in str_rows:
            padded_row = [row[i].ljust(col_widths[i]) if i < len(row) else " " * col_widths[i] for i in range(col_count)]
            result.append("| " + " | ".join(padded_row) + " |")
    
    return "\n".join(result)
