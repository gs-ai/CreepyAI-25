    #!/usr/bin/env python3
"""
Icon Path Fix for CreepyAI
This script ensures the application correctly finds icons in the existing resources directory.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("IconPathFix")

def update_icon_class():
    """Update the Icons class to point to the correct directory."""
    icons_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             "resources", "icons.py")
    
    # Create the file if it doesn't exist
    os.makedirs(os.path.dirname(icons_file), exist_ok=True)
    
    # Content for the Icons class
    content = """#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PyQt5.QtGui import QIcon, QPixmap

class Icons:
    \"\"\"Helper class to provide icons from the correct location\"\"\"

    # Point directly to the existing resources directory
    ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")

    @staticmethod
    def get_icon(name):
        \"\"\"Get an icon either from resources or from filesystem\"\"\"
        # Try from resources first (prefix with 'creepy/')
        icon = QIcon(f":/creepy/icon/{name}")
        
        # If the icon is empty, try to load from file
        if icon.isNull():
            # First try in the root resources directory
            icon_path = os.path.join(Icons.ICON_DIR, f"{name}.png")
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
            else:
                # Then try in any subdirectories
                for root, _, files in os.walk(Icons.ICON_DIR):
                    for file in files:
                        if file == f"{name}.png":
                            icon = QIcon(os.path.join(root, file))
                            return icon
                
                # Return a blank icon rather than None to avoid crashes
                print(f"Warning: Icon '{name}' not found")
                icon = QIcon()
                
        return icon

    @staticmethod
    def get_pixmap(name):
        \"\"\"Get a pixmap either from resources or from filesystem\"\"\"
        # Try from resources first
        pixmap = QPixmap(f":/creepy/icon/{name}")
        
        # If the pixmap is empty, try to load from file
        if pixmap.isNull():
            # First try in the root resources directory
            pixmap_path = os.path.join(Icons.ICON_DIR, f"{name}.png")
            if os.path.exists(pixmap_path):
                pixmap = QPixmap(pixmap_path)
            else:
                # Then try in any subdirectories
                for root, _, files in os.walk(Icons.ICON_DIR):
                    for file in files:
                        if file == f"{name}.png":
                            pixmap = QPixmap(os.path.join(root, file))
                            return pixmap
                
                # Return a blank pixmap rather than None to avoid crashes
                print(f"Warning: Pixmap '{name}' not found")
                pixmap = QPixmap()
                
        return pixmap
"""
    
    # Create backup if the file exists
    if os.path.exists(icons_file):
        backup = icons_file + '.bak'
        shutil.copy2(icons_file, backup)
        logger.info(f"Created backup at {backup}")
    
    # Write the new content
    with open(icons_file, 'w') as f:
        f.write(content)
    
    logger.info(f"Updated Icons class at {icons_file}")
    return True

def create_resource_generator():
    """Create a script to generate the Qt resource file from existing icons."""
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                              "generate_resources.py")
    
    content = """#!/usr/bin/env python3
# This script generates the Qt resource file from icons in the resources directory

import os
import sys
import subprocess
from pathlib import Path

def generate_qrc():
    \"\"\"Generate the .qrc XML file from icons in resources directory\"\"\"
    # Get the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(base_dir, "creepy", "resources")
    qrc_path = os.path.join(base_dir, "creepy.qrc")
    
    # Start the QRC file
    with open(qrc_path, "w") as qrc_file:
        qrc_file.write('<!DOCTYPE RCC>\\n<RCC version="1.0">\\n')
        qrc_file.write('    <qresource prefix="/creepy">\\n')
        
        # Walk through the resources directory
        for root, _, files in os.walk(resources_dir):
            for file in files:
                if file.endswith(".png"):
                    # Get relative path from resources dir
                    rel_dir = os.path.relpath(root, resources_dir)
                    if rel_dir == ".":
                        # File is in the root resources directory
                        file_path = f"icon/{file}"
                    else:
                        # File is in a subdirectory
                        file_path = f"icon/{rel_dir}/{file}"
                    
                    # Get absolute path for the resource compiler
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, base_dir)
                    
                    # Add to QRC file
                    qrc_file.write(f'        <file alias="{file_path}">{rel_path}</file>\\n')
        
        # Close the QRC file
        qrc_file.write('    </qresource>\\n')
        qrc_file.write('</RCC>\\n')
    
    print(f"Generated QRC file at {qrc_path}")
    return qrc_path

def compile_resources(qrc_path):
    \"\"\"Compile the .qrc file into a Python resource file\"\"\"
    try:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "creepy_resources_rc.py")
        
        # Try using pyrcc5 (for PyQt5)
        try:
            result = subprocess.run(["pyrcc5", qrc_path, "-o", output_path], 
                                   check=True, capture_output=True, text=True)
            print(f"Successfully compiled resources to {output_path}")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error running pyrcc5: {e}")
            print(e.stderr)
            
            # Try using rcc directly as fallback
            try:
                result = subprocess.run(["rcc", "-g", "python", qrc_path, "-o", output_path], 
                                       check=True, capture_output=True, text=True)
                print(f"Successfully compiled resources using rcc to {output_path}")
                print(result.stdout)
                return True
            except subprocess.CalledProcessError as e2:
                print(f"Error running rcc: {e2}")
                print(e2.stderr)
                return False
                
    except Exception as e:
        print(f"Error compiling resources: {e}")
        return False

if __name__ == "__main__":
    print("Generating Qt resources from existing icons...")
    qrc_path = generate_qrc()
    if compile_resources(qrc_path):
        print("Resource compilation complete!")
    else:
        print("Resource compilation failed.")
        sys.exit(1)
"""
    
    with open(script_path, 'w') as f:
        f.write(content)
    
    # Make it executable
    os.chmod(script_path, 0o755)
    
    logger.info(f"Created resource generator script at {script_path}")
    return True

def create_icon_documentation():
    """Create documentation about the icons and their usage."""
    doc_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                           "docs", "IconUsage.md")
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(doc_path), exist_ok=True)
    
    content = """# CreepyAI Icon Usage Guide

## Icon Location

All icons for CreepyAI are located in the following directory:
```
/Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources
```

This directory should not be moved or renamed as it would break icon references.

## Using Icons in the Application

There are three ways to use icons in the application:

### 1. Using the Icons Helper Class

The recommended way to use icons is through the Icons helper class:

```python
from resources.icons import Icons

# Get a QIcon object
my_icon = Icons.get_icon("plus")

# Get a QPixmap object
my_pixmap = Icons.get_pixmap("user")
```

This method provides fallbacks if the Qt resource system fails.

### 2. Using Qt Resource System

If the resource file is properly compiled, you can use the Qt resource system:

```python
from PyQt5.QtGui import QIcon, QPixmap

# Get a QIcon object
my_icon = QIcon(":/creepy/icon/plus.png")

# Get a QPixmap object
my_pixmap = QPixmap(":/creepy/icon/user.png")
```

### 3. Direct File Access (Not Recommended)

As a last resort, you can load icons directly from files:

```python
from PyQt5.QtGui import QIcon, QPixmap

# Get a QIcon object
my_icon = QIcon("/Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources/plus.png")

# Get a QPixmap object
my_pixmap = QPixmap("/Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources/user.png")
```

## Regenerating the Resource File

If you add or modify icons, you should regenerate the Qt resource file:

```bash
python /Users/mbaosint/Desktop/Projects/CreepyAI/generate_resources.py
```

This will scan the resources directory and create an updated resource file.

## Troubleshooting

If icons are not displaying:

1. Verify the icon exists in the resources directory
2. Try recompiling the resource file
3. Use the Icons helper class which provides fallbacks
4. Check the application logs for icon loading errors
"""
    
    with open(doc_path, 'w') as f:
        f.write(content)
    
    logger.info(f"Created icon documentation at {doc_path}")
    return True

def main():
    logger.info("Starting icon path fix")
    
    # Update the Icons class
    if update_icon_class():
        logger.info("Successfully updated Icons class")
    else:
        logger.error("Failed to update Icons class")
        return 1
    
    # Create resource generator script
    if create_resource_generator():
        logger.info("Successfully created resource generator script")
    else:
        logger.error("Failed to create resource generator script")
        return 1
    
    # Create icon documentation
    if create_icon_documentation():
        logger.info("Successfully created icon documentation")
    else:
        logger.error("Failed to create icon documentation")
        return 1
    
    logger.info("Icon path fix completed successfully")
    logger.info("To regenerate the resource file, run:")
    logger.info("python /Users/mbaosint/Desktop/Projects/CreepyAI/generate_resources.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
