#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import configparser
import logging
from yapsy.IPlugin import IPlugin

logger = logging.getLogger(__name__)

class InputPlugin(IPlugin):
    """
    Base class for all input plugins used by CreepyAI.
    
    Each plugin must implement the following methods:
    - activate()
    - deactivate()
    - searchForTargets(search_term)
    - returnLocations(target, search_params)
    - readConfiguration(section)
    - saveConfiguration(config_dict)
    - isConfigured()
    """

    def __init__(self):
        self.options = {}
        self.error_count = 0
        self.hasWizard = False
        IPlugin.__init__(self)

    def activate(self):
        """
        Called when the plugin is activated.
        """
        logger.debug(f"Plugin {self.__class__.__name__} activated")
        IPlugin.activate(self)
        return

    def deactivate(self):
        """
        Called when the plugin is deactivated.
        """
        logger.debug(f"Plugin {self.__class__.__name__} deactivated")
        IPlugin.deactivate(self)
        return

    def searchForTargets(self, search_term):
        """
        Search for targets based on a search term.
        
        Args:
            search_term: The term to search for
            
        Returns:
            List of targets found
        """
        logger.warning(f"searchForTargets not implemented in {self.__class__.__name__}")
        return []

    def returnLocations(self, target, search_params):
        """
        Return locations for a specific target.
        
        Args:
            target: Target to find locations for
            search_params: Parameters to control the search
            
        Returns:
            List of locations found
        """
        logger.warning(f"returnLocations not implemented in {self.__class__.__name__}")
        return []

    def readConfiguration(self, section):
        """
        Read configuration for this plugin.
        
        Args:
            section: Configuration section to read
            
        Returns:
            Tuple containing success status and configuration dictionary
        """
        try:
            config = configparser.ConfigParser()
            config_path = self.getConfigurationFilePath()
            if not os.path.exists(config_path):
                return (False, None)
            config.read(config_path)
            if section not in config.sections():
                return (False, None)
            return (True, dict(config[section]))
        except Exception as e:
            logger.error(f"Error reading configuration for plugin {self.__class__.__name__}: {str(e)}")
            return (False, None)

    def saveConfiguration(self, config_dict):
        """
        Save configuration for this plugin.
        
        Args:
            config_dict: Dictionary containing configuration settings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            config = configparser.ConfigParser()
            config_path = self.getConfigurationFilePath()
            
            # Read existing config if it exists
            if os.path.exists(config_path):
                config.read(config_path)
            
            # Update config with new values
            for section, options in config_dict.items():
                if section not in config:
                    config[section] = {}
                for key, value in options.items():
                    config[section][key] = value
            
            # Save config file
            with open(config_path, 'w') as configfile:
                config.write(configfile)
            
            logger.info(f"Configuration saved for plugin {self.__class__.__name__}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration for plugin {self.__class__.__name__}: {str(e)}")
            self.error_count += 1
            return False

    def isConfigured(self):
        """
        Check if the plugin is properly configured.
        
        Returns:
            Tuple containing status and message
        """
        logger.warning(f"isConfigured not implemented in {self.__class__.__name__}")
        return (False, "Method not implemented")

    def getLabelForKey(self, key):
        """
        Get a human-readable label for a configuration key.
        
        Args:
            key: Configuration key
            
        Returns:
            Human-readable label
        """
        # Default implementation: replace underscores with spaces and capitalize
        label = key.replace('_', ' ')
        return label.capitalize()

    def getConfigurationFilePath(self):
        """
        Get the path to the configuration file for this plugin.
        
        Returns:
            Path to the configuration file
        """
        plugin_name = self.__class__.__name__
        return os.path.join(os.getcwd(), 'plugins', f'{plugin_name}.conf')

    def runConfigWizard(self):
        """
        Run configuration wizard for this plugin.
        
        Returns:
            True if wizard completed successfully, False otherwise
        """
        logger.warning(f"runConfigWizard not implemented in {self.__class__.__name__}")
        return False
