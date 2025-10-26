"""
Top-level utilities compatibility shim.

Some parts of the application and plugins import modules using
"from utilities import ..." or "from utilities.X import Y". The canonical
modules live under "app.utilities". This shim re-exports the commonly used
symbols and also registers module aliases in sys.modules so submodule imports
continue to work without modifying every call site.
"""
from __future__ import annotations

import importlib
import sys

def _alias_module(alias: str, target: str) -> None:
    """Map an import alias to a target module path in sys.modules."""
    try:
        mod = importlib.import_module(target)
        sys.modules.setdefault(alias, mod)
    except Exception:
        # Best-effort: leave alias unresolved if target missing
        pass

# Register submodule aliases first so "from utilities.WebScrapingUtility ..."
# works even if only the package is imported initially.
_alias_module("utilities.WebScrapingUtility", "app.utilities.WebScrapingUtility")
_alias_module("utilities.PluginManager", "app.utilities.PluginManager")
_alias_module("utilities.webengine_compat", "app.utilities.webengine_compat")
_alias_module("utilities.webengine", "app.utilities.webengine")

# Re-export selected names for star-imports or direct attribute access
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

__all__ = ["PluginManager", "WebScrapingUtility", "setup_webengine_options"]
