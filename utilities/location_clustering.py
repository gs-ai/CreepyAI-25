#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import logging
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from collections import defaultdict
import datetime

logger = logging.getLogger('CreepyAI.LocationClustering')

class LocationClusterer:
    """Class for clustering location data to find patterns and significant places"""
    
    def __init__(self, epsilon=0.05, min_samples=5, min_locations=10):
        """
        Initialize the location clusterer
        
        Args:
            epsilon: Maximum distance (in km) between points to be considered in the same cluster
            min_samples: Minimum number of points to form a cluster
            min_locations: Minimum number of locations needed for clustering to be meaningful
        """
        self.epsilon = epsilon  # in kilometers
        self.min_samples = min_samples
        self.min_locations = min_locations
        self.clusters = []
        self.noise_points = []
    
    def cluster_locations(self, locations):
        """
        Cluster the given locations
        
        Args:
            locations: List of Location objects
            
        Returns:
            List of clusters, where each cluster is a list of Location objects
        """
        if len(locations) < self.min_locations:
            logger.warning(f"Not enough locations for clustering. Need at least {self.min_locations}, got {len(locations)}")
            self.clusters = []
            self.noise_points = locations
            return [], locations
        
        # Extract coordinates
        coords = np.array([[loc.latitude, loc.longitude] for loc in locations])
        
        # Convert epsilon from km to radians for DBSCAN
        kms_per_radian = 6371.0  # Earth's radius in km
        epsilon_radians = self.epsilon / kms_per_radian
        
        # Perform clustering
        try:
            db = DBSCAN(
                eps=epsilon_radians,
                min_samples=self.min_samples,
                algorithm='ball_tree',
                metric='haversine'
            ).fit(np.radians(coords))
            
            # Get the cluster labels
            cluster_labels = db.labels_
            
            # Process clusters
            num_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
            logger.info(f"Found {num_clusters} clusters in {len(locations)} locations")
            
            # Group locations by cluster
            clusters = defaultdict(list)
            for i, label in enumerate(cluster_labels):
                clusters[label].append(locations[i])
            
            # Extract clusters and noise points
            self.clusters = [clusters[label] for label in set(cluster_labels) if label != -1]
            self.noise_points = clusters.get(-1, [])
            
            return self.clusters, self.noise_points
            
        except Exception as e:
            logger.error(f"Error during clustering: {e}")
            self.clusters = []
            self.noise_points = locations
            return [], locations
    
    def analyze_clusters(self):
        """
        Analyze clusters to extract insights
        
        Returns:
            Dictionary with analysis results
        """
        if not self.clusters:
            return {"error": "No clusters available for analysis"}
        
        analysis = {
            "num_clusters": len(self.clusters),
            "total_clustered_locations": sum(len(cluster) for cluster in self.clusters),
            "total_noise_points": len(self.noise_points),
            "clusters": []
        }
        
        for i, cluster in enumerate(self.clusters):
            # Calculate cluster center
            lat_sum = sum(loc.latitude for loc in cluster)
            lon_sum = sum(loc.longitude for loc in cluster)
            center = (lat_sum / len(cluster), lon_sum / len(cluster))
            
            # Calculate time range for this cluster
            times = [loc.datetime for loc in cluster if loc.datetime]
            time_range = (min(times), max(times)) if times else (None, None)
            
            # Count locations by source
            sources = {}
            for loc in cluster:
                sources[loc.source] = sources.get(loc.source, 0) + 1
            
            # Find most common source
            most_common_source = max(sources.items(), key=lambda x: x[1])[0] if sources else None
            
            cluster_info = {
                "id": i,
                "size": len(cluster),
                "center": center,
                "radius": self._calculate_cluster_radius(cluster, center),
                "time_range": time_range,
                "sources": sources,
                "most_common_source": most_common_source,
                "possible_significance": self._determine_significance(cluster, time_range)
            }
            
            analysis["clusters"].append(cluster_info)
        
        return analysis
    
    def _calculate_cluster_radius(self, cluster, center):
        """Calculate the radius of a cluster in meters"""
        if not cluster:
            return 0
            
        # Calculate distances from center to all points
        distances = [
            great_circle(center, (loc.latitude, loc.longitude)).meters
            for loc in cluster
        ]
        
        # Return the maximum distance as the radius
        return max(distances) if distances else 0
    
    def _determine_significance(self, cluster, time_range):
        """Try to determine the significance of a cluster based on patterns"""
        if not cluster or len(cluster) < 5:
            return "Unknown"
            
        if not time_range[0] or not time_range[1]:
            return "Unknown"
            
        # Count occurrences by time of day
        times_of_day = {
            "morning": 0,  # 5am-12pm
            "afternoon": 0,  # 12pm-5pm
            "evening": 0,  # 5pm-10pm
            "night": 0  # 10pm-5am
        }
        
        for loc in cluster:
            if not loc.datetime:
                continue
                
            hour = loc.datetime.hour
            
            if 5 <= hour < 12:
                times_of_day["morning"] += 1
            elif 12 <= hour < 17:
                times_of_day["afternoon"] += 1
            elif 17 <= hour < 22:
                times_of_day["evening"] += 1
            else:
                times_of_day["night"] += 1
        
        # Count occurrences by day of week
        days_of_week = defaultdict(int)
        for loc in cluster:
            if not loc.datetime:
                continue
                
            day_name = loc.datetime.strftime("%A")  # Monday, Tuesday, etc.
            days_of_week[day_name] += 1
        
        # Determine most common time of day and day of week
        most_common_time = max(times_of_day.items(), key=lambda x: x[1])[0] if any(times_of_day.values()) else None
        most_common_day = max(days_of_week.items(), key=lambda x: x[1])[0] if days_of_week else None
        
        # Try to determine significance based on patterns
        if most_common_time == "morning" and sum(days_of_week.get(day, 0) for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]) > sum(days_of_week.get(day, 0) for day in ["Saturday", "Sunday"]):
            return "Likely workplace or regular morning location"
        
        if most_common_time == "night" and sum(times_of_day.values()) > 10:
            return "Likely residence"
        
        if most_common_day in ["Saturday", "Sunday"] and most_common_time in ["afternoon", "evening"]:
            return "Possible weekend activity location"
        
        if len(cluster) > 20:
            return "Frequently visited location"
        
        return "Regular visited location"
