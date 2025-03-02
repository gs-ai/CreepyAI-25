# CREEPYAI-25 - OSINT INTELLIGENCE TOOL


CreepyAI is an advanced open-source intelligence (OSINT) gathering and analysis tool with an intuitive graphical user interface. It helps security researchers, investigators, and analysts collect and analyze publicly available information efficiently.

## Features

- **Multi-source Intelligence**: Gather data from social media, public records, professional networks, news sources, and image repositories
- **User-friendly GUI**: Intuitive tabbed interface for different OSINT operations
- **Project Management**: Create and manage investigation projects to keep related searches organized
- **Data Visualization**: Generate network graphs, timelines, heatmaps and relationship diagrams
- **Comprehensive Reporting**: Create executive summaries or detailed technical reports
- **Plugin System**: Extend functionality through custom plugins
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites

- Python 3.6+
- pip package manager
- Tkinter (usually included with Python)
- Pillow library

### Quick Install

bash
```markdown
# Clone the repository
git clone https://github.com/gs-ai/CreepyAI-25
cd CreepyAI

# Install dependencies
pip install -r requirements.txt
```

### Running CreepyAI

```bash
# Launch the GUI
python gui_preview.py
```

## Usage

### Basic Search

1. Launch CreepyAI
2. Go to the "Search" tab
3. Enter target information (name, username, etc.)
4. Select desired data sources
5. Click "Start Search"

### Working with Projects

Projects help organize related searches:

1. Go to "Projects" menu
2. Select "Create New Project" 
3. Name your investigation
4. All subsequent searches will be saved in this project

### Data Analysis

1. Navigate to the "Analysis" tab
2. Select visualization type (Network Graph, Timeline, etc.)
3. Choose data sources to include
4. Generate visualizations

### Reporting

1. Go to the "Reports" tab
2. Select report type
3. Configure options (include visualizations, raw data, etc.)
4. Generate report

## Screenshots

![Dashboard](resources/screenshot_dashboard.png) *(Create screenshots later)*

![Search Interface](resources/screenshot_search.png) *(Create screenshots later)*

![Analysis View](resources/screenshot_analysis.png) *(Create screenshots later)*

## Configuration

CreepyAI stores configuration in `~/.config/creepyai/config.json`. You can modify this file directly or through the Preferences dialog in the application.

### API Keys

Some data sources require API keys:
- Go to "File" > "Preferences"
- Select the "API Keys" tab
- Enter your keys for various services

## Development

### Project Structure

```
CreepyAI/
├── creepyai_gui.py     # Main GUI implementation
├── gui_preview.py      # GUI launcher
├── resources/          # Images and other resources
├── plugins/            # Plugin directory
└── docs/               # Documentation
```

### Creating Plugins

Plugins allow you to extend CreepyAI's functionality:

1. Create a Python file in the `plugins` directory
2. Implement the required plugin interface
3. Register your plugin in the system
4. See `docs/plugin_development.md` for detailed instructions

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

CreepyAI is intended for educational and legitimate research purposes only. Users are responsible for complying with applicable laws and regulations while using this tool. The developers assume no liability for misuse of this software.

### Special Thanks 
~The OG





