"""Compatibility wrapper for legacy tooling imports.

This module re-exports everything from ``app.plugins.plugin_test`` so that
any code importing from ``app.plugins.tools`` continues to function
without maintaining duplicate implementations.
"""
from app.plugins.plugin_test import *  # noqa: F401,F403
import runpy as _runpy

if '__all__' not in globals():
    __all__ = [name for name in globals() if not name.startswith('_')]

if __name__ == '__main__':
    _runpy.run_module('app.plugins.plugin_test', run_name='__main__')
