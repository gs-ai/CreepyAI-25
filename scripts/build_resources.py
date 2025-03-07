#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Resource compiler script for CreepyAI.

This script automates the process of compiling Qt resource files (.qrc)
into Python modules that can be imported by the application.

After compilation, you can import resources with:
    import creepy_resources_rc
"""

import os
import sys
import subprocess
import argparse
import logging
from typing import List, Optional, Dict, Any
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_pyrcc5() -> Optional[str]:
    """
    Find the pyrcc5 executable in the system PATH.
    
    Returns:
        str: Path to pyrcc5 executable or None if not found
    """
    # Common names for the pyrcc5 executable
    pyrcc_names = ['pyrcc5', 'pyrcc5.exe', 'pyrcc5-3.8', 'pyrcc5-3.9', 'pyrcc5-3.10', 'pyrcc5-3.11']
    
    for name in pyrcc_names:
        try:
            # Check if executable exists in PATH
            if sys.platform.startswith('win'):
                # On Windows, use where command
                result = subprocess.run(['where', name], 
                                       capture_output=True, 
                                       text=True, 
                                       check=False)
            else:
                # On Unix-like systems, use which command
                result = subprocess.run(['which', name], 
                                       capture_output=True, 
                                       text=True, 
                                       check=False)
                
            if result.returncode == 0:
                path = result.stdout.strip().split('\n')[0]
                logger.debug(f"Found pyrcc5: {path}")
                return path
        except Exception as e:
            logger.debug(f"Error searching for {name}: {e}")
    
    return None

def validate_resource_files(qrc_file: str) -> Dict[str, List[str]]:
    """
    Validate that all resource files referenced in the .qrc file exist.
    
    Args:
        qrc_file: Path to the .qrc file
        
    Returns:
        Dict with 'missing' and 'found' lists of files
    """
    result = {
        'missing': [],
        'found': []
    }
    
    try:
        # Parse the XML file
        tree = ET.parse(qrc_file)
        root = tree.getroot()
        
        # Get the directory of the .qrc file
        base_dir = os.path.dirname(qrc_file)
        
        # Check each file in the resource
        for file_elem in root.findall('.//file'):
            file_path = file_elem.text
            full_path = os.path.join(base_dir, file_path)
            
            if os.path.exists(full_path) and os.path.isfile(full_path):
                result['found'].append(file_path)
            else:
                result['missing'].append(file_path)
                logger.warning(f"Missing resource file: {file_path}")
                
        logger.info(f"Resource validation: {len(result['found'])} files found, {len(result['missing'])} missing")
        return result
        
    except Exception as e:
        logger.error(f"Error validating resource files: {e}")
        return result

def compile_resource(qrc_file: str, output_file: str, pyrcc5_path: Optional[str] = None) -> bool:
    """
    Compile a .qrc file into a Python module using pyrcc5.
    
    Args:
        qrc_file: Path to the .qrc file
        output_file: Path for the output Python file
        pyrcc5_path: Optional path to pyrcc5 executable
        
    Returns:
        bool: True if compilation was successful, False otherwise
    """
    try:
        # Check if input file exists
        if not os.path.isfile(qrc_file):
            logger.error(f"Resource file not found: {qrc_file}")
            return False
            
        # Validate resource files
        validation = validate_resource_files(qrc_file)
        if validation['missing']:
            logger.warning(f"Some resource files are missing. Compilation may not include all resources.")
            
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Find pyrcc5 if not specified
        if not pyrcc5_path:
            pyrcc5_path = find_pyrcc5()
            if not pyrcc5_path:
                logger.error("pyrcc5 not found. Please install PyQt5 or specify path.")
                return False
                
        # Build command
        cmd = [
            pyrcc5_path,
            '-o', output_file,
            qrc_file
        ]
        
        # Execute command
        logger.info(f"Compiling {qrc_file} to {output_file}...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            logger.error(f"Compilation failed: {result.stderr}")
            return False
        
        # Add extra error handling to the output file
        add_error_handling_to_compiled_resource(output_file)
            
        logger.info(f"Successfully compiled {os.path.basename(qrc_file)}")
        return True
        
    except Exception as e:
        logger.error(f"Error compiling resource: {e}")
        return False

def add_error_handling_to_compiled_resource(output_file: str) -> bool:
    """
    Add error handling code to the compiled resource file.
    
    Args:
        output_file: Path to the compiled Python resource file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the current content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Add imports and error handling
        import_line = "from PyQt5 import QtCore"
        logging_import = "import logging\n# Configure logger\nlogger = logging.getLogger(__name__)"
        
        # Update the qInitResources function with error handling
        init_updated = False
        lines = content.split('\n')
        new_lines = []
        
        in_init = False
        in_cleanup = False
        
        for line in lines:
            # Add logging import after PyQt5 import
            if line.strip() == import_line:
                new_lines.append(line)
                new_lines.append(logging_import)
                continue
                
            # Update qInitResources function
            if line.strip().startswith('def qInitResources'):
                in_init = True
                new_lines.append('def qInitResources():')
                new_lines.append('    """Initialize Qt resources by registering resource data."""')
                new_lines.append('    try:')
                continue
            
            # Update qCleanupResources function
            if line.strip().startswith('def qCleanupResources'):
                in_init = False
                in_cleanup = True
                new_lines.append('def qCleanupResources():')
                new_lines.append('    """Clean up Qt resources by unregistering resource data."""')
                new_lines.append('    try:')
                continue
                
            # Add indentation inside functions
            if in_init or in_cleanup:
                if line.strip() and not line.strip().startswith('def'):
                    new_lines.append('        ' + line.strip())
                    if line.strip() == 'return':
                        new_lines.append('    except Exception as e:')
                        if in_init:
                            new_lines.append('        logger.error(f"Failed to initialize resources: {e}")')
                        else:
                            new_lines.append('        logger.error(f"Failed to cleanup resources: {e}")')
                        new_lines.append('        return')
                        in_init = False
                        in_cleanup = False
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        # Add initialization when imported
        new_lines.append('\n# Auto-initialize resources when module is imported')
        new_lines.append('if __name__ != "__main__":')
        new_lines.append('    try:')
        new_lines.append('        qInitResources()')
        new_lines.append('    except Exception as e:')
        new_lines.append('        logger.error(f"Failed to auto-initialize resources: {e}")')
        
        # Add message when executed directly
        new_lines.append('\n# If this file is run directly, report that it\'s not designed to be executed')
        new_lines.append('if __name__ == "__main__":')
        new_lines.append('    print("This is a PyQt5 resource file and is not meant to be executed directly.")')
        new_lines.append('    print("Import this module in your application instead.")')
        new_lines.append('    print("To recompile resources, use the build_resources.py script.")')
        
        # Write the updated content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
            
        logger.info(f"Added error handling to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding error handling: {e}")
        return False

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Compile Qt resource files for CreepyAI"
    )
    
    parser.add_argument(
        '--qrc',
        default='resources/creepy_resources.qrc',
        help='Path to .qrc file (default: resources/creepy_resources.qrc)'
    )
    
    parser.add_argument(
        '--output',
        default='creepy_resources_rc.py',
        help='Output Python module (default: creepy_resources_rc.py)'
    )
    
    parser.add_argument(
        '--pyrcc5',
        help='Path to pyrcc5 executable (will search in PATH if not specified)'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate resource files without compiling'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_arguments()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Convert paths to absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    qrc_file = os.path.join(base_dir, args.qrc)
    output_file = os.path.join(base_dir, args.output)
    
    # Validate resource files
    if not os.path.exists(qrc_file):
        logger.error(f"QRC file not found: {qrc_file}")
        return 1
        
    validation = validate_resource_files(qrc_file)
    
    # Stop if validation only
    if args.validate_only:
        if validation['missing']:
            logger.error(f"Validation failed: {len(validation['missing'])} files missing")
            for file in validation['missing']:
                print(f"Missing: {file}")
            return 1
        logger.info("Validation successful!")
        return 0
    
    # Compile resource file
    success = compile_resource(qrc_file, output_file, args.pyrcc5)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
