#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Data Analysis Tool for CreepyAI
Analyzes location data for patterns and insights
"""

import os
import sys
import argparse
import logging
import sqlite3
import json
import csv
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict, Counter

# Add parent directory to path so we can import plugins
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(SCRIPT_DIR)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("data_analysis")

class LocationAnalyzer:
    """Analyzes location data to extract patterns and insights"""
    
    def __init__(self, db_path: str = None):
        """
        Initialize the analyzer with a database connection
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.df = None
        
        if db_path:
            self.connect_db(db_path)
            
    def connect_db(self, db_path: str) -> bool:
        """
        Connect to the SQLite database
        
        Args:
            db_path: Path to the SQLite database file
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row
            return True
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return False
            
    def load_data_from_db(self, plugin_name: Optional[str] = None, 
                         target_id: Optional[str] = None) -> bool:
        """
        Load location data from the database into a pandas DataFrame
        
        Args:
            plugin_name: Optional filter by plugin name
            target_id: Optional filter by target ID
            
        Returns:
            True if data loaded successfully, False otherwise
        """
        if not self.conn:
            logger.error("No database connection")
            return False
            
        try:
            # Build query based on filters
            query = 'SELECT * FROM locations WHERE 1=1'
            params = []
            
            if plugin_name:
                query += ' AND plugin_name = ?'
                params.append(plugin_name)
                
            if target_id:
                query += ' AND target_id = ?'
                params.append(target_id)
                
            # Load data into pandas DataFrame
            self.df = pd.read_sql_query(query, self.conn, params=params)
            
            # Convert timestamp strings to datetime objects
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], errors='coerce')
            
            logger.info(f"Loaded {len(self.df)} location records")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data from database: {e}")
            return False
            
    def load_data_from_json(self, json_file: str) -> bool:
        """
        Load location data from a JSON file
        
        Args:
            json_file: Path to JSON file containing location data
            
        Returns:
            True if data loaded successfully, False otherwise
        """
        try:
            # Load data from JSON file
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Convert to DataFrame
            self.df = pd.DataFrame(data)
            
            # Convert timestamp strings to datetime objects
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], errors='coerce')
            
            logger.info(f"Loaded {len(self.df)} location records from JSON file")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data from JSON: {e}")
            return False
            
    def load_data_from_csv(self, csv_file: str) -> bool:
        """
        Load location data from a CSV file
        
        Args:
            csv_file: Path to CSV file containing location data
            
        Returns:
            True if data loaded successfully, False otherwise
        """
        try:
            # Load data from CSV file
            self.df = pd.read_csv(csv_file)
            
            # Convert timestamp strings to datetime objects
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], errors='coerce')
            
            logger.info(f"Loaded {len(self.df)} location records from CSV file")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data from CSV: {e}")
            return False
    
    def analyze_time_patterns(self) -> Dict[str, Any]:
        """
        Analyze time patterns in the data
        
        Returns:
            Dictionary of time pattern statistics
        """
        if self.df is None or len(self.df) == 0:
            return {}
            
        try:
            # Extract date components
            self.df['date'] = self.df['timestamp'].dt.date
            self.df['hour'] = self.df['timestamp'].dt.hour
            self.df['day_of_week'] = self.df['timestamp'].dt.dayofweek
            self.df['month'] = self.df['timestamp'].dt.month
            self.df['year'] = self.df['timestamp'].dt.year
            
            # Calculate statistics
            stats = {
                'date_range': {
                    'start': self.df['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S'),
                    'end': self.df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S'),
                    'days': (self.df['timestamp'].max() - self.df['timestamp'].min()).days
                },
                'count_by_hour': self.df.groupby('hour').size().to_dict(),
                'count_by_day_of_week': self.df.groupby('day_of_week').size().to_dict(),
                'count_by_month': self.df.groupby('month').size().to_dict(),
                'most_active_day': self.df.groupby('date').size().idxmax().strftime('%Y-%m-%d'),
                'records_by_source': self.df.groupby('source').size().to_dict(),
            }
            
            # Calculate hourly activity patterns (weekday vs weekend)
            weekday_mask = self.df['day_of_week'] < 5  # Monday=0, Sunday=6
            weekend_mask = ~weekday_mask
            
            weekday_hours = self.df[weekday_mask].groupby('hour').size()
            weekend_hours = self.df[weekend_mask].groupby('hour').size()
            
            stats['weekday_hourly_pattern'] = weekday_hours.to_dict()
            stats['weekend_hourly_pattern'] = weekend_hours.to_dict()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error analyzing time patterns: {e}")
            return {}
    
    def find_frequent_locations(self, radius_meters: float = 100.0, 
                              min_visits: int = 3) -> List[Dict[str, Any]]:
        """
        Find frequently visited locations
        
        Args:
            radius_meters: Radius in meters to consider as the same location
            min_visits: Minimum number of visits to consider a location as frequent
            
        Returns:
            List of frequent location clusters
        """
        if self.df is None or len(self.df) == 0:
            return []
            
        try:
            # Convert DataFrame to list of dicts for easier processing
            locations = self.df[['latitude', 'longitude', 'timestamp', 'source', 'context']].to_dict('records')
            
            # Group points into clusters based on distance
            clusters = []
            for loc in locations:
                # Check if point belongs to an existing cluster
                added_to_cluster = False
                for cluster in clusters:
                    # Calculate distance to cluster center
                    center = cluster['center']
                    distance = self.haversine_distance(
                        center['latitude'], center['longitude'],
                        loc['latitude'], loc['longitude']
                    )
                    
                    if distance <= radius_meters:
                        # Add to existing cluster
                        cluster['points'].append(loc)
                        
                        # Update center (average of all points)
                        n = len(cluster['points'])
                        center['latitude'] = ((n-1) * center['latitude'] + loc['latitude']) / n
                        center['longitude'] = ((n-1) * center['longitude'] + loc['longitude']) / n
                        
                        added_to_cluster = True
                        break
                        
                if not added_to_cluster:
                    # Create new cluster
                    clusters.append({
                        'center': {
                            'latitude': loc['latitude'],
                            'longitude': loc['longitude']
                        },
                        'points': [loc]
                    })
            
            # Filter clusters by minimum visits
            frequent_clusters = [c for c in clusters if len(c['points']) >= min_visits]
            
            # Sort clusters by number of visits (descending)
            frequent_clusters.sort(key=lambda c: len(c['points']), reverse=True)
            
            # Enrich cluster information
            for cluster in frequent_clusters:
                points = cluster['points']
                sources = Counter([p['source'] for p in points])
                times = [p['timestamp'] for p in points]
                
                # Add metadata to cluster
                cluster['visit_count'] = len(points)
                cluster['sources'] = dict(sources)
                cluster['first_visit'] = min(times).strftime('%Y-%m-%d %H:%M:%S')
                cluster['last_visit'] = max(times).strftime('%Y-%m-%d %H:%M:%