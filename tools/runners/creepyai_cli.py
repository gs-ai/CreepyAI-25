#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CreepyAI Command Line Interface
A unified interface for accessing all CreepyAI tools and functionality
"""

import os
import sys
import logging
import argparse
import subprocess
import shutil
import textwrap
from datetime import datetime
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CreepyAI-CLI')

# Get paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Command definitions and documentation
COMMANDS = {
    # UI launch commands
    'start': {
        'description': 'Start CreepyAI with default UI',
        'function': 'cmd_start_app',
        'help': 'Launches the main CreepyAI application with default UI settings.',
        'args': []
    },
    'start-tkinter': {
        'description': 'Start CreepyAI with Tkinter UI',
        'function': 'cmd_start_tkinter',
        'help': 'Launches CreepyAI using the simplified Tkinter interface.',
        'args': []
    },
    
    # Testing commands
    'test-qt': {
        'description': 'Test PyQt5 environment',
        'function': 'cmd_test_qt',
        'help': 'Opens a test window to verify PyQt5 installation and environment.',
        'args': []
    },
    'test-plugins': {
        'description': 'Test plugins system',
        'function': 'cmd_test_plugins',
        'help': 'Tests the plugin system by discovering and loading available plugins.',
        'args': []
    },
    
    # Plugin management
    'list-plugins': {
        'description': 'List all available plugins',
        'function': 'cmd_list_plugins',
        'help': 'Discovers and displays a list of all available plugins.',
        'args': []
    },
    'run-plugin': {
        'description': 'Run a specific plugin',
        'function': 'cmd_run_plugin',
        'help': 'Runs a specific plugin with given target and options.',
        'args': [
            {'name': 'plugin', 'help': 'Plugin name to run'},
            {'name': 'target', 'help': 'Target for the plugin (username, profile, etc.)'},
            {'name': '--output', 'help': 'Output file for results (JSON format)'},
            {'name': '--from-date', 'help': 'Start date filter (YYYY-MM-DD)'},
            {'name': '--to-date', 'help': 'End date filter (YYYY-MM-DD)'}
        ]
    },
    'plugin-health': {
        'description': 'Check health status of plugins',
        'function': 'cmd_plugin_health',
        'help': 'Validates plugins and reports their status.',
        'args': [
            {'name': '--detail', 'action': 'store_true', 'help': 'Show detailed information for each plugin'}
        ]
    },
    
    # Maintenance commands
    'setup': {
        'description': 'Install dependencies and prepare environment',
        'function': 'cmd_setup',
        'help': 'Installs required dependencies and sets up the CreepyAI environment.',
        'args': []
    },
    'compile-resources': {
        'description': 'Compile Qt resources',
        'function': 'cmd_compile_resources',
        'help': 'Compiles Qt resource files for the application UI.',
        'args': []
    },
    
    # Information
    'info': {
        'description': 'Show system information and environment details',
        'function': 'cmd_info',
        'help': 'Displays information about the system, Python environment, and CreepyAI.',
        'args': []
    },
    'help': {
        'description': 'Show help information',
        'function': 'cmd_help',
        'help': 'Shows detailed help information about available commands.',
        'args': [
            {'name': 'command', 'help': 'Command name to get help for', 'nargs': '?'}
        ]
    },
    
    # Plugin troubleshooting
    'fix-plugins': {
        'description': 'Scan and fix issues in plugins',
        'function': 'cmd_fix_plugins',
        'help': 'Scans plugins for syntax errors and attempts to fix common issues.',
        'args': [
            {'name': '--scan-only', 'action': 'store_true', 'help': 'Only scan for issues, don\'t fix'}█████╗██████╗ ███████╗███████╗██████╗ ██╗   ██╗ █████╗ ██╗
        ]   ██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗██║
    },    ██║     ██████╔╝█████╗  █████╗  ██████╔╝ ╚████╔╝ ███████║██║
    'create-dummy': {╗██╔══╝  ██╔══╝  ██╔═══╝   ╚██╔╝  ██╔══██║██║
        'description': 'Create a working dummy plugin',╗██║        ██║   ██║  ██║██║
        'function': 'cmd_create_dummy', ╚═╝╚══════╝╚══════╝╚═╝        ╚═╝   ╚═╝  ╚═╝╚═╝
        'help': 'Creates a working dummy plugin for testing.',
        'args': []
    }
}

def print_banner():
    """Print CreepyAI CLI banner"""ommands"""
    banner = """command and command in COMMANDS:
    ██████╗██████╗ ███████╗███████╗██████╗ ██╗   ██╗ █████╗ ██╗= COMMANDS[command]
    ██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗██║ription']}")
    ██║     ██████╔╝█████╗  █████╗  ██████╔╝ ╚████╔╝ ███████║██║        print("-" * (len(command) + 2 + len(cmd_info['description'])))
    ██║     ██╔══██╗██╔══╝  ██╔══╝  ██╔═══╝   ╚██╔╝  ██╔══██║██║)
    ╚██████╗██║  ██║███████╗███████╗██║        ██║   ██║  ██║██║
     ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝        ╚═╝   ╚═╝  ╚═╝╚═╝
                               Command Line Interface
    """
    print(banner)
    print(f"Project Path: {PROJECT_ROOT}\n")'):
            print(f"  {name}: {arg['help']} (optional)")
def cmd_help(command=None, **kwargs):
    """Show help for a specific command or list all commands"""name}: {arg['help']} (required)")
    if command and command in COMMANDS:
        cmd_info = COMMANDS[command]kes no arguments.")
        print(f"\n{command}: {cmd_info['description']}")
        print("-" * (len(command) + 2 + len(cmd_info['description'])))
        print(f"{cmd_info['help']}\n") 'run-plugin':
        _user")
        if cmd_info['args']:rint("  creepyai_cli.py run-plugin TwitterPlugin username --output results.json --from-date 2023-01-01")
            print("Arguments:")
            for arg in cmd_info['args']:print("  creepyai_cli.py start")
                name = arg['name']
                if name.startswith('--'):py {command}")
                    print(f"  {name}: {arg['help']} (optional)")
                else:
                    print(f"  {name}: {arg['help']} (required)")=")
        else:
            print("This command takes no arguments.")md_name, cmd_info in sorted(COMMANDS.items()):
            scription']}")
        print("\nUsage examples:")
        if command == 'run-plugin':a specific command:")
            print("  creepyai_cli.py run-plugin DummyPlugin test_user")lp COMMAND")
            print("  creepyai_cli.py run-plugin TwitterPlugin username --output results.json --from-date 2023-01-01")print("  For example: creepyai_cli.py help run-plugin")
        elif command == 'start':
            print("  creepyai_cli.py start")
        else:tart CreepyAI with default UI"""
            print(f"  creepyai_cli.py {command}")
    else:_creepyai.py")
        print("\nAvailable commands:")
        print("==================")
        gs):
        for cmd_name, cmd_info in sorted(COMMANDS.items()):
            print(f"{cmd_name:15} - {cmd_info['description']}") Tkinter UI...")
        ")
        print("\nFor detailed help on a specific command:")
        print("  creepyai_cli.py help COMMAND")
        print("  For example: creepyai_cli.py help run-plugin")

def cmd_start_app(**kwargs):
    """Start CreepyAI with default UI"""
    print("Starting CreepyAI...")t_path)
    script_path = os.path.join(SCRIPT_DIR, "run_creepyai.py")
    return run_python_script(script_path)rgs):
"
def cmd_start_tkinter(**kwargs):
    """Start CreepyAI with Tkinter UI""".py")
    print("Starting CreepyAI with Tkinter UI...")
    script_path = os.path.join(SCRIPT_DIR, "run_tkinter_ui.sh")
    return run_script(script_path)
s"""
def cmd_test_qt(**kwargs):
    """Run PyQt5 test script"""
    print("Testing PyQt5 environment...")
    script_path = os.path.join(SCRIPT_DIR, "test_qt.py")    try:
    return run_python_script(script_path)ys.path if needed
ath:
def cmd_test_plugins(**kwargs):ECT_ROOT)
    """Run plugin system test"""        
    print("Testing plugin system...")
    script_path = os.path.join(SCRIPT_DIR, "test_plugins.py")from plugins.plugins_manager import PluginsManager
    return run_python_script(script_path)
over plugins
def cmd_list_plugins(**kwargs):
    """List all available plugins"""ins = plugin_manager.discover_plugins()
    print("Discovering plugins...")
    
    # Try to import plugin managerif plugins:
    try:)
        # Add project root to sys.path if needed
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)    for plugin_id, info in sorted(plugins.items()):
            fo.get('name', plugin_id)
        # Import plugins managercription = info.get('description', 'No description available')
        from plugins.plugins_manager import PluginsManagern')
        
        # Create plugin manager and discover plugins    print(f"\n{name} (v{version})")
        plugin_manager = PluginsManager()
        plugins = plugin_manager.discover_plugins()idth=60))
        
        # Display results
        if plugins:if 'author' in info:
            print(f"\nFound {len(plugins)} plugins:")or']}")
            print("=" * 60)
            
            for plugin_id, info in sorted(plugins.items()):
                name = info.get('name', plugin_id)
                description = info.get('description', 'No description available')
                version = info.get('version', 'unknown')
                 {os.path.join(PROJECT_ROOT, 'plugins')}")
                print(f"\n{name} (v{version})")
                print("-" * len(f"{name} (v{version})"))
                print(textwrap.fill(description, width=60)) as e:
                (f"Error listing plugins: {e}")
                # Show additional info if availableCLI...")
                if 'author' in info:
                    print(f"Author: {info['author']}")to plugin CLI
                if 'website' in info:pt_path = os.path.join(SCRIPT_DIR, "run_plugin_cli.py")
                    print(f"Website: {info['website']}")script(script_path, ["--list"])
                
            return 0*kwargs):
        else:un a specific plugin"""
            print("No plugins found!")
            print(f"Plugin directory: {os.path.join(PROJECT_ROOT, 'plugins')}")
            return 1AME TARGET [options]")
                    return 1
    except Exception as e:
        print(f"Error listing plugins: {e}")gin} for target {target}...")
        print("Falling back to plugin CLI...")
        
        # Fall back to plugin CLI
        script_path = os.path.join(SCRIPT_DIR, "run_plugin_cli.py")lugin", plugin, "--target", target]
        return run_python_script(script_path, ["--list"])

def cmd_run_plugin(plugin=None, target=None, **kwargs):if kwargs.get('output'):
    """Run a specific plugin"""rgs['output']])
    if not plugin or not target:
        print("Error: Plugin name and target are required")
        print("Usage: creepyai_cli.py run-plugin PLUGIN_NAME TARGET [options]")if kwargs.get('from_date'):
        return 1, kwargs['from_date']])
        :
    print(f"Running plugin {plugin} for target {target}...")])
        
    # Build arguments for plugin CLI
    script_path = os.path.join(SCRIPT_DIR, "run_plugin_cli.py")
    args = ["--plugin", plugin, "--target", target]
    
    # Add output file if specified
    if kwargs.get('output'):
        args.extend(["--output", kwargs['output']])gs):
     and prepare environment"""
    # Add date filters if specified environment...")
    if kwargs.get('from_date'):
        args.extend(["--from-date", kwargs['from_date']])
    if kwargs.get('to_date'):    python_version = sys.version_info
        args.extend(["--to-date", kwargs['to_date']])on: {python_version.major}.{python_version.minor}.{python_version.micro}")
        or == 3 and python_version.minor < 6):
    # Add debug flagn 3.6 or newer")
    if kwargs.get('debug'):
        args.append("--debug")
        ..")
    return run_python_script(script_path, args)

def cmd_setup(**kwargs):
    """Install dependencies and prepare environment"""    "psutil", 
    print("Setting up CreepyAI environment...")
    
    # Check Python version
    python_version = sys.version_info,
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        print("Warning: CreepyAI requires Python 3.6 or newer")
    ge in requirements:
    # Install dependenciest(f"Installing {package}...")
    print("\nInstalling dependencies...")t = subprocess.run(
    requirements = [           [sys.executable, "-m", "pip", "install", package],
        "PyQt5",            capture_output=True,
        "PyQtWebEngine",        text=True
        "psutil", 
        "requests",
        "folium",led to install {package}: {result.stderr}")
        "yapsy",
        "pyyaml",installed successfully")
    ]:
    (f"Error installing dependencies: {e}")
    try:
        for package in requirements:
            print(f"Installing {package}...")ng scripts executable...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],s.listdir(SCRIPT_DIR):
                capture_output=True,e_name)
                text=True        if file_name.endswith(('.py', '.sh')) and os.path.isfile(file_path):
            )_path, 0o755)
            if result.returncode != 0:w executable")
                print(f"Warning: Failed to install {package}: {result.stderr}")pt Exception as e:
            else: {e}")
                print(f"✓ {package} installed successfully")
    except Exception as e:
        print(f"Error installing dependencies: {e}")
    
    # Make scripts executable
    print("\nMaking scripts executable...")
    try:return 0
        for file_name in os.listdir(SCRIPT_DIR):
            file_path = os.path.join(SCRIPT_DIR, file_name)
            if file_name.endswith(('.py', '.sh')) and os.path.isfile(file_path):"""
                os.chmod(file_path, 0o755)print("Compiling Qt resources...")
                print(f"✓ {file_name} is now executable")
    except Exception as e: = os.path.join(PROJECT_ROOT, 'resources', 'creepy_resources.qrc')
        print(f"Error making scripts executable: {e}")    output_file = os.path.join(PROJECT_ROOT, 'resources', 'creepy_resources_rc.py')
    
    # Compile resourcesxists
    print("\nCompiling resources...")
    cmd_compile_resources()    print(f"Error: Resource file not found: {qrc_file}")
    
    print("\nSetup complete!")
    return 0# Try to compile using compile_resources module

def cmd_compile_resources(**kwargs):oin(PROJECT_ROOT, 'scripts'))
    """Compile Qt resources"""ompile_rc
    print("Compiling Qt resources...")
        if compile_rc(qrc_file, output_file):
    qrc_file = os.path.join(PROJECT_ROOT, 'resources', 'creepy_resources.qrc') to {output_file}")
    output_file = os.path.join(PROJECT_ROOT, 'resources', 'creepy_resources_rc.py')    return 0
    
    # Check if resource file existss module")
    if not os.path.exists(qrc_file):pt Exception as e:
        print(f"Error: Resource file not found: {qrc_file}")rces module: {e}")
        return 1
    c5 directly
    # Try to compile using compile_resources module
    try:
        sys.path.insert(0, os.path.join(PROJECT_ROOT, 'scripts'))s.run(
        from compile_resources import compile_resources as compile_rc
                capture_output=True,
        if compile_rc(qrc_file, output_file):
            print(f"Resources compiled successfully to {output_file}"))
            return 0
        else:0:
            print("Failed to compile resources using compile_resources module")with pyrcc5 to {output_file}")
    except Exception as e:
        print(f"Error importing compile_resources module: {e}")
       print(f"pyrcc5 failed: {result.stderr}")
    # Try using pyrcc5 directlypt Exception as e:
    try:c5: {e}")
        print("Trying direct pyrcc5 command...")
        result = subprocess.run( compile resources")
            ['pyrcc5', '-o', output_file, qrc_file],
            capture_output=True,
            text=True
        )
        print("\nCreepyAI System Information")
        if result.returncode == 0:
            print(f"Resources compiled successfully with pyrcc5 to {output_file}")
            return 0    # System info
        else:
            print(f"pyrcc5 failed: {result.stderr}")atform.system()} {platform.release()}")
    except Exception as e:}")
        print(f"Error running pyrcc5: {e}")python_version()}")
    print(f"Python Path: {sys.executable}")
    print("Failed to compile resources")
    return 1

def cmd_info(**kwargs): 'VERSION')
    """Show system information"""
    print("\nCreepyAI System Information")
    print("=========================")        version = f.read().strip()
    epyAI Version: {version}")
    # System info
    import platformot found)")
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Platform: {platform.platform()}")
    print(f"Python Version: {platform.python_version()}")
    print(f"Python Path: {sys.executable}")
    "PyQt5", "PyQt5 UI framework"),
    # CreepyAI info
    print(f"\nCreepyAI Path: {PROJECT_ROOT}")    ("yapsy", "Plugin system"),
    version_file = os.path.join(PROJECT_ROOT, 'VERSION')g"),
    if os.path.exists(version_file):onitoring"),
        with open(version_file, 'r') as f:
            version = f.read().strip()
        print(f"CreepyAI Version: {version}")
    else:
        print("CreepyAI Version: Unknown (VERSION file not found)")
    talled ({description})")
    # Check for key dependencies   except ImportError:
    print("\nDependencies:")        print(f"✗ {module_name}: Not installed ({description})")
    dependencies = [
        ("PyQt5", "PyQt5 UI framework"), info
        ("PyQt5.QtWebEngineWidgets", "WebEngine support"),
        ("yapsy", "Plugin system"),
        ("folium", "Map rendering"),th.join(PROJECT_ROOT, 'plugins')
        ("psutil", "System monitoring"),
    ]        plugins = [f for f in os.listdir(plugins_dir) if f.endswith('.py') and not f.startswith('__')]
    (f"Found {len(plugins)} plugin files")
    for module_name, description in dependencies:lugins):
        try:        print(f"  - {plugin}")
            __import__(module_name)
            print(f"✓ {module_name}: Installed ({description})")ot found")
        except ImportError:
            print(f"✗ {module_name}: Not installed ({description})")
    
    # Plugin info
    print("\nPlugin Information:")
    try:
        plugins_dir = os.path.join(PROJECT_ROOT, 'plugins') in plugins"""
        if os.path.isdir(plugins_dir):lugin_fixer.py")
            plugins = [f for f in os.listdir(plugins_dir) if f.endswith('.py') and not f.startswith('__')]
            print(f"Found {len(plugins)} plugin files")s.path.exists(plugin_fixer):
            for plugin in sorted(plugins):        print("Plugin fixer script not found!")
                print(f"  - {plugin}")y script exists in the tools directory")
        else:
            print("Plugins directory not found")
    except Exception as e:if scan_only:
        print(f"Error accessing plugins: {e}")es...")
    ["--scan"])
    return 0

def cmd_fix_plugins(scan_only=False, **kwargs):un_python_script(plugin_fixer, ["--fix"])
    """Scan and fix issues in plugins"""
    plugin_fixer = os.path.join(SCRIPT_DIR, "plugin_fixer.py")ript(script_path, args=None):
    hon interpreter"""
    if not os.path.exists(plugin_fixer):
        print("Plugin fixer script not found!")rint(f"Error: Script not found: {script_path}")
        print("Creating plugin_fixer.py...")
        # Download or create the plugin_fixer.py script here
        return 1    cmd = [sys.executable, script_path]
    
    if scan_only:
        print("Scanning plugins for issues...")
        return run_python_script(plugin_fixer, ["--scan"])try:
    else:ect root
        print("Scanning and fixing plugins...")
        return run_python_script(plugin_fixer, ["--fix"])
HONPATH'] = f"{PROJECT_ROOT}:{python_path}" if python_path else PROJECT_ROOT
def cmd_create_dummy(**kwargs):    
    """Create a working dummy plugin"""
    plugin_fixer = os.path.join(SCRIPT_DIR, "plugin_fixer.py")
            return process.returncode
    if not os.path.exists(plugin_fixer):
        print("Plugin fixer script not found!")
        print("Please run 'creepyai fix-plugins' first")
        return 1
    cript_path, args=None):
    print("Creating dummy plugin...")un a shell script"""
    return run_python_script(plugin_fixer, ["--create-dummy"])
t(f"Error: Script not found: {script_path}")
def cmd_plugin_health(detail=False, **kwargs):
    """Check health status of plugins"""
    plugin_health = os.path.join(SCRIPT_DIR, "plugin_health.py")ke sure the script is executable
    
    if not os.path.exists(plugin_health):
        print("Plugin health script not found!")
        print("Please ensure the plugin_health.py script exists in the tools directory")
        return 1cmd.extend(args)
    
    args = []
    if detail:
        args.append("--detail")ss.run(cmd)
        
    print("Checking plugin health status...")tion as e:
    return run_python_script(plugin_health, args)        print(f"Error running script: {e}")

def run_python_script(script_path, args=None):
    """Run a Python script with the current Python interpreter"""
    if not os.path.exists(script_path):
        print(f"Error: Script not found: {script_path}")parse.ArgumentParser(
        return 1    description="CreepyAI Command Line Interface",
        he help ourselves
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)ent
        dd_argument('command', nargs='?', default='help',
    try:lp='Command to run')
        # Set PYTHONPATH to include project root              
        env = os.environ.copy()d debug flag
        python_path = env.get('PYTHONPATH', '')'--debug', action='store_true',
        env['PYTHONPATH'] = f"{PROJECT_ROOT}:{python_path}" if python_path else PROJECT_ROOTbug logging')
        
        # Run the script args first
        process = subprocess.run(cmd, env=env)gs()
        return process.returncode
    except Exception as e:    # Set logging level based on debug flag
        print(f"Error running script: {e}"):
        return 1ogging.DEBUG)

def run_script(script_path, args=None):
    """Run a shell script"""
    if not os.path.exists(script_path):ain():
        print(f"Error: Script not found: {script_path}")"""Main entry point"""
        return 1nts
    
    # Make sure the script is executable
    os.chmod(script_path, 0o755)
    
    cmd = [script_path]
    if args:
        cmd.extend(args)valid command
        
    try:d}'")
        # Run the script    cmd_help()
        process = subprocess.run(cmd)
        return process.returncode
    except Exception as e:
        print(f"Error running script: {e}")cmd_info = COMMANDS[command]
        return 1
    # Parse remaining arguments based on command definition
def parse_args():_args = {}
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="CreepyAI Command Line Interface",d-specific arguments
        add_help=False  # We'll handle the help ourselvesrse.ArgumentParser(prog=f"creepyai_cli.py {command}")
    )    
    mand-specific arguments
    # Add command argument_args = []
    parser.add_argument('command', nargs='?', default='help',    for arg_info in cmd_info['args']:
                      help='Command to run')
                      '--'):
    # Add debug flag
    parser.add_argument('--debug', action='store_true',d_parser.add_argument(
                      help='Enable debug logging')    name, 
                                      help=arg_info.get('help', ''),
    # Parse only the known args firstfault=arg_info.get('default', None)
    args, remaining = parser.parse_known_args()
            else:
    # Set logging level based on debug flag
    if args.debug:ional_args.append(name)
        logging.getLogger().setLevel(logging.DEBUG)            cmd_parser.add_argument(
    ,
    return args, remaining

def main():        )
    """Main entry point"""
    # Parse initial argumentsific arguments
    args, remaining = parse_args()remaining)
    command = args.commands)
    
    # Show banneronal arguments
    print_banner()
    and_args and command_args[arg] is None:
    # Check if it's a valid commandgument '{arg}'")
    if command not in COMMANDS:{' '.join(positional_args)}")
        print(f"Error: Unknown command '{command}'")eturn 1
        cmd_help()
        return 1
    
    # Get command info
    cmd_info = COMMANDS[command]func_name]
    
    # Parse remaining arguments based on command definition
    command_args = {}rgs['debug'] = args.debug
    
    if cmd_info['args']:
        # Create parser for command-specific arguments
        cmd_parser = argparse.ArgumentParser(prog=f"creepyai_cli.py {command}")
        print(f"Error: Function {func_name} not found for command {command}")
        # Add command-specific arguments
        positional_args = []
        for arg_info in cmd_info['args']:
            name = arg_info['name']
            if name.startswith('--'):                # Optional argument                cmd_parser.add_argument(                    name,                     help=arg_info.get('help', ''),                    default=arg_info.get('default', None)                )            else:                # Positional argument                positional_args.append(name)                cmd_parser.add_argument(                    name,                    help=arg_info.get('help', ''),                    nargs=arg_info.get('nargs', None)                )                # Parse command-specific arguments        cmd_args = cmd_parser.parse_args(remaining)        command_args = vars(cmd_args)        
        # Check for required positional arguments
        for arg in positional_args:
            if arg in command_args and command_args[arg] is None:
                print(f"Error: Missing required argument '{arg}'")
                print(f"Usage: creepyai_cli.py {command} {' '.join(positional_args)}")
                return 1
    
    # Get function from command info
    func_name = cmd_info['function']
    if func_name in globals():
        func = globals()[func_name]
        
        # Add debug flag from main args
        command_args['debug'] = args.debug
        
        # Run the command function
        return func(**command_args)
    else:
        print(f"Error: Function {func_name} not found for command {command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
