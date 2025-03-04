#!/usr/bin/python
# -*- coding: utf-8 -*-
from yapsy.IPlugin import IPlugin
from configobj import ConfigObj
import logging
import os
<<<<<<< HEAD
import json
import traceback
from creepy.utilities import GeneralUtilities

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Use os.path.expanduser instead of GeneralUtilities.getUserHome
log_path = os.path.join(os.path.expanduser("~"), '.creepyai', 'logs', 'creepy_main.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
fh = logging.FileHandler(log_path)
=======
from utilities import GeneralUtilities

#set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(GeneralUtilities.getUserHome(),'creepy_main.log'))
>>>>>>> gs-ai-patch-1
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

class InputPlugin(IPlugin):
<<<<<<< HEAD
    """Base class for CreepyAI input plugins"""

    def __init__(self):
        self.name = "base_plugin"
        self.description = "Base plugin class"
        self.version = "1.0.0"
        self.error_count = 0

    def activate(self):
        """Called when plugin is activated"""
        logger.info(f"Activating plugin: {self.name}")
        pass
        
    def deactivate(self):
        """Called when plugin is deactivated"""
        logger.info(f"Deactivating plugin: {self.name}")
        pass
    
    def searchForTargets(self, search_term):
        """Search for targets using the given term"""
        logger.debug(f"Base searchForTargets called with term: {search_term}")
        return 'dummyUser'
    
    def loadConfiguration(self):
        """Load plugin configuration"""
        logger.debug(f"Loading configuration for {self.name}")
        pass
    
    def isConfigured(self):
        """
        Check if the plugin is properly configured
        
        Returns:
            tuple: (is_configured, error_message) where is_configured is a boolean
                  and error_message is a string explaining any issues
        """
        return (True, "")
    
    def returnLocations(self, target, search_params):
        """
        Return locations for a target based on search parameters
        
        Args:
            target: Target information
            search_params: Search parameters
            
        Returns:
            list: List of location objects
        """
        pass
    
    def returnPersonalInformation(self, search_params):
        """
        Return personal information based on search parameters
        
        Args:
            search_params: Search parameters
            
        Returns:
            dict: Personal information data
        """
        pass
        
    def getConfigObj(self):
        """
        Get the configuration object for the plugin
        
        Returns:
            ConfigObj: Configuration object
        """
        try:
            config_filename = self.name + ".conf"
            config_file = os.path.join(os.getcwd(), 'plugins', self.name, config_filename)
            config = ConfigObj(infile=config_file)
            config.create_empty = False
            return config
        except Exception as e:
            logger.error(f"Error loading config for {self.name}: {str(e)}")
            self.error_count += 1
            return ConfigObj()
    
    def readConfiguration(self, category):
        """
        Read configuration for a specific category
        
        Args:
            category: Category name
            
        Returns:
            tuple: (config, options) where config is the full ConfigObj and 
                  options are the specific category settings
        """
=======

    def __init__(self):
        pass
    def activate(self):
        pass
        
    def deactivate(self):
        pass
    
    def searchForTargets(self, search_term):
        return 'dummyUser'
    
    def loadConfiguration(self):
        pass
    
    def isConfigured(self):
        return (True,"")
    
    def returnLocations(self, target, search_params):
        pass
    
    def returnPersonalInformation(self, search_params):
        pass
    def getConfigObj(self):    
        config_filename = self.name + ".conf"
        config_file = os.path.join(os.getcwd(), 'plugins', self.name, config_filename)
        config = ConfigObj(infile=config_file)
        config.create_empty = False
        return config
    
    def readConfiguration(self, category):
>>>>>>> gs-ai-patch-1
        config, options = self.getConfigObj(), None
        try:
            options = config[category]
        except Exception as err:
            logger.error(f'Could not load the {category} for the {self.name} plugin.')
            logger.exception(err)
<<<<<<< HEAD
            self.error_count += 1
        return config, options

    def saveConfiguration(self, new_config):
        """
        Save plugin configuration
        
        Args:
            new_config: New configuration dictionary
        """
        config_filename = self.name + '.conf'
        config_file = os.path.join(os.getcwd(), 'plugins', self.name, config_filename)
        
        try:
            config = ConfigObj(infile=config_file)
            config.create_empty = False
            
            if 'string_options' in new_config:
                config['string_options'] = new_config['string_options']
            
            if 'boolean_options' in new_config:
                config['boolean_options'] = new_config['boolean_options']
                
            config.write()
            logger.info(f"Configuration for {self.name} saved successfully")
            
        except Exception as err:
            logger.error(f'Could not save the configuration for the {self.name} plugin.')
            logger.exception(err)
            self.error_count += 1
            raise

    def loadSearchConfigurationParameters(self):
        """
        Load search configuration parameters
        
        Returns:
            dict: Search parameters or None if not available
        """
        try:
            config_filename = self.name + '.conf'
            config_file = os.path.join(os.getcwd(), 'plugins', self.name, config_filename)
            config = ConfigObj(infile=config_file)
            config.create_empty = False
            return config.get('search_options', {})
        except Exception as err:
            logger.error(f'Could not load the search configuration parameters for the {self.name} plugin.')
            logger.exception(err)
            self.error_count += 1
            return None
            
    def getLabelForKey(self, key):
        """
        Get human-readable label for a configuration key
        
        Args:
            key: Configuration key
            
        Returns:
            str: Human-readable label
        """
        # Try to load labels file if exists
        try:
            labels_filename = self.name + ".labels"
            labels_file = os.path.join(os.getcwd(), 'plugins', self.name, labels_filename)
            
            if os.path.exists(labels_file):
                with open(labels_file, 'r') as f:
                    labels = json.load(f)
                    if key in labels:
                        return labels[key]
        except Exception as e:
            logger.warning(f"Error loading labels for {self.name}: {str(e)}")
            
        # Default behavior: return the key itself
        return key
        
    def log_error(self, error_message, context=None):
        """
        Log an error with the plugin
        
        Args:
            error_message: Error message 
            context: Additional context information
        """
        self.error_count += 1
        error_info = {
            'plugin': self.name,
            'error': error_message,
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        logger.error(f"Plugin error: {json.dumps(error_info)}")
=======
        return config, options

    def saveConfiguration(self, new_config):
        config_filename = self.name+'.conf'
        config_file = os.path.join(os.getcwd(),'plugins',self.name, config_filename)
        config = ConfigObj(infile=config_file)
        config.create_empty=False
        try:
            config['string_options'] = new_config['string_options']
            config['boolean_options'] = new_config['boolean_options']
            config.write()
        except Exception as err:
            logger.error('Could not save the configuration for the '+self.name+' plugin.')
            logger.exception(err)

    def loadSearchConfigurationParameters(self):
        config_filename = self.name+'.conf'
        config_file = os.path.join(os.getcwd(),  'plugins', self.name, config_filename)
        config = ConfigObj(infile=config_file)
        config.create_empty = False
        try:
            params = config['search_options']
        except Exception as err:
            params= None
            logger.error('Could not load the search configuration parameters for the '+self.name+' plugin.')
            logger.exception(err)
        
        return params    
            
    def getLabelForKey(self, key):
        '''
        If the developer of the plugin has not implemented this function in the plugin, 
        return the key name to be used in the label
        '''  
        return key
>>>>>>> gs-ai-patch-1
