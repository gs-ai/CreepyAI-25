# CreepyAI Tools

This directory contains various utility scripts and tools for the CreepyAI project.

## Command Line Interface

The main entry point for all CreepyAI functionality is the command line interface:

```bash
# Run the CLI tool
python tools/creepyai_cli.py

# Get help on available commands
python tools/creepyai_cli.py help

# Run a specific command
python tools/creepyai_cli.py start
python tools/creepyai_cli.py run-plugin TwitterPlugin username
```

For convenience, you can also use the shortcut script in the project root:

```bash
# Make sure it's executable first
chmod +x creepyai
./creepyai help
```

## Available Commands

- `start` - Start CreepyAI with default UI
- `start-tkinter` - Start CreepyAI with Tkinter UI
- `test-qt` - Test PyQt5 environment
- `test-plugins` - Test plugins system
- `list-plugins` - List all available plugins
- `run-plugin` - Run a specific plugin
- `setup` - Install dependencies and prepare environment
- `compile-resources` - Compile Qt resources
- `info` - Show system information and environment details
- `help` - Show help information

## Individual Tools

### Testing Tools
- `test_qt.py` - Tests the PyQt5 environment and displays a test window
- `test_plugins.py` - Tests the plugin system, discovery, and execution

### Launchers
- `run_creepyai.py` - Main Python launcher with PyQt5 WebEngine compatibility
- `run_creepyai.sh` - Shell launcher for the main application
- `run_tkinter_ui.sh` - Launcher for the Tkinter UI variant

### Utility Scripts
- `run_plugin_cli.py` - Command-line interface for running individual plugins
- `commands.txt` - Common commands reference

## Usage

Most tools can be run directly from the command line:

```bash
# Test PyQt5 environment
python tools/test_qt.py

# Test plugin system
python tools/test_plugins.py

# Run the main application
./tools/run_creepyai.sh

# Run with Tkinter UI
./tools/run_tkinter_ui.sh

# Use the plugin CLI
python tools/run_plugin_cli.py --list
python tools/run_plugin_cli.py --plugin DummyPlugin --target "test"
```

Make sure to run all scripts from the project root directory for proper path resolution.
