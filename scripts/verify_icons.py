#!/usr/bin/env python3
"""
Icon Verification Script for CreepyAI
Checks that all icon mappings point to existing files
"""

import os
import sys

# Add the project root to the path to allow importing our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from creepy.resources.icon_mapping import ICON_MAPPING
except ImportError:
    print("Error: Could not import ICON_MAPPING. Make sure the file exists and is properly formatted.")
    sys.exit(1)

def verify_icon_mappings():
    """Verify that all icon mappings point to actual files."""
    # Get the resources directory
    resources_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "creepy", "resources"
    )
    
    print(f"Resources directory: {resources_dir}")
    
    # Get all .png files in the resources dir
    available_icons = []
    for root, _, files in os.walk(resources_dir):
        for file in files:
            if file.endswith('.png'):
                available_icons.append(file)
    
    print(f"Found {len(available_icons)} icon files in resources directory.\n")
    
    # Check each icon mapping
    missing_icons = []
    for simple_name, filenames in ICON_MAPPING.items():
        print(f"Checking mapping for '{simple_name}':")
        found = False
        
        for filename in filenames:
            png_filename = f"{filename}.png"
            if png_filename in available_icons:
                print(f"  ✓ {png_filename}")
                found = True
            else:
                print(f"  ✗ {png_filename} (not found)")
                missing_icons.append((simple_name, png_filename))
        
        if not found:
            print(f"  ! No valid icon files found for '{simple_name}'")
        print()
    
    # Summary
    print("\n--- SUMMARY ---")
    if missing_icons:
        print(f"Found {len(missing_icons)} missing icon references:")
        for simple_name, filename in missing_icons:
            print(f"  - '{simple_name}' references missing file: {filename}")
    else:
        print("All icon mappings point to valid files. Icon system should work correctly.")

if __name__ == "__main__":
    print("Starting icon verification...\n")
    verify_icon_mappings()
