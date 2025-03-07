# CreepyAI Plugin Development Guide

## Overview
CreepyAI uses a plugin system based on yapsy to extend its functionality for retrieving location data from different sources. This guide explains how to create a new plugin.

## Plugin Structure
Each plugin must be in a separate directory under the `plugins` folder with these files:
- `plugin_name.py`: Main plugin code
- `plugin_name.yapsy-plugin`: Plugin metadata
- `plugin_name.conf`: Configuration settings
- `logo.png`: Plugin icon (32x32px recommended)

## Creating a Plugin

### 1. Plugin Metadata File (example.yapsy-plugin)
