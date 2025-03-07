# Plugin Troubleshooting Guide

This document provides guidance for resolving issues with CreepyAI plugins.

## Common Plugin Issues

### Syntax Errors

Common syntax issues include:
- Unclosed parentheses, brackets, or braces
- Unterminated string literals
- Missing colons after control flow statements
- Missing indentation after control flow statements

Use the plugin fixer to identify and resolve these issues:

```bash
./creepyai fix-plugins --scan-only  # Just scan for issues
./creepyai fix-plugins              # Scan and attempt to fix issues
```

### Plugin Structure Issues

Plugin structure issues occur when a plugin doesn't follow the expected format:
- Missing required methods (`get_version`, `is_configured`, `collect_locations`)
- Class definition problems
- Missing imports

Use the plugin health check to validate plugin structure:

```bash
./creepyai plugin-health
./creepyai plugin-health --detail   # For more detailed information
```

### Import Errors

Import errors occur when a plugin tries to import modules that aren't installed:

1. Install required dependencies:
   ```bash
   pip install <module_name>
   ```

2. Check for typos in import statements.

## Plugin Requirements

To be valid, a plugin must:

1. Be a Python file (`.py`) in the `plugins/` directory
2. Define at least one class with the following methods:
   - `get_version()`: Returns the plugin version
   - `is_configured()`: Checks if the plugin is properly configured
   - `collect_locations(target, date_from=None, date_to=None)`: Collects location data

## Testing Plugins

Use the plugin CLI to test a specific plugin:

```bash
./creepyai run-plugin <plugin_name> <target>
```

For example:
```bash
./creepyai run-plugin twitter_plugin username123
```

## Resolving Specific Issues

### Plugin Not Found

If a plugin isn't showing up in the list:
1. Make sure it's in the `plugins/` directory
2. Check for syntax errors with `./creepyai fix-plugins`
3. Make sure the filename ends with `.py` and doesn't start with `__`

### Plugin Won't Load

If a plugin is found but won't load:
1. Check for import errors in the plugin code
2. Verify the plugin has all required methods
3. Run `./creepyai plugin-health --detail` for more information

### Plugin Crashes When Used

If a plugin crashes during execution:
1. Run with debug logging: `./creepyai run-plugin <plugin_name> <target> --debug`
2. Check the plugin's error handling
3. Verify API endpoints if the plugin connects to external services

## Getting Help

If you continue to have issues, check the CreepyAI documentation or seek help from the community.