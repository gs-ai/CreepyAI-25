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
   python main
   ```

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

### Command Line Usage

The application supports command-line operation:

