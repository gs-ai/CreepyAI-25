"""
Plugin system for the CreepyAI application.
All plugins are API-free and work with local data sources.
"""

from .base_plugin import BasePlugin, LocationPoint
from .twitter_plugin import TwitterPlugin
from .instagram_plugin import InstagramPlugin
from .facebook_plugin import FacebookPlugin
from .local_files_plugin import LocalFilesPlugin
from .google_takeout_plugin import GoogleTakeoutPlugin
from .linkedin_plugin import LinkedInPlugin
from .email_plugin import EmailPlugin
from .flickr_plugin import FlickrPlugin
from .foursquare_plugin import FoursquarePlugin
from .google_maps_plugin import GoogleMapsPlugin
from .tiktok_plugin import TikTokPlugin
from .snapchat_plugin import SnapchatPlugin
from .pinterest_plugin import PinterestPlugin
from .wifi_mapper_plugin import WifiMapperPlugin
from .yelp_plugin import YelpPlugin

# List of all available plugins
available_plugins = [
    TwitterPlugin,
    InstagramPlugin,
    FacebookPlugin,
    LocalFilesPlugin,
    GoogleTakeoutPlugin,
    LinkedInPlugin,
    EmailPlugin,
    FlickrPlugin,
    FoursquarePlugin,
    GoogleMapsPlugin,
    TikTokPlugin,
    SnapchatPlugin,
    PinterestPlugin,
    WifiMapperPlugin,
    YelpPlugin
]

def get_all_plugins():
    """Return instances of all available plugins."""
    return [plugin_class() for plugin_class in available_plugins]

def get_plugin_by_name(name):
    """Get a plugin instance by name."""
    for plugin_class in available_plugins:
        plugin = plugin_class()
        if plugin.name.lower() == name.lower():
            return plugin
    return None
