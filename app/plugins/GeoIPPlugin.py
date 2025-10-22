"""Backward compatible import for the offline GeoIP plugin."""

from app.plugins.location_services.GeoIPPlugin import GeoIPPlugin

__all__ = ["GeoIPPlugin"]
