<<<<<<< HEAD
# CreepyAI - Geolocation Intelligence Tool

CreepyAI is an open-source intelligence (OSINT) application that allows for geolocation data gathering and visualization from various sources including social media platforms and local files. This tool helps investigators, researchers, and security professionals to analyze location patterns from publicly available data.

![CreepyAI Screenshot](docs/images/screenshot.png)

## Features

- Unified interface for multiple data sources (Twitter, Instagram, Facebook, etc.)
- Interactive mapping visualization
- Location data filtering and analysis
- Project-based workflow for organized investigations
- Export capabilities in multiple formats (KML, CSV, JSON, HTML)
- Mock data generation for training and demonstrations

## Installation

### Requirements

- Python 3.6+ (3.9 recommended)
- Git
- Conda (recommended for environment management)
- Internet connection for downloading dependencies

### Setting Up with Conda

1. **Clone the repository**:
   ```bash
   git clone https://github.com/creepyai/creepyai.git
   cd creepyai
   ```

2. **Create and activate a Conda environment**:
   ```bash
   conda create -n creepyai25ENV python=3.9
   conda activate creepyai25ENV
   ```

3. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install optional dependencies** (recommended for full functionality):
   ```bash
   pip install simplekml folium tweepy flickrapi geopy openpyxl
   ```

## Configuration

### First Run Setup

1. **Launch CreepyAI for the first time**:
   ```bash
   python3 CreepyMain.py
   ```

2. **Default directories and configuration files** will be created in:
   - `~/.creepyai/` (Linux/Mac)
   - `%USERPROFILE%\.creepyai\` (Windows)

### API Keys (Optional)

To use social media plugins, you'll need to configure API credentials for each service:

1. Navigate to "Tools" → "Plugin Configuration" in the application
2. Select the plugin you wish to configure
3. Follow the wizard steps to set up API credentials

## Usage

### Starting a New Project

1. **Launch CreepyAI**:
   ```bash
   python3 CreepyMain.py
   ```

2. **Create a New Project**:
   - Click "New Project" button or select File → New Project
   - Enter project details (name, description, location)
   - Select targets to investigate

### Gathering Location Data

1. **Select Data Sources**:
   - In the New Project wizard, select which plugins to use
   - Configure search parameters for each source

2. **Run the Search**:
   - Click "Analyze Now" in the final wizard step, or
   - Click the "Analyze" button in the toolbar after project creation

3. **Review Data Collection Progress**:
   - A progress dialog will show status for each selected plugin
   - Collection time varies based on amount of data and API rate limits

### Working with Results

1. **View Locations on the Map**:
   - Points appear on the map representing found locations
   - Click on points to view details (time, source, context)

2. **Filter Data**:
   - Use "Filter by Date" to show locations within a time range
   - Use "Filter by Location" to focus on specific geographic areas

3. **Export Results**:
   - Select File → Export and choose your preferred format
   - Options include KML (Google Earth), CSV, JSON, and HTML reports

### Using Mock Data

If you need to test or demonstrate without real data:

1. **Create a new project**
2. **Choose the "Mock Social" plugin**
3. **Enter any username as the search term**
4. The plugin will generate realistic-looking location patterns for demonstration

## Plugins

CreepyAI supports the following data sources:

- **Twitter**: Extracts location data from geotagged tweets
- **Instagram**: Collects location data from posts and stories
- **Facebook**: Extracts location information from posts, photos, and check-ins
- **Foursquare**: Retrieves check-in data
- **Flickr**: Extracts location data from geotagged photos
- **Local Files**: Extracts location metadata from local photos and files
- **Mock Social**: Generates synthetic location data for testing

## Troubleshooting

### Missing Plugins

If plugins fail to load:
=======
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




>>>>>>> gs-ai-patch-1

