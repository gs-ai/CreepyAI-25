
# CreepyAI - OSINT Assistant

CreepyAI is an open-source OSINT (Open Source Intelligence) assistant designed to help researchers, analysts, and cybersecurity professionals gather and analyze public information effectively.

## Features

- **Multi-platform Search**: Query multiple sources simultaneously
- **Credential-free Operation**: Work entirely with offline data exports and open data sources—no API keys or logins required
- **Data Visualization**: Visualize relationships between data points
- **Project Management**: Save and organize your research
- **Plugin System**: Extend functionality with custom plugins
- **Reporting**: Generate comprehensive reports

## Quick Start

### Installation

1. **Using the setup script (recommended)**:
   ```bash
   chmod +x setup_creepyai.sh
   ./setup_creepyai.sh
   ```

2. **Manual installation**:
   ```bash
   # With Conda
   conda env create -f environment.yml
   conda activate creepyai
   
   # OR with virtualenv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Running the Application

Launch using the provided shell script:
```bash
chmod +x launch_macos.sh
./launch_macos.sh
```

On Windows:
```bash
launch_windows.bat
```

## Usage

1. Start by creating a new project or opening an existing one
2. Configure your search parameters in the Search tab
3. Execute the search and review results
4. Analyze data using the Analysis tab
5. Generate reports as needed

## Configuration

CreepyAI uses a configuration file located at `~/.config/creepyai/config.json`. You can modify settings through the application's Preferences dialog or by directly editing this file.

## Plugins

CreepyAI supports plugins to extend its functionality. Plugins are stored in `~/.config/creepyai/plugins/` by default.

### Offline Data Imports

Each plugin now watches a dedicated ingest directory so you no longer need to browse for exports manually. Drop your ZIP archives or extracted folders into the matching subdirectory and enable the plugin's checkbox.

- **Linux**: `~/.local/share/creepyai/imports/<plugin_slug>`
- **macOS**: `~/Library/Application Support/CreepyAI/imports/<plugin_slug>`
- **Windows**: `%APPDATA%\CreepyAI\imports\<plugin_slug>`

The slug corresponds to the plugin name in lowercase with spaces replaced by underscores (for example, `Instagram` → `instagram`, `Email Analysis` → `email_analysis`). The configuration dialog displays the resolved path for each plugin as a reminder.

### Creating Plugins

To create a plugin:

1. Create a new Python file in the plugins directory
2. Inherit from the `BasePlugin` class
3. Implement the required methods
4. See `plugin_base.py` for more details

## Troubleshooting

### PyQt5 Issues

If you encounter Qt/PyQt5 errors:

1. **Run the diagnostic tool**:
   ```bash
   python launch_creepyai.py --diagnose-qt
   ```

2. **For Conda environments with PyQt5 problems**:
   ```bash
   chmod +x fix_pyqt_conda.sh
   ./fix_pyqt_conda.sh
   ```

3. **Common issues**:
   - **Multiple Qt installations**: Use a clean virtual environment
   - **Missing plugins**: Run the fix script or reinstall PyQt5 and PyQtWebEngine
   - **macOS specific**: Clear any conflicting Qt environment variables

### Building from Source

Use the build script:
```bash
python build_creepyai.py --package
```

Options:
- `--package`: Create executable package
- `--docs`: Build documentation
- `--clean`: Clean build artifacts

## Development

### Project Structure

- `gui/`: User interface implementations
- `plugins/`: Plugin system for data sources
- `resources/`: Application resources
- `docs/`: Documentation

### Building Documentation

```bash
python build_creepyai.py --docs
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is intended for legal OSINT research purposes only. Users are responsible for compliance with applicable laws and regulations. The authors are not responsible for any misuse of this software.
