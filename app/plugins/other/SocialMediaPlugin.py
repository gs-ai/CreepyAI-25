"""Utility base class used by a handful of legacy social media plugins."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from app.plugins.base_plugin import BasePlugin


@dataclass
class SocialMediaPost:
    platform: str
    identifier: str
    created_at: datetime
    text: str
    url: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "platform": self.platform,
            "identifier": self.identifier,
            "created_at": self.created_at.isoformat(),
            "text": self.text,
            "url": self.url,
        }


class SocialMediaPlugin(BasePlugin):
    """Common behaviour shared by social media scraping plugins."""

    def __init__(self, name: str, description: str) -> None:
        super().__init__(name=name, description=description)
        self.version = "1.0.0"
        self.author = "CreepyAI Team"

    def get_info(self) -> Dict[str, str]:
        info = super().get_info()
        info.update({"version": self.version, "author": self.author})
        return info


class Plugin(SocialMediaPlugin):
    def __init__(self) -> None:
        super().__init__(
            name="Social Media Plugin",
            description="Base implementation used for compatibility",
        )


__all__ = ["SocialMediaPlugin", "SocialMediaPost", "Plugin"]
