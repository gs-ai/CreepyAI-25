"""
Top-level utilities compatibility shim.

Some parts of the application and plugins import modules using
"from utilities import ...". The canonical modules live under
"app.utilities". This shim re-exports the commonly used symbols so those
imports continue to work without modifying every call site.
"""
from __future__ import annotations

# Re-export module attributes from app.utilities
try:
    from app.utilities.PluginManager import PluginManager  # type: ignore
except Exception:  # pragma: no cover - defensive
    PluginManager = None  # type: ignore

try:
    from app.utilities.WebScrapingUtility import WebScrapingUtility  # type: ignore
except Exception:  # pragma: no cover - defensive
    WebScrapingUtility = None  # type: ignore

try:
    from app.utilities.webengine_compat import setup_webengine_options  # type: ignore
except Exception:  # pragma: no cover - defensive
    def setup_webengine_options():  # type: ignore
        return None

# Optional helpers
try:
    from app.utilities import webengine as _webengine  # type: ignore
except Exception:  # pragma: no cover - defensive
    _webengine = None  # type: ignore

__all__ = [
    "PluginManager",
    "WebScrapingUtility",
    "setup_webengine_options",
]
