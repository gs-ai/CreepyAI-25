    """
Date and time utilities for CreepyAI.
"""
import time
import calendar
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Union


def get_current_timestamp() -> float:
    """
    Get current Unix timestamp
    
    Returns:
        Current Unix timestamp (seconds since epoch)
    """
    return time.time()


def get_current_iso_datetime() -> str:
    """
    Get current datetime in ISO format
    
    Returns:
        Current datetime in ISO format
    """
    return datetime.now().isoformat()


def parse_iso_datetime(iso_string: str) -> datetime:
    """
    Parse ISO format datetime string
    
    Args:
        iso_string: Datetime in ISO format
        
    Returns:
        Datetime object
    """
    return datetime.fromisoformat(iso_string)


def datetime_to_timestamp(dt: datetime) -> float:
    """
    Convert datetime object to Unix timestamp
    
    Args:
        dt: Datetime object
        
    Returns:
        Unix timestamp
    """
    return dt.timestamp()


def timestamp_to_datetime(timestamp: float) -> datetime:
    """
    Convert Unix timestamp to datetime object
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        Datetime object
    """
    return datetime.fromtimestamp(timestamp)


def get_date_range(start_date: datetime, end_date: datetime, step: timedelta = timedelta(days=1)) -> List[datetime]:
    """
    Generate a list of dates in a range
    
    Args:
        start_date: Start date
        end_date: End date
        step: Time step between dates
        
    Returns:
        List of datetime objects
    """
    result = []
    current = start_date
    while current <= end_date:
        result.append(current)
        current += step
    return result


def get_month_start_end(year: int, month: int) -> Tuple[datetime, datetime]:
    """
    Get start and end datetime for a month
    
    Args:
        year: Year
        month: Month (1-12)
        
    Returns:
        Tuple of (start_datetime, end_datetime)
    """
    start_date = datetime(year, month, 1, 0, 0, 0)
    
    # Get last day of month
    _, last_day = calendar.monthrange(year, month)
    end_date = datetime(year, month, last_day, 23, 59, 59)
    
    return start_date, end_date


def is_weekend(dt: datetime) -> bool:
    """
    Check if a date is on a weekend
    
    Args:
        dt: Datetime to check
        
    Returns:
        True if date is on weekend (Saturday or Sunday), False otherwise
    """
    return dt.weekday() >= 5  # 5 = Saturday, 6 = Sunday


def add_business_days(dt: datetime, days: int) -> datetime:
    """
    Add business days to a date
    
    Args:
        dt: Starting datetime
        days: Number of business days to add
        
    Returns:
        Datetime after adding business days
    """
    if days == 0:
        return dt
        
    result = dt
    remaining_days = days
    
    # Determine sign of days
    step = 1 if days > 0 else -1
    
    while remaining_days != 0:
        result += timedelta(days=step)
        if not is_weekend(result):
            remaining_days -= step
            
    return result


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object as string
    
    Args:
        dt: Datetime object
        format_str: Format string for strftime
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse string into datetime object
    
    Args:
        date_str: Date string to parse
        format_str: Format string for strptime
        
    Returns:
        Datetime object
    """
    return datetime.strptime(date_str, format_str)


def get_relative_date(days: int = 0, months: int = 0, years: int = 0) -> datetime:
    """
    Get date relative to today
    
    Args:
        days: Days to add (can be negative)
        months: Months to add (can be negative)
        years: Years to add (can be negative)
        
    Returns:
        Datetime object
    """
    today = datetime.now()
    
    # Add years and months
    if months != 0 or years != 0:
        new_year = today.year + years
        new_month = today.month + months
        
        # Adjust month overflow/underflow
        if new_month > 12:
            new_year += new_month // 12
            new_month = new_month % 12
        elif new_month <= 0:
            new_year -= (abs(new_month) // 12) + 1
            new_month = 12 - (abs(new_month) % 12)
        
        # Get proper last day of month
        day = min(today.day, calendar.monthrange(new_year, new_month)[1])
        
        result = today.replace(year=new_year, month=new_month, day=day)
    else:
        result = today
    
    # Add days
    if days != 0:
        result += timedelta(days=days)
        
    return result
