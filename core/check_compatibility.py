#!/usr/bin/env python3
"""
CreepyAI Compatibility Checker
------------------------------
This script checks the compatibility of dependencies with the current Python version
and suggests compatible versions.
"""

import sys
import subprocess
import re
import pkg_resources
from packaging.version import parse

def get_python_version():
    """Get the current Python version"""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def get_max_compatible_version(package_name, python_version):
    """Find the maximum compatible version of a package for the current Python version"""
    try:
        # Get all available versions
        result = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", package_name],
            capture_output=True,
            text=True
        )
        
        output = result.stdout
        
        # Parse output to find available versions
        available_versions = re.findall(r'Available versions: (.*)', output)
        if not available_versions:
            return None
            
        version_list = available_versions[0].split(", ")
        compatible_versions = []
        
        # Check each version for compatibility
        for version_str in version_list:
            try:
                # Try to find version in PyPI without installing
                metadata = subprocess.run(
                    [sys.executable, "-m", "pip", "install", f"{package_name}=={version_str}", "--dry-run"],
                    capture_output=True,
                    text=True
                )
                
                # If no Python version error, it's compatible
                if "Requires-Python" not in metadata.stderr:
                    compatible_versions.append(version_str)
            except Exception:
                continue
                
        if compatible_versions:
            # Sort versions and return the highest
            sorted_versions = sorted(compatible_versions, key=parse)
            return sorted_versions[-1]
        
        return None
    
    except Exception as e:
        print(f"Error checking {package_name}: {e}")
        return None

def check_requirements_file(file_path):
    """Check and suggest fixes for requirements file"""
    python_version = get_python_version()
    print(f"Checking compatibility with Python {python_version}")
    
    with open(file_path, 'r') as f:
        requirements = f.readlines()
    
    new_requirements = []
    incompatible_found = False
    
    for req in requirements:
        req = req.strip()
        if not req or req.startswith('#'):
            new_requirements.append(req)
            continue
            
        # Parse requirement
        try:
            package_req = pkg_resources.Requirement.parse(req)
            package_name = package_req.name
            
            # Check if already installed
            try:
                pkg_resources.get_distribution(req)
                print(f"✓ {req} - Already installed and compatible")
                new_requirements.append(req)
            except pkg_resources.DistributionNotFound:
                print(f"! {req} - Not installed, checking compatibility...")
                compatible_version = get_max_compatible_version(package_name, python_version)
                
                if compatible_version:
                    new_req = f"{package_name}=={compatible_version}"
                    print(f"  Suggested replacement: {new_req}")
                    new_requirements.append(new_req)
                    incompatible_found = True
                else:
                    print(f"  No compatible version found for {package_name}")
                    new_requirements.append(f"# {req} - No compatible version found for Python {python_version}")
                    incompatible_found = True
            except pkg_resources.VersionConflict:
                print(f"! {req} - Version conflict, checking compatibility...")
                compatible_version = get_max_compatible_version(package_name, python_version)
                
                if compatible_version:
                    new_req = f"{package_name}=={compatible_version}"
                    print(f"  Suggested replacement: {new_req}")
                    new_requirements.append(new_req)
                    incompatible_found = True
                else:
                    print(f"  No compatible version found for {package_name}")
                    new_requirements.append(f"# {req} - No compatible version found for Python {python_version}")
                    incompatible_found = True
        except Exception as e:
            print(f"Error parsing requirement {req}: {e}")
            new_requirements.append(req)
    
    if incompatible_found:
        backup_path = file_path + ".bak"
        with open(backup_path, 'w') as f:
            f.write("\n".join(requirements))
        
        response = input("Would you like to update your requirements.txt with compatible versions? (y/N): ")
        if response.lower() == 'y':
            with open(file_path, 'w') as f:
                f.write("\n".join(new_requirements))
            print(f"Updated {file_path} with compatible versions. Original backed up to {backup_path}")
        else:
            print("No changes made to requirements.txt")
    else:
        print("All requirements are compatible. No changes needed.")

if __name__ == "__main__":
    import os
    requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    
    if os.path.exists(requirements_file):
        check_requirements_file(requirements_file)
    else:
        print("requirements.txt file not found!")
