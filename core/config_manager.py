import os
import json
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration and settings (without API keys)."""
    
    def __init__(self, config_path=None):
        self.config_path = config_path or os.path.join(os.path.expanduser("~"), ".creepyai", "config.json")
        self.config = {}
        self._load_config()
        
    def _load_config(self):
        """Load configuration from file or create default."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info("Configuration loaded successfully")
            else:
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                self.config = self._get_default_config()
                self._save_config()
                logger.info("Created default configuration")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            self.config = self._get_default_config()
            
    def _save_config(self):
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
    
    def _get_default_config(self):
        """Return default configuration (no API keys)."""
        return {
            "settings": {
                "max_results": 100,
                "use_cache": True,
                "cache_ttl": 86400,
                "proxy": None,
                "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            },
            "plugins": {
                "twitter": {"enabled": True, "use_scraping": True},
                "facebook": {"enabled": True, "use_scraping": True},
                "instagram": {"enabled": True, "use_scraping": True},
                "local_files": {"enabled": True},
                "email_analysis": {"enabled": True}
                # Additional plugins will be detected automatically
            },
            "scraping": {
                "timeout": 30,
                "retry_count": 3,
                "delay_between_requests": 5,
                "respect_robots_txt": True,
                "use_stealth_mode": False
            },
            "privacy": {
                "anonymize_results": False,
                "store_raw_data": True
            }
        }
        
    def get_setting(self, setting, default=None):
        """Get a specific setting value."""
        return self.config.get("settings", {}).get(setting, default)
        
    def set_setting(self, setting, value):
        """Set a specific setting value."""
        if "settings" not in self.config:
            self.config["settings"] = {}
        self.config["settings"][setting] = value
        self._save_config()
        
    def get_plugin_setting(self, plugin_name, setting, default=None):
        """Get a plugin-specific setting."""
        if plugin_name not in self.config.get("plugins", {}):
            return default
        return self.config["plugins"][plugin_name].get(setting, default)
        
    def set_plugin_setting(self, plugin_name, setting, value):
        """Set a plugin-specific setting."""
        if "plugins" not in self.config:
            self.config["plugins"] = {}
        if plugin_name not in self.config["plugins"]:
            self.config["plugins"][plugin_name] = {}
        self.config["plugins"][plugin_name][setting] = value
        self._save_config()
        
    def get_scraping_setting(self, setting, default=None):
        """Get a scraping-specific setting."""
        return self.config.get("scraping", {}).get(setting, default)
        
    def set_scraping_setting(self, setting, value):
        """Set a scraping-specific setting."""
        if "scraping" not in self.config:
            self.config["scraping"] = {}
        self.config["scraping"][setting] = value
        self._save_config()
    
    def get(self, key, default=None):
        """Get a configuration value with an optional default"""
        try:
            if key in self.config:
                return self.config[key]
            return default
        except Exception as e:
            logger.error(f"Error retrieving config key '{key}': {str(e)}")
            return default
    
    def set(self, key, value):
        """Set a configuration value"""
        try:
            self.config[key] = value
            return True
        except Exception as e:
            logger.error(f"Error setting config key '{key}': {str(e)}")
            return False
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
