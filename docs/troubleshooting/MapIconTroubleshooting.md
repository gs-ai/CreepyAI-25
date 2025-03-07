# Map Icon Troubleshooting Guide

## Common Issues with Map Icons

If icons are not appearing on the map in CreepyAI, try these troubleshooting steps:

### 1. Check for Missing Icon Files

The map component may be looking for specific icon filenames:

```bash
# Important map icon filenames
marker.png
marker-icon.png
map-marker.png
pin.png
location.png
```

These should be present in one of these directories:
- `/Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources/`
- `/Users/mbaosint/Desktop/Projects/CreepyAI/creepy/ui/map_resources/`
- `/Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources/leaflet/images/`

### 2. Check Map Implementation

Depending on which mapping library is used, the icon loading mechanism differs:

#### For Leaflet Maps:
- Icons must be in a specific directory structure
- Standard names like `marker-icon.png` and `marker-shadow.png` are expected
- Default path is `/leaflet/images/` relative to the application resources

#### For PyQt WebEngine Maps:
- Icons may need to be encoded in base64 within HTML/JavaScript
- Check if the map HTML template has proper icon references

#### For Custom QWidget-based Maps:
- Look for `QIcon` or `QPixmap` usage in the map view code
- Make sure the icons are loaded using the Icons helper class

### 3. Try Manual Icon Placement

If automated fixes don't work, you can try manually placing icons in all potential locations:

```bash
# Create directories
mkdir -p /Users/mbaosint/Desktop/Projects/CreepyAI/creepy/ui/map_resources/
mkdir -p /Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources/leaflet/images/

# Copy icons to all locations
cp /Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources/*.png /Users/mbaosint/Desktop/Projects/CreepyAI/creepy/ui/map_resources/
cp /Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources/*.png /Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources/leaflet/images/

# Create standard marker icons from existing icons
cp /Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources/map_32dp_000000.png /Users/mbaosint/Desktop/Projects/CreepyAI/creepy/ui/map_resources/marker.png
cp /Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources/map_32dp_000000.png /Users/mbaosint/Desktop/Projects/CreepyAI/creepy/ui/map_resources/marker-icon.png
cp /Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources/map_32dp_000000.png /Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources/leaflet/images/marker-icon.png
```

### 4. Add Debug Logging

Add debug statements to identify where the application is looking for icons:

```python
import os, logging
logger = logging.getLogger("MapIcons")

# List all places to look for icons
icon_locations = [
    "/Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources/",
    "/Users/mbaosint/Desktop/Projects/CreepyAI/creepy/ui/map_resources/",
    "/Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources/leaflet/images/"
]

# Check for common icon names
icon_names = ["marker.png", "marker-icon.png", "map_32dp_000000.png", "person_24dp_000000.png"]

for loc in icon_locations:
    for name in icon_names:
        path = os.path.join(loc, name)
        if os.path.exists(path):
            logger.info(f"Icon found: {path}")
        else:
            logger.warning(f"Icon missing: {path}")
```

### 5. Check Resource Compilation

Ensure the Qt resource system correctly includes the map icons:

```bash
# Generate a new resource file that explicitly includes map icons
python /Users/mbaosint/Desktop/Projects/CreepyAI/generate_resources.py

# Compile the resource file
pyrcc5 /Users/mbaosint/Desktop/Projects/CreepyAI/creepy.qrc -o /Users/mbaosint/Desktop/Projects/CreepyAI/creepy_resources_rc.py
```

### 6. Last Resort: Hardcode Icon Paths

If nothing else works, you may need to directly hardcode icon paths in the map implementation:

1. Find the map view file and locate where markers are created
2. Replace icon references with absolute paths to your icon files
3. If using Leaflet, modify any HTML/JS templates to use absolute paths
