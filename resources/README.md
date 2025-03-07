# CreepyAI Resources

This directory contains all resource files used by CreepyAI.

## Directory Structure

- `icons/` - Application icons and images
- `styles/` - QSS style files for theming
- `ui/` - Qt Designer UI files
- `templates/` - Template files for new projects
- `data/` - Default database and configuration templates

## Compiling Resources

Resource files need to be compiled before they can be used by the application:

1. Compile Qt Resources:
   ```bash
   pyrcc5 -o resources/creepy_resources_rc.py resources/creepy_resources.qrc
   ```

2. Compile UI Files:
   ```bash
   python compile_ui.py
   ```

## Adding New Resources

When adding new resources:

1. Add the file to the appropriate subdirectory
2. Update the `creepy_resources.qrc` file to include the new resource
3. Recompile the resources

## Theme Files

The application supports multiple themes through QSS stylesheets:

- `styles/base.qss` - Common styling used by all themes
- `styles/dark.qss` - Dark theme
- `styles/light.qss` - Light theme
