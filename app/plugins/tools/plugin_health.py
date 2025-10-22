"""Compatibility wrapper for legacy tooling imports.

This module re-exports everything from ``app.plugins.plugin_health`` so that
any code importing from ``app.plugins.tools`` continues to function
without maintaining duplicate implementations.
"""
from app.plugins.tools._compat import alias_module

_run_main = alias_module(__name__)

if __name__ == "__main__":
    _run_main()
