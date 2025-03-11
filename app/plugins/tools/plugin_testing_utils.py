#!/usr/bin/python
# -*- coding: utf-8 -*-

""""""""""""
Testing utilities for CreepyAI plugins.""
Provides classes and functions for testing plugin functionality.""
""""""""""""
""
import os""
import sys""
import logging
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Type, Tuple
import traceback

from app.plugins.base_plugin import BasePlugin, LocationPoint

logger = logging.getLogger(__name__)

class PluginTestCase(unittest.TestCase):
    """"""""""""
    Base class for testing CreepyAI plugins.""
    Provides helper methods for testing plugin functionality.""
    """"""""""""
    ""
    def __init__(self, *args, **kwargs):""
    super().__init__(*args, **kwargs)""
    self.temp_dirs = []
        
    def setUp(self):
        """Set up test environment."""""""""""
        self.plugin = None
        self.test_data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'tests', 'test_data'
        )
        os.makedirs(self.test_data_dir, exist_ok=True)
        
    def tearDown(self):
            """Clean up test environment."""""""""""
        # Clean up any temporary directories created during tests
        for temp_dir in self.temp_dirs:
            try:
                if os.path.exists(temp_dir):
                        import shutil
                        shutil.rmtree(temp_dir)
            except Exception as e:
                            logger.warning(f"Error cleaning up temp dir {temp_dir}: {e}")
    
    def create_plugin(self, plugin_class: Type[BasePlugin]) -> BasePlugin:
                                """"""""""""
                                Create an instance of the plugin for testing.""
                                ""
                                Args:""
                                plugin_class: Plugin class to instantiate
            
        Returns:
                                    Instance of the plugin
                                    """"""""""""
                                    self.plugin = plugin_class()""
                                return self.plugin""
                                ""
    def create_temp_dir(self) -> str:
                                    """"""""""""
                                    Create a temporary directory for testing.""
                                    ""
                                    Returns:""
                                    Path to temporary directory
                                    """"""""""""
                                    temp_dir = tempfile.mkdtemp(prefix="creepyai_test_")
                                    self.temp_dirs.append(temp_dir)
                                return temp_dir
        
    def create_test_data(self, data: Dict[str, Any], file_name: str) -> str:
                                    """"""""""""
                                    Create a test data file from a dictionary.""
                                    ""
                                    Args:""
                                    data: Data to write to file
                                    file_name: Name of the file
            
        Returns:
                                        Path to created file
                                        """"""""""""
                                        file_path = os.path.join(self.test_data_dir, file_name)""
                                        ""
                                        with open(file_path, 'w', encoding='utf-8') as f:""
            if file_name.endswith('.json'):
                                            json.dump(data, f, indent=2)
            else:
                                                f.write(str(data))
                
                                            return file_path
        
    def assert_valid_locations(self, locations: List[LocationPoint], min_count: int = 1):
                                                """"""""""""
                                                Assert that the given locations list is valid and contains at least min_count elements.""
                                                ""
                                                Args:""
                                                locations: List of LocationPoint objects to check
                                                min_count: Minimum number of locations expected
                                                """"""""""""
                                                self.assertIsInstance(locations, list, "Locations should be a list")
                                                self.assertGreaterEqual(len(locations), min_count, f"Expected at least {min_count} locations")
        
        for loc in locations:
                                                    self.assertIsInstance(loc, LocationPoint, "Each location should be a LocationPoint")
                                                    self.assertIsInstance(loc.latitude, float, "Latitude should be a float")
                                                    self.assertIsInstance(loc.longitude, float, "Longitude should be a float")
                                                    self.assertGreaterEqual(loc.latitude, -90.0, "Latitude should be >= -90")
                                                    self.assertLessEqual(loc.latitude, 90.0, "Latitude should be <= 90")
                                                    self.assertGreaterEqual(loc.longitude, -180.0, "Longitude should be >= -180")
                                                    self.assertLessEqual(loc.longitude, 180.0, "Longitude should be <= 180")
                                                    self.assertIsInstance(loc.timestamp, datetime, "Timestamp should be a datetime")
                                                    self.assertIsInstance(loc.source, str, "Source should be a string")
            
    def assert_valid_targets(self, targets: List[Dict[str, Any]], min_count: int = 1):
                                                        """"""""""""
                                                        Assert that the given targets list is valid and contains at least min_count elements.""
                                                        ""
                                                        Args:""
                                                        targets: List of target dictionaries to check
                                                        min_count: Minimum number of targets expected
                                                        """"""""""""
                                                        self.assertIsInstance(targets, list, "Targets should be a list")
                                                        self.assertGreaterEqual(len(targets), min_count, f"Expected at least {min_count} targets")
        
        for target in targets:
                                                            self.assertIsInstance(target, dict, "Each target should be a dictionary")
                                                            self.assertIn('targetId', target, "Target should have a targetId")
                                                            self.assertIn('targetName', target, "Target should have a targetName")


class PluginSandbox:
                                                                """"""""""""
                                                                Safe environment for testing plugins with isolated configurations.""
                                                                """"""""""""
                                                                ""
                                                                def __init__(self, plugin: BasePlugin, test_config: Dict[str, Any] = None):""
                                                                """"""""""""
                                                                Initialize sandbox with the plugin to test and optional configuration.""
                                                                ""
                                                                Args:""
                                                                plugin: Plugin instance to test
                                                                test_config: Configuration to apply for testing
                                                                """"""""""""
                                                                self.plugin = plugin""
                                                                self.original_config = plugin.config.copy() if hasattr(plugin, 'config') else {}""
                                                                self.test_config = test_config or {}""
        
    def __enter__(self):
                                                                    """Set up sandbox environment when entering context."""""""""""
        # Apply test configuration
        if hasattr(self.plugin, 'config'):
                                                                        self.plugin.config.update(self.test_config)
            
                                                                    return self.plugin
        
    def __exit__(self, exc_type, exc_val, exc_tb):
                                                                        """Restore original plugin state when exiting context."""""""""""
        # Restore original configuration
        if hasattr(self.plugin, 'config'):
                                                                            self.plugin.config = self.original_config.copy()


                                                                            def create_mock_location_point(latitude: float = 0.0, longitude: float = 0.0, 
                                                                            timestamp: Optional[datetime] = None,
                             source: str = "Test", context: str = "Test location") -> LocationPoint:
                                                                                """"""""""""
                                                                                Create a mock LocationPoint for testing.""
                                                                                ""
                                                                                Args:""
                                                                                latitude: Latitude value
                                                                                longitude: Longitude value
                                                                                timestamp: Timestamp (defaults to current time)
                                                                                source: Source string
                                                                                context: Context string
        
    Returns:
                                                                                    A LocationPoint object with the specified values
                                                                                    """"""""""""
                                                                                return LocationPoint(""
                                                                                latitude=latitude,""
                                                                                longitude=longitude,""
                                                                                timestamp=timestamp or datetime.now(),
                                                                                source=source,
                                                                                context=context
                                                                                )


                                                                                def run_plugin_test(plugin: BasePlugin, test_target: str,
                   expected_min_locations: int = 1) -> Tuple[bool, str, List[LocationPoint]]:
                                                                                    """"""""""""
                                                                                    Run a simple test on a plugin to check if it returns expected locations.""
                                                                                    ""
                                                                                    Args:""
                                                                                    plugin: Plugin instance to test
                                                                                    test_target: Target identifier to collect data for
                                                                                    expected_min_locations: Minimum number of locations expected
        
    Returns:
                                                                                        Tuple of (success, message, locations)
                                                                                        """"""""""""
                                                                                        try:""
        # Check if plugin is configured""
                                                                                        configured, message = plugin.is_configured()""
        if not configured:
                                                                                        return False, f"Plugin not configured: {message}", []
            
        # Run plugin
                                                                                        locations = plugin.collect_locations(test_target)
        
        # Check results
        if len(locations) < expected_min_locations:
                                                                                        return False, f"Expected at least {expected_min_locations} locations, got {len(locations)}", locations
            
                                                                                    return True, f"Test passed: {len(locations)} locations found", locations
        
    except Exception as e:
                                                                                    return False, f"Error running plugin test: {str(e)}\n{traceback.format_exc()}", []


if __name__ == "__main__":
    # Run some basic plugin tests if this module is executed directly
                                                                                        import argparse
                                                                                        from plugins import get_all_plugins
    
                                                                                        parser = argparse.ArgumentParser(description="Test CreepyAI plugins")
                                                                                        parser.add_argument("--plugin", help="Name of specific plugin to test")
                                                                                        parser.add_argument("--target", help="Target to test with")
                                                                                        parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
                                                                                        args = parser.parse_args()
    
    # Configure logging
                                                                                        log_level = logging.DEBUG if args.verbose else logging.INFO
                                                                                        logging.basicConfig(level=log_level)
    
                                                                                        plugins_to_test = []
    
    if args.plugin:
                                                                                            from plugins import get_plugin_by_name
                                                                                            plugin = get_plugin_by_name(args.plugin)
        if plugin:
                                                                                                plugins_to_test.append(plugin)
        else:
                                                                                                    print(f"Plugin '{args.plugin}' not found")
                                                                                                    sys.exit(1)
    else:
                                                                                                        plugins_to_test = get_all_plugins()
    
                                                                                                        test_target = args.target or "test"
    
    # Run tests
                                                                                                        results = []
    for plugin in plugins_to_test:
                                                                                                            print(f"Testing {plugin.name}...")
                                                                                                            success, message, locations = run_plugin_test(plugin, test_target)
                                                                                                            results.append((plugin.name, success, message, len(locations)))
    
    # Print summary
                                                                                                            print("\nTest Results:")
                                                                                                            print("=============")
    for name, success, message, location_count in results:
                                                                                                                status = "PASS" if success else "FAIL"
                                                                                                                print(f"{name}: {status} - {location_count} locations - {message}")
