#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Plugin Creator for CreepyAI
Generates new plugin templates based on specified options
"""

import os
import sys
import argparse
import logging
import shutil
import re
from datetime import datetime
from string import Template

# Add parent directory to path so we can import plugins
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(SCRIPT_DIR)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("plugin_creator")

# Define plugin template types
PLUGIN_TEMPLATES = {
    "basic": {
        "description": "Basic plugin template with minimal implementation",
        "files": ["plugin.py", "config.conf"]
    },
    "social": {
        "description": "Plugin template for social media data sources",
        "files": ["plugin.py", "config.conf"]
    },
    "file": {
        "description": "Plugin template for processing local files",
        "files": ["plugin.py", "config.conf"]
    },
    "network": {
        "description": "Plugin template for network scanning tools",
        "files": ["plugin.py", "config.conf"]
    }
}

class PluginCreator:
    """
    Creates new CreepyAI plugin templates
    """
    
    def __init__(self, plugins_dir: str = None):
        """
        Initialize the plugin creator
        
        Args:
            plugins_dir: Directory where plugins are stored
        """
        self.plugins_dir = plugins_dir or os.path.join(parent_dir, "plugins")
        self.templates_dir = os.path.join(SCRIPT_DIR, "templates")
        
        # Create templates directory if it doesn't exist
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
            # Copy default templates from the project
            self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default plugin templates if they don't exist"""
        # Create basic plugin template
        basic_template = """#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
$docstring
"""

from plugins.base_plugin import BasePlugin, LocationPoint
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class $classname(BasePlugin):
    """$description"""
    
    def __init__(self):
        super().__init__(
            name="$name",
            description="$description"
        )
        self.version = "$version"
        self.author = "$author"
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        """Return configuration options for this plugin"""
        return [
            {
                "name": "option1",
                "display_name": "Option 1",
                "type": "string",
                "default": "",
                "required": True,
                "description": "Description of option 1"
            },
            {
                "name": "option2",
                "display_name": "Option 2",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Description of option 2"
            }
        ]
    
    def is_configured(self) -> Tuple[bool, str]:
        """Check if the plugin is properly configured"""
        if not self.config.get("option1"):
            return False, "Option 1 must be configured"
        return True, "Plugin is configured"
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None,
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
        """
        Collect location data for the given target
        
        Args:
            target: Target to collect data for
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            List of LocationPoint objects
        """
        locations = []
        
        # TODO: Add implementation to collect location data
        
        # Example of creating a location point
        # locations.append(
        #     LocationPoint(
        #         latitude=40.7128,
        #         longitude=-74.0060,
        #         timestamp=datetime.now(),
        #         source="$plugin_id",
        #         context="Example location"
        #     )
        # )
        
        # Apply date filtering
        if date_from or date_to:
            locations = [
                loc for loc in locations 
                if (not date_from or loc.timestamp >= date_from) and
                   (not date_to or loc.timestamp <= date_to)
            ]
        
        return locations
"""
        
        # Create config template
        config_template = """[string_options]
option1 = 

[boolean_options]
option2 = True

[integer_options]
timeout = 30
retry_attempts = 3

[array_options]
excluded_items = ["item1", "item2"]
"""
        
        # Write basic template
        with open(os.path.join(self.templates_dir, "basic_plugin.py"), "w") as f:
            f.write(basic_template)
            
        with open(os.path.join(self.templates_dir, "basic_config.conf"), "w") as f:
            f.write(config_template)
            
        # Create templates for other types based on the basic template
        # Social media template
        social_template = basic_template.replace(
            "# TODO: Add implementation to collect location data",
            """# Implement social media data collection
        try:
            # 1. Authenticate with the social media API
            # 2. Fetch location data for the target
            # 3. Convert to LocationPoint objects
            pass
        except Exception as e:
            logger.error(f"Error collecting locations: {e}")"""
        )
        
        with open(os.path.join(self.templates_dir, "social_plugin.py"), "w") as f:
            f.write(social_template)
            
        # File processing template
        file_template = basic_template.replace(
            "# TODO: Add implementation to collect location data",
            """# Implement file processing logic
        try:
            # 1. Validate target is a file or directory
            if not os.path.exists(target):
                logger.error(f"Target does not exist: {target}")
                return locations
                
            # 2. Process files to extract location data
            # 3. Convert to LocationPoint objects
            pass
        except Exception as e:
            logger.error(f"Error processing files: {e}")"""
        )
        
        with open(os.path.join(self.templates_dir, "file_plugin.py"), "w") as f:
            f.write(file_template)
            
        # Network tool template
        network_template = basic_template.replace(
            "# TODO: Add implementation to collect location data",
            """# Implement network scanning logic
        try:
            # 1. Validate target is a valid network target
            # 2. Scan network or devices
            # 3. Extract location data
            # 4. Convert to LocationPoint objects
            pass
        except Exception as e:
            logger.error(f"Error scanning network: {e}")"""
        )
        
        with open(os.path.join(self.templates_dir, "network_plugin.py"), "w") as f:
            f.write(network_template)
            
    def get_template_path(self, template_type: str, file_type: str) -> str:
        """
        Get the path to a template file
        
        Args:
            template_type: Type of template (basic, social, etc.)
            file_type: Type of file (plugin, config)
            
        Returns:
            Path to template file
        """
        if template_type not in PLUGIN_TEMPLATES:
            template_type = "basic"
            
        if file_type == "plugin":
            return os.path.join(self.templates_dir, f"{template_type}_plugin.py")
        elif file_type == "config":
            return os.path.join(self.templates_dir, f"{template_type}_config.conf")
        else:
            return None
    
    def create_plugin(self, plugin_id: str, name: str, description: str, 
                    template_type: str = "basic", author: str = "") -> bool:
        """
        Create a new plugin
        
        Args:
            plugin_id: ID for the new plugin
            name: Display name for the new plugin
            description: Description of what the plugin does
            template_type: Type of template to use
            author: Author of the plugin
            
        Returns:
            True if creation was successful, False otherwise
        """
        # Validate plugin_id format (lowercase, no spaces, alphanumeric with underscores)
        if not re.match(r'^[a-z0-9_]+$', plugin_id):
            logger.error(f"Invalid plugin ID: '{plugin_id}'. Use lowercase letters, numbers, and underscores only.")
            return False
            
        # Add 'Plugin' suffix if not present
        if not plugin_id.endswith("Plugin") and not plugin_id.endswith("_plugin"):
            plugin_id = f"{plugin_id}_plugin"
            
        # Check if plugin already exists
        plugin_file = os.path.join(self.plugins_dir, f"{plugin_id}.py")
        if os.path.exists(plugin_file):
            logger.error(f"Plugin already exists: {plugin_file}")
            return False
            
        # Validate template type
        if template_type not in PLUGIN_TEMPLATES:
            logger.warning(f"Unknown template type: {template_type}. Using 'basic' template.")
            template_type = "basic"
            
        try:
            # Get class name from plugin ID
            class_name = ''.join(x.capitalize() or '_' for x in plugin_id.split('_'))
            if not class_name.endswith('Plugin'):
                class_name += 'Plugin'
                
            # Load template
            template_path = self.get_template_path(template_type, "plugin")
            with open(template_path, 'r') as f:
                template_content = f.read()
                
            # Create template substitution
            template = Template(template_content)
            plugin_content = template.substitute(
                classname=class_name,
                plugin_id=plugin_id,
                name=name,
                description=description,
                version="1.0.0",
                author=author,
                docstring=f"CreepyAI {name} Plugin\n{description}"
            )
            
            # Write plugin file
            with open(plugin_file, 'w') as f:
                f.write(plugin_content)
            
            # Create config file
            config_template_path = self.get_template_path(template_type, "config")
            config_file = os.path.join(self.plugins_dir, f"{plugin_id}.conf")
            
            if os.path.exists(config_template_path):
                shutil.copy(config_template_path, config_file)
                
            logger.info(f"Created new plugin: {plugin_id}")
            logger.info(f"Plugin file: {plugin_file}")
            logger.info(f"Config file: {config_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating plugin: {e}")
            return False
            
def main():
    """Main function for running the creator from command line"""
    parser = argparse.ArgumentParser(description="Create new CreepyAI plugin")
    parser.add_argument("plugin_id", help="ID for the new plugin (lowercase, no spaces, alphanumeric with underscores)")
    parser.add_argument("--name", help="Display name for the plugin")
    parser.add_argument("--description", help="Description of what the plugin does")
    parser.add_argument("--template", choices=PLUGIN_TEMPLATES.keys(), default="basic",
                       help="Template type to use")
    parser.add_argument("--author", default="", help="Author of the plugin")
    parser.add_argument("--dir", help="Plugins directory")
    args = parser.parse_args()
    
    # If name not provided, generate from plugin ID
    if not args.name:
        args.name = ' '.join(word.capitalize() for word in args.plugin_id.split('_'))
        if args.name.lower().endswith("plugin"):
            args.name = args.name[:-6]  # Remove "plugin" suffix
    
    # If description not provided, use a generic one
    if not args.description:
        args.description = f"Collects location data from {args.name} sources"
        
    creator = PluginCreator(args.dir)
    success = creator.create_plugin(
        plugin_id=args.plugin_id,
        name=args.name,
        description=args.description,
        template_type=args.template,
        author=args.author
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":