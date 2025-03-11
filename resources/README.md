# CreepyAI Resources

This directory contains static resources used by the CreepyAI application.

## Directory Structure

- `assets/` - Static assets like images, icons, etc.
  - `images/` - General images used in the application
  - `icons/` - Application and UI icons
  - `sounds/` - Audio files and alert sounds
- `templates/` - Template files for generating content
  - `plugins/` - Templates for creating new plugins
  - `projects/` - Templates for creating new projects
  - `reports/` - Templates for report generation
- `docs/` - Documentation resources
- `samples/` - Sample data files and examples

## Usage

Resources can be accessed in the application using the resource manager:

```python
from app.utils.resource_manager import ResourceManager

# Get a resource file path
resource_manager = ResourceManager()
image_path = resource_manager.get_resource_path('assets/images/logo.png')
```
