# CreepyAI Social Media Plugins

This document provides information about the social media plugins available in CreepyAI, how to configure them, and how to use them effectively.

## Overview

CreepyAI's social media plugins allow you to extract location data from various social media platforms without requiring API access. These plugins work with data exports from the respective platforms, which users can obtain through the platforms' data download features.

## Available Plugins

| Plugin | Data Source | Export Type | Location Data Types |
|--------|------------|-------------|---------------------|
| Facebook | Data export | ZIP/folder | Check-ins, posts with location, location history |
| Instagram | Data export | ZIP/folder | Posts with location, stories with location |
| Twitter | Data export | ZIP/folder | Tweets with location, profile location |
| LinkedIn | Data export | ZIP/folder | Profile location, job locations, education locations |
| TikTok | Data export | ZIP/folder | Videos with location, profile information |
| Snapchat | Data export | ZIP/folder | Memories, stories with location |
| Pinterest | Data export | ZIP/folder | Pins with location, boards with location |
| Yelp | Data export | ZIP/folder | Check-ins, reviews, profile location |

## How to Get Data Exports

### Facebook
1. Go to **Settings & Privacy** > **Settings** > **Your Facebook Information** > **Download Your Information**
2. Select JSON format and media quality (low is fine for location data)
3. Select relevant data categories (Posts, Location, etc.)
4. Create file and download when ready

### Instagram
1. Go to **Settings** > **Privacy and Security** > **Data Download**
2. Request download in JSON format
3. Download when ready

### Twitter
1. Go to **Settings and Privacy** > **Your Account** > **Download an archive of your data**
2. Confirm your password and request the archive
3. Download when ready (usually takes 24 hours)

### LinkedIn
1. Go to **Settings & Privacy** > **Data Privacy** > **Get a copy of your data**
2. Select the data you want (connections, positions)
3. Request archive and download when ready

### TikTok
1. Go to **Settings and Privacy** > **Privacy** > **Personalization and Data** > **Download TikTok Data**
2. Request data and download when ready

### Snapchat
1. Go to **Settings** > **My Data** > **Submit Request**
2. Download when ready (usually takes 24 hours)

### Pinterest
1. Go to **Settings** > **Privacy and Data** > **Request your data**
2. Download when ready

### Yelp
1. Go to **Account Settings** > **Privacy Settings** > **Download Yelp Data**
2. Request data and download when ready

## Plugin Configuration

Each plugin requires specific configuration to work properly. Here are the configuration options for each plugin:

### Facebook Plugin

```json
{
  "data_directory": "/path/to/facebook/export"
}
```

### Instagram Plugin

```json
{
  "data_directory": "/path/to/instagram/export"
}
```

### Twitter Plugin

```json
{
  "archive_location": "/path/to/twitter/export"
}
```

### LinkedIn Plugin

```json
{
  "data_directory": "/path/to/linkedin/export",
  "include_connections": true,
  "include_jobs": true,
  "include_education": true
}
```

### TikTok Plugin

```json
{
  "data_directory": "/path/to/tiktok/export",
  "attempt_geocoding": true
}
```

### Snapchat Plugin

```json
{
  "data_directory": "/path/to/snapchat/export",
  "memories_json": "",
  "process_memories": true,
  "process_stories": true
}
```

### Pinterest Plugin

```json
{
  "data_directory": "/path/to/pinterest/export",
  "attempt_geocoding": true
}
```

### Yelp Plugin

```json
{
  "data_directory": "/path/to/yelp/export"
}
```

## Testing Plugins

You can test plugins using the included `plugin_tester.py` script:

```bash
python -m app.plugins.social_media.plugin_tester facebook /path/to/facebook/export --visualize
```

## Privacy and Ethical Use

These plugins are designed for educational and legitimate investigative purposes. Always use them responsibly:

1. **Only analyze data you have legal access to**
2. **Respect privacy laws and regulations**
3. **Do not use for stalking or harassment**
4. **Secure any extracted data appropriately**

## Troubleshooting

### Common Issues

1. **Plugin says "not configured"**
   - Make sure you've set the data_directory to a valid path
   - Check that the directory contains the expected data files

2. **No locations found**
   - Check if there are actually locations in the data export
   - Look at log files for any errors
   - Try with a different data export

3. **Error reading files**
   - Make sure the export is in JSON format
   - Try extracting the ZIP file manually first
   - Check for non-standard characters in filenames

### Logging

Enable DEBUG level logging to get more information about what the plugin is doing:

```python
import logging
logging.getLogger('creepyai.plugins.social_media').setLevel(logging.DEBUG)
```

## Contributing

We welcome contributions to improve these plugins:

1. Better handling of different export formats
2. Support for additional platforms
3. Enhanced location extraction techniques
4. Improved geocoding for text-based locations

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details on how to contribute.
