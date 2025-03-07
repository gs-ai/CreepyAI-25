#!/usr/bin/env python3
"""
CreepyAI Health Check Tool

This script performs a comprehensive health check of your CreepyAI installation,
verifying all components are working correctly and providing recommendations.
"""
import os
import sys
import importlib
import logging
import subprocess
import platform
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='health_check.log'
)
logger = logging.getLogger('CreepyAI Health Check')

# Add project directories to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'core'))

class HealthCheck:
    """Health check class for CreepyAI"""
    
    def __init__(self):
        self.issues = []
        self.recommendations = []
        self.report_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'creepyai_path': BASE_DIR,
            'environment_status': {},
            'ui_status': {},
            'plugin_status': {},
            'paths_status': {},
            'issues': [],
            'recommendations': []
        }
    
    def run_all_checks(self):
        """Run all health checks"""
        print("Running CreepyAI Health Check...")
        
        self.check_system()
        self.check_dependencies()
        self.check_ui_frameworks()
        self.check_directory_structure()
        self.check_plugins()
        self.check_python_path()
        self.check_file_permissions()
        
        return self.generate_report()
    
    def check_system(self):
        """Check system information"""
        print("Checking system information...")
        
        # Record system information
        self.report_data['environment_status']['os'] = platform.system()
        self.report_data['environment_status']['os_release'] = platform.release()
        
        # Check disk space
        if shutil.disk_usage(BASE_DIR).free < 1000000000:  # Less than 1 GB
            self.add_issue("Low disk space", "Your system is low on disk space, which may affect performance.")
            self.add_recommendation("Free up at least 1 GB of disk space for optimal performance.")
    
    def check_dependencies(self):
        """Check project dependencies"""
        print("Checking dependencies...")
        
        essential_modules = [
            "PyQt5", "PyQt5.QtCore", "PyQt5.QtWidgets", 
            "tkinter", "json", "folium", "simplekml", "yapsy"
        ]
        
        for module in essential_modules:
            try:
                importlib.import_module(module)
                self.report_data['environment_status'][module] = "Installed"
            except ImportError:
                self.report_data['environment_status'][module] = "Missing"
                self.add_issue(f"Missing dependency: {module}", f"The module {module} is required but not installed.")
                
                if module.startswith('PyQt5'):
                    self.add_recommendation("Run 'sh tools/install_macos_deps.sh' to install PyQt5 dependencies.")
                else:
                    self.add_recommendation(f"Install {module} with 'pip install {module}'.")
    
    def check_ui_frameworks(self):
        """Check UI frameworks"""
        print("Checking UI frameworks...")
        
        # Check PyQt5
        try:
            import PyQt5.QtCore
            self.report_data['ui_status']['pyqt5'] = "Available"
        except ImportError:
            self.report_data['ui_status']['pyqt5'] = "Not available"
            self.add_issue("PyQt5 not available", "The PyQt5 UI framework is not available.")
        
        # Check Tkinter
        try:
            import tkinter
            self.report_data['ui_status']['tkinter'] = "Available"
        except ImportError:
            self.report_data['ui_status']['tkinter'] = "Not available"
            self.add_issue("Tkinter not available", "The Tkinter UI framework is not available.")
        
        # Check if at least one UI is available
        if all(status == "Not available" for status in self.report_data['ui_status'].values()):
            self.add_issue("No UI frameworks available", "Neither PyQt5 nor Tkinter is available.")
            self.add_recommendation("Install at least one UI framework: PyQt5 or Tkinter.")
    
    def check_directory_structure(self):
        """Check directory structure"""
        print("Checking directory structure...")
        
        required_dirs = ['core', 'models', 'plugins', 'ui', 'utilities', 'resources']
        for dir_name in required_dirs:
            dir_path = os.path.join(BASE_DIR, dir_name)
            if not os.path.isdir(dir_path):
                self.add_issue(f"Missing directory: {dir_name}", f"The {dir_name} directory is missing.")
                self.add_recommendation(f"Create the {dir_name} directory in the project root.")
            
        required_files = ['launch_creepyai.py', 'requirements.txt', 'run_creepyai.sh']
        for file_name in required_files:
            file_path = os.path.join(BASE_DIR, file_name)
            if not os.path.isfile(file_path):
                self.add_issue(f"Missing file: {file_name}", f"The {file_name} file is missing.")
                self.add_recommendation(f"Restore the {file_name} file from backup or repository.")
    
    def check_plugins(self):
        """Check plugins"""
        print("Checking plugins...")
        
        plugins_dir = os.path.join(BASE_DIR, 'plugins')
        if not os.path.isdir(plugins_dir):
            self.add_issue("Missing plugins directory", "The plugins directory is missing.")
            return
        
        # Count plugins
        py_files = [f for f in os.listdir(plugins_dir) if f.endswith('.py') and not f == '__init__.py']
        self.report_data['plugin_status']['count'] = len(py_files)
        
        # Check for base_plugin.py
        if not os.path.isfile(os.path.join(plugins_dir, 'base_plugin.py')):
            self.add_issue("Missing base plugin", "The base_plugin.py file is missing.")
            self.add_recommendation("Restore base_plugin.py from backup or repository.")
    
    def check_python_path(self):
        """Check Python path"""
        print("Checking Python path...")
        
        # Check if project directory is in Python path
        if BASE_DIR not in sys.path:
            self.add_issue("Project directory not in Python path", "The project directory is not in the Python path.")
            self.add_recommendation("Add the project directory to PYTHONPATH environment variable.")
        
        # Check if creepy module is properly set up
        creepy_dir = os.path.join(BASE_DIR, 'creepy')
        if os.path.isdir(creepy_dir):
            init_file = os.path.join(creepy_dir, '__init__.py')
            if not os.path.isfile(init_file):
                self.add_issue("Missing __init__.py in creepy directory", "The __init__.py file is missing in the creepy directory.")
                self.add_recommendation("Create an __init__.py file in the creepy directory.")
    
    def check_file_permissions(self):
        """Check file permissions"""
        print("Checking file permissions...")
        
        # Check if run scripts are executable
        scripts = ['run_creepyai.sh', 'tools/install_macos_deps.sh']
        for script in scripts:
            script_path = os.path.join(BASE_DIR, script)
            if os.path.isfile(script_path) and not os.access(script_path, os.X_OK):
                self.add_issue(f"Script not executable: {script}", f"The {script} script is not executable.")
                self.add_recommendation(f"Make the script executable with: chmod +x {script}")
    
    def add_issue(self, title, description):
        """Add an issue to the report"""
        self.issues.append({'title': title, 'description': description})
        self.report_data['issues'].append({'title': title, 'description': description})
    
    def add_recommendation(self, recommendation):
        """Add a recommendation to the report"""
        if recommendation not in self.recommendations:
            self.recommendations.append(recommendation)
            self.report_data['recommendations'].append(recommendation)
    
    def generate_report(self):
        """Generate health check report"""
        print("\n=== CreepyAI Health Check Report ===")
        print(f"Timestamp: {self.report_data['timestamp']}")
        print(f"Platform: {self.report_data['platform']}")
        print(f"Python Version: {self.report_data['python_version']}")
        print(f"CreepyAI Path: {self.report_data['creepyai_path']}")
        print("\n--- Environment Status ---")
        for module, status in self.report_data['environment_status'].items():
            print(f"{module}: {status}")
        print("\n--- UI Status ---")
        for ui, status in self.report_data['ui_status'].items():
            print(f"{ui}: {status}")
        
        print(f"\nFound {len(self.issues)} issues.")
        
        if self.issues:
            print("\n--- Issues ---")
            for i, issue in enumerate(self.issues):
                print(f"{i+1}. {issue['title']}")
                print(f"   {issue['description']}")
        
        if self.recommendations:
            print("\n--- Recommendations ---")
            for i, recommendation in enumerate(self.recommendations):
                print(f"{i+1}. {recommendation}")
        
        # Save report to file
        report_path = os.path.join(BASE_DIR, 'health_check_report.txt')
        try:
            with open(report_path, 'w') as f:
                f.write(f"=== CreepyAI Health Check Report ===\n")
                f.write(f"Timestamp: {self.report_data['timestamp']}\n")
                f.write(f"Platform: {self.report_data['platform']}\n")
                f.write(f"Python Version: {self.report_data['python_version']}\n")
                f.write(f"CreepyAI Path: {self.report_data['creepyai_path']}\n")
                f.write("\n--- Environment Status ---\n")
                for module, status in self.report_data['environment_status'].items():
                    f.write(f"{module}: {status}\n")
                f.write("\n--- UI Status ---\n")
                for ui, status in self.report_data['ui_status'].items():
                    f.write(f"{ui}: {status}\n")
                
                f.write(f"\nFound {len(self.issues)} issues.\n")
                
                if self.issues:
                    f.write("\n--- Issues ---\n")
                    for i, issue in enumerate(self.issues):
                        f.write(f"{i+1}. {issue['title']}\n")
                        f.write(f"   {issue['description']}\n")
                
                if self.recommendations:
                    f.write("\n--- Recommendations ---\n")
                    for i, recommendation in enumerate(self.recommendations):
                        f.write(f"{i+1}. {recommendation}\n")
            
            print(f"\nReport saved to: {report_path}")
        except Exception as e:
            print(f"Error saving report: {e}")
        
        return {
            'issues': self.issues,
            'recommendations': self.recommendations
        }

def main():
    """Main function"""
    health_check = HealthCheck()
    health_check.run_all_checks()
    
    if not health_check.issues:
        print("\nGreat! No issues were found. Your CreepyAI installation appears to be healthy.")
    else:
        print(f"\n{len(health_check.issues)} issues were found. Please review the recommendations above.")

if __name__ == "__main__":
    main()
