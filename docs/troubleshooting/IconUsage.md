# CreepyAI Icon Usage Guide

## Icon Location

All icons for CreepyAI are located in the following directory:
```
/Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources
```

**Important**: This directory should not be moved or renamed as it would break icon references.

## Using Icons in the Application

There are three ways to use icons in the application:

### 1. Using the Icons Helper Class

The recommended way to use icons is through the Icons helper class:

```python
from creepy.resources.icons import Icons

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

## Checking and Fixing Missing Icons

To check for and fix missing icons:

1. Run the icon path fix utility:
   ```bash
   python /Users/mbaosint/Desktop/Projects/CreepyAI/creepy/utilities/icon_path_fix.py
   ```

2. Regenerate the Qt resource file:
   ```bash
   python /Users/mbaosint/Desktop/Projects/CreepyAI/generate_resources.py
   ```

3. Restart CreepyAI to load the updated resources

## Troubleshooting

If icons are not displaying:

1. Verify the icon exists in the resources directory:
   ```bash
   find /Users/mbaosint/Desktop/Projects/CreepyAI/creepy/resources -name "*.png"
   ```

2. Try recompiling the resource file manually:
   ```bash
   pyrcc5 /Users/mbaosint/Desktop/Projects/CreepyAI/creepy.qrc -o /Users/mbaosint/Desktop/Projects/CreepyAI/creepy_resources_rc.py
   ```

3. Use the Icons helper class which provides fallbacks

4. Check the application logs for icon loading errors
