#!/usr/bin/env python3
"""
Plugin Tester for CreepyAI Social Media Plugins

This script allows testing individual social media plugins with various configurations
and visualizes the results. It's useful for plugin development and debugging.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import csv
import webbrowser
import tempfile

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

# Import plugin classes
from app.plugins.social_media.facebook_plugin import FacebookPlugin
from app.plugins.social_media.instagram_plugin import InstagramPlugin
from app.plugins.social_media.twitter_plugin import TwitterPlugin
from app.plugins.social_media.linkedin_plugin import LinkedInPlugin
from app.plugins.social_media.tiktok_plugin import TikTokPlugin
from app.plugins.social_media.snapchat_plugin import SnapchatPlugin
from app.plugins.social_media.pinterest_plugin import PinterestPlugin
from app.plugins.social_media.yelp_plugin import YelpPlugin
from app.plugins.base_plugin import LocationPoint

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("plugin_tester")

# Plugin mapping
PLUGINS = {
    "facebook": FacebookPlugin,
    "instagram": InstagramPlugin,
    "twitter": TwitterPlugin,
    "linkedin": LinkedInPlugin,
    "tiktok": TikTokPlugin,
    "snapchat": SnapchatPlugin,
    "pinterest": PinterestPlugin,
    "yelp": YelpPlugin
}

def test_plugin(plugin_name: str, config: Dict[str, Any], target: str, 
                date_from: Optional[datetime] = None, 
                date_to: Optional[datetime] = None,
                export_results: bool = False) -> List[LocationPoint]:
    """
    Test a specific plugin with the given configuration
    
    Args:
        plugin_name: Name of the plugin to test
        config: Plugin configuration dictionary
        target: Target to search for
        date_from: Optional start date filter
        date_to: Optional end date filter
        export_results: Whether to export results to JSON
        
    Returns:
        List of LocationPoint objects found
    """
    if plugin_name.lower() not in PLUGINS:
        logger.error(f"Plugin '{plugin_name}' not found. Available plugins: {', '.join(PLUGINS.keys())}")
        return []
    
    # Initialize the plugin
    plugin_class = PLUGINS[plugin_name.lower()]
    plugin = plugin_class()
    logger.info(f"Testing {plugin.name} plugin ({plugin_name})")
    
    # Apply configuration
    for key, value in config.items():
        plugin.config[key] = value
    
    # Check if plugin is properly configured
    is_configured, message = plugin.is_configured()
    if not is_configured:
        logger.error(f"Plugin is not properly configured: {message}")
        return []
    
    logger.info(f"Plugin configuration: {plugin.config}")
    
    # Collect locations
    logger.info(f"Collecting locations for target '{target}'...")
    start_time = datetime.now()
    locations = plugin.collect_locations(target, date_from, date_to)
    elapsed_time = datetime.now() - start_time
    
    # Display results
    logger.info(f"Found {len(locations)} locations in {elapsed_time.total_seconds():.2f} seconds")
    
    if export_results and locations:
        export_path = export_to_csv(locations, plugin_name)
        logger.info(f"Exported results to {export_path}")
    
    return locations

def export_to_csv(locations: List[LocationPoint], plugin_name: str) -> str:
    """Export location points to CSV file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = f"{plugin_name}_results_{timestamp}.csv"
    
    with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['latitude', 'longitude', 'timestamp', 'source', 'context']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for loc in locations:
            writer.writerow({
                'latitude': loc.latitude,
                'longitude': loc.longitude,
                'timestamp': loc.timestamp.isoformat(),
                'source': loc.source,
                'context': loc.context
            })
    
    return os.path.abspath(export_path)

def export_to_json(locations: List[LocationPoint], plugin_name: str) -> str:
    """Export location points to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = f"{plugin_name}_results_{timestamp}.json"
    
    location_dicts = []
    for loc in locations:
        location_dicts.append({
            'latitude': loc.latitude,
            'longitude': loc.longitude,
            'timestamp': loc.timestamp.isoformat(),
            'source': loc.source,
            'context': loc.context
        })
    
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(location_dicts, f, indent=2)
    
    return os.path.abspath(export_path)

def visualize_results(locations: List[LocationPoint], plugin_name: str) -> None:
    """Create an HTML map to visualize the location points"""
    if not locations:
        logger.info("No locations to visualize")
        return
    
    # Create a simple HTML map using folium
    try:
        import folium
        from folium.plugins import MarkerCluster
    except ImportError:
        logger.error("Folium is required for visualization. Install with: pip install folium")
        return
    
    # Calculate map center
    lat_sum = sum(loc.latitude for loc in locations)
    lon_sum = sum(loc.longitude for loc in locations)
    center = [lat_sum / len(locations), lon_sum / len(locations)]
    
    # Create the map
    m = folium.Map(location=center, zoom_start=5)
    
    # Add marker cluster
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers
    for idx, loc in enumerate(locations):
        tooltip = f"{loc.source}: {loc.context[:50]}..." if len(loc.context) > 50 else loc.context
        popup_html = f"""
        <div style="width: 250px">
            <h4>{loc.source}</h4>
            <p><b>Date:</b> {loc.timestamp.strftime('%Y-%m-%d %H:%M')}</p>
            <p><b>Coordinates:</b> {loc.latitude:.6f}, {loc.longitude:.6f}</p>
            <p><b>Context:</b> {loc.context}</p>
        </div>
        """
        folium.Marker(
            [loc.latitude, loc.longitude],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=tooltip,
        ).add_to(marker_cluster)
    
    # Save the map to a temporary file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = os.path.join(tempfile.gettempdir(), f"{plugin_name}_map_{timestamp}.html")
    m.save(html_path)
    
    # Open in browser
    webbrowser.open(f"file://{html_path}")
    logger.info(f"Map visualization created at {html_path}")

def parse_date(date_str: str) -> datetime:
    """Parse date string into datetime object"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        try:
            return datetime.strptime(date_str, "%Y/%m/%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD or YYYY/MM/DD.")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Test CreepyAI social media plugins")
    parser.add_argument("plugin", help=f"Plugin to test. Available: {', '.join(PLUGINS.keys())}")
    parser.add_argument("target", help="Target to search for (username, term, or directory path)")
    parser.add_argument("--config", "-c", help="Path to JSON configuration file")
    parser.add_argument("--data-dir", "-d", help="Path to data directory")
    parser.add_argument("--from-date", help="Start date filter (YYYY-MM-DD)")
    parser.add_argument("--to-date", help="End date filter (YYYY-MM-DD)")
    parser.add_argument("--export", "-e", choices=["csv", "json", "both"], help="Export results to file")
    parser.add_argument("--visualize", "-v", action="store_true", help="Visualize results on a map")
    
    args = parser.parse_args()
    
    # Process dates if provided
    date_from = None
    if args.from_date:
        try:
            date_from = parse_date(args.from_date)
        except ValueError as e:
            logger.error(str(e))
            return 1
    
    date_to = None
    if args.to_date:
        try:
            date_to = parse_date(args.to_date)
        except ValueError as e:
            logger.error(str(e))
            return 1
    
    # Load config from file or create basic config
    config = {}
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            return 1
    
    # Override data directory if provided
    if args.data_dir:
        config["data_directory"] = args.data_dir
    
    # Test plugin
    locations = test_plugin(args.plugin, config, args.target, date_from, date_to)
    
    # Export results if requested
    if args.export:
        if args.export in ["csv", "both"]:
            export_path = export_to_csv(locations, args.plugin)
            logger.info(f"Exported CSV results to {export_path}")
        
        if args.export in ["json", "both"]:
            export_path = export_to_json(locations, args.plugin)
            logger.info(f"Exported JSON results to {export_path}")
    
    # Visualize if requested
    if args.visualize:
        visualize_results(locations, args.plugin)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
