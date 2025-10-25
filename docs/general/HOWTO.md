# CreepyAI-25 - Complete User Guide

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

CreepyAI-25 relies on offline GeoIP lookups using a CSV dataset that **you** provide. Place the file at `~/.creepyai/data/GeoIPPlugin/geoip_database.csv` (or update the plugin configuration) and ensure it follows the `ip_start, ip_end, latitude, longitude, city, region, country` column format. This keeps the workflow credential-free while respecting licensing constraints on third-party datasets.
