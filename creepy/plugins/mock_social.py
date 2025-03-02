#!/usr/bin/python
# -*- coding: utf-8 -*-
from models.InputPlugin import InputPlugin
import os
import datetime
import random
import logging
import json
import math
from geopy.distance import geodesic

# set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MockSocialPlugin(InputPlugin):
    name = "mock_social"
    
    def __init__(self):
        InputPlugin.__init__(self)
        self.description = "Generate realistic social media data for demonstrations"
        self.searchOffline = True
        self.hasWizard = False
        
    def activate(self):
        logger.info("MockSocialPlugin activated")
        
    def deactivate(self):
        logger.info("MockSocialPlugin deactivated")
    
    def isConfigured(self):
        return (True, "Ready to generate social data")
        
    def _generate_random_location(self, base_lat, base_lon, radius_km=50):
        """Generate a random location within radius_km of the base coordinates"""
        # Earth's radius in km
        R = 6371.0
        
        # Convert radius from km to radians
        radius_rad = radius_km / R
        
        # Random distance within the radius
        u = random.random()
        v = random.random()
        
        # Calculate random point
        w = radius_rad * math.sqrt(u)
        t = 2 * math.pi * v
        
        # Adjust for latitude and longitude
        x = w * math.cos(t)
        y = w * math.sin(t)
        
        # Adjust for Earth's curvature
        lat = base_lat + y * (180 / math.pi)
        lon = base_lon + x * (180 / math.pi) / math.cos(base_lat * math.pi / 180)
        
        return (lat, lon)
        
    def _generate_mock_data(self, username, count=10):
        """Generate realistic social media data"""
        locations = []
        
        # Use major cities and popular locations
        cities = [
            {"name": "New York", "lat": 40.7128, "lon": -74.0060, "places": ["Central Park", "Times Square", "Brooklyn Bridge", "Empire State Building", "MoMA"]},
            {"name": "London", "lat": 51.5074, "lon": -0.1278, "places": ["Hyde Park", "Tower Bridge", "Covent Garden", "British Museum", "Shoreditch"]},
            {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503, "places": ["Shibuya Crossing", "Tokyo Tower", "Shinjuku Gyoen", "Akihabara", "Ginza"]},
            {"name": "Paris", "lat": 48.8566, "lon": 2.3522, "places": ["Eiffel Tower", "Louvre Museum", "Montmartre", "Seine River", "Le Marais"]},
            {"name": "San Francisco", "lat": 37.7749, "lon": -122.4194, "places": ["Golden Gate Park", "Fisherman's Wharf", "Mission District", "Alcatraz", "Chinatown"]}
        ]
        
        # Social media activities and caption templates
        activities = [
            {"type": "Photo", "templates": [
                "Amazing view at {place}! #travel",
                "Enjoying my time at {place} #vacation",
                "Beautiful day at {place} ✨",
                "Check out this spot at {place}! #photography"
            ]},
            {"type": "Check-in", "templates": [
                "Just arrived at {place}",
                "Having coffee at {place}",
                "Working from {place} today",
                "Meeting friends at {place}"
            ]},
            {"type": "Review", "templates": [
                "Great experience at {place} - highly recommend!",
                "The atmosphere at {place} is amazing",
                "Visited {place} - 4/5 stars",
                "Service at {place} could be better"
            ]}
        ]
        
        # Create more realistic time patterns
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=365)
        
        # Generate dates with realistic patterns (more posts on weekends, holidays)
        dates = []
        current_date = start_date
        while current_date <= end_date:
            # Higher probability on weekends
            if current_date.weekday() >= 5:  # Weekend
                probability = 0.35
            else:
                probability = 0.15
                
            if random.random() < probability:
                # Add random time of day (more posts during certain hours)
                hour = random.choices(range(24), weights=[1,1,1,1,1,2,3,5,7,6,5,8,10,7,5,6,8,10,9,7,5,4,2,1])[0]
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                post_date = current_date.replace(hour=hour, minute=minute, second=second)
                dates.append(post_date)
            
            current_date += datetime.timedelta(days=1)
        
        # Sort dates and select 'count' number of them
        dates.sort()
        if len(dates) > count:
            dates = random.sample(dates, count)
        
        # Create posts for each date
        for post_date in dates:
            # Choose a city with higher probability for nearby posts
            if locations and random.random() < 0.7:
                # Use the same city as the last post
                last_city_index = next((i for i, city in enumerate(cities) 
                                       if city["name"] in locations[-1]["shortName"]), None)
                if last_city_index is not None:
                    city = cities[last_city_index]
                else:
                    city = random.choice(cities)
            else:
                city = random.choice(cities)
            
            # Choose a place in the city
            place = random.choice(city["places"])
            
            # Generate coordinates near the specific place
            lat, lon = self._generate_random_location(city["lat"], city["lon"], 5)
            
            # Choose activity type and template
            activity = random.choice(activities)
            template = random.choice(activity["templates"])
            
            # Create content
            content = template.format(place=place)
            location_name = f"{place}, {city['name']}"
            
            # Create infowindow HTML
            infowindow = f"""<div class="social-post">
                <strong>{activity["type"]}</strong>
                <p>{content}</p>
                <div class="post-meta">
                    <span class="location">{location_name}</span>
                    <span class="date">{post_date.strftime('%b %d, %Y at %H:%M')}</span>
                </div>
            </div>"""
            
            locations.append({
                "plugin": self.name,
                "lat": lat,
                "lon": lon,
                "date": post_date,
                "context": f"{username} {activity['type'].lower()}ed at {location_name}",
                "infowindow": infowindow,
                "shortName": location_name
            })
            
        return sorted(locations, key=lambda x: x["date"])
    
    def searchForTargets(self, search_term):
        """Return realistic user profiles based on search term"""
        # Generate a consistent user profile based on the search term
        username = search_term.lower().replace(" ", "_")
        name_parts = search_term.split()
        
        if len(name_parts) > 1:
            first_name = name_parts[0].capitalize()
            last_name = name_parts[-1].capitalize()
        else:
            first_name = search_term.capitalize()
            last_name = "Smith"  # Default last name
            
        full_name = f"{first_name} {last_name}"
        
        return [{
            'targetUsername': username,
            'targetUserid': f"user_{hash(username) % 10000000}",
            'targetFullname': full_name,
            'targetPicture': 'default.png',
            'pluginName': self.name
        }]
    
    def returnLocations(self, target, search_params):
        """Return location data for the target"""
        # Determine number of locations to generate
        count = 20  # Default
        if search_params and 'location_count' in search_params:
            try:
                count = int(search_params['location_count'])
                count = min(max(count, 5), 100)  # Limit between 5 and 100
            except ValueError:
                logger.warning(f"Invalid location_count value: {search_params['location_count']}")
                
        logger.info(f"Generating {count} mock locations for {target['targetUsername']}")
        return self._generate_mock_data(target['targetUsername'], count)
        
    def getLabelForKey(self, key):
        """Return user-friendly labels for configuration keys"""
        if key == "location_count":
            return "Number of locations to generate (5-100)"
        return key
