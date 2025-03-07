#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Unit tests for the Facebook plugin.
"""

import os
import sys
import unittest
import json
import tempfile
from datetime import datetime
import shutil

# Add parent directory to path to import plugins
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from plugins.plugin_testing_utils import PluginTestCase, create_mock_location_point
from plugins.facebook_plugin import FacebookPlugin

class TestFacebookPlugin(PluginTestCase):
    def setUp(self):
        super().setUp()
        self.plugin = FacebookPlugin()
        
        # Create a temporary test directory
        self.test_dir = self.create_temp_dir()
        
        # Set up a test configuration
        self.plugin.configure({
            "data_directory": self.test_dir
        })
        
    def test_initialization(self):
        """Test that the plugin initializes correctly."""
        self.assertEqual(self.plugin.name, "Facebook")
        self.assertIsNotNone(self.plugin.geocoder)
        
    def test_get_configuration_options(self):
        """Test that configuration options are returned."""
        options = self.plugin.get_configuration_options()
        self.assertIsInstance(options, list)
        self.assertGreater(len(options), 0)
        
        # Check that at least one option has required properties
        option = options[0]
        self.assertIn('name', option)
        self.assertIn('display_name', option)
        self.assertIn('type', option)
        
    def test_is_configured(self):
        """Test configuration validation."""
        # Should be configured since we set data_directory in setUp
        is_configured, message = self.plugin.is_configured()
        self.assertTrue(is_configured)
        
        # Test with invalid configuration
        self.plugin.config['data_directory'] = '/path/that/does/not/exist'
        is_configured, message = self.plugin.is_configured()
        self.assertFalse(is_configured)
        
    def test_empty_directory(self):
        """Test that an empty directory returns no locations."""
        locations = self.plugin.collect_locations('test_target')
        self.assertEqual(len(locations), 0)
        
    def test_location_history_processing(self):
        """Test processing of location history file."""
        # Create test location history file
        location_dir = os.path.join(self.test_dir, 'location_history')
        os.makedirs(location_dir, exist_ok=True)
        
        location_data = [
            {
                "timestamp": int(datetime.now().timestamp()),
                "latitude": 40.7128,
                "longitude": -74.0060,
                "name": "New York City"
            },
            {
                "timestamp": int(datetime.now().timestamp()),
                "latitude": 34.0522,
                "longitude": -118.2437,
                "name": "Los Angeles"
            }
        ]
        
        # Write test data to file
        with open(os.path.join(location_dir, 'location_history.json'), 'w') as f:
            json.dump(location_data, f)
        
        # Test location collection
        locations = self.plugin.collect_locations('test_target')
        self.assertEqual(len(locations), 2)
        
        # Verify the first location
        self.assertEqual(locations[0].latitude, 40.7128)
        self.assertEqual(locations[0].longitude, -74.0060)
        self.assertEqual(locations[0].source, "Facebook Location")
        
    def test_post_location_processing(self):
        """Test extraction of locations from posts."""
        # Create test posts file
        posts_dir = os.path.join(self.test_dir, 'posts')
        os.makedirs(posts_dir, exist_ok=True)
        
        post_data = {
            "posts": [
                {
                    "post": "Enjoying my vacation!",
                    "timestamp": int(datetime.now().timestamp()),
                    "place": {
                        "name": "Eiffel Tower",
                        "location": {
                            "latitude": 48.8584,
                            "longitude": 2.2945
                        }
                    }
                },
                {
                    "post": "Business trip",
                    "timestamp": int(datetime.now().timestamp()),
                    "place": {
                        "name": "Tokyo Tower",
                        "location": {
                            "latitude": 35.6586,
                            "longitude": 139.7454
                        }
                    }
                }
            ]
        }
        
        # Write test data to file
        with open(os.path.join(posts_dir, 'your_posts.json'), 'w') as f:
            json.dump(post_data, f)
            
        # Test location collection
        locations = self.plugin.collect_locations('test_target')
        self.assertEqual(len(locations), 2)
        
        # Verify the content
        self.assertAlmostEqual(locations[0].latitude, 48.8584)
        self.assertAlmostEqual(locations[0].longitude, 2.2945)
        self.assertEqual(locations[0].source, "Facebook Post")
        
    def test_zip_archive_handling(self):
        """Test handling of zipped Facebook exports."""
        import zipfile
        
        # Create a ZIP file with test data
        zip_path = os.path.join(self.test_dir, 'facebook_data.zip')
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            # Add location history
            location_data = [
                {
                    "timestamp": int(datetime.now().timestamp()),
                    "latitude": 51.5074,
                    "longitude": -0.1278,
                    "name": "London"
                }
            ]
            
            zip_file.writestr('location/location_history.json', json.dumps(location_data))
        
        # Configure plugin to use the ZIP file
        self.plugin.configure({
            "data_directory": zip_path
        })
        
        # Test location collection from ZIP file
        locations = self.plugin.collect_locations('test_target')
        self.assertEqual(len(locations), 1)
        self.assertAlmostEqual(locations[0].latitude, 51.5074)
        self.assertAlmostEqual(locations[0].longitude, -0.1278)
        
    def test_date_filtering(self):
        """Test date filtering functionality."""
        # Create test location file with dates
        location_dir = os.path.join(self.test_dir, 'location_history')
        os.makedirs(location_dir, exist_ok=True)
        
        now = datetime.now()
        past_timestamp = int(datetime(now.year-1, now.month, now.day).timestamp())
        future_timestamp = int(datetime(now.year+1, now.month, now.day).timestamp())
        
        location_data = [
            {
                "timestamp": past_timestamp,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "name": "New York City"
            },
            {
                "timestamp": future_timestamp,
                "latitude": 34.0522,
                "longitude": -118.2437,
                "name": "Los Angeles"
            }
        ]
        
        # Write test data to file
        with open(os.path.join(location_dir, 'location_history.json'), 'w') as f:
            json.dump(location_data, f)
        
        # Test with date_from filter
        date_from = datetime(now.year, now.month, now.day)
        locations = self.plugin.collect_locations('test_target', date_from=date_from)
        self.assertEqual(len(locations), 1)  # Should only get the future location
        self.assertAlmostEqual(locations[0].latitude, 34.0522)
        
        # Test with date_to filter
        date_to = datetime(now.year, now.month, now.day)
        locations = self.plugin.collect_locations('test_target', date_to=date_to)
        self.assertEqual(len(locations), 1)  # Should only get the past location
        self.assertAlmostEqual(locations[0].latitude, 40.7128)
        
        # Test with both filters
        locations = self.plugin.collect_locations('test_target', date_from=date_from, date_to=date_to)
        self.assertEqual(len(locations), 0)  # Should get no locations
        
    def tearDown(self):
        super().tearDown()
        # Any additional teardown steps can go here
        
if __name__ == '__main__':
    unittest.main()
