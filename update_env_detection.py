#!/usr/bin/env python3
"""
CreepyAI Environment Detection Tool
----------------------------------
This script detects the current Python environment and provides 
information about upgrading if needed.
"""

import sys
import os
import platform
import subprocess
from packaging import version

def get_python_info():
    """Get current Python version and environment information"""
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    implementation = platform.python_implementation()
    
    env_info = {
        "version": python_version,
        "implementation": implementation,
        "executable": sys.executable,
        "is_conda": "conda" in sys.executable or "Anaconda" in sys.executable or "Miniconda" in sys.executable
    }
    
    # Get conda env name if applicable
    if env_info["is_conda"]:
        try:
            conda_env = os.environ.get("CONDA_DEFAULT_ENV", "base")
            env_info["conda_env"] = conda_env
        except Exception:
            env_info["conda_env"] = "unknown"
    
    return env_info

def check_pkg_compatibility():
    """Check if current Python version is compatible with all requirements"""
    current_python = version.parse(f"{sys.version_info.major}.{sys.version_info.minor}")
    
    compatibility_issues = []
    
    # Define packages with specific Python version requirements
    critical_packages = {
        "scikit-learn>=1.5.0": version.parse("3.9"),
        "Pillow>=10.0.0": version.parse("3.9"),
        "black>=24.0.0": version.parse("3.8")
    }
    
    for pkg, min_python in critical_packages.items():
        if current_python < min_python:
            compatibility_issues.append(f"{pkg} requires Python {min_python}+")
    
    return compatibility_issues

def main():
    """Main function to check environment and display upgrade information"""
    print("CreepyAI Environment Detection Tool")
    print("==================================")
    
    env_info = get_python_info()
    print(f"\nPython version: {env_info['version']} ({env_info['implementation']})")
    print(f"Executable: {env_info['executable']}")
    
    if env_info["is_conda"]:
        print(f"Conda environment: {env_info.get('conda_env', 'unknown')}")
    
    compatibility_issues = check_pkg_compatibility()
    
    if compatibility_issues:
        print("\nCompatibility Issues Detected:")
        for issue in compatibility_issues:
            print(f"  - {issue}")
        
        print("\nRecommended Action:")
        print("  Run the upgrade script to create a new environment with a compatible Python version:")
        print("  ./upgrade_python_env.sh")
    else:
        print("\nYour Python environment is compatible with all dependencies.")
    
    # Provide additional information on latest Python
    try:
        if env_info["is_conda"]:
            result = subprocess.run(
                ["conda", "search", "python"], 
                capture_output=True, 
                text=True,
                check=True
            )
            latest_line = [line for line in result.stdout.splitlines() if "py3" in line][-1]
            latest_python = latest_line.split()[1]
            
            current_py_version = version.parse(env_info["version"])
            latest_py_version = version.parse(latest_python)
            
            if latest_py_version > current_py_version:
                print(f"\nA newer Python version ({latest_python}) is available.")
                print(f"You're currently using Python {env_info['version']}.")
                print("Consider upgrading to take advantage of latest features and performance improvements.")
    except Exception:
        # Silently pass if we can't determine latest version
        pass

if __name__ == "__main__":
    main()
