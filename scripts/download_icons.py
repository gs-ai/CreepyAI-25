#!/usr/bin/env python3
"""
Icon Downloader for CreepyAI

Downloads and prepares icons for social media platforms and other sources
used in CreepyAI.
"""

import os
import sys
import argparse
import logging
import json
import urllib.request
import shutil
from typing import Dict, Any, List, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("icon_downloader")

# Path to resources
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
RESOURCES_DIR = os.path.join(PROJECT_ROOT, "app", "resources")
ICONS_DIR = os.path.join(RESOURCES_DIR, "icons")

# Icon sources
ICON_SOURCES = {
    "facebook": "https://www.facebook.com/favicon.ico",
    "instagram": "https://www.instagram.com/favicon.ico",
    "twitter": "https://twitter.com/favicon.ico",
    "linkedin": "https://www.linkedin.com/favicon.ico",
    "tiktok": "https://www.tiktok.com/favicon.ico",
    "snapchat": "https://www.snapchat.com/favicon.ico",
    "pinterest": "https://www.pinterest.com/favicon.ico",
    "yelp": "https://www.yelp.com/favicon.ico",
    "google": "https://www.google.com/favicon.ico",
    "maps": "https://maps.google.com/favicon.ico",
    "youtube": "https://www.youtube.com/favicon.ico",
    "reddit": "https://www.reddit.com/favicon.ico",
    "github": "https://github.com/favicon.ico"
}

def ensure_directory(path: str) -> None:
    """Ensure the directory exists, create if not"""
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Created directory: {path}")

def download_icon(name: str, url: str, output_dir: str, overwrite: bool = False) -> str:
    """
    Download an icon from a URL
    
    Args:
        name: Name for the icon file
        url: URL to download from
        output_dir: Directory to save to
        overwrite: Whether to overwrite existing files
        
    Returns:
        Path to downloaded file
    """
    output_path = os.path.join(output_dir, f"{name}-icon.png")
    
    if os.path.exists(output_path) and not overwrite:
        logger.info(f"Icon for {name} already exists, skipping")
        return output_path
    
    try:
        logger.info(f"Downloading icon for {name} from {url}")
        
        # Download the file
        with urllib.request.urlopen(url) as response:
            with open(output_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        
        logger.info(f"Saved icon to {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Failed to download icon for {name}: {e}")
        return ""

def resize_icon(input_path: str, size: Tuple[int, int]) -> bool:
    """
    Resize an icon to the specified dimensions
    
    Args:
        input_path: Path to icon file
        size: (width, height) tuple
        
    Returns:
        True if successful
    """
    try:
        from PIL import Image
        
        # Open and resize
        img = Image.open(input_path)
        img = img.resize(size, Image.LANCZOS)
        
        # Save back to same path
        img.save(input_path, optimize=True)
        
        logger.info(f"Resized {os.path.basename(input_path)} to {size[0]}x{size[1]}")
        return True
    
    except ImportError:
        logger.warning("Pillow not installed, skipping resize. Install with: pip install Pillow")
        return False
    
    except Exception as e:
        logger.error(f"Failed to resize {input_path}: {e}")
        return False

def convert_icon(input_path: str) -> bool:
    """
    Convert icon to PNG format if needed
    
    Args:
        input_path: Path to icon file
        
    Returns:
        True if successful
    """
    try:
        from PIL import Image
        
        # Check if conversion is needed
        filename, ext = os.path.splitext(input_path)
        if ext.lower() != '.png':
            output_path = f"{filename}.png"
            
            # Open and convert
            img = Image.open(input_path)
            img.save(output_path, "PNG")
            
            # Replace original with PNG version
            os.remove(input_path)
            
            logger.info(f"Converted {os.path.basename(input_path)} to PNG format")
        
        return True
    
    except ImportError:
        logger.warning("Pillow not installed, skipping conversion. Install with: pip install Pillow")
        return False
    
    except Exception as e:
        logger.error(f"Failed to convert {input_path}: {e}")
        return False

def download_all_icons(output_dir: str, overwrite: bool = False, resize: bool = True) -> None:
    """
    Download all icons and process them
    
    Args:
        output_dir: Directory to save icons to
        overwrite: Whether to overwrite existing files
        resize: Whether to resize icons to standard size
    """
    ensure_directory(output_dir)
    
    for name, url in ICON_SOURCES.items():
        icon_path = download_icon(name, url, output_dir, overwrite)
        
        if icon_path and resize:
            convert_icon(icon_path)
            resize_icon(icon_path, (64, 64))

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Download and prepare icons for CreepyAI")
    parser.add_argument("--output-dir", "-o", default=ICONS_DIR,
                      help=f"Output directory for icons (default: {ICONS_DIR})")
    parser.add_argument("--overwrite", action="store_true",
                      help="Overwrite existing files")
    parser.add_argument("--no-resize", action="store_true",
                      help="Skip resizing icons (requires Pillow)")
    
    args = parser.parse_args()
    
    # Download all icons
    download_all_icons(args.output_dir, args.overwrite, not args.no_resize)
    
    logger.info("Icon download completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
