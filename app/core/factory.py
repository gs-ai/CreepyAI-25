import logging
from typing import Optional
from .main_window import CreepyMainWindow
from .settings_manager import SettingsManager

class CreepyMainWindowFactory:
    """Factory class for creating properly configured main window instances."""
    
    @staticmethod
    def create_main_window(settings_path: Optional[str] = None, *args, **kwargs):
        """
        Create and configure a main window instance with its dependencies.
        
        Args:
            settings_path: Optional custom path for settings file
            *args, **kwargs: Additional arguments to pass to the main window constructor
            
        Returns:
            Configured CreepyMainWindow instance
        """
        # Initialize logger if not already done
        if not logging.getLogger().handlers:
            logging.basicConfig(level=logging.INFO, 
                               format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create settings manager
        settings_manager = SettingsManager(settings_path)
        
        # Create main window with dependencies injected
        main_window = CreepyMainWindow(settings_manager=settings_manager, *args, **kwargs)
        
        return main_window
