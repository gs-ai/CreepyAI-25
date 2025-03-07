#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create placeholder icons for CreepyAI.

This script generates basic placeholder icons for the application.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_icon(filename, text, size=(64, 64), bg_color=(60, 60, 60), text_color=(240, 240, 240)):
    """Create a simple text-based icon."""
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Create a new image with the specified background color
    image = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(image)
    
    # Try to load a font, fall back to default if not available
    try:
        font = ImageFont.truetype("Arial", 20)
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (20, 20)
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # Draw the text
    draw.text(position, text, font=font, fill=text_color)
    
    # Save the image
    image.save(filename)
    logger.info(f"Created icon: {filename}")

def main():
    """Create all required icons."""
    # Base directory for icons
    icon_dir = os.path.join('resources', 'icons')
    os.makedirs(icon_dir, exist_ok=True)
    
    # Create application icon
    create_icon(os.path.join(icon_dir, 'app_icon.png'), 'C', bg_color=(40, 80, 120))
    
    # Create action icons
    action_icons = {
        'new.png': 'N',
        'open.png': 'O',
        'save.png': 'S',
        'settings.png': 'P',
    }
    
    for filename, text in action_icons.items():
        create_icon(os.path.join(icon_dir, filename), text, bg_color=(60, 100, 60))
    
    logger.info("All icons created successfully")

if __name__ == "__main__":
    main()
    print("Run this script to create placeholder icons before compiling resources")
