"""Compatibility shim for the canonical Google Maps plugin implementation."""

from app.plugins.tools._compat import alias_module

alias_module(__name__, base_package="app.plugins.location_services")
