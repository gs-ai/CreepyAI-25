class CreepyMainWindow:
    def __init__(self, *args, **kwargs):
        # ...existing code...
        
        # Initialize recent projects list
        self.recent_projects = []
        self.load_recent_projects()
        
        # ...existing code...
    
    def setup_ui(self):
        # ...existing code...
    
    def load_recent_projects(self):
        """Load recent projects from settings or create empty list."""
        try:
            # Example implementation - adjust according to your settings system
            from settings import load_settings
            settings = load_settings()
            self.recent_projects = settings.get('recent_projects', [])
        except Exception as e:
            print(f"Failed to load recent projects: {e}")
            self.recent_projects = []