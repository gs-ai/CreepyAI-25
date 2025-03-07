# Migration Guide

This guide explains how to migrate from the older PyQt5-based Creepy to the newer CreepyAI implementation, which supports both PyQt5 and Tkinter interfaces.

## Overview of Changes

CreepyAI now supports two distinct UI frameworks:

1. **PyQt5** - The original UI used in Creepy
2. **Tkinter** - A new UI implementation that doesn't require PyQt5

The core functionality has been abstracted to work with either UI through a bridge layer.

## How to Migrate Projects

### For End Users

1. **Launch the new application** using `python launch_creepyai.py`
2. The launcher will automatically detect available UI frameworks and choose the appropriate one.
3. You can specify a UI preference with the `--ui` flag:
   - `python launch_creepyai.py --ui pyqt5` (for PyQt5)
   - `python launch_creepyai.py --ui tkinter` (for Tkinter)

### For Plugin Developers

1. **Use the new plugin interface** defined in `plugins/base_plugin.py`
2. Ensure your plugins work with the `PluginManager` class instead of directly with the UI
3. Return data in standard Python types (dictionaries, lists) rather than UI-specific types

### Configuration Files

The configuration system has been unified:

1. Configuration files are now stored in:
   - Windows: `%APPDATA%\Local\CreepyAI`
   - macOS: `~/.config/creepyai`
   - Linux: `~/.local/share/creepyai`

2. Projects can be imported from the old format to the new format using the UI

## Project Structure

The new project structure maintains backward compatibility while introducing new components:

```
CreepyAI/
├── core/                 # Core functionality
│   ├── config_manager.py # Configuration management
│   ├── ui_bridge.py      # Bridge between UI implementations
│   └── ...
├── models/               # Data models
│   ├── PluginManager.py  # Unified plugin manager
│   └── ...
├── plugins/              # Plugin implementations
├── ui/                   # UI components
├── utilities/            # Utility functions
├── CreepyMain.py         # PyQt5 main application
├── creepyai_gui.py       # Tkinter main application
└── launch_creepyai.py    # Unified launcher script
```

## Key API Changes

### Plugin API

Plugins now need to implement the following interface:

```python
class MyPlugin:
    def __init__(self):
        self.name = "My Plugin"
        self.description = "Description of my plugin"
        
    def getName(self):
        return self.name
        
    # Instead of UI-specific configuration
    def getConfiguration(self):
        return {
            "string_options": {"api_key": ""},
            "boolean_options": {"enabled": True}
        }
        
    # Return standard Python types
    def returnLocations(self, target, config):
        return [{
            "plugin": self.name,
            "date": datetime.datetime.now(),
            "lon": 0.0,
            "lat": 0.0,
            "context": "Context information",
            "infowindow": "Info for display",
            "shortName": "Location name"
        }]
```

## Troubleshooting

If you encounter issues migrating:

1. Check the logs in `creepyai.log` and `launcher.log`
2. Make sure all dependencies are installed:
   ```
   pip install -r requirements.txt
   ```
3. For PyQt5 issues on macOS, run the fix script:
   ```
   ./fix_pyqt_installation.sh
   ```

## Getting Help

For more assistance, visit the project repository or consult the documentation in the `docs/` directory.
