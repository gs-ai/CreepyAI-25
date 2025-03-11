#!/usr/bin/env python3
"""
Test plugins by running them and displaying their locations on a map.
This is a standalone script to verify that plugins are generating location data.
"""
import os
import sys
import logging
from typing import List, Dict, Any
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_plugins_for_locations():
    """Test running plugins and see if they generate location data"""
    try:
        # Import plugin manager
        from app.core.plugins import PluginManager
        
        # Create plugin manager
        plugin_manager = PluginManager()
        
        # Discover plugins
        plugins = plugin_manager.discover_plugins()
        logger.info(f"Discovered {len(plugins)} plugins")
        
        # Get all categories
        categories = plugin_manager.get_categories()
        logger.info(f"Plugin categories: {', '.join(categories)}")
        
        # Test location plugins
        location_plugins = plugin_manager.get_plugins_by_category("location_services")
        logger.info(f"Found {len(location_plugins)} location service plugins")
        
        if not location_plugins:
            logger.warning("No location service plugins found. Checking all plugins for location data capabilities.")
            # Try all plugins
            location_plugins = plugins
        
        for name, plugin in location_plugins.items():
            logger.info(f"Testing plugin: {name}")
            category = plugin_manager.get_category(name)
            
            # Different plugins need different inputs
            try:
                if name == "osm_search":
                    # For OSM search, we need a search term
                    logger.info("Running OSM search plugin with test query 'Paris'")
                    results = plugin_manager.run_plugin(name, "Paris")
                    
                elif name == "exif_extractor":
                    # For EXIF extraction, we need image files
                    logger.info("EXIF extractor plugin needs image files with GPS data - skipping automated test")
                    continue
                    
                else:
                    # Try running without arguments
                    logger.info(f"Running plugin {name} with no arguments")
                    results = plugin_manager.run_plugin(name)
                
                # Check results
                if results:
                    if isinstance(results, list):
                        locations = [item for item in results if isinstance(item, dict) and 'lat' in item and 'lon' in item]
                        if locations:
                            logger.info(f"Plugin {name} returned {len(locations)} locations")
                            for i, loc in enumerate(locations[:3]):  # Show first 3
                                logger.info(f"  Location {i+1}: {loc.get('lat')}, {loc.get('lon')} - {loc.get('name', 'Unnamed')}")
                            if len(locations) > 3:
                                logger.info(f"  ... and {len(locations) - 3} more locations")
                        else:
                            logger.warning(f"Plugin {name} returned data but no recognizable locations: {results[:100]}...")
                    else:
                        logger.warning(f"Plugin {name} did not return a list: {type(results)}")
                else:
                    logger.warning(f"Plugin {name} returned no results")
            except Exception as e:
                logger.error(f"Error testing plugin {name}: {e}", exc_info=True)
        
        # Generate a simple HTML map to display results
        generate_test_map()
                
    except ImportError as e:
        logger.error(f"Error importing PluginManager: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)

def generate_test_map():
    """Generate a simple HTML map with test location data"""
    try:
        # Create test data with a few locations
        test_locations = [
            {"lat": 48.8566, "lon": 2.3522, "name": "Paris", "info": "Test location"},
            {"lat": 51.5074, "lon": -0.1278, "name": "London", "info": "Test location"},
            {"lat": 40.7128, "lon": -74.0060, "name": "New York", "info": "Test location"},
        ]
        
        # Create HTML file
        html_file = os.path.join(project_root, 'test_map.html')
        with open(html_file, 'w') as f:
            f.write('''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>CreepyAI Plugin Test Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <style>
        body { margin: 0; padding: 0; }
        #map { position: absolute; top: 0; bottom: 0; width: 100%; }
        .info-panel {
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1000;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
            max-width: 300px;
        }
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="info-panel">
        <h3>CreepyAI Plugin Test</h3>
        <p>This map shows test location data.</p>
        <p>To see actual plugin data, run the application and use the plugin browser.</p>
    </div>
    <script>
        var map = L.map('map').setView([0, 0], 2);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        var bounds = L.latLngBounds();
        
        // Add test markers
        var locations = ''' + json.dumps(test_locations) + ''';
        
        locations.forEach(function(loc) {
            var marker = L.marker([loc.lat, loc.lon]).addTo(map);
            marker.bindPopup("<b>" + loc.name + "</b><br>" + loc.info);
            bounds.extend([loc.lat, loc.lon]);
        });
        
        // Fit bounds to markers
        if (locations.length > 0) {
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    </script>
</body>
</html>''')
        
        logger.info(f"Generated test map at {html_file}")
        logger.info(f"Open {html_file} in your browser to view the test map")
        
    except Exception as e:
        logger.error(f"Error generating test map: {e}", exc_info=True)

if __name__ == "__main__":
    test_plugins_for_locations()
