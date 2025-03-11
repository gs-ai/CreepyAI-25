    #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to create a basic app icon if one doesn't exist.
Run this script once to generate the app_icon.png file.
"""

import os
from PIL import Image, ImageDraw

# Create a 256x256 icon with a simple design
def create_app_icon():
    size = 256
    icon = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(icon)
    
    # Draw a blue circle as background
    draw.ellipse((20, 20, size-20, size-20), fill=(41, 128, 185, 255))
    
    # Draw a map pin shape
    draw.polygon([
        (size//2, size//4),
        (size//4, size//2),
        (size//3, size*3//4),
        (size//2, size*2//3),
        (size*2//3, size*3//4),
        (size*3//4, size//2)
    ], fill=(236, 240, 241, 255), outline=(44, 62, 80, 255))
    
    # Save the icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_icon.png')
    icon.save(icon_path, 'PNG')
    print(f"App icon created at {icon_path}")

if __name__ == "__main__":
    create_app_icon()
