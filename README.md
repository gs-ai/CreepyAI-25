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

