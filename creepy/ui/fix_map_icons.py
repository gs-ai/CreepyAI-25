#!/usr/bin/env python3
"""
Map Icon Fix for CreepyAI
This script specifically addresses missing icons in the map view.
"""

import os
import re
import logging
import shutil
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MapIconFix")

def find_map_view_file(base_dir):
    """Find the map view file that contains icon references."""
    potential_files = [
        "creepy_map_view.py",
        "map_view.py",
        "mapview.py",
        "map_widget.py"
    ]
    
    for root, _, files in os.walk(base_dir):
        for filename in files:
            if filename.lower() in [f.lower() for f in potential_files]:
                return os.path.join(root, filename)
    
    return None

def add_direct_icon_paths(map_file):
    """Modify the map view file to add direct icon path references."""
    if not os.path.exists(map_file):
        logger.error(f"Map view file not found: {map_file}")
        return False
    
    # Create backup
    backup_path = map_file + '.bak'
    shutil.copy2(map_file, backup_path)
    logger.info(f"Created backup at {backup_path}")
    
    try:
        with open(map_file, 'r') as f:
            content = f.read()
        
        # Check if we need to add imports
        needs_import = 'from creepy.resources.icons import Icons' not in content
        
        if needs_import:
            # Add import for Icons class
            import_pattern = r'(from\s+PyQt5\.QtGui\s+import.*?)(\n)'
            if re.search(import_pattern, content):
                content = re.sub(
                    import_pattern, 
                    r'\1\2from creepy.resources.icons import Icons\n', 
                    content
                )
            else:
                # Try another common import pattern
                import_pattern = r'(import\s+.*?)(\n\n)'
                if re.search(import_pattern, content):
                    content = re.sub(
                        import_pattern, 
                        r'\1\2from creepy.resources.icons import Icons\n\n', 
                        content
                    )
                else:
                    # Add at the top if no other imports found
                    content = "from creepy.resources.icons import Icons\n\n" + content
        
        # Add debug logging for icon loading
        init_pattern = r'def\s+__init__\s*\(\s*self\s*,.*?\):\s*'
        if re.search(init_pattern, content, re.DOTALL):
            init_end = re.search(init_pattern, content, re.DOTALL).end()
            debug_code = "\n        # Debug icon loading\n"
            debug_code += "        import logging\n"
            debug_code += "        self.logger = logging.getLogger(__name__)\n"
            debug_code += "        self.logger.info('Map view initialized, checking icons...')\n"
            debug_code += "        icon_names = ['add_24dp_000000', 'remove_24dp_000000', 'map_32dp_000000', 'person_24dp_000000']\n"
            debug_code += "        for name in icon_names:\n"
            debug_code += "            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources', f'{name}.png')\n"
            debug_code += "            if os.path.exists(icon_path):\n"
            debug_code += "                self.logger.info(f'Icon {name} found at {icon_path}')\n"
            debug_code += "            else:\n"
            debug_code += "                self.logger.warning(f'Icon {name} NOT found at {icon_path}')\n"
            
            content = content[:init_end] + debug_code + content[init_end:]
        
        # Find icon references in the map view
        icon_patterns = [
            r'QIcon\s*\(\s*[\'"]([^\'"]*)[\'"]\s*\)',
            r'QPixmap\s*\(\s*[\'"]([^\'"]*)[\'"]\s*\)',
            r'\.setIcon\s*\(\s*QIcon\s*\(\s*[\'"]([^\'"]*)[\'"]\s*\)\s*\)',
            r'\.setPixmap\s*\(\s*QPixmap\s*\(\s*[\'"]([^\'"]*)[\'"]\s*\)\s*\)',
        ]
        
        # Replace icon references with direct paths or Icons class usage
        for pattern in icon_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                full_match = match.group(0)
                icon_path = match.group(1)
                
                # Skip if already using Icons class
                if "Icons.get_icon" in full_match or "Icons.get_pixmap" in full_match:
                    continue
                
                # If using resource path
                if icon_path.startswith(":/") or ":/creepy/icon/" in icon_path:
                    icon_name = icon_path.split("/")[-1].split(".")[0]
                    if "QIcon" in full_match:
                        replacement = f"Icons.get_icon(\"{icon_name}\")"
                    else:
                        replacement = f"Icons.get_pixmap(\"{icon_name}\")"
                    content = content.replace(full_match, replacement)
                    logger.info(f"Replaced resource icon reference: {icon_name}")
                
                # If using relative or absolute path
                elif ".png" in icon_path.lower():
                    icon_name = os.path.basename(icon_path).split(".")[0]
                    if "QIcon" in full_match:
                        replacement = f"Icons.get_icon(\"{icon_name}\")"
                    else:
                        replacement = f"Icons.get_pixmap(\"{icon_name}\")"
                    content = content.replace(full_match, replacement)
                    logger.info(f"Replaced file path icon reference: {icon_name}")
        
        # Add a special check for marker icons which might be loaded differently
        marker_patterns = [
            r'(\w+)\s*=\s*L\.marker\s*\(',
            r'\.marker\s*\(\s*\[',
            r'\.marker\s*\('
        ]
        
        for pattern in marker_patterns:
            if re.search(pattern, content):
                # Add code to ensure marker icons have proper paths
                setup_method = re.search(r'def\s+setup(UI|Map|View).*?\(.*?\):', content)
                if setup_method:
                    setup_pos = setup_method.end()
                    marker_fix = "\n        # Ensure marker icons are available\n"
                    marker_fix += "        try:\n"
                    marker_fix += "            import os\n"
                    marker_fix += "            marker_icon = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources', 'map_32dp_000000.png')\n"
                    marker_fix += "            self.logger.info(f'Using marker icon from: {marker_icon}')\n"
                    marker_fix += "            if hasattr(self, 'map') and hasattr(self.map, 'options'):\n"
                    marker_fix += "                self.map.options['icon'] = marker_icon\n"
                    marker_fix += "                self.logger.info('Set marker icon in map options')\n"
                    marker_fix += "        except Exception as e:\n"
                    marker_fix += "            self.logger.error(f'Failed to set marker icon: {e}')\n"
                    
                    content = content[:setup_pos] + marker_fix + content[setup_pos:]
                    logger.info("Added marker icon fix")
        
        # Write the modified content
        with open(map_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Successfully patched map view file: {map_file}")
        return True
    
    except Exception as e:
        logger.error(f"Error patching map view file: {e}")
        # Restore backup
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, map_file)
            logger.info(f"Restored backup from {backup_path}")
        return False

def create_marker_icons(resources_dir):
    """Ensure marker icons are available and properly named for the map."""
    # Common map marker icon names
    marker_icon_names = [
        "marker.png",
        "marker-icon.png",
        "marker_icon.png",
        "map-marker.png",
        "map_marker.png",
        "pin.png",
        "location.png",
        "location-marker.png"
    ]
    
    # Check if we have our material design map icon
    map_icon = os.path.join(resources_dir, "map_32dp_000000.png")
    if os.path.exists(map_icon):
        logger.info(f"Found map icon: {map_icon}")
        
        # Create marker icons if they don't exist
        for name in marker_icon_names:
            marker_path = os.path.join(resources_dir, name)
            if not os.path.exists(marker_path):
                try:
                    shutil.copy2(map_icon, marker_path)
                    logger.info(f"Created marker icon: {marker_path}")
                except Exception as e:
                    logger.error(f"Failed to create marker icon: {e}")
    else:
        logger.warning(f"Map icon not found: {map_icon}")
        # Try to find any icon that might work as a marker
        for root, _, files in os.walk(resources_dir):
            for file in files:
                if file.endswith(".png") and ("map" in file.lower() or "marker" in file.lower() or "pin" in file.lower() or "location" in file.lower()):
                    source = os.path.join(root, file)
                    for name in marker_icon_names:
                        marker_path = os.path.join(resources_dir, name)
                        if not os.path.exists(marker_path):
                            try:
                                shutil.copy2(source, marker_path)
                                logger.info(f"Created marker icon from {file}: {marker_path}")
                            except Exception as e:
                                logger.error(f"Failed to create marker icon: {e}")
                    break
    
    return True

def main():
    logger.info("Starting map icon fix")
    
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..")
    resources_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
    
    # Find the map view file
    map_file = find_map_view_file(base_dir)
    if not map_file:
        logger.error("Could not find map view file")
        return 1
    
    logger.info(f"Found map view file: {map_file}")
    
    # Create marker icons
    if create_marker_icons(resources_dir):
        logger.info("Successfully created marker icons")
    else:
        logger.error("Failed to create marker icons")
    
    # Patch the map view file
    if add_direct_icon_paths(map_file):
        logger.info("Successfully patched map view file with direct icon paths")
    else:
        logger.error("Failed to patch map view file")
        return 1
    
    logger.info("Map icon fix completed successfully")
    logger.info("Please restart CreepyAI for changes to take effect")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
