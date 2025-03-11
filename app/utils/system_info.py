    """
System information utilities for CreepyAI.
"""
import os
import sys
import platform
import logging
import socket
import time
import uuid
import json
import datetime
import subprocess
from pathlib import Path
import psutil
import shutil
from typing import Dict, Any, List, Optional

logger = logging.getLogger('creepyai.utilities.system_info')


def get_system_info():
    """Get detailed system information for diagnostics and compatibility checks"""
    info = {
        'system': {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': socket.gethostname(),
            'mac_address': ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                                    for elements in range(0, 48, 8)][::-1]),
            'python_version': sys.version,
            'python_implementation': platform.python_implementation(),
        },
        'resources': {
            'cpu_count': psutil.cpu_count(logical=False),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_total': psutil.disk_usage('/').total,
            'disk_free': psutil.disk_usage('/').free,
        },
        'environment': {
            'path': os.environ.get('PATH', ''),
            'home': os.environ.get('HOME', ''),
            'user': os.environ.get('USER', ''),
            'shell': os.environ.get('SHELL', ''),
            'virtual_env': os.environ.get('VIRTUAL_ENV', ''),
            'conda_env': os.environ.get('CONDA_DEFAULT_ENV', ''),
        }
    }
    
    # Add detailed GPU information if available
    try:
        if platform.system() == 'Darwin':  # macOS
            cmd = "system_profiler SPDisplaysDataType"
            gpu_info = subprocess.check_output(cmd, shell=True).decode('utf-8')
            info['gpu'] = {'raw_info': gpu_info}
        elif platform.system() == 'Windows':
            cmd = "wmic path win32_VideoController get name"
            gpu_info = subprocess.check_output(cmd, shell=True).decode('utf-8')
            info['gpu'] = {'name': gpu_info.strip().split('\n')[1]}
        elif platform.system() == 'Linux':
            cmd = "lspci | grep -i 'vga\|3d\|2d'"
            gpu_info = subprocess.check_output(cmd, shell=True).decode('utf-8')
            info['gpu'] = {'raw_info': gpu_info}
    except Exception as e:
        logger.warning(f"Could not retrieve GPU information: {e}")
    
    # Add installed packages information
    try:
        import pkg_resources
        info['packages'] = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
    except Exception as e:
        logger.warning(f"Could not retrieve package information: {e}")
    
    return info


def check_dependencies():
    """Check if all required dependencies are installed and compatible"""
    required_executables = {
        'python': sys.executable,
        'pip': shutil.which('pip') or shutil.which('pip3'),
    }
    
    # Check for optional but useful executables
    optional_executables = {
        'git': shutil.which('git'),
        'curl': shutil.which('curl'),
        'conda': shutil.which('conda'),
        'npm': shutil.which('npm'),
    }
    
    dependency_status = {
        'required': {name: bool(path) for name, path in required_executables.items()},
        'optional': {name: bool(path) for name, path in optional_executables.items()},
    }
    
    # Check Python packages
    required_packages = ['PyQt5', 'numpy', 'requests', 'yaml', 'folium']
    optional_packages = ['matplotlib', 'scikit-learn', 'pandas']
    
    installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
    
    dependency_status['python_packages'] = {
        'required': {pkg: pkg.lower() in installed_packages for pkg in required_packages},
        'optional': {pkg: pkg.lower() in installed_packages for pkg in optional_packages},
    }
    
    return dependency_status


def write_system_info_to_file(file_path=None):
    """Write system information to a file for diagnostic purposes"""
    info = get_system_info()
    dependencies = check_dependencies()
    
    if file_path is None:
        file_path = Path.home() / 'creepyai_system_info.json'
    
    data = {
        'system_info': info,
        'dependencies': dependencies,
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"System information written to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to write system information: {e}")
        return False


def get_compatibility_report():
    """Generate a compatibility report for the current system"""
    info = get_system_info()
    dependencies = check_dependencies()
    
    system = info['system']['platform']
    issues = []
    recommendations = []
    
    # Check Python version
    python_version = tuple(map(int, platform.python_version_tuple()))
    if python_version < (3, 8):
        issues.append(f"Python version {platform.python_version()} is below the recommended 3.8+")
        recommendations.append("Upgrade Python to version 3.8 or higher")
    
    # Check memory
    min_memory = 4 * 1024 * 1024 * 1024  # 4GB
    if info['resources']['memory_total'] < min_memory:
        issues.append(f"System has less than the recommended 4GB RAM")
        recommendations.append("Consider upgrading RAM for better performance")
    
    # Check disk space
    min_disk = 5 * 1024 * 1024 * 1024  # 5GB
    if info['resources']['disk_free'] < min_disk:
        issues.append(f"System has less than 5GB free disk space")
        recommendations.append("Free up disk space for better performance and to prevent errors")
    
    # Check dependencies
    for pkg, installed in dependencies['python_packages']['required'].items():
        if not installed:
            issues.append(f"Required package {pkg} is not installed")
            recommendations.append(f"Install {pkg} using pip install {pkg}")
    
    return {
        'compatible': len(issues) == 0,
        'issues': issues,
        'recommendations': recommendations,
        'system': system
    }


if __name__ == "__main__":
    import datetime
    info = get_system_info()
    print(json.dumps(info, indent=2, default=str))
    
    print("\nCompatibility Report:")
    report = get_compatibility_report()
    if report['compatible']:
        print("✅ Your system is compatible with CreepyAI")
    else:
        print("⚠️ Your system has some compatibility issues:")
        for issue in report['issues']:
            print(f"  - {issue}")
        
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  - {rec}")
