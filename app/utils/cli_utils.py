    """
Command-line interface utilities for CreepyAI.
"""
import os
import sys
import time
import shutil
from typing import List, Optional, Any, Dict, Callable


def confirm(message: str, default: bool = True) -> bool:
    """
    Ask for user confirmation
    
    Args:
        message: Confirmation message to display
        default: Default response if user just presses Enter
        
    Returns:
        True if user confirms, False otherwise
    """
    default_text = "[Y/n]" if default else "[y/N]"
    response = input(f"{message} {default_text} ").strip().lower()
    
    if not response:
        return default
        
    return response[0] == 'y'


def progress_bar(iterable: Any, total: Optional[int] = None, prefix: str = '', suffix: str = '', 
                length: int = 30, fill: str = '█', print_end: str = '\r'):
    """
    Display a progress bar for an iterable
    
    Args:
        iterable: Iterable to process
        total: Total number of items (calculated from iterable if None)
        prefix: Prefix string
        suffix: Suffix string
        length: Character length of bar
        fill: Bar fill character
        print_end: End character (e.g. '\r', '\n')
    
    Returns:
        Generator yielding items from the iterable
    """
    total = total or len(iterable)
    
    # Print initial bar
    print(f"\r{prefix} |{' ' * length}| 0% {suffix}", end=print_end)
    
    count = 0
    start_time = time.time()
    
    # Process each item
    for item in iterable:
        yield item
        count += 1
        
        # Update progress bar
        percent = int(100 * (count / float(total)))
        filled_length = int(length * count // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        
        # Calculate elapsed time and ETA
        elapsed = time.time() - start_time
        if count > 0 and elapsed > 0:
            items_per_second = count / elapsed
            eta = (total - count) / items_per_second if items_per_second > 0 else 0
            elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))
            eta_str = time.strftime("%H:%M:%S", time.gmtime(eta))
            time_str = f"[{elapsed_str}<{eta_str}]"
        else:
            time_str = ""
            
        print(f"\r{prefix} |{bar}| {percent}% {suffix} {time_str}", end=print_end)
        
        # Print newline on completion
        if count == total:
            print()


def get_terminal_size() -> Dict[str, int]:
    """
    Get terminal size
    
    Returns:
        Dictionary with 'width' and 'height' of terminal
    """
    terminal_size = shutil.get_terminal_size()
    return {
        'width': terminal_size.columns,
        'height': terminal_size.lines
    }


def print_table(headers: List[str], rows: List[List[Any]], max_width: Optional[int] = None) -> None:
    """
    Print a formatted table
    
    Args:
        headers: List of column headers
        rows: List of rows (each row is a list of values)
        max_width: Maximum width of the table (default is terminal width)
    """
    if not max_width:
        max_width = get_terminal_size()['width']
    
    # Convert all values to strings
    str_rows = [[str(cell) for cell in row] for row in rows]
    
    # Calculate column widths (minimum width is header width)
    col_widths = [len(h) for h in headers]
    for row in str_rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(cell))
    
    # Truncate columns if they exceed max_width
    total_width = sum(col_widths) + (3 * len(headers) - 1)
    if total_width > max_width:
        # Calculate available width for columns after accounting for separators
        avail_width = max_width - (3 * len(headers) - 1)
        
        # Distribute width proportionally
        factor = avail_width / sum(col_widths)
        col_widths = [max(3, int(w * factor)) for w in col_widths]
    
    # Create the formatters for each row
    separator = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
    format_str = '|' + '|'.join(' {:%s} ' % w for w in col_widths) + '|'
    
    # Print the table
    print(separator)
    print(format_str.format(*[h[:w] for h, w in zip(headers, col_widths)]))
    print(separator)
    for row in str_rows:
        # Truncate cells if they exceed column width
        truncated_row = [cell[:w] if len(cell) > w else cell for cell, w in zip(row, col_widths)]
        print(format_str.format(*truncated_row))
    print(separator)


def spinner(message: str = '', delay: float = 0.1) -> Callable:
    """
    Display a spinner while a function is running
    
    Args:
        message: Message to display alongside the spinner
        delay: Delay between spinner updates in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            spinner_chars = '|/-\\'
            stop_spinner = False
            
            def spin():
                i = 0
                while not stop_spinner:
                    sys.stdout.write(f"\r{message} {spinner_chars[i % len(spinner_chars)]}")
                    sys.stdout.flush()
                    time.sleep(delay)
                    i += 1
            
            import threading
            spinner_thread = threading.Thread(target=spin)
            spinner_thread.daemon = True
            
            try:
                spinner_thread.start()
                result = func(*args, **kwargs)
                stop_spinner = True
                sys.stdout.write('\r' + ' ' * (len(message) + 2) + '\r')
                return result
            finally:
                stop_spinner = True
                spinner_thread.join()
                
        return wrapper
    return decorator
