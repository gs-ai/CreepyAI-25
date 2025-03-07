#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Basic tests for CreepyAI.
"""

import os
import sys
import unittest

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestCreepyAI(unittest.TestCase):
    """Basic tests for CreepyAI."""
    
    def test_import_modules(self):
        """Test that we can import the main modules."""
        try:
            import qt_setup
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import qt_setup module")
    
    def test_qt_environment(self):
        """Test that PyQt5 is installed correctly."""
        try:
            import PyQt5
            from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import PyQt5")


if __name__ == '__main__':
    unittest.main()
