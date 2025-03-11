"""
Web scraping utility for CreepyAI.
"""
import logging
import importlib
from typing import Dict, Any, Optional

logger = logging.getLogger('creepyai.utilities.webscraping')

class WebScrapingUtility:
    """Utility for web scraping operations."""
    
    def __init__(self):
        """Initialize web scraping utility."""
        self.initialized = False
        self.available_backends = {}
        
        # Try to import common scraping libraries
        self._import_backends()
    
    def _import_backends(self) -> None:
        """Import available web scraping backends."""
        backends = {
            "requests": "requests",
            "selenium": "selenium",
            "beautifulsoup": "bs4",
            "scrapy": "scrapy"
        }
        
        for name, module in backends.items():
            try:
                importlib.import_module(module)
                self.available_backends[name] = True
                logger.info(f"Web scraping backend '{name}' is available")
            except ImportError:
                self.available_backends[name] = False
                logger.debug(f"Web scraping backend '{name}' is not available")
        
        self.initialized = True
    
    def get_available_backends(self) -> Dict[str, bool]:
        """Get available web scraping backends.
        
        Returns:
            Dict mapping backend names to availability status
        """
        return self.available_backends
    
    def fetch_url(self, url: str, backend: str = "requests", **kwargs) -> Optional[str]:
        """Fetch content from URL.
        
        Args:
            url: URL to fetch
            backend: Backend to use ('requests', 'selenium', etc.)
            **kwargs: Additional arguments for the backend
            
        Returns:
            Content as string or None if failed
        """
        if backend == "requests" and self.available_backends.get("requests"):
            try:
                import requests
                response = requests.get(url, **kwargs)
                if response.status_code == 200:
                    return response.text
                logger.warning(f"Failed to fetch URL, status code: {response.status_code}")
            except Exception as e:
                logger.error(f"Error fetching URL with requests: {e}")
        else:
            logger.error(f"Backend '{backend}' is not available or not supported")
        
        return None
    
    def parse_html(self, html: str) -> Any:
        """Parse HTML content.
        
        Args:
            html: HTML content to parse
            
        Returns:
            Parsed HTML or None if failed
        """
        if self.available_backends.get("beautifulsoup"):
            try:
                from bs4 import BeautifulSoup
                return BeautifulSoup(html, 'html.parser')
            except Exception as e:
                logger.error(f"Error parsing HTML: {e}")
        else:
            logger.error("BeautifulSoup is not available for HTML parsing")
        
        return None

# Create a singleton instance
web_scraping_utility = WebScrapingUtility()
