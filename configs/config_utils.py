    """
Configuration utilities for CreepyAI.
"""
import os
import json
import logging
from typing import Any, Dict, Optional, List, Union

logger = logging.getLogger(__name__)


def read_json_config(filepath: str) -> Dict[str, Any]:
    """
    Read configuration from JSON file
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Dictionary with configuration
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {filepath}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in configuration file: {filepath}")
        return {}
    except Exception as e:
        logger.error(f"Error reading configuration file {filepath}: {str(e)}")
        return {}


def write_json_config(filepath: str, config: Dict[str, Any]) -> bool:
    """
    Write configuration to JSON file
    
    Args:
        filepath: Path to JSON file
        config: Configuration dictionary
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error writing configuration to {filepath}: {str(e)}")
        return False


def read_yaml_config(filepath: str) -> Dict[str, Any]:
    """
    Read configuration from YAML file
    
    Args:
        filepath: Path to YAML file
        
    Returns:
        Dictionary with configuration
    """
    try:
        import yaml
        
        with open(filepath, 'r') as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        logger.error("PyYAML not installed. Install it with: pip install PyYAML")
        return {}
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {filepath}")
        return {}
    except yaml.YAMLError:
        logger.error(f"Invalid YAML in configuration file: {filepath}")
        return {}
    except Exception as e:
        logger.error(f"Error reading configuration file {filepath}: {str(e)}")
        return {}


def write_yaml_config(filepath: str, config: Dict[str, Any]) -> bool:
    """
    Write configuration to YAML file
    
    Args:
        filepath: Path to YAML file
        config: Configuration dictionary
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import yaml
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        with open(filepath, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except ImportError:
        logger.error("PyYAML not installed. Install it with: pip install PyYAML")
        return False
    except Exception as e:
        logger.error(f"Error writing configuration to {filepath}: {str(e)}")
        return False


def get_config_value(config: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Get value from nested configuration dictionary using dot notation
    
    Args:
        config: Configuration dictionary
        path: Path to value using dot notation (e.g. "database.host")
        default: Default value if path not found
        
    Returns:
        Configuration value or default
    """
    if not path:
        return config
        
    parts = path.split('.')
    current = config
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
            
    return current


def set_config_value(config: Dict[str, Any], path: str, value: Any) -> Dict[str, Any]:
    """
    Set value in nested configuration dictionary using dot notation
    
    Args:
        config: Configuration dictionary
        path: Path to value using dot notation (e.g. "database.host")
        value: Value to set
        
    Returns:
        Modified configuration dictionary
    """
    if not path:
        return config
        
    parts = path.split('.')
    current = config
    
    # Navigate to the deepest dict that should contain the value
    for i, part in enumerate(parts[:-1]):
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]
            
    # Set the actual value
    current[parts[-1]] = value
    
    return config


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries
    
    Args:
        base: Base configuration
        override: Override configuration (takes precedence)
        
    Returns:
        Merged configuration dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        # If both values are dicts, merge recursively
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
            
    return result


def expand_env_vars(config: Any) -> Any:
    """
    Recursively expand environment variables in configuration values
    
    Args:
        config: Configuration object (dict, list, or scalar)
        
    Returns:
        Configuration with environment variables expanded
    """
    import re
    
    env_var_pattern = re.compile(r'\$\{([A-Za-z0-9_]+)(?::([^}]*))?\}')
    
    def _replace_env_var(match):
        var_name = match.group(1)
        default_value = match.group(2)
        
        return os.environ.get(var_name, default_value if default_value is not None else '')
    
    if isinstance(config, dict):
        return {k: expand_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [expand_env_vars(v) for v in config]
    elif isinstance(config, str):
        return env_var_pattern.sub(_replace_env_var, config)
    else:
        return config


def validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """
    Validate configuration against a schema
    
    Args:
        config: Configuration dictionary
        schema: Schema dictionary defining required fields and types
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    for key, spec in schema.items():
        path = key
        required = spec.get('required', False)
        expected_type = spec.get('type')
        allowed_values = spec.get('allowed_values')
        
        # Check if required field exists
        value = get_config_value(config, path)
        if required and value is None:
            errors.append(f"Required field '{path}' is missing")
            continue
            
        if value is not None:
            # Check type
            if expected_type:
                if expected_type == 'str' and not isinstance(value, str):
                    errors.append(f"Field '{path}' should be a string")
                elif expected_type == 'int' and not isinstance(value, int):
                    errors.append(f"Field '{path}' should be an integer")
                elif expected_type == 'float' and not isinstance(value, (int, float)):
                    errors.append(f"Field '{path}' should be a number")
                elif expected_type == 'bool' and not isinstance(value, bool):
                    errors.append(f"Field '{path}' should be a boolean")
                elif expected_type == 'list' and not isinstance(value, list):
                    errors.append(f"Field '{path}' should be a list")
                elif expected_type == 'dict' and not isinstance(value, dict):
                    errors.append(f"Field '{path}' should be a dictionary")
            
            # Check allowed values
            if allowed_values and value not in allowed_values:
                errors.append(f"Field '{path}' should be one of {allowed_values}")
                
            # Check nested fields
            nested_schema = spec.get('schema')
            if nested_schema and isinstance(value, dict):
                for nested_key, nested_spec in nested_schema.items():
                    nested_path = f"{path}.{nested_key}"
                    nested_schema_entry = {nested_path: nested_spec}
                    nested_errors = validate_config(config, nested_schema_entry)
                    errors.extend(nested_errors)
    
    return errors
