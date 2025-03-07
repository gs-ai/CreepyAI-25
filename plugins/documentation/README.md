# CreepyAI Plugins

This directory contains plugins for CreepyAI that extend its functionality.

## Plugin Structure

Each plugin should be in its own directory with the following structure:

```
plugin_name/
├── __init__.py          # Plugin initialization
├── plugin_name.yapsy-plugin  # Plugin metadata
└── resources/           # Plugin-specific resources
```

## Creating a New Plugin

1. Create a new directory for your plugin
2. Create a `.yapsy-plugin` file with metadata
3. Implement the required methods in your plugin class

## Available Plugin Types

- **DataSource**: Plugins that gather data from external sources
- **Analyzer**: Plugins that analyze collected data
- **Visualizer**: Plugins that visualize data in different formats
- **Exporter**: Plugins that export data to different formats

## Example Plugin

See `example_plugin/` for a basic plugin implementation.

## Plugin API Documentation

Refer to the `docs/plugins/` directory for full API documentation.
