# CreepyAI - OSINT Geolocation Tool

CreepyAI is a geolocation intelligence tool that collects and analyzes social media and online data to track and visualize user locations without relying on APIs.

## Features

- Social media data collection through web scraping (Twitter, Facebook, Instagram, etc.)
- Local file analysis for geolocation data (photos, KML, GPX, etc.)
- Geolocation mapping and visualization
- Timeline analysis of user movement patterns
- Export capabilities (KML, HTML, CSV)
- Extensible plugin system

## Installation

### Requirements

- Python 3.9 or higher
- PyQt5
- Internet connection for web scraping

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/CreepyAI.git
   cd CreepyAI
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv creepyai25ENV
   source creepyai25ENV/bin/activate  # On Windows: creepyai25ENV\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python CreepyMain.py
   ```

## Configuration

Application settings can be configured through the GUI or by editing the configuration file located at:
- Linux/macOS: `~/.creepyai/config.json`
- Windows: `%USERPROFILE%\.creepyai\config.json`

## Usage

### Creating a Project

1. Launch CreepyAI
2. Click "New Project"
3. Enter project details and target information
4. Select data sources to use (web scraping, local files)
5. Start the collection process

### Analyzing Data

- Use the map view to visualize locations
- Filter data by date, source, or location
- Generate reports through the export options

### Working with Local Files

CreepyAI can extract location data from various file types:
- Photos with EXIF data
- KML/KMZ files from Google Maps
- GPX files from GPS devices
- JSON files with location data
- HTML and other content with embedded coordinates

## Web Scraping Considerations

CreepyAI uses web scraping instead of APIs for data collection. Please be aware of the following:

1. **Rate Limiting**: Web scraping operations are throttled to respect website limits
2. **Legal Considerations**: Only scrape publicly available data and follow website terms of service
3. **Accuracy**: Scraped data may be less accurate than API data
4. **Stealth Mode**: Configure the scraping settings to avoid detection

## Plugin Development

See [plugin_development_guide.md](plugin_development_guide.md) for details on creating custom plugins.

## License

This project is licensed under the terms specified in the LICENSE file.





