# CreepyAI UI Components

This directory contains UI component definitions for CreepyAI that are not part of the main PyQt5 implementation.

## Directory Structure

```
ui/
├── components/       # Reusable UI components
├── forms/           # Form definitions
├── dialogs/         # Custom dialog definitions
└── theme/           # Theme-related files
```

## Creating Custom UI Components

1. Create a new Python file in the appropriate directory
2. Implement your component using PyQt5
3. Document the component API
4. Register the component in the UI registry

## Using UI Components

Import components as needed:

```python
from ui.components.map_widget import MapWidget
from ui.dialogs.export_dialog import ExportDialog

# Use the components
map_widget = MapWidget()
export_dialog = ExportDialog()
```

## UI Design Guidelines

- Follow the application's design language
- Support both light and dark themes
- Ensure all components are accessible
- Use the provided theme variables for colors
