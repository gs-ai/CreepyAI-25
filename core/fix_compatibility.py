#!/usr/bin/env python3
"""
CreepyAI Compatibility Fixer
---------------------------
This script patches common compatibility issues when installing dependencies
on newer Python versions.
"""

import os
import sys
import re
import subprocess
import site
import shutil
import tempfile
from pathlib import Path

def fix_pkgutil_impimporter_issue():
    """Fix the pkgutil.ImpImporter issue in affected packages"""
    print("Checking for pkgutil.ImpImporter issues in installed packages...")
    
    # Find site-packages directory
    site_packages = site.getsitepackages()[0]
    print(f"Scanning site-packages directory: {site_packages}")
    
    # Search for files using ImpImporter
    problematic_files = []
    for path in Path(site_packages).glob('**/*.py'):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'pkgutil.ImpImporter' in content:
                    problematic_files.append(path)
        except Exception as e:
            print(f"Error reading {path}: {e}")
    
    if not problematic_files:
        print("No files with pkgutil.ImpImporter issue found.")
        return
    
    print(f"Found {len(problematic_files)} file(s) with potential issues:")
    for path in problematic_files:
        print(f"  - {path}")
    
    # Patch the files
    for path in problematic_files:
        print(f"Patching {path}...")
        # Create backup
        backup_path = path.with_suffix('.py.bak')
        shutil.copy2(path, backup_path)
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace ImpImporter with a compatibility shim
        patched_content = content.replace(
            'pkgutil.ImpImporter',
            '(getattr(pkgutil, "ImpImporter", object))'
        )
        
        # Add import compatibility at the top of the file
        if 'import pkgutil' in content:
            # Add compatibility code after pkgutil import
            patched_content = re.sub(
                r'(import\s+pkgutil)',
                r'\1\n\n# Compatibility shim for Python 3.12+\nif not hasattr(pkgutil, "ImpImporter"):\n    pkgutil.ImpImporter = object\n',
                patched_content
            )
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(patched_content)
        
        print(f"  ✓ Applied patch and created backup at {backup_path}")

def create_compatibility_wrapper():
    """Create a compatibility wrapper script for running pip install"""
    wrapper_path = Path("pip_compat_install.sh")
    
    content = """#!/bin/bash
# Compatibility wrapper for pip install
# This script provides workarounds for common compatibility issues

# Detect Python version
PY_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Using Python $PY_VERSION"

# Set environment variables to help with compatibility
export SETUPTOOLS_ENABLE_FEATURES="legacy-editable"

# For the pkgutil.ImpImporter issue in Python 3.12+
if [[ "$PY_VERSION" == "3.12" || "$PY_VERSION" > "3.12" ]]; then
    echo "Warning: Python 3.12+ has known compatibility issues."
    echo "Consider downgrading to Python 3.11 for better compatibility."
    
    echo "Applying Python 3.12+ compatibility workarounds..."
    export PYTHONPATH="$PYTHONPATH:$(pwd)/compat_shims"
    
    # Create shims directory if it doesn't exist
    mkdir -p compat_shims
    
    # Create pkgutil shim
    cat > compat_shims/pkgutil_compat.py << 'EOF'
import sys
import pkgutil

# Add ImpImporter compatibility for Python 3.12+
if not hasattr(pkgutil, 'ImpImporter'):
    class ImpImporter(object):
        def __init__(self, *args, **kwargs):
            pass
    pkgutil.ImpImporter = ImpImporter

# Patch sys.modules to ensure our patched version is used
sys.modules['pkgutil'] = pkgutil
EOF

    # Inject the compatibility code
    PYTHONPATH="$PYTHONPATH:$(pwd)/compat_shims" python -c "import pkgutil_compat" || echo "Failed to apply compatibility patch"
fi

# Run pip with the requested command
echo "Running: pip $@"
pip "$@"

# Clean up if needed
# rm -rf compat_shims
"""
    
    with open(wrapper_path, 'w') as f:
        f.write(content)
    
    os.chmod(wrapper_path, 0o755)
    print(f"Created compatibility wrapper at {wrapper_path}")
    print("Use it by running: ./pip_compat_install.sh install -r requirements.txt")

def modify_requirements_file():
    """Modify requirements.txt file to use compatible versions"""
    req_path = Path("requirements.txt")
    if not req_path.exists():
        print(f"Error: {req_path} not found")
        return
    
    # Create backup
    backup_path = req_path.with_suffix('.txt.bak')
    shutil.copy2(req_path, backup_path)
    print(f"Created backup of requirements.txt at {backup_path}")
    
    # Read current requirements
    with open(req_path, 'r') as f:
        requirements = f.readlines()
    
    # Known problematic packages with fixes
    fixes = {
        r'yapsy==': 'yapsy==1.12.2',
        r'configobj==': 'configobj==5.0.9',
        # Add more package fixes here
    }
    
    new_requirements = []
    modified = False
    
    for req in requirements:
        req = req.strip()
        if not req or req.startswith('#'):
            new_requirements.append(req)
            continue
        
        # Apply fixes for known problematic packages
        for pattern, replacement in fixes.items():
            if re.match(f"^{pattern}", req):
                new_requirements.append(replacement)
                print(f"Modified: {req} -> {replacement}")
                modified = True
                break
        else:
            # No fix applied, keep original
            new_requirements.append(req)
    
    if modified:
        with open(req_path, 'w') as f:
            f.write('\n'.join(new_requirements) + '\n')
        print(f"Updated {req_path} with compatibility fixes")
    else:
        print("No modifications needed for requirements.txt")

def main():
    """Main function to fix compatibility issues"""
    print("CreepyAI Compatibility Fixer")
    print("==========================")
    
    # Get Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Running with Python {py_version}")
    
    # Check for Python 3.12
    if sys.version_info.major == 3 and sys.version_info.minor >= 12:
        print("\nWARNING: You're using Python 3.12+ which has known compatibility issues with some packages.")
        print("For best results, consider downgrading to Python 3.11:\n")
        print("    conda install python=3.11\n")
    
    # Fix existing installations if needed
    fix_pkgutil_impimporter_issue()
    
    # Create compatibility wrapper for future installations
    create_compatibility_wrapper()
    
    # Modify requirements.txt if needed
    modify_requirements_file()
    
    print("\nRecommendations:")
    print("1. Try installing dependencies with the compatibility wrapper:")
    print("   ./pip_compat_install.sh install -r requirements.txt")
    print("2. If certain packages still fail, install them one by one to identify problematic ones")
    print("3. For persistent issues, downgrade to Python 3.11:")
    print("   conda install -y python=3.11")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
