#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example plugin for CreepyAI.

This is a template for creating new plugins.
"""

import logging
from yapsy.IPlugin import IPlugin

class ExamplePlugin(IPlugin):
    """Example plugin implementation."""
    
    def __init__(self):
        """Initialize the plugin."""
        super(ExamplePlugin, self).__init__()
        self.name = "Example Plugin"
        self.description = "This is an example plugin for CreepyAI"
        self.version = "1.0"
        self.logger = logging.getLogger('CreepyAI.Plugins.Example')
        
    def activate(self):
        """
        Activate the plugin.
        
        Called when the plugin is activated by the plugin manager.
        """
        self.logger.info("Example plugin activated")
        super(ExamplePlugin, self).activate()
        return True
        
    def deactivate(self):
        """
        Deactivate the plugin.
        
        Called when the plugin is deactivated by the plugin manager.
        """
        self.logger.info("Example plugin deactivated")
        super(ExamplePlugin, self).deactivate()
        
    def get_capabilities(self):
        """
        Return the plugin's capabilities.
        
        Returns:
            dict: Capabilities of this plugin
        """
        return {
            "type": "example",
            "provides": ["example_data"],
            "requires": []
        }
        
    def execute(self, input_data=None):
        """
        Execute the plugin's main functionality.
        
        Args:
            input_data: Input data for the plugin (if any)
            
        Returns:
            dict: Results of the plugin execution
        """
        self.logger.info("Example plugin executing")
        
        # Plugin logic would go here
        result = {
            "status": "success",
            "data": {
                "message": "Hello from Example Plugin!",
                "timestamp": "2025-03-06T12:00:00Z",
            }
        }
        
        return result
