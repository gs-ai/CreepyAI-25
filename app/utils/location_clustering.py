    #!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any, Optional
import math

try:
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available, advanced clustering will be disabled")

logger = logging.getLogger('creepyai.utilities.location_clustering')

class LocationCluster:
    """Represents a cluster of geographic locations with common attributes"""
    
    def __init__(self, locations=None, center=None, radius=None, start_time=None, end_time=None):
        self.locations = locations or []
        self.center = center  # (latitude, longitude)
        self.radius = radius  # in meters
        self.start_time = start_time
        self.end_time = end_time
        self.metadata = {}
    
    def add_location(self, location):
        """Add a location to the cluster"""
        self.locations.append(location)
        self.recalculate()
    
    def recalculate(self):
        """Recalculate cluster properties based on contained locations"""
        if not self.locations:
            return
        
        # Calculate center as mean of lat/lng
        lats = [loc['latitude'] for loc in self.locations]
        lngs = [loc['longitude'] for loc in self.locations]
        self.center = (sum(lats) / len(lats), sum(lngs) / len(lngs))
        
        # Calculate radius as max distance from center to any point
        max_distance = 0
        for loc in self.locations:
            dist = haversine_distance(self.center[0], self.center[1], 
                                     loc['latitude'], loc['longitude'])
            max_distance = max(max_distance, dist)
        
        self.radius = max_distance
        
        # Calculate time span
        times = [loc.get('timestamp') for loc in self.locations 
                if loc.get('timestamp') is not None]
        if times:
            self.start_time = min(times)
            self.end_time = max(times)
    
    def merge(self, other_cluster):
        """Merge another cluster into this one"""
        self.locations.extend(other_cluster.locations)
        self.recalculate()
    
    def to_dict(self):
        """Convert cluster to dictionary representation"""
        return {
            'center': self.center,
            'radius': self.radius,
            'count': len(self.locations),
            'start_time': self.start_time,
            'end_time': self.end_time,
            'metadata': self.metadata,
            'locations': self.locations
        }

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371000  # Radius of earth in meters
    return c * r

def cluster_locations_dbscan(locations, eps=100, min_samples=5):
    """
    Cluster locations using DBSCAN algorithm
    
    Args:
        locations: List of location dictionaries with 'latitude' and 'longitude'
        eps: Maximum distance (meters) between points in the same cluster
        min_samples: Minimum number of points to form a cluster
    
    Returns:
        List of LocationCluster objects
    """
    if not SKLEARN_AVAILABLE:
        logger.warning("scikit-learn not available, falling back to simple clustering")
        return cluster_locations_simple(locations)
    
    if not locations:
        return []
    
    # Extract coordinates
    coords = np.array([[loc['latitude'], loc['longitude']] for loc in locations])
    
    # Scale to improve clustering - approximately normalize for lat/lng differences
    scaler = StandardScaler()
    coords_scaled = scaler.fit_transform(coords)
    
    # Run DBSCAN clustering
    db = DBSCAN(eps=eps/110000, min_samples=min_samples, algorithm='ball_tree', metric='euclidean')
    labels = db.fit_predict(coords)
    
    # Create clusters from results
    clusters = []
    unique_labels = set(labels)
    
    for label in unique_labels:
        # Skip noise points (label == -1)
        if label == -1:
            continue
            
        # Get all points in this cluster
        cluster_indices = np.where(labels == label)[0]
        cluster_locations = [locations[i] for i in cluster_indices]
        
        # Create cluster
        cluster = LocationCluster(locations=cluster_locations)
        cluster.recalculate()
        clusters.append(cluster)
    
    return clusters

def cluster_locations_simple(locations, distance_threshold=100):
    """
    Simple clustering algorithm for locations based on distance
    
    Args:
        locations: List of location dictionaries with 'latitude' and 'longitude'
        distance_threshold: Maximum distance (meters) between points in the same cluster
    
    Returns:
        List of LocationCluster objects
    """
    if not locations:
        return []
    
    clusters = []
    processed = [False] * len(locations)
    
    for i, location in enumerate(locations):
        if processed[i]:
            continue
        
        # Create a new cluster with this location
        cluster_locations = [location]
        processed[i] = True
        
        # Find all nearby locations
        for j, other_location in enumerate(locations):
            if processed[j] or i == j:
                continue
            
            dist = haversine_distance(
                location['latitude'], location['longitude'],
                other_location['latitude'], other_location['longitude']
            )
            
            if dist <= distance_threshold:
                cluster_locations.append(other_location)
                processed[j] = True
        
        cluster = LocationCluster(locations=cluster_locations)
        cluster.recalculate()
        clusters.append(cluster)
    
    return clusters

def generate_location_heatmap(locations, resolution=100):
    """
    Generate a heatmap of locations
    
    Args:
        locations: List of location dictionaries with 'latitude' and 'longitude'
        resolution: Resolution of the heatmap grid
        
    Returns:
        Dictionary with heatmap data
    """
    if not locations:
        return {'grid': [], 'bounds': None}
    
    # Find bounds
    min_lat = min(loc['latitude'] for loc in locations)
    max_lat = max(loc['latitude'] for loc in locations)
    min_lng = min(loc['longitude'] for loc in locations)
    max_lng = max(loc['longitude'] for loc in locations)
    
    # Add padding
    lat_padding = (max_lat - min_lat) * 0.1 or 0.01
    lng_padding = (max_lng - min_lng) * 0.1 or 0.01
    
    min_lat -= lat_padding
    max_lat += lat_padding
    min_lng -= lng_padding
    max_lng += lng_padding
    
    # Create grid
    lat_step = (max_lat - min_lat) / resolution
    lng_step = (max_lng - min_lng) / resolution
    
    grid = [[0 for _ in range(resolution)] for _ in range(resolution)]
    
    # Count locations in each grid cell
    for loc in locations:
        lat_idx = min(resolution - 1, max(0, int((loc['latitude'] - min_lat) / lat_step)))
        lng_idx = min(resolution - 1, max(0, int((loc['longitude'] - min_lng) / lng_step)))
        grid[lat_idx][lng_idx] += 1
    
    return {
        'grid': grid,
        'bounds': {
            'min_lat': min_lat,
            'max_lat': max_lat,
            'min_lng': min_lng,
            'max_lng': max_lng,
        }
    }

def identify_significant_locations(clusters, min_duration=timedelta(hours=1), min_visits=3):
    """
    Identify significant locations from clusters
    
    Args:
        clusters: List of LocationCluster objects
        min_duration: Minimum duration to consider a location significant
        min_visits: Minimum number of visits to consider a location significant
        
    Returns:
        List of significant LocationCluster objects
    """
    significant = []
    
    for cluster in clusters:
        # Skip clusters without time information
        if not cluster.start_time or not cluster.end_time:
            continue
        
        # Calculate total duration
        duration = cluster.end_time - cluster.start_time
        
        # Count visits (separated by at least 6 hours)
        visits = 1
        last_time = cluster.locations[0].get('timestamp')
        
        for loc in sorted(cluster.locations, key=lambda x: x.get('timestamp', 0)):
            time = loc.get('timestamp')
            if time and last_time and (time - last_time).total_seconds() > 6 * 3600:
                visits += 1
                last_time = time
        
        if duration >= min_duration or visits >= min_visits:
            cluster.metadata['visits'] = visits
            cluster.metadata['duration'] = duration
            cluster.metadata['significant'] = True
            significant.append(cluster)
    
    return significant
