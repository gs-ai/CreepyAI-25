"""Social media plugin exports and registry."""

from __future__ import annotations

import logging
from typing import Dict, Type

from app.plugins.social_media.base import ArchiveSocialMediaPlugin
from app.plugins.social_media.facebook_plugin import FacebookPlugin
from app.plugins.social_media.instagram_plugin import InstagramPlugin
from app.plugins.social_media.linkedin_plugin import LinkedInPlugin
from app.plugins.social_media.pinterest_plugin import PinterestPlugin
from app.plugins.social_media.snapchat_plugin import SnapchatPlugin
from app.plugins.social_media.tiktok_plugin import TikTokPlugin
from app.plugins.social_media.twitter_plugin import TwitterPlugin
from app.plugins.social_media.yelp_plugin import YelpPlugin

logger = logging.getLogger("creepyai.plugins.social_media")

SOCIAL_MEDIA_PLUGINS: Dict[str, Type[ArchiveSocialMediaPlugin]] = {
    "facebook": FacebookPlugin,
    "instagram": InstagramPlugin,
    "linkedin": LinkedInPlugin,
    "pinterest": PinterestPlugin,
    "snapchat": SnapchatPlugin,
    "tiktok": TikTokPlugin,
    "twitter": TwitterPlugin,
    "yelp": YelpPlugin,
}

plugins = list(SOCIAL_MEDIA_PLUGINS.values())

__all__ = [
    "ArchiveSocialMediaPlugin",
    "FacebookPlugin",
    "InstagramPlugin",
    "LinkedInPlugin",
    "PinterestPlugin",
    "SnapchatPlugin",
    "TikTokPlugin",
    "TwitterPlugin",
    "YelpPlugin",
    "SOCIAL_MEDIA_PLUGINS",
    "plugins",
]

logger.info(
    "Loaded %d social media plugins: %s",
    len(plugins),
    ", ".join(sorted(SOCIAL_MEDIA_PLUGINS)),
)
