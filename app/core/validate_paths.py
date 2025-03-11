"""
Path validation utility for CreepyAI.
Checks that all necessary directories exist and are properly configured.
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Use absolute imports for better reliability
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from app.core.path_utils import (
    get_app_root, normalize_path, STANDARD_DIRS, DIR_STRUCTURE, ensure_app_dirs
)

def validate_config_paths(config_file: str) -> Dict[str, List[str]]:
    """Validate paths in configuration file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Dictionary with invalid and missing paths
    """
    app_root = get_app_root()
    invalid_paths = []
    missing_paths = []
    
    try:
        if not os.path.exists(config_file):
            missing_paths.append(config_file)
            return {'invalid': invalid_paths, 'missing': missing_paths}
            
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        # Check paths section
        if 'paths' in config:
            for key, path in config['paths'].items():
                if not isinstance(path, str):
                    continue
                    
                # Check if path is absolute or relative
                if os.path.isabs(path):
                    full_path = path
                else:
                    full_path = os.path.join(app_root, path)
                    
                # Validate path
                if not os.path.exists(full_path):
                    missing_paths.append(full_path)
                elif not os.access(full_path, os.R_OK):
                    invalid_paths.append(full_path)
        
        # Check plugin paths
        if 'plugins' in config:
            plugin_config = config['plugins']
            
            # Check plugin directory
            if 'directory' in plugin_config:
                plugin_dir = plugin_config['directory']
                if os.path.isabs(plugin_dir):
                    full_path = plugin_dir
                else:
                    full_path = os.path.join(app_root, plugin_dir)
                    
                if not os.path.exists(full_path):
                    missing_paths.append(full_path)
                elif not os.access(full_path, os.R_OK):
                    invalid_paths.append(full_path)
            
            # Check plugin config directory
            if 'config_directory' in plugin_config:
                config_dir = plugin_config['config_directory']
                if os.path.isabs(config_dir):
                    full_path = config_dir
                else:
                    full_path = os.path.join(app_root, config_dir)
                    
                if not os.path.exists(full_path):
                    missing_paths.append(full_path)
                elif not os.access(full_path, os.R_OK):
                    invalid_paths.append(full_path)
        
    except Exception as e:
        print(f"Error validating config paths: {e}")
        invalid_paths.append(config_file)
        
    return {'invalid': invalid_paths, 'missing': missing_paths}

def validate_standard_paths() -> Dict[str, List[str]]:
    """Validate standard directories.
    
    Returns:
        Dictionary with invalid and missing paths
    """
    app_root = get_app_root()
    invalid_paths = []
    missing_paths = []
    
    # Check standard directories
    for dir_type, dirname in STANDARD_DIRS.items():
        dir_path = os.path.join(app_root, dirname)
        
        if not os.path.exists(dir_path):
            missing_paths.append(dir_path)
            continue
            
        if not os.path.isdir(dir_path):
            invalid_paths.append(dir_path)
            continue
            
        if not os.access(dir_path, os.R_OK | os.W_OK):
            invalid_paths.append(dir_path)
            
        # Check subdirectories
        if dir_type in DIR_STRUCTURE:
            for subdir in DIR_STRUCTURE[dir_type]:
                subdir_path = os.path.join(dir_path, subdir)
                
                if not os.path.exists(subdir_path):
                    missing_paths.append(subdir_path)
                elif not os.path.isdir(subdir_path):
                    invalid_paths.append(subdir_path)
                elif not os.access(subdir_path, os.R_OK | os.W_OK):
                    invalid_paths.append(subdir_path)
    
    return {'invalid': invalid_paths, 'missing': missing_paths}

def create_missing_directories(missing_paths: List[str]) -> int:
    """Create missing directories.
    
    Args:
        missing_paths: List of paths to create
        
    Returns:
        Number of directories created
    """
    count = 0
    for path in missing_paths:
        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                print(f"Created directory: {path}")
                count += 1
        except Exception as e:
            print(f"Failed to create {path}: {e}")
    
    return count

def main():
    """Main function."""
    app_root = get_app_root()
    print(f"Validating paths for CreepyAI installation at {app_root}")
    
    # Validate standard paths
    path_results = validate_standard_paths()
    invalid_paths = path_results['invalid']
    missing_paths = path_results['missing']
    
    # Validate config paths
    config_file = os.path.join(app_root, 'configs', 'app_config.json')
    config_results = validate_config_paths(config_file)
    invalid_paths.extend(config_results['invalid'])
    missing_paths.extend(config_results['missing'])
    
    # Report results
    if invalid_paths:
        print("\nINVALID PATHS:")
        for path in invalid_paths:
            print(f" - {path}")
    
    if missing_paths:
        print("\nMISSING PATHS:")
        for path in missing_paths:
            print(f" - {path}")
        
        # Offer to create missing directories
        response = input("\nCreate missing directories? (y/n): ")
        if response.lower().startswith('y'):
            created = create_missing_directories(missing_paths)
            print(f"Created {created} directories.")
    
    if not invalid_paths and not missing_paths:
        print("\nAll paths are valid. No issues found.")
        return 0
        
    if invalid_paths:
        print("\nPlease fix the invalid paths listed above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
