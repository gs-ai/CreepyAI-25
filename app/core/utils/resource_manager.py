"""
Resource manager for accessing application resources.
"""
import os
import logging
import jinja2
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ResourceManager:
    """
    Manages access to application resources like templates, assets, etc.
    """
    
    def __init__(self, resources_dir: Optional[str] = None):
        """
        Initialize the resource manager
        
        Args:
            resources_dir: Path to resources directory. If None, uses default location.
        """
        if resources_dir is None:
            # Default to resources directory in the project root
            project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            resources_dir = os.path.join(project_dir, "resources")
        
        self.resources_dir = resources_dir
        self.template_env = self._initialize_template_env()
    
    def _initialize_template_env(self) -> jinja2.Environment:
        """Initialize the Jinja2 template environment"""
        template_dir = os.path.join(self.resources_dir, "templates")
        
        try:
            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(template_dir),
                trim_blocks=True,
                lstrip_blocks=True
            )
            return env
        except Exception as e:
            logger.warning(f"Failed to initialize template environment: {str(e)}")
            # Return a simple environment with no template directory
            return jinja2.Environment()
    
    def get_resource_path(self, relative_path: str) -> str:
        """
        Get the absolute path to a resource file
        
        Args:
            relative_path: Path relative to the resources directory
            
        Returns:
            Absolute path to the resource file
        """
        absolute_path = os.path.join(self.resources_dir, relative_path)
        
        # Check if the file exists
        if not os.path.exists(absolute_path):
            logger.warning(f"Resource not found: {relative_path}")
        
        return absolute_path
    
    def render_template(self, template_path: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context
        
        Args:
            template_path: Path to the template file, relative to the templates directory
            context: Dictionary of variables to use in the template
            
        Returns:
            Rendered template as a string
        """
        try:
            template = self.template_env.get_template(template_path)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_path}: {str(e)}")
            raise
    
    def create_from_template(self, template_path: str, output_path: str, context: Dict[str, Any]) -> bool:
        """
        Create a file from a template
        
        Args:
            template_path: Path to the template file, relative to the templates directory
            output_path: Path where the rendered template should be saved
            context: Dictionary of variables to use in the template
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create the directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Render the template
            rendered = self.render_template(template_path, context)
            
            # Write the output file
            with open(output_path, 'w') as f:
                f.write(rendered)
            
            logger.info(f"Created file from template: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating file from template: {str(e)}")
            return False
