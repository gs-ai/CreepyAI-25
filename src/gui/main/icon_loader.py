#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Icon loader for CreepyAI application.
"""

import os
import logging
from PyQt5.QtGui import QIcon

logger = logging.getLogger(__name__)

class IconLoader:
    """
    Handles loading and applying icon styles for the application.
    """
    
    @staticmethod
    def load_icon_styles(window):
        """
        Load icon styles for the application window.
        
        Args:
            window: The main window instance to apply styles to
        """
        try:
            # Make sure window is properly initialized
            if not hasattr(window, 'setWindowIcon'):
                logger.error("Window object doesn't have setWindowIcon method")
                return
                
            # Set application icon
            app_icon_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'resources', 'app_icon.png'
            )
            
            if os.path.exists(app_icon_path):
                window.setWindowIcon(QIcon(app_icon_path))
                logger.info("Icon styles loaded successfully")
            else:
                logger.warning(f"Application icon not found at {app_icon_path}")
                
        except Exception as e:
            logger.error(f"Failed to load icon styles: {str(e)}")
