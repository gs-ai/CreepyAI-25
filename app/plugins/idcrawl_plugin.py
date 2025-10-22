"""Compatibility shim for the canonical Idcrawl plugin implementation."""

from app.plugins.tools._compat import alias_module

alias_module(__name__, base_package="app.plugins.data_extraction")
