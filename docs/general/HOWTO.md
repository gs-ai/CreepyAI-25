# CreepyAI - Complete User Guide

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Basic Usage](#basic-usage)
- [Working with Projects](#working-with-projects)
- [Using Plugins](#using-plugins)
- [Data Analysis](#data-analysis)
- [Exporting Data](#exporting-data)
- [Troubleshooting](#troubleshooting)
- [GUI Interface](#gui-interface)

## Installation

### Prerequisites

- Python 3.6+
- pip package manager
- Internet connection
- No API keys are required for the bundled tools

### Quick Install

## Using Plugins

### Offline GeoIP Lookups

CreepyAI includes an offline GeoIP plugin that reads a CSV database shipped with the application. The file lives in `~/.creepyai/data/GeoIPPlugin/geoip_database.csv` by default and can be replaced with any dataset that follows the `ip_start, ip_end, latitude, longitude, city, region, country` column format. A starter dataset is copied automatically so you can test lookups without configuring API keys or creating external accounts.
