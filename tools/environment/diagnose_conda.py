#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Diagnose conda environment for CreepyAI.

This script helps diagnose issues with conda environments and Python paths.
"""

import os
import sys
import subprocess
import platform
import site
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_environment_variables():
    """Check environment variables related to conda."""
    print("Checking environment variables:")
    
    conda_vars = {
        "CONDA_PREFIX": os.environ.get("CONDA_PREFIX", "Not set"),
        "CONDA_DEFAULT_ENV": os.environ.get("CONDA_DEFAULT_ENV", "Not set"),
        "CONDA_PYTHON_EXE": os.environ.get("CONDA_PYTHON_EXE", "Not set"),
        "CONDA_EXE": os.environ.get("CONDA_EXE", "Not set"),
        "PATH": os.environ.get("PATH", "Not set")
    }
    
    for var, value in conda_vars.items():
        if var == "PATH":
            print(f"  {var}: {'...' + value[-50:] if len(value) > 50 else value}")
            conda_in_path = any("conda" in p for p in os.environ.get("PATH", "").split(os.pathsep))
            print(f"  Conda in PATH: {'Yes' if conda_in_path else 'No'}")
        else:
            print(f"  {var}: {value}")
    
    return True

def check_python_info():
    """Check Python interpreter information."""
    print("\nPython information:")
    print(f"  Executable: {sys.executable}")
    print(f"  Version: {platform.python_version()}")
    print(f"  Implementation: {platform.python_implementation()}")
    
    # Check if this is a conda interpreter
    is_conda = "conda" in sys.version or "Continuum" in sys.version
    print(f"  Conda Python: {'Yes' if is_conda else 'No'}")
    
    # Print site packages locations
    print("\nSite packages directories:")
    for path in site.getsitepackages():
        print(f"  {path}")
    
    return True

def find_conda_binary():
    """Find the conda binary."""
    print("\nSearching for conda binary:")
    
    # Try using environment variable
    if "CONDA_EXE" in os.environ:
        conda_exe = os.environ["CONDA_EXE"]
        if os.path.exists(conda_exe):
            print(f"  Found via CONDA_EXE: {conda_exe}")
            return conda_exe
    
    # Try using which command
    try:
        result = subprocess.run(["which", "conda"], 
                               capture_output=True, text=True, check=False)
        if result.returncode == 0:
            conda_exe = result.stdout.strip()
            print(f"  Found via which: {conda_exe}")
            return conda_exe
    except Exception:
        pass
    
    # Try common locations
    common_locations = [
        os.path.expanduser("~/anaconda3/bin/conda"),
        os.path.expanduser("~/miniconda3/bin/conda"),
        "/opt/anaconda3/bin/conda",
        "/usr/local/anaconda3/bin/conda",
    ]
    
    for location in common_locations:
        if os.path.exists(location):
            print(f"  Found at common location: {location}")
            return location
    
    # Try to find relative to CONDA_PREFIX
    if "CONDA_PREFIX" in os.environ:
        base_path = os.environ["CONDA_PREFIX"]
        # Check if we're in an environment
        if os.path.basename(os.path.dirname(base_path)) == "envs":
            # Go up two levels to find base conda
            base_conda = os.path.dirname(os.path.dirname(base_path))
            conda_exe = os.path.join(base_conda, "bin", "conda")
            if os.path.exists(conda_exe):
                print(f"  Found via CONDA_PREFIX: {conda_exe}")
                return conda_exe
    
    print("  Conda binary not found")
    return None

def check_conda_info():
    """Check conda information."""
    conda_exe = find_conda_binary()
    
    if not conda_exe:
        print("\nConda information: Not available (conda not found)")
        return False
    
    print("\nConda information:")
    try:
        # Get conda info
        result = subprocess.run([conda_exe, "info"], 
                               capture_output=True, text=True, check=False)
        if result.returncode == 0:
            # Print selected info (not all of it)
            info_lines = result.stdout.strip().split("\n")
            for line in info_lines[:20]:  # Print first 20 lines
                if any(key in line for key in ["base environment", "conda version", "platform", "user", "active env"]):
                    print(f"  {line.strip()}")
            
            # List environments
            print("\nConda environments:")
            env_section = False
            for line in info_lines:
                if line.strip() == "environments:":
                    env_section = True
                    continue
                if env_section and line.strip():
                    if not line.startswith(" "):
                        break
                    print(f"  {line.strip()}")
            
            return True
        else:
            print(f"  Error running conda info: {result.stderr}")
            return False
    except Exception as e:
        print(f"  Error checking conda info: {e}")
        return False

def check_fix_script():
    """Check if fix_pyqt_conda.sh is properly setup."""
    script_path = "fix_pyqt_conda.sh"
    
    print(f"\nChecking {script_path}:")
    
    if not os.path.exists(script_path):
        print(f"  {script_path} not found")
        return False
    
    try:
        with open(script_path, "r") as f:
            content = f.read()
        
        # Check if the script is using a hardcoded conda path
        if "CONDA_CMD=" in content:
            conda_path = content.split("CONDA_CMD=")[1].split("\n")[0].strip('"')
            print(f"  Script is using conda at: {conda_path}")
            if os.path.exists(conda_path):
                print(f"  ✓ Conda path is valid")
            else:
                print(f"  ✗ Conda path is invalid")
                return False
        else:
            print("  Script is not using a hardcoded conda path")
            return False
        
        # Check if the script is executable
        if os.access(script_path, os.X_OK):
            print("  ✓ Script is executable")
        else:
            print("  ✗ Script is not executable")
            print("  Run: chmod +x fix_pyqt_conda.sh")
            return False
        
        return True
    except Exception as e:
        print(f"  Error checking fix script: {e}")
        return False

def main():
    """Main function."""
    print("="*50)
    print("CreepyAI Conda Environment Diagnostics")
    print("="*50)
    
    check_environment_variables()
    check_python_info()
    check_conda_info()
    check_fix_script()
    
    print("\nDiagnostics completed.")
    print("\nIf you're having issues with conda detection, try:")
    print("1. Make sure conda is properly installed")
    print("2. Activate your conda environment before running scripts")
    print("3. Run 'python fix_conda_path.py' to update conda paths")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
