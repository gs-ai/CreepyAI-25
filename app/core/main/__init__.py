"""
Main module for CreepyAI application
"""
import os
import sys
import logging

logger = logging.getLogger('creepyai.main')

def start_application():
    """Start the CreepyAI application"""
    logger.info("Starting CreepyAI application")
    
    # Import here to avoid circular imports
    from app.core.engine import Engine
    
    # Create and initialize engine
    engine = Engine()
    engine.initialize({})
    
    return engine
