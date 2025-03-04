"""
CreepyAI Plugins
---------------
This package contains input plugins for CreepyAI.

Available plugins:
- mock_social: Generate realistic social media data for demonstrations
- location_history: Extract and analyze location history data
- email_analysis: Extract location and contact data from email headers
- wifi_mapper: Map wireless networks from exports and war-driving data
- facebook: Extract location data from Facebook photos, check-ins and tagged places

To create your own plugin:
1. Create a new directory in the plugins folder
2. Create a Python file with a class extending InputPlugin
3. Implement the required methods
"""

__all__ = ['mock_social', 'location_history', 'email_analysis', 'wifi_mapper', 'facebook']
