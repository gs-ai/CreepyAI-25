import logging
import re
import time
import random
from bs4 import BeautifulSoup
import sys
import os

# Fix import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from creepy.models.ScrapingPlugin import ScrapingPlugin
from creepy.models.Location import Location
from datetime import datetime

logger = logging.getLogger(__name__)

class InstagramPlugin(ScrapingPlugin):
    """
    Instagram plugin that uses web scraping instead of Instagram API.
    """
    
    def __init__(self):
        ScrapingPlugin.__init__(self)
        self.name = "Instagram"
        self.description = "Collects location data from Instagram profiles and posts"
        
        # Patterns for extracting location data
        self.search_patterns = {
            'coordinates': r'[-+]?\d{1,2}\.\d+,\s*[-+]?\d{1,3}\.\d+',  # Basic lat,long pattern
            'location_meta': ['place:location', 'instapp:location', 'location'],
            'post_location': r'location\/([^\/]+)',
            'profile_location': r'(?:location|based in|lives in):\s*([^,\n]+)',
        }
        
        # Maximum number of posts to scrape
        self.max_posts = 50
    
    def search_locations(self, target, search_params=None):
        """
        Search for locations in Instagram profiles and posts.
        
        Args:
            target (dict): Target information (name, username, etc.)
            search_params (dict): Additional search parameters
            
        Returns:
            list: List of locations found
        """
        if not self.is_configured():
            logger.warning("Instagram plugin is not properly configured")
            return []
        
        locations = []
        username = target.get('username', '')
        if not username:
            logger.warning("No username provided for Instagram plugin")
            return []
            
        # Clean the username
        username = self._clean_username(username)
        
        # Generate profile URL
        profile_urls = self._extract_profile_urls(username, 'instagram')
        
        # Try to scrape each possible profile URL
        for profile_url in profile_urls:
            try:
                # Check cache first
                cached_content = self._get_cached_result(profile_url)
                
                if cached_content:
                    logger.info(f"Using cached Instagram profile for {username}")
                    profile_html = cached_content['content']
                else:
                    logger.info(f"Scraping Instagram profile for {username}")
                    profile_html = self.web_scraper.fetch_page(profile_url)
                    
                    if profile_html:
                        # Cache the result
                        if hasattr(target, 'id'):
                            self._cache_result(profile_url, profile_html, target.id)
                        else:
                            self._cache_result(profile_url, profile_html)
                
                if not profile_html:
                    logger.warning(f"Failed to fetch Instagram profile for {username}")
                    continue
                
                # Extract locations from the profile
                profile_locations = self._extract_locations_from_profile(profile_html, username)
                locations.extend(profile_locations)
                
                # Extract post URLs
                post_urls = self._extract_post_urls(profile_html, username)
                
                # Limit the number of posts to analyze
                post_limit = min(len(post_urls), self.max_posts)
                
                for i, post_url in enumerate(post_urls[:post_limit]):
                    # Add random delay between requests
                    if i > 0:
                        delay = random.uniform(1.5, 5.0)
                        time.sleep(delay)
                    
                    # Check cache first
                    cached_content = self._get_cached_result(post_url)
                    
                    if cached_content:
                        post_html = cached_content['content']
                    else:
                        post_html = self.web_scraper.fetch_page(post_url)
                        
                        if post_html:
                            # Cache the result
                            if hasattr(target, 'id'):
                                self._cache_result(post_url, post_html, target.id)
                            else:
                                self._cache_result(post_url, post_html)
                    
                    if post_html:
                        # Extract locations from the post
                        post_locations = self._extract_locations_from_post(post_html, post_url)
                        locations.extend(post_locations)
            
            except Exception as e:
                logger.error(f"Error scraping Instagram profile {username}: {str(e)}")
        
        return locations
    
    def _extract_locations_from_profile(self, html_content, username):
        """Extract location information from Instagram profile HTML."""
        locations = []
        
        if not html_content:
            return locations
            
        try:
            # First use the general location extraction
            general_locations = self.web_scraper.extract_locations(html_content)
            locations.extend(general_locations)
            
            # Parse with BeautifulSoup for more specific Instagram structures
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for location in meta tags
            meta_tags = soup.find_all('meta')
            for tag in meta_tags:
                if (tag.get('name') in self.search_patterns['location_meta'] or 
                    tag.get('property') in self.search_patterns['location_meta']):
                    content = tag.get('content', '')
                    if content and content.lower() not in ['worldwide', 'global', 'earth']:
                        # Create a location without coordinates until geocoded
                        location = Location()
                        location.latitude = 0
                        location.longitude = 0
                        location.time = datetime.now()
                        location.context = f"Instagram profile location: {content}"
                        location.accuracy = 'Low - Text-based location'
                        location.source = f"Instagram profile @{username}"
                        locations.append(location)
            
            # Look for location in the profile information
            profile_location_pattern = self.search_patterns['profile_location']
            matches = re.finditer(profile_location_pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match.group(1).lower() not in ['worldwide', 'global', 'earth']:
                    location = Location()
                    location.latitude = 0
                    location.longitude = 0
                    location.time = datetime.now()
                    location.context = f"Instagram profile mentions location: {match.group(1)}"
                    location.accuracy = 'Low - Text-based location'
                    location.source = f"Instagram profile @{username}"
                    locations.append(location)
            
        except Exception as e:
            logger.error(f"Error extracting locations from Instagram profile: {str(e)}")
            
        return locations
    
    def _extract_post_urls(self, html_content, username):
        """Extract post URLs from the profile page."""
        post_urls = []
        
        if not html_content:
            return post_urls
            
        try:
            # Common patterns for post URLs
            post_pattern = re.compile(r'https?://(?:www\.)?instagram\.com/p/[a-zA-Z0-9_-]+')
            
            # Find all matches
            matches = post_pattern.finditer(html_content)
            for match in matches:
                post_url = match.group(0)
                if post_url not in post_urls:
                    post_urls.append(post_url)
            
        except Exception as e:
            logger.error(f"Error extracting post URLs: {str(e)}")
            
        return post_urls
    
    def _extract_locations_from_post(self, html_content, post_url):
        """Extract location information from an Instagram post."""
        locations = []
        
        if not html_content:
            return locations
            
        try:
            # First use the general location extraction
            general_locations = self.web_scraper.extract_locations(html_content)
            
            # Add source information to each location
            for location in general_locations:
                if isinstance(location, dict):
                    location['source'] = f"Instagram post: {post_url}"
                    location['context'] = f"Found in post: {post_url}"
                    
                    # Convert dict to Location object
                    loc_obj = Location()
                    loc_obj.latitude = location.get('latitude', 0)
                    loc_obj.longitude = location.get('longitude', 0)
                    loc_obj.time = datetime.now()
                    loc_obj.context = location.get('context', '')
                    loc_obj.accuracy = location.get('accuracy', 'medium')
                    loc_obj.source = location.get('source', '')
                    locations.append(loc_obj)
                else:
                    location.source = f"Instagram post: {post_url}"
                    location.context = f"Found in post: {post_url}"
                    locations.append(location)
            
            # Parse with BeautifulSoup for more Instagram-specific structures
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for location tags
            location_links = soup.find_all('a', href=re.compile(r'/explore/locations/'))
            for link in location_links:
                location_text = link.get_text().strip()
                if location_text and location_text.lower() not in ['worldwide', 'global', 'earth']:
                    location = Location()
                    location.latitude = 0
                    location.longitude = 0
                    location.time = datetime.now()
                    location.context = f"Instagram post tagged location: {location_text}"
                    location.accuracy = 'Low - Text-based location'
                    location.source = f"Instagram post: {post_url}"
                    locations.append(location)
            
            # Look for location in post text
            post_text = ""
            caption_divs = soup.find_all('div', {'class': ['caption', 'C4VMK']})
            for div in caption_divs:
                if div.get_text():
                    post_text += div.get_text() + " "
            
            # Find location mentions in post text
            location_pattern = r'(?:at|in|from|📍|📌) ([A-Z][a-zA-Z\s\-\']+(?:,\s*[A-Z][a-zA-Z\s\-\']+)?)'
            matches = re.finditer(location_pattern, post_text)
            for match in matches:
                location_text = match.group(1)
                if location_text.lower() not in ['worldwide', 'global', 'earth']:
                    location = Location()
                    location.latitude = 0
                    location.longitude = 0
                    location.time = datetime.now()
                    location.context = f"Instagram post mentions location: {location_text}"
                    location.accuracy = 'Low - Text-based location'
                    location.source = f"Instagram post: {post_url}"
                    locations.append(location)
                    
        except Exception as e:
            logger.error(f"Error extracting locations from Instagram post: {str(e)}")
            
        return locations
