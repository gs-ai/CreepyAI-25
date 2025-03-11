"""
CreepyAI Social Media Plugins
"""
import logging

# Configure plugin-specific logger
logger = logging.getLogger('creepyai.plugins.social_media')

# Import all social media plugins
from app.plugins.social_media.facebook_plugin import FacebookPlugin
from app.plugins.social_media.instagram_plugin import InstagramPlugin
from app.plugins.social_media.linkedin_plugin import LinkedInPlugin
from app.plugins.social_media.pinterest_plugin import PinterestPlugin
from app.plugins.social_media.snapchat_plugin import SnapchatPlugin
from app.plugins.social_media.tiktok_plugin import TikTokPlugin
from app.plugins.social_media.twitter_plugin import TwitterPlugin
from app.plugins.social_media.yelp_plugin import YelpPlugin

# List of all social media plugins to expose to the main application
plugins = [
    FacebookPlugin,
    InstagramPlugin,
    LinkedInPlugin,
    PinterestPlugin,
    SnapchatPlugin,
    TikTokPlugin,
    TwitterPlugin,
    YelpPlugin
]

__all__ = [
    'FacebookPlugin',
    'InstagramPlugin',
    'LinkedInPlugin',
    'PinterestPlugin',
    'SnapchatPlugin',
    'TikTokPlugin', 
    'TwitterPlugin',
    'YelpPlugin',
    'plugins'
]

logger.info(f"Loaded {len(plugins)} social media plugins")
