<<<<<<< HEAD
# CreepyAI-25

### Current Version 
25.0

### Description 
Geolocation OSINT tool.

Creepy-25 is a geolocation OSINT tool. Gathers geolocation related information from online sources, and allows for presentation on map, search filtering based on exact location and/or date, export in csv format or kml for further analysis in Google Maps.

### Special Thanks 
The OG




=======
# CreepyAI - Geolocation OSINT Tool

CreepyAI is a geolocation intelligence tool that collects and analyzes location data from various sources including social networks, image metadata and other public sources. It allows OSINT investigators to track, visualize and export location data without requiring any API keys.

## Repository

This project is available on GitHub: [https://github.com/gs-ai/CreepyAI-25](https://github.com/gs-ai/CreepyAI-25)

## Features

- Extract location data from image EXIF metadata
- Generate mock social media data for testing and demonstrations
- Visualize locations on interactive maps
- Filter results by date and geographic proximity
- Generate heat maps to identify location clusters
- Export data to multiple formats (CSV, KML, GeoJSON, Interactive HTML)
- Plugin system for easy extension

## Setup

To set up the repository:

```bash
# Clone the repository
git clone https://github.com/gs-ai/CreepyAI-25.git
cd CreepyAI-25

# Set up your environment (example)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

If you encounter issues with PyQt5 installation (especially on macOS), use our helper script:

```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

## Starting CreepyAI

```bash
cd CreepyAI-25/creepy
python CreepyMain.py
```

## Using CreepyAI Without API Keys

CreepyAI includes plugins that don't require API keys:

### Local Files Plugin

Extract geolocation data from EXIF metadata in local image files:

1. Go to "File" > "New Project"
2. Enter project details and select "Local Files Plugin"
3. Enter the path to a directory containing images
4. Select the directory from the search results
5. Click "Finish" to create the project
6. Right-click on the project in the tree view and select "Analyze Target"
7. View the extracted location data on the map

### Mock Social Media Plugin

Generate mock social media data for testing and demonstrations:

1. Go to "File" > "New Project"
2. Enter project details and select "Mock Social Media Plugin"
3. Enter any username as a search term
4. Select the user from the search results
5. Click "Finish" to create the project
6. Right-click on the project in the tree view and select "Analyze Target"
7. View the generated mock location data on the map

## Working with Location Data

### Filtering Locations

- **Date Filter**: Filter locations based on date ranges
  - Go to "Analysis" > "Filter Locations" > "By Date"
  - Select start and end dates

- **Position Filter**: Filter locations within a radius of a point
  - Go to "Analysis" > "Filter Locations" > "By Position"
  - Select a point on the map and specify a radius

- **Remove Filters**: Clear all active filters
  - Go to "Analysis" > "Remove Filters"

### Visualizing Data

- **Heat Map**: Toggle between marker view and heat map
  - Go to "View" > "Show Heat Map"
  
- **Map Navigation**: 
  - Zoom with mouse wheel or +/- buttons
  - Click and drag to pan
  - Click on markers to see details

### Exporting Data

- **CSV Export**: Export all or filtered locations to CSV
  - Right-click on a project > "Export as CSV"
  - For filtered data, use "Export Filtered" > "Export as CSV"

- **KML Export**: Export to Google Earth format
  - Right-click on a project > "Export as KML"

- **GeoJSON Export**: Export to GeoJSON format for GIS tools
  - Right-click on a project > "Export as GeoJSON"

- **Interactive HTML**: Export as standalone interactive map
  - Right-click on a project > "Export as Interactive HTML"

## Extending CreepyAI

### Creating Custom Plugins

1. Create a directory under `/plugins` with your plugin name
2. Create three required files:
   - `plugin_name.py`: Implementation of your plugin
   - `plugin_name.yapsy-plugin`: Plugin metadata
   - `plugin_name.conf`: Configuration settings
3. Implement the required methods:
   - `searchForTargets(self, search_term)`: Find potential targets
   - `returnLocations(self, target, search_params)`: Retrieve location data
4. Restart CreepyAI to load your plugin

See the included plugins for examples.

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   - Ensure all required packages are installed
   - Try reinstalling with `pip install -r requirements.txt`
   - For PyQt5 issues, run `./install_dependencies.sh`

2. **Plugin Not Working**
   - Check plugin configuration in "Tools" > "Plugins Configuration"
   - Verify that the plugin is properly enabled in your project

3. **No Locations Found**
   - For Local Files: Ensure images have EXIF GPS data
   - For Mock Data: Try increasing the location count in plugin settings

4. **Application Crashes**
   - Check the log files in the application directory
   - Try updating to the latest version

## Pushing Updates

To push updates to the repository:

```bash
python push_updates.py "Your commit message"
```

## Project Structure

- `CreepyAI-25/`: Main project directory
  - `creepy/`: Core application code
    - `models/`: Data models and plugin interfaces
    - `utilities/`: Helper functions and utilities
  - `plugins/`: Input and analysis plugins

## License

This project is licensed under the MIT License.

## Acknowledgements

CreepyAI is based on the original Creepy geolocation tool, updated and enhanced with modern features and no-API plugins.

Homage to the OG.
>>>>>>> 17db464 (Update)
