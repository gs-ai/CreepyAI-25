    #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to create missing icons for the application.
Run this script once to generate any missing icons.
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Set of icon names that should be available
REQUIRED_ICONS = [
    "folder_open_24dp_000000",
    "save_24dp_000000",
    "analytics_24dp_000000",
    "export_24dp_000000",
    "date_range_24dp_000000", 
    "place_24dp_000000",
    "clear_24dp_000000"
]

def create_text_icon(text, filename, size=24):
    """Create a simple text-based icon"""
    icon = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(icon)
    
    # Try to get a font, use default if not available
    try:
        font = ImageFont.truetype("Arial", 14)
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate text position using the newer method textbbox
    # Fix: Use textbbox instead of textsize
    try:
        # For newer Pillow versions
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        text_width = right - left
        text_height = bottom - top
    except AttributeError:
        try:
            # For even newer Pillow versions
            text_width = draw.textlength(text, font=font)
            # Approximate height as 80% of font size
            text_height = font.size * 0.8
        except AttributeError:
            # Fallback to fixed dimensions if all else fails
            text_width = size // 2
            text_height = size // 2
    
    position = ((size - text_width) // 2, (size - text_height) // 2)
    
    # Draw text with black color
    draw.text(position, text, fill=(0, 0, 0, 255), font=font)
    
    # Save the icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{filename}.png')
    icon.save(icon_path, 'PNG')
    print(f"Created icon at {icon_path}")

def create_missing_icons():
    """Create all missing icons"""
    resources_dir = os.path.dirname(os.path.abspath(__file__))
    existing_icons = [f[:-4] for f in os.listdir(resources_dir) if f.endswith('.png')]
    
    print(f"Found {len(existing_icons)} existing icons")
    
    for icon_name in REQUIRED_ICONS:
        if icon_name not in existing_icons:
            # Create a simple text-based icon with the first letter
            first_letter = icon_name[0].upper()
            create_text_icon(first_letter, icon_name)
    
    # Also create app icon if missing
    if 'app_icon' not in existing_icons:
        from create_app_icon import create_app_icon
        create_app_icon()

if __name__ == "__main__":
    create_missing_icons()
