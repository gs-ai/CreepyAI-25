#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import datetime
import logging
from sklearn.cluster import DBSCAN
from utilities.GeneralUtilities import calcDistance

logger = logging.getLogger(__name__)

class LocationClusterer:
    """Utility class to cluster location data based on proximity"""
    
    def __init__(self, eps_meters=100, min_samples=3):
        """
        Initialize clusterer with parameters
        
        Args:
            eps_meters: Maximum distance (in meters) between two points to be considered in the same cluster
            min_samples: Minimum number of points to form a core cluster
        """
        self.eps_meters = eps_meters
        self.min_samples = min_samples
        
    def cluster_locations(self, locations):
        """
        Cluster locations based on geographic proximity
        
        Args:
            locations: List of Location objects with latitude and longitude attributes
            
        Returns:
            List of clusters, where each cluster is a list of Location objects
        """
        if not locations:
            return []
            
        try:
            # Convert locations to numpy array for DBSCAN
            coords = np.array([[loc.latitude, loc.longitude] for loc in locations])
            
            # Use DBSCAN with haversine distance metric
            db = DBSCAN(
                eps=self.eps_meters / 111320.0,  # Approximate conversion from meters to degrees
                min_samples=self.min_samples,
                metric=self._haversine_distance
            ).fit(coords)
            
            # Get cluster labels (-1 = noise)
            labels = db.labels_
            
            # Group locations by cluster label
            clusters = {}
            for idx, label in enumerate(labels):
                if label == -1:  # Skip noise points
                    continue
                    
                if label not in clusters:
                    clusters[label] = []
                    
                clusters[label].append(locations[idx])
                
            return list(clusters.values())
            
        except Exception as e:
            logger.error(f"Error clustering locations: {str(e)}")
            return []
            
    def _haversine_distance(self, p1, p2):
        """Haversine distance between two points in latitude/longitude"""
        lat1, lon1 = p1
        lat2, lon2 = p2
        return calcDistance(lat1, lon1, lat2, lon2) / 1000.0  # Convert meters to km
        
    def get_cluster_stats(self, cluster):
        """
        Get statistics for a cluster of locations
        
        Args:
            cluster: List of Location objects in the cluster
            
        Returns:
            Dictionary with cluster statistics
        """
        if not cluster:
            return {}
            
        try:
            # Calculate center point (centroid)
            lat_sum = sum(loc.latitude for loc in cluster)
            lon_sum = sum(loc.longitude for loc in cluster)
            center_lat = lat_sum / len(cluster)
            center_lon = lon_sum / len(cluster)
            
            # Calculate temporal range
            dates = [loc.datetime for loc in cluster]
            start_date = min(dates)
            end_date = max(dates)
            duration = end_date - start_date
            
            # Calculate radius (maximum distance from center)
            max_distance = max(calcDistance(center_lat, center_lon, loc.latitude, loc.longitude) 
                              for loc in cluster)
            
            # Most frequent plugin source
            plugins = [loc.plugin for loc in cluster]
            plugin_counts = {}
            for p in plugins:
                plugin_counts[p] = plugin_counts.get(p, 0) + 1
            main_source = max(plugin_counts.items(), key=lambda x: x[1])[0]
            
            return {
                'center': (center_lat, center_lon),
                'start_date': start_date,
                'end_date': end_date,
                'duration': duration,
                'locations': len(cluster),
                'radius': max_distance,
                'main_source': main_source
            }
        except Exception as e:
            logger.error(f"Error calculating cluster statistics: {str(e)}")
            return {}
