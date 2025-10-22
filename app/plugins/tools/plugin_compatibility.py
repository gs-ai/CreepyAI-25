"""Compatibility wrapper for legacy tooling imports.

This module re-exports everything from :mod:`app.plugins.plugin_compatibility`
so that any code importing from :mod:`app.plugins.tools` continues to function
without maintaining duplicate implementations.
"""

from __future__ import annotations

from app.plugins.tools._compat import alias_module

_run_main = alias_module(__name__)

from app.plugins.plugin_compatibility import *  # noqa: F401,F403

if "__all__" not in globals():
    __all__ = [name for name in globals() if not name.startswith("_")]

if __name__ == "__main__":  # pragma: no cover - manual execution helper
    _run_main()
