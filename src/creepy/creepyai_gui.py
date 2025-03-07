import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import threading
import logging
from typing import Dict, Any, List, Optional, Callable
import webbrowser
from pathlib import Path
import importlib
import sys

# Try to import optional dependencies
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Local imports - will be imported if available
try:
    from utils.message_utils import show_message_box
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='creepyai.log'
)
logger = logging.getLogger('CreepyAI GUI')

class CreepyAIGUI:
    def __init__(self, root, config_path=None):
        """
        Initialize the CreepyAI GUI application
        
        Args:
            root: Tkinter root window
            config_path: Optional path to configuration file
        """
        self.root = root
        self.root.title("CreepyAI - OSINT Assistant")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Set default config path if not provided
        if not config_path:
            config_path = os.path.expanduser("~/.config/creepyai/config.json")
        self.config_path = config_path
        
        # Load configuration
        self.config = self.load_config()
        
        # Set up the main frame
        self.setup_ui()
        
        # Initialize project management
        self.project_manager = ProjectManager(self)
        self.current_project = None
        
        # Initialize plugin system
        self.plugin_manager = PluginManager(self)
        
        # Search state
        self.search_running = False
        
        # Application state
        self.results_data = []
        
        # Apply theme based on configuration
        self.apply_theme()
        
        # Register event handlers
        self.register_events()

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file with error handling
        
        Returns:
            Configuration dictionary
        """
        default_config = {
            "api_keys": {},
            "output_directory": os.path.expanduser("~/Documents/CreepyAI"),
            "plugins_directory": os.path.expanduser("~/.config/creepyai/plugins"),
            "theme": "system",
            "auto_save": True,
            "auto_check_updates": True,
            "recent_projects": []
        }
        
        try:
            # Ensure directory exists
            config_dir = os.path.dirname(self.config_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                
            # Load config if exists, otherwise create default
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                
                # Update default config with loaded values
                for key, value in loaded_config.items():
                    default_config[key] = value
                    
                logger.info("Configuration loaded successfully")
            else:
                # Create default config
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info("Default configuration created")
                
            return default_config
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.show_message("Configuration Error", f"Error loading configuration: {e}")
            return default_config

    def save_config(self) -> bool:
        """
        Save configuration to file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info("Configuration saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            self.show_message("Configuration Error", f"Error saving configuration: {e}")
            return False

    def show_message(self, title: str, message: str, message_type: str = "info") -> None:
        """
        Show a message box with the specified title and message
        
        Args:
            title: Message box title
            message: Message to display
            message_type: Type of message (info, error, warning, question)
        """
        if UTILS_AVAILABLE:
            # Use external message utility if available
            show_message_box(title, message, message_type)
        else:
            # Use built-in messagebox
            if message_type == "error":
                messagebox.showerror(title, message)
            elif message_type == "warning":
                messagebox.showwarning(title, message)
            else:
                messagebox.showinfo(title, message)
        
        # Log the message
        log_method = getattr(logger, message_type if message_type in ('info', 'error', 'warning') else 'info')
        log_method(f"{title}: {message}")

    def setup_ui(self):
        """Set up the user interface"""
        # Create menu
        self.create_menu()
        
        # Create main notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_search_tab()
        self.create_results_tab()
        self.create_analysis_tab()
        self.create_reports_tab()
        
        # Status bar
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Project status
        self.project_status_var = tk.StringVar(value="No project open")
        project_status = ttk.Label(self.status_frame, textvariable=self.project_status_var, anchor=tk.W)
        project_status.pack(side=tk.LEFT, padx=5)
        
        # Main status
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        # Progress bar (initially hidden)
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self.status_frame, variable=self.progress_var, maximum=100, mode='determinate')
        # Only packed when needed

    def create_menu(self):
        """Create the application menu with keyboard shortcuts"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Search", command=self.new_search, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Open Project", command=self.open_project, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Project", command=self.save_project, accelerator="Ctrl+S")
        file_menu.add_command(label="Close Project", command=self.close_project, accelerator="Ctrl+W")
        file_menu.add_separator()
        file_menu.add_command(label="Import Data", command=self.import_data, accelerator="Ctrl+I")
        file_menu.add_command(label="Export Results", command=self.export_data, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Preferences", command=self.show_preferences, accelerator="Ctrl+,")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.confirm_exit, accelerator="Alt+F4")
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Copy", command=self.copy_selected, accelerator="Ctrl+C")
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.find_in_results, accelerator="Ctrl+F")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Projects menu
        projects_menu = tk.Menu(menubar, tearoff=0)
        projects_menu.add_command(label="Create New Project", command=self.create_project)
        projects_menu.add_command(label="Open Existing Project", command=self.open_project)
        projects_menu.add_command(label="Project Settings", command=self.project_settings)
        projects_menu.add_separator()
        
        # Recent projects submenu (will be populated dynamically)
        self.recent_projects_menu = tk.Menu(projects_menu, tearoff=0)
        projects_menu.add_cascade(label="Recent Projects", menu=self.recent_projects_menu)
        self.update_recent_projects_menu()
        
        menubar.add_cascade(label="Projects", menu=projects_menu)
        
        # Plugins menu
        plugins_menu = tk.Menu(menubar, tearoff=0)
        plugins_menu.add_command(label="Plugin Manager", command=self.plugin_manager_dialog)
        plugins_menu.add_command(label="Install Plugin", command=self.install_plugin_dialog)
        plugins_menu.add_separator()
        plugins_menu.add_command(label="Plugin Settings", command=self.plugin_settings_dialog)
        plugins_menu.add_separator()
        
        # Plugin submenu (will be populated dynamically)
        self.plugin_menu = tk.Menu(plugins_menu, tearoff=0)
        plugins_menu.add_cascade(label="Available Plugins", menu=self.plugin_menu)
        self.update_plugin_menu()
        
        menubar.add_cascade(label="Plugins", menu=plugins_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.show_documentation, accelerator="F1")
        help_menu.add_command(label="View Logs", command=self.show_logs)
        help_menu.add_command(label="Check for Updates", command=self.check_for_updates)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # Register keyboard shortcuts
        self.register_keyboard_shortcuts()

    def register_keyboard_shortcuts(self):
        """Register keyboard shortcuts for common actions"""
        # File menu shortcuts
        self.root.bind("<Control-n>", lambda event: self.new_search())
        self.root.bind("<Control-o>", lambda event: self.open_project())
        self.root.bind("<Control-s>", lambda event: self.save_project())
        self.root.bind("<Control-w>", lambda event: self.close_project())
        self.root.bind("<Control-i>", lambda event: self.import_data())
        self.root.bind("<Control-e>", lambda event: self.export_data())
        self.root.bind("<Control-comma>", lambda event: self.show_preferences())
        
        # Edit menu shortcuts
        self.root.bind("<Control-c>", lambda event: self.copy_selected())
        self.root.bind("<Control-a>", lambda event: self.select_all())
        self.root.bind("<Control-f>", lambda event: self.find_in_results())
        
        # Help menu shortcuts
        self.root.bind("<F1>", lambda event: self.show_documentation())
        
        # Tab navigation
        self.root.bind("<Control-Tab>", lambda event: self.next_tab())
        self.root.bind("<Control-Shift-Tab>", lambda event: self.prev_tab())

    def update_recent_projects_menu(self):
        """Update the recent projects menu with items from config"""
        # Clear current menu items
        self.recent_projects_menu.delete(0, tk.END)
        
        # Get recent projects from config
        recent_projects = self.config.get("recent_projects", [])
        
        if recent_projects:
            # Add each project to the menu
            for project_path in recent_projects:
                # Get the project name (last directory in path)
                project_name = os.path.basename(project_path)
                
                # Create a callback that captures the current project_path
                callback = lambda path=project_path: self.open_recent_project(path)
                
                # Add to menu
                self.recent_projects_menu.add_command(label=project_name, command=callback)
            
            # Add separator and clear option
            self.recent_projects_menu.add_separator()
            self.recent_projects_menu.add_command(label="Clear Recent Projects", 
                                                 command=self.clear_recent_projects)
        else:
            # No recent projects
            self.recent_projects_menu.add_command(label="No Recent Projects", state=tk.DISABLED)

    def update_plugin_menu(self):
        """Update the plugin menu with installed plugins"""
        # Clear current menu items
        self.plugin_menu.delete(0, tk.END)
        
        # Get plugins from plugin manager
        plugins = self.plugin_manager.get_plugins()
        
        if plugins:
            # Add each plugin to the menu
            for plugin_id, plugin_info in plugins.items():
                # Create a callback that captures the current plugin_id
                callback = lambda p_id=plugin_id: self.run_plugin(p_id)
                
                # Add to menu with plugin name
                self.plugin_menu.add_command(label=plugin_info.get("name", plugin_id), 
                                           command=callback)
        else:
            # No plugins installed
            self.plugin_menu.add_command(label="No Plugins Installed", state=tk.DISABLED)

    def create_dashboard_tab(self):
        """Create the dashboard tab with welcome message and quick actions"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Welcome message
        welcome_frame = ttk.Frame(dashboard_frame)
        welcome_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(
            welcome_frame, 
            text="Welcome to CreepyAI OSINT Assistant", 
            font=("TkDefaultFont", 16)
        ).pack(pady=10)
        
        ttk.Label(
            welcome_frame,
            text="Start by creating a new project or opening an existing one",
            font=("TkDefaultFont", 10)
        ).pack(pady=5)
        
        # Quick actions frame
        actions_frame = ttk.LabelFrame(dashboard_frame, text="Quick Actions")
        actions_frame.pack(fill=tk.BOTH, expand=False, padx=20, pady=10)
        
        # Create a grid for buttons with proper spacing
        for i in range(3):
            actions_frame.columnconfigure(i, weight=1)
        
        button_new = ttk.Button(actions_frame, text="New Search", command=self.new_search)
        button_new.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        button_open = ttk.Button(actions_frame, text="Open Project", command=self.open_project)
        button_open.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        button_import = ttk.Button(actions_frame, text="Import Data", command=self.import_data)
        button_import.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        button_plugins = ttk.Button(actions_frame, text="Manage Plugins", command=self.plugin_manager_dialog)
        button_plugins.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        button_report = ttk.Button(actions_frame, text="Generate Report", command=self.generate_report)
        button_report.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        button_help = ttk.Button(actions_frame, text="Documentation", command=self.show_documentation)
        button_help.grid(row=1, column=2, padx=10, pady=10, sticky="ew")
        
        # Recent activity frame
        recent_frame = ttk.LabelFrame(dashboard_frame, text="Recent Activity")
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create a treeview for recent activity
        columns = ("timestamp", "type", "description")
        self.activity_tree = ttk.Treeview(recent_frame, columns=columns, show="headings")
        
        # Define column headings
        self.activity_tree.heading("timestamp", text="Time")
        self.activity_tree.heading("type", text="Activity")
        self.activity_tree.heading("description", text="Description")
        
        # Configure column widths
        self.activity_tree.column("timestamp", width=150)
        self.activity_tree.column("type", width=100)
        self.activity_tree.column("description", width=500)
        
        # Add scrollbar
        activity_scroll = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL, command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=activity_scroll.set)
        
        # Pack the treeview and scrollbar
        activity_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.activity_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add some sample activities (in a real app, these would come from a log)
        self.activity_tree.insert("", tk.END, values=("2023-05-15 10:30:45", "Login", "User logged in"))
        self.activity_tree.insert("", tk.END, values=("2023-05-15 10:31:20", "Project", "Created new project 'Investigation1'"))
        self.activity_tree.insert("", tk.END, values=("2023-05-15 10:35:10", "Search", "Executed search for 'John Smith'"))
        
        # Project statistics frame
        if self.current_project:
            self.update_dashboard_statistics()
        else:
            stats_frame = ttk.LabelFrame(dashboard_frame, text="Project Statistics")
            stats_frame.pack(fill=tk.BOTH, expand=False, padx=20, pady=10)
            
            ttk.Label(stats_frame, text="No project open").pack(pady=10)

    def update_dashboard_statistics(self):
        """Update the dashboard with current project statistics"""
        # Implementation would depend on project data structure
        pass

    def create_search_tab(self):
        """Create the search tab with target input and search options"""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="Search")
        
        # Search configuration
        config_frame = ttk.LabelFrame(search_frame, text="Search Configuration")
        config_frame.pack(fill=tk.X, expand=False, padx=20, pady=10)
        
        # Target input
        ttk.Label(config_frame, text="Target:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.target_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.target_var, width=50).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Target type
        ttk.Label(config_frame, text="Target Type:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.target_type_var = tk.StringVar(value="Person")
        target_types = ["Person", "Organization", "Domain", "IP Address", "Username", "Email", "Phone Number"]
        ttk.Combobox(config_frame, textvariable=self.target_type_var, values=target_types, state="readonly").grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5
        )
        
        # Location input
        ttk.Label(config_frame, text="Location:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.location_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.location_var, width=50).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Profile selection
        ttk.Label(config_frame, text="Profile:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.profile_var = tk.StringVar(value="Basic")
        profiles = ["Basic", "Professional", "Comprehensive", "Social Media", "Custom"]
        ttk.Combobox(config_frame, textvariable=self.profile_var, values=profiles, state="readonly").grid(
            row=3, column=1, sticky=tk.W, padx=5, pady=5
        )
        
        # Time range
        time_frame = ttk.LabelFrame(search_frame, text="Time Range")
        time_frame.pack(fill=tk.X, expand=False, padx=20, pady=10)
        
        # Enable time range
        self.enable_time_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            time_frame, text="Limit Time Range", variable=self.enable_time_var,
            command=self.toggle_time_range
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Start date
        ttk.Label(time_frame, text="Start Date:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.start_date_var = tk.StringVar()
        self.start_date_entry = ttk.Entry(time_frame, textvariable=self.start_date_var, width=15, state=tk.DISABLED)
        self.start_date_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(time_frame, text="(YYYY-MM-DD)").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # End date
        ttk.Label(time_frame, text="End Date:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.end_date_var = tk.StringVar()
        self.end_date_entry = ttk.Entry(time_frame, textvariable=self.end_date_var, width=15, state=tk.DISABLED)
        self.end_date_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(time_frame, text="(YYYY-MM-DD)").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Sources frame
        sources_frame = ttk.LabelFrame(search_frame, text="Data Sources")
        sources_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Data source checkboxes
        self.source_vars = {}
        sources = ["Social Media", "Public Records", "Professional Networks", "News Articles", 
                  "Image Search", "Forums", "Dark Web", "Government Records"]
        
        # Organize sources in a grid (4 columns)
        for i, source in enumerate(sources):
            self.source_vars[source] = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                sources_frame, text=source, variable=self.source_vars[source]
            ).grid(row=i//4, column=i%4, sticky=tk.W, padx=20, pady=5)
        
        # Advanced options frame
        advanced_frame = ttk.LabelFrame(search_frame, text="Advanced Options")
        advanced_frame.pack(fill=tk.X, expand=False, padx=20, pady=10)
        
        # Depth level
        ttk.Label(advanced_frame, text="Search Depth:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.depth_var = tk.IntVar(value=1)
        depth_spin = ttk.Spinbox(advanced_frame, from_=1, to=3, textvariable=self.depth_var, width=5)
        depth_spin.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(advanced_frame, text="(Higher values take longer)").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Results limit
        ttk.Label(advanced_frame, text="Results Limit:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.limit_var = tk.IntVar(value=100)
        limit_spin = ttk.Spinbox(advanced_frame, from_=10, to=1000, increment=10, textvariable=self.limit_var, width=5)
        limit_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(advanced_frame, text="(Maximum results per source)").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Search button with progress indicator
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame, 
            text="Start Search", 
            command=self.start_search
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            button_frame, 
            text="Reset Form", 
            command=self.reset_search_form
        ).pack(side=tk.LEFT, padx=10)

    def toggle_time_range(self):
        """Enable or disable time range inputs based on checkbox"""
        state = tk.NORMAL if self.enable_time_var.get() else tk.DISABLED
        self.start_date_entry.config(state=state)
        self.end_date_entry.config(state=state)

    def create_results_tab(self):
        """Create the results tab with filtering and display options"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Results")
        
        # Results control panel
        control_frame = ttk.Frame(results_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Filter controls
        filter_frame = ttk.LabelFrame(control_frame, text="Filter Results")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Filter by text
        ttk.Label(filter_frame, text="Text:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.filter_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Filter by source
        ttk.Label(filter_frame, text="Source:").grid(row=0, column=2, padx=5, pady=5)
        self.filter_source_var = tk.StringVar(value="All")
        self.filter_source_combo = ttk.Combobox(filter_frame, textvariable=self.filter_source_var, width=15)
        self.filter_source_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Apply filter button
        ttk.Button(filter_frame, text="Apply Filter", command=self.apply_filter).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(filter_frame, text="Clear Filter", command=self.clear_filter).grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Separator(results_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)
        
        # Results view frame
        view_frame = ttk.Frame(results_frame)
        view_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Results treeview
        self.results_tree = ttk.Treeview(
            view_frame, 
            columns=("Source", "Type", "Date", "Confidence"),
            selectmode="extended"
        )
        
        # Configure columns
        self.results_tree.heading("#0", text="Item")
        self.results_tree.heading("Source", text="Source")
        self.results_tree.heading("Type", text="Type")
        self.results_tree.heading("Date", text="Date")
        self.results_tree.heading("Confidence", text="Confidence")
        
        self.results_tree.column("#0", width=300)
        self.results_tree.column("Source", width=120)
        self.results_tree.column("Type", width=100)
        self.results_tree.column("Date", width=100)
        self.results_tree.column("Confidence", width=80)
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(view_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        x_scroll = ttk.Scrollbar(view_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Pack everything
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Actions panel
        actions_panel = ttk.Frame(results_frame)
        actions_panel.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(actions_panel, text="Export Results", command=self.export_data).pack(side=tk.RIGHT, padx=5)
        ttk.Button(actions_panel, text="Copy Selected", command=self.copy_selected).pack(side=tk.RIGHT, padx=5)
        ttk.Button(actions_panel, text="View Details", command=self.view_result_details).pack(side=tk.RIGHT, padx=5)

    def create_analysis_tab(self):
        """Create the analysis tab with visualization options"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="Analysis")
        
        # Create layout with options on left, visualization on right
        options_frame = ttk.Frame(analysis_frame, width=300)
        options_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        options_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        visualization_frame = ttk.LabelFrame(analysis_frame, text="Visualization")
        visualization_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Visualization options
        options_label = ttk.LabelFrame(options_frame, text="Visualization Options")
        options_label.pack(fill=tk.X, pady=10)
        
        # Visualization type
        ttk.Label(options_label, text="Visualization:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.viz_var = tk.StringVar(value="Network Graph")
        viz_types = ["Network Graph", "Timeline", "Heatmap", "Word Cloud", "Relationship Diagram"]
        ttk.Combobox(options_label, textvariable=self.viz_var, values=viz_types, state="readonly", width=20).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5
        )
        
        # Data source
        ttk.Label(options_label, text="Data Source:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.data_source_var = tk.StringVar(value="All Results")
        data_sources = ["All Results", "Social Media Only", "Public Records Only", "Custom Selection"]
        ttk.Combobox(options_label, textvariable=self.data_source_var, values=data_sources, state="readonly", width=20).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5
        )
        
        # Date range controls
        date_frame = ttk.LabelFrame(options_frame, text="Time Period")
        date_frame.pack(fill=tk.X, pady=10)
        
        # Use date range checkbox
        self.use_date_range_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            date_frame, text="Limit to time period", 
            variable=self.use_date_range_var,
            command=self.toggle_analysis_date_range
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Start date
        ttk.Label(date_frame, text="Start:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.analysis_start_var = tk.StringVar()
        self.analysis_start_entry = ttk.Entry(date_frame, textvariable=self.analysis_start_var, width=12, state=tk.DISABLED)
        self.analysis_start_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # End date
        ttk.Label(date_frame, text="End:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.analysis_end_var = tk.StringVar()
        self.analysis_end_entry = ttk.Entry(date_frame, textvariable=self.analysis_end_var, width=12, state=tk.DISABLED)
        self.analysis_end_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Advanced options frame
        advanced_frame = ttk.LabelFrame(options_frame, text="Advanced Options")
        advanced_frame.pack(fill=tk.X, pady=10)
        
        # Include frequency analysis
        self.include_freq_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            advanced_frame, text="Include frequency analysis",
            variable=self.include_freq_var
        ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Cluster similar items
        self.cluster_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            advanced_frame, text="Cluster similar items",
            variable=self.cluster_var
        ).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Buttons
        ttk.Button(
            options_frame, text="Generate Visualization",
            command=self.generate_visualization
        ).pack(pady=10, fill=tk.X)
        
        ttk.Button(
            options_frame, text="Export Visualization",
            command=self.export_visualization
        ).pack(pady=5, fill=tk.X)
        
        # Placeholder for visualization
        self.viz_placeholder = ttk.Label(visualization_frame, text="Visualization will appear here")
        self.viz_placeholder.pack(expand=True)
        
        # Canvas for visualization (initially hidden)
        self.viz_canvas = tk.Canvas(visualization_frame, bg="white")

    def toggle_analysis_date_range(self):
        """Enable or disable date range inputs for analysis based on checkbox"""
        state = tk.NORMAL if self.use_date_range_var.get() else tk.DISABLED
        self.analysis_start_entry.config(state=state)
        self.analysis_end_entry.config(state=state)

    def create_reports_tab(self):
        """Create the reports tab with report generation options"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reports")
        
        # Left panel for options
        options_frame = ttk.Frame(reports_frame, width=300)
        options_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        options_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Right panel for preview
        preview_frame = ttk.LabelFrame(reports_frame, text="Report Preview")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Report options
        options_label = ttk.LabelFrame(options_frame, text="Report Options")
        options_label.pack(fill=tk.X, pady=10)
        
        # Report type
        ttk.Label(options_label, text="Report Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.report_type_var = tk.StringVar(value="Executive Summary")
        report_types = ["Executive Summary", "Full Technical Report", "Data Sheet", "Custom Report"]
        ttk.Combobox(
            options_label, textvariable=self.report_type_var, 
            values=report_types, state="readonly", width=20
        ).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Report format
        ttk.Label(options_label, text="Format:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.report_format_var = tk.StringVar(value="PDF")
        formats = ["PDF", "HTML", "DOCX", "Markdown", "Plain Text"]
        ttk.Combobox(
            options_label, textvariable=self.report_format_var, 
            values=formats, state="readonly", width=20
        ).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Include sections frame
        sections_frame = ttk.LabelFrame(options_frame, text="Include Sections")
        sections_frame.pack(fill=tk.X, pady=10)
        
        # Include options checkboxes
        self.include_viz_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            sections_frame, text="Visualizations",
            variable=self.include_viz_var
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.include_raw_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            sections_frame, text="Raw Data",
            variable=self.include_raw_var
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.include_analysis_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            sections_frame, text="Analysis",
            variable=self.include_analysis_var
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        self.include_map_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            sections_frame, text="Maps",
            variable=self.include_map_var
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        # Output options frame
        output_frame = ttk.LabelFrame(options_frame, text="Output Options")
        output_frame.pack(fill=tk.X, pady=10)
        
        # Output path
        ttk.Label(output_frame, text="Save to:").pack(anchor=tk.W, padx=5, pady=2)
        
        path_frame = ttk.Frame(output_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.report_path_var = tk.StringVar(value=os.path.expanduser("~/Documents"))
        path_entry = ttk.Entry(path_frame, textvariable=self.report_path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            path_frame, text="Browse", width=8,
            command=lambda: self.report_path_var.set(filedialog.askdirectory(
                initialdir=self.report_path_var.get()
            ))
        ).pack(side=tk.RIGHT, padx=2)
        
        # Buttons
        ttk.Button(
            options_frame, text="Generate Report",
            command=self.generate_report
        ).pack(pady=10, fill=tk.X)
        
        ttk.Button(
            options_frame, text="View Recent Reports",
            command=self.view_recent_reports
        ).pack(pady=5, fill=tk.X)
        
        # Placeholder for preview
        self.report_preview_label = ttk.Label(
            preview_frame, 
            text="Report preview will appear here.\nGenerate a report to preview."
        )
        self.report_preview_label.pack(expand=True)
        
        # Preview text widget (initially hidden)
        self.report_preview = tk.Text(preview_frame, wrap=tk.WORD)
        self.report_preview_scroll = ttk.Scrollbar(
            preview_frame, command=self.report_preview.yview
        )
        self.report_preview.configure(yscrollcommand=self.report_preview_scroll.set)
    
    def register_events(self):
        """Register event handlers for UI events"""
        # Notebook tab change
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Results tree events
        self.results_tree.bind("<Double-1>", self.on_result_double_click)
        self.results_tree.bind("<Button-3>", self.on_result_right_click)
        
        # Window close event
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)
    
    def on_tab_changed(self, event):
        """Handle notebook tab change event"""
        current_tab = self.notebook.index(self.notebook.select())
        tab_names = ["Dashboard", "Search", "Results", "Analysis", "Reports"]
        if current_tab < len(tab_names):
            self.status_var.set(f"Viewing {tab_names[current_tab]} tab")
            
            # Perform any tab-specific updates
            if tab_names[current_tab] == "Dashboard":
                self.update_dashboard_statistics()
            elif tab_names[current_tab] == "Results":
                self.update_filter_sources()
    
    def on_result_double_click(self, event):
        """Handle double-click on a result item"""
        item_id = self.results_tree.identify('item', event.x, event.y)
        if item_id:
            self.view_result_details(item_id)
    
    def on_result_right_click(self, event):
        """Show context menu on right-click in results tree"""
        item_id = self.results_tree.identify('item', event.x, event.y)
        if item_id:
            # Select the item that was right-clicked
            self.results_tree.selection_set(item_id)
            
            # Create popup menu
            popup = tk.Menu(self.root, tearoff=0)
            popup.add_command(label="View Details", command=lambda: self.view_result_details(item_id))
            popup.add_command(label="Copy Value", command=self.copy_selected)
            popup.add_separator()
            popup.add_command(label="Remove from Results", command=lambda: self.remove_result(item_id))
            
            # Display popup menu
            try:
                popup.tk_popup(event.x_root, event.y_root, 0)
            finally:
                popup.grab_release()
    
    def apply_theme(self):
        """Apply theme based on configuration"""
        theme = self.config.get("theme", "system")
        # In a real app, this would apply the selected theme
        logger.info(f"Applied theme: {theme}")
    
    # Navigation methods
    def next_tab(self):
        """Switch to the next tab"""
        current = self.notebook.index(self.notebook.select())
        if current < len(self.notebook.tabs()) - 1:
            self.notebook.select(current + 1)
    
    def prev_tab(self):
        """Switch to the previous tab"""
        current = self.notebook.index(self.notebook.select())
        if current > 0:
            self.notebook.select(current - 1)
    
    # Project management methods
    def new_search(self):
        """Reset and start a new search"""
        if self.search_running:
            self.show_message(
                "Search in Progress", 
                "A search is already running. Please wait or cancel it.",
                "warning"
            )
            return
        
        # Switch to search tab
        self.notebook.select(1)  # Search tab (index 1)
        
        # Reset search form
        self.reset_search_form()
    
    def reset_search_form(self):
        """Reset all search form fields to defaults"""
        self.target_var.set("")
        self.target_type_var.set("Person")
        self.location_var.set("")
        self.profile_var.set("Basic")
        self.enable_time_var.set(False)
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.depth_var.set(1)
        self.limit_var.set(100)
        
        # Enable all sources
        for source_var in self.source_vars.values():
            source_var.set(True)
            
        # Update UI elements
        self.toggle_time_range()
        self.status_var.set("Ready for new search")
    
    def open_project(self):
        """Open an existing project"""
        project_path = filedialog.askdirectory(
            title="Open CreepyAI Project",
            initialdir=self.config.get("output_directory")
        )
        
        if project_path:
            try:
                # Attempt to open the project
                project_loaded = self.project_manager.load_project(project_path)
                
                if project_loaded:
                    # Update current project reference
                    self.current_project = project_path
                    
                    # Add to recent projects
                    self.add_to_recent_projects(project_path)
                    
                    # Update UI elements
                    project_name = os.path.basename(project_path)
                    self.project_status_var.set(f"Project: {project_name}")
                    self.status_var.set(f"Project opened: {project_name}")
                    
                    # Load project data
                    self.load_project_data()
                    
                    # Switch to dashboard
                    self.notebook.select(0)  # Dashboard tab (index 0)
                else:
                    self.show_message(
                        "Error", 
                        f"Could not load project from {project_path}. Invalid project format.",
                        "error"
                    )
            except Exception as e:
                logger.error(f"Failed to open project: {e}", exc_info=True)
                self.show_message(
                    "Error", 
                    f"Failed to open project: {e}",
                    "error"
                )
    
    def open_recent_project(self, project_path: str):
        """Open a project from the recent projects list"""
        if os.path.exists(project_path):
            # Use the regular open project logic
            try:
                project_loaded = self.project_manager.load_project(project_path)
                
                if project_loaded:
                    # Update current project
                    self.current_project = project_path
                    
                    # Move to top of recent list
                    self.add_to_recent_projects(project_path)
                    
                    # Update UI
                    project_name = os.path.basename(project_path)
                    self.project_status_var.set(f"Project: {project_name}")
                    self.status_var.set(f"Project opened: {project_name}")
                    
                    # Load project data
                    self.load_project_data()
                    
                    # Switch to dashboard
                    self.notebook.select(0)  # Dashboard tab (index 0)
                else:
                    self.show_message(
                        "Error", 
                        f"Could not load project from {project_path}. Invalid project format.",
                        "error"
                    )
            except Exception as e:
                logger.error(f"Failed to open recent project: {e}", exc_info=True)
                self.show_message(
                    "Error", 
                    f"Failed to open project: {e}",
                    "error"
                )
        else:
            # Project doesn't exist anymore
            self.show_message(
                "Project Not Found", 
                f"The project at {project_path} no longer exists.",
                "warning"
            )
            
            # Remove from recent projects
            self.remove_from_recent_projects(project_path)
    
    def create_project(self):
        """Create a new project"""
        project_name = tk.simpledialog.askstring("New Project", "Enter project name:")
        if not project_name:
            return  # User canceled
        
        # Clean project name (remove invalid characters)
        project_name = self.sanitize_filename(project_name)
        if not project_name:
            self.show_message(
                "Invalid Name", 
                "Please enter a valid project name with alphanumeric characters.",
                "warning"
            )
            return
        
        project_path = os.path.join(self.config.get("output_directory"), project_name)
        
        try:
            # Check if project exists
            if os.path.exists(project_path):
                overwrite = messagebox.askyesno(
                    "Project Exists",
                    f"A project named '{project_name}' already exists. Overwrite it?"
                )
                if not overwrite:
                    return
            
            # Create project
            project_created = self.project_manager.create_project(project_name, project_path)
            
            if project_created:
                # Set as current project
                self.current_project = project_path
                
                # Add to recent projects
                self.add_to_recent_projects(project_path)
                
                # Update UI
                self.project_status_var.set(f"Project: {project_name}")
                self.status_var.set(f"Project created: {project_name}")
                
                # Switch to search tab
                self.notebook.select(1)  # Search tab (index 1)
            else:
                self.show_message(
                    "Error", 
                    f"Failed to create project '{project_name}'.",
                    "error"
                )
        except Exception as e:
            logger.error(f"Failed to create project: {e}", exc_info=True)
            self.show_message(
                "Error", 
                f"Failed to create project: {e}",
                "error"
            )
    
    def save_project(self):
        """Save current project"""
        if not self.current_project:
            self.show_message(
                "No Project", 
                "No project is currently open. Create or open a project first.",
                "warning"
            )
            return
        
        try:
            # Save project data
            saved = self.project_manager.save_project(self.current_project)
            
            if saved:
                project_name = os.path.basename(self.current_project)
                self.status_var.set(f"Project saved: {project_name}")
            else:
                self.show_message(
                    "Error", 
                    "Failed to save project.",
                    "error"
                )
        except Exception as e:
            logger.error(f"Failed to save project: {e}", exc_info=True)
            self.show_message(
                "Error", 
                f"Failed to save project: {e}",
                "error"
            )
    
    def close_project(self):
        """Close the current project"""
        if not self.current_project:
            return
        
        # Ask to save if changes exist
        if self.project_manager.has_unsaved_changes():
            save = messagebox.askyesnocancel(
                "Save Project",
                "Do you want to save the changes before closing?"
            )
            
            if save is None:  # Cancel
                return
            elif save:  # Yes
                self.save_project()
        
        # Close the project
        self.project_manager.close_project()
        
        # Clear current project reference
        self.current_project = None
        
        # Update UI
        self.project_status_var.set("No project open")
        self.status_var.set("Project closed")
        
        # Clear displays
        self.clear_displays()
    
    def load_project_data(self):
        """Load data from current project into UI"""
        if not self.current_project or not self.project_manager.project_data:
            return
        
        # Get project data
        project_data = self.project_manager.project_data
        
        # Load target information if available
        if "target" in project_data:
            self.target_var.set(project_data["target"].get("name", ""))
            self.target_type_var.set(project_data["target"].get("type", "Person"))
        
        # Load results if available
        if "results" in project_data:
            self.results_data = project_data["results"]
            self.populate_results_tree()
        
        # Update dashboard
        self.update_dashboard_statistics()
    
    def clear_displays(self):
        """Clear all UI displays"""
        # Clear results tree
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Clear analysis visualizations
        if hasattr(self, 'viz_placeholder'):
            self.viz_placeholder.pack(expand=True)
            
        if hasattr(self, 'viz_canvas'):
            self.viz_canvas.pack_forget()
        
        # Clear report preview
        if hasattr(self, 'report_preview'):
            self.report_preview.pack_forget()
            self.report_preview_scroll.pack_forget()
            
        if hasattr(self, 'report_preview_label'):
            self.report_preview_label.pack(expand=True)
    
    def add_to_recent_projects(self, project_path: str):
        """Add a project to the recent projects list"""
        recent_projects = self.config.get("recent_projects", [])
        
        # Remove if already in list to avoid duplicates
        if project_path in recent_projects:
            recent_projects.remove(project_path)
        
        # Add to front of list
        recent_projects.insert(0, project_path)
        
        # Trim list if needed
        max_recent = self.config.get("recent_projects_limit", 10)
        if len(recent_projects) > max_recent:
            recent_projects = recent_projects[:max_recent]
        
        # Update config
        self.config["recent_projects"] = recent_projects
        self.save_config()
        
        # Update UI
        self.update_recent_projects_menu()
    
    def remove_from_recent_projects(self, project_path: str):
        """Remove a project from the recent projects list"""
        recent_projects = self.config.get("recent_projects", [])
        
        if project_path in recent_projects:
            recent_projects.remove(project_path)
            
            # Update config
            self.config["recent_projects"] = recent_projects
            self.save_config()
            
            # Update UI
            self.update_recent_projects_menu()
    
    def clear_recent_projects(self):
        """Clear the list of recent projects"""
        self.config["recent_projects"] = []
        self.save_config()
        self.update_recent_projects_menu()
    
    def project_settings(self):
        """Show project settings dialog"""
        if not self.current_project:
            self.show_message(
                "No Project", 
                "No project is open. Please open a project first.",
                "warning"
            )
            return
        
        # Create settings dialog
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Project Settings")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Project info frame
        info_frame = ttk.LabelFrame(settings_window, text="Project Information")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Project name
        project_name = os.path.basename(self.current_project)
        ttk.Label(info_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar(value=project_name)
        ttk.Entry(info_frame, textvariable=name_var).grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Project path
        ttk.Label(info_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(info_frame, text=self.current_project).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Created date
        created_date = self.project_manager.get_project_metadata().get("created", "Unknown")
        ttk.Label(info_frame, text="Created:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(info_frame, text=created_date).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Last modified
        modified_date = self.project_manager.get_project_metadata().get("modified", "Unknown")
        ttk.Label(info_frame, text="Last Modified:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(info_frame, text=modified_date).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(settings_window, text="Project Options")
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Auto-save option
        auto_save_var = tk.BooleanVar(value=self.project_manager.get_project_setting("auto_save", True))
        ttk.Checkbutton(
            options_frame, text="Auto-save project changes",
            variable=auto_save_var
        ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Backup option
        backup_var = tk.BooleanVar(value=self.project_manager.get_project_setting("create_backups", True))
        ttk.Checkbutton(
            options_frame, text="Create backups before saving",
            variable=backup_var
        ).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Actions frame
        actions_frame = ttk.Frame(settings_window)
        actions_frame.pack(fill=tk.X, padx=10, pady=20)
        
        # Buttons
        ttk.Button(
            actions_frame, text="Create Backup",
            command=lambda: self.project_manager.create_backup()
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            actions_frame, text="Export Project",
            command=lambda: self.export_project()
        ).pack(side=tk.LEFT, padx=5)
        
        # OK/Cancel buttons
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            button_frame, text="OK",
            command=lambda: self.save_project_settings(
                settings_window, name_var.get(), auto_save_var.get(), backup_var.get()
            )
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame, text="Cancel",
            command=settings_window.destroy
        ).pack(side=tk.RIGHT, padx=5)
    
    def save_project_settings(self, window, name: str, auto_save: bool, create_backups: bool):
        """
        Save project settings and close the settings window
        
        Args:
            window: Settings dialog window to close
            name: New project name
            auto_save: Auto-save setting
            create_backups: Create backups setting
        """
        try:
            # Update project name if changed
            current_name = os.path.basename(self.current_project)
            if name != current_name:
                self.project_manager.rename_project(name)
                self.project_status_var.set(f"Project: {name}")
            
            # Update project settings
            self.project_manager.set_project_setting("auto_save", auto_save)
            self.project_manager.set_project_setting("create_backups", create_backups)
            
            # Save changes
            self.project_manager.save_project(self.current_project)
            
            # Close window
            window.destroy()
            
        except Exception as e:
            logger.error(f"Failed to save project settings: {e}", exc_info=True)
            self.show_message(
                "Error", 
                f"Failed to save project settings: {e}",
                "error"
            )
    
    def export_project(self):
        """Export project to a zip file"""
        if not self.current_project:
            self.show_message(
                "No Project", 
                "No project is open. Please open a project first.",
                "warning"
            )
            return
            
        project_name = os.path.basename(self.current_project)
        export_path = filedialog.asksaveasfilename(
            title="Export Project",
            initialdir=os.path.expanduser("~/Documents"),
            initialfile=f"{project_name}.zip",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        
        if export_path:
            try:
                # Make sure it has .zip extension
                if not export_path.endswith(".zip"):
                    export_path += ".zip"
                
                # Export project
                success = self.project_manager.export_project(export_path)
                
                if success:
                    self.show_message(
                        "Project Exported",
                        f"Project successfully exported to {export_path}",
                        "info"
                    )
                else:
                    self.show_message(
                        "Export Failed",
                        "Failed to export project",
                        "error"
                    )
                    
            except Exception as e:
                logger.error(f"Failed to export project: {e}", exc_info=True)
                self.show_message(
                    "Error",
                    f"Failed to export project: {e}",
                    "error"
                )
    
    def import_data(self):
        """Import data from a file into the current project"""
        if not self.current_project:
            self.show_message(
                "No Project",
                "Please create or open a project first.",
                "warning"
            )
            return
        
        import_file = filedialog.askopenfilename(
            title="Import Data",
            filetypes=[
                ("All supported", "*.json;*.csv;*.xlsx"),
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )
        
        if not import_file:
            return  # User cancelled
            
        try:
            # Get file extension
            _, ext = os.path.splitext(import_file)
            ext = ext.lower()
            
            # Show import options dialog
            import_options = self.get_import_options(ext)
            
            if import_options is None:
                return  # User cancelled
                
            # Start import process
            self.status_var.set(f"Importing data from {os.path.basename(import_file)}...")
            self.show_progress(True)
            
            # Run import in a thread to keep UI responsive
            threading.Thread(
                target=self._import_data_thread,
                args=(import_file, ext, import_options),
                daemon=True
            ).start()
            
        except Exception as e:
            logger.error(f"Failed to import data: {e}", exc_info=True)
            self.show_message(
                "Import Error",
                f"Failed to import data: {e}",
                "error"
            )
            self.show_progress(False)
    
    def _import_data_thread(self, file_path: str, file_type: str, options: Dict[str, Any]):
        """
        Import data in a background thread
        
        Args:
            file_path: Path to the file to import
            file_type: File extension (.json, .csv, etc)
            options: Import options from dialog
        """
        try:
            # Import data based on file type
            if file_type == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
            elif file_type == '.csv':
                # In a real app, use pandas or csv module
                data = {"message": "CSV import not implemented"}
            elif file_type == '.xlsx':
                # In a real app, use pandas or openpyxl
                data = {"message": "Excel import not implemented"}
            else:
                data = {"message": "Unsupported file format"}
                
            # Process imported data
            # In a real app, this would parse the data into application objects
            
            # Update UI
            self.root.after(0, lambda: self._import_data_complete(data))
            
        except Exception as e:
            logger.error(f"Error in import thread: {e}", exc_info=True)
            self.root.after(0, lambda: self._import_data_error(str(e)))
    
    def _import_data_complete(self, data):
        """Handle successful data import"""
        self.show_progress(False)
        self.status_var.set("Data import completed")
        
        # In a real app, update UI with imported data
        self.show_message(
            "Import Complete",
            f"Successfully imported {len(data)} items",
            "info"
        )
    
    def _import_data_error(self, error_message):
        """Handle error in data import"""
        self.show_progress(False)
        self.status_var.set("Data import failed")
        
        self.show_message(
            "Import Error",
            f"Failed to import data: {error_message}",
            "error"
        )
    
    def get_import_options(self, file_type: str) -> Optional[Dict[str, Any]]:
        """
        Show dialog to get import options
        
        Args:
            file_type: File extension to determine options
            
        Returns:
            Dictionary of options or None if cancelled
        """
        # Create options dialog
        options_window = tk.Toplevel(self.root)
        options_window.title("Import Options")
        options_window.transient(self.root)
        options_window.grab_set()
        
        # Default result (will be updated by dialog)
        result = {"cancelled": True}
        
        # Create options based on file type
        if file_type == '.json':
            ttk.Label(options_window, text="JSON Import Options").pack(padx=10, pady=5)
            
            # Merge option
            merge_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                options_window, text="Merge with existing data",
                variable=merge_var
            ).pack(anchor=tk.W, padx=10, pady=5)
            
            # Overwrite option
            overwrite_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                options_window, text="Overwrite duplicates",
                variable=overwrite_var
            ).pack(anchor=tk.W, padx=10, pady=5)
            
        elif file_type == '.csv':
            ttk.Label(options_window, text="CSV Import Options").pack(padx=10, pady=5)
            
            # Delimiter option
            ttk.Label(options_window, text="Delimiter:").pack(anchor=tk.W, padx=10, pady=5)
            delimiter_var = tk.StringVar(value=",")
            delimiters = [",", ";", "\\t", "|"]
            ttk.Combobox(
                options_window, values=delimiters,
                textvariable=delimiter_var, width=5
            ).pack(anchor=tk.W, padx=10, pady=5)
            
            # Header option
            header_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                options_window, text="File contains header row",
                variable=header_var
            ).pack(anchor=tk.W, padx=10, pady=5)
            
        elif file_type == '.xlsx':
            ttk.Label(options_window, text="Excel Import Options").pack(padx=10, pady=5)
            
            # Sheet option
            ttk.Label(options_window, text="Sheet name:").pack(anchor=tk.W, padx=10, pady=5)
            sheet_var = tk.StringVar(value="Sheet1")
            ttk.Entry(options_window, textvariable=sheet_var).pack(anchor=tk.W, padx=10, pady=5)
            
            # Header option
            header_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                options_window, text="File contains header row",
                variable=header_var
            ).pack(anchor=tk.W, padx=10, pady=5)
            
        else:
            ttk.Label(options_window, text="No options available for this file type").pack(padx=10, pady=5)
            
        # OK/Cancel buttons
        button_frame = ttk.Frame(options_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # OK button handler
        def on_ok():
            # Save options
            options = {}
            
            # Get options based on file type
            if file_type == '.json':
                options["merge"] = merge_var.get()
                options["overwrite"] = overwrite_var.get()
            elif file_type == '.csv':
                options["delimiter"] = delimiter_var.get()
                options["header"] = header_var.get()
            elif file_type == '.xlsx':
                options["sheet"] = sheet_var.get()
                options["header"] = header_var.get()
                
            # Update result
            result.clear()
            result.update(options)
            
            # Close dialog
            options_window.destroy()
        
        ttk.Button(
            button_frame, text="OK",
            command=on_ok
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame, text="Cancel",
            command=options_window.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        # Wait for dialog to close
        self.root.wait_window(options_window)
        
        # Return None if cancelled
        if "cancelled" in result:
            return None
        return result

    def export_data(self):
        """Export data to a file"""
        if not self.results_data:
            self.show_message(
                "No Data",
                "There is no data to export.",
                "warning"
            )
            return
            
        # Get selected export format
        file_types = [
            ("CSV files", "*.csv"),
            ("JSON files", "*.json"),
            ("Excel files", "*.xlsx"),
            ("All files", "*.*")
        ]
        
        export_file = filedialog.asksaveasfilename(
            title="Export Data",
            filetypes=file_types,
            defaultextension=".csv"
        )
        
        if not export_file:
            return  # User cancelled
            
        try:
            # Get file extension
            _, ext = os.path.splitext(export_file)
            ext = ext.lower()
            
            # Export data based on file type
            if ext == '.json':
                self._export_to_json(export_file)
            elif ext == '.csv':
                self._export_to_csv(export_file)
            elif ext == '.xlsx':
                self._export_to_excel(export_file)
            else:
                self.show_message(
                    "Export Error",
                    f"Unsupported file format: {ext}",
                    "error"
                )
                return
                
            self.status_var.set(f"Data exported to {os.path.basename(export_file)}")
            
        except Exception as e:
            logger.error(f"Failed to export data: {e}", exc_info=True)
            self.show_message(
                "Export Error",
                f"Failed to export data: {e}",
                "error"
            )
    
    def _export_to_json(self, file_path: str):
        """Export data to JSON file"""
        # In a real app, convert application objects to JSON-serializable format
        export_data = self.results_data
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        self.show_message(
            "Export Complete",
            f"Data successfully exported to {file_path}",
            "info"
        )
    
    def _export_to_csv(self, file_path: str):
        """Export data to CSV file"""
        # In a real app, use pandas or csv module
        self.show_message(
            "Not Implemented",
            "CSV export not implemented in this sample",
            "info"
        )
    
    def _export_to_excel(self, file_path: str):
        """Export data to Excel file"""
        # In a real app, use pandas or openpyxl
        self.show_message(
            "Not Implemented",
            "Excel export not implemented in this sample",
            "info"
        )
    
    # Plugin management methods
    def plugin_manager_dialog(self):
        """Show plugin manager dialog"""
        # Create plugin manager dialog
        manager_window = tk.Toplevel(self.root)
        manager_window.title("Plugin Manager")
        manager_window.geometry("700x500")
        manager_window.transient(self.root)
        manager_window.grab_set()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(manager_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Installed plugins tab
        installed_frame = ttk.Frame(notebook)
        notebook.add(installed_frame, text="Installed Plugins")
        
        # Available plugins tab
        available_frame = ttk.Frame(notebook)
        notebook.add(available_frame, text="Available Plugins")
        
        # Settings tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        
        # Installed plugins list
        ttk.Label(installed_frame, text="Installed Plugins:").pack(anchor=tk.W, padx=10, pady=5)
        
        # Create list with scrollbar
        installed_frame_inner = ttk.Frame(installed_frame)
        installed_frame_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Plugins list
        columns = ("name", "version", "status")
        self.plugin_tree = ttk.Treeview(installed_frame_inner, columns=columns, show="headings")
        
        # Set column headings
        self.plugin_tree.heading("name", text="Name")
        self.plugin_tree.heading("version", text="Version")
        self.plugin_tree.heading("status", text="Status")
        
        # Configure columns
        self.plugin_tree.column("name", width=250)
        self.plugin_tree.column("version", width=100)
        self.plugin_tree.column("status", width=100)
        
        # Add scrollbar
        plugin_scroll = ttk.Scrollbar(installed_frame_inner, orient=tk.VERTICAL, command=self.plugin_tree.yview)
        self.plugin_tree.configure(yscrollcommand=plugin_scroll.set)
        
        # Pack treeview and scrollbar
        plugin_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.plugin_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Populate the list with installed plugins
        plugins = self.plugin_manager.get_plugins()
        for plugin_id, plugin_info in plugins.items():
            self.plugin_tree.insert(
                "", tk.END,
                values=(
                    plugin_info.get("name", plugin_id),
                    plugin_info.get("version", "1.0.0"),
                    plugin_info.get("status", "Active")
                )
            )
        
        # Plugin action buttons
        button_frame = ttk.Frame(installed_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            button_frame, text="Configure",
            command=lambda: self.configure_plugin()
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, text="Enable",
            command=lambda: self.toggle_plugin(True)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, text="Disable",
            command=lambda: self.toggle_plugin(False)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, text="Uninstall",
            command=lambda: self.uninstall_plugin()
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, text="Update",
            command=lambda: self.update_plugin()
        ).pack(side=tk.LEFT, padx=5)
        
        # Available plugins tab content
        ttk.Label(available_frame, text="Plugins Repository:").pack(anchor=tk.W, padx=10, pady=5)
        
        # Placeholder for available plugins (in a real app, this would retrieve from a repository)
        available_list = tk.Listbox(available_frame)
        available_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Populate with sample data
        for i in range(5):
            available_list.insert(tk.END, f"Sample Plugin {i+1}")
        
        # Plugin repository buttons
        repo_button_frame = ttk.Frame(available_frame)
        repo_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            repo_button_frame, text="Install",
            command=lambda: self.install_plugin_from_repo()
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            repo_button_frame, text="Refresh List",
            command=lambda: self.refresh_plugin_list()
        ).pack(side=tk.LEFT, padx=5)
        
        # Settings tab content
        ttk.Label(settings_frame, text="Plugin Settings:").pack(anchor=tk.W, padx=10, pady=5)
        
        # Plugin directory
        dir_frame = ttk.Frame(settings_frame)
        dir_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dir_frame, text="Plugin Directory:").pack(side=tk.LEFT)
        
        plugin_dir_var = tk.StringVar(value=self.config.get("plugins_directory", "plugins"))
        dir_entry = ttk.Entry(dir_frame, textvariable=plugin_dir_var, width=40)
        dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(
            dir_frame, text="Browse",
            command=lambda: plugin_dir_var.set(filedialog.askdirectory(
                initialdir=plugin_dir_var.get()
            ))
        ).pack(side=tk.LEFT, padx=5)
        
        # Auto-update
        auto_update_var = tk.BooleanVar(value=self.config.get("auto_update_plugins", False))
        ttk.Checkbutton(
            settings_frame, text="Automatically check for plugin updates",
            variable=auto_update_var
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Plugin security
        security_frame = ttk.LabelFrame(settings_frame, text="Security")
        security_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Verify plugins
        verify_var = tk.BooleanVar(value=self.config.get("verify_plugins", True))
        ttk.Checkbutton(
            security_frame, text="Verify plugins before installation",
            variable=verify_var
        ).pack(anchor=tk.W, padx=5, pady=5)
        
        # Sandbox plugins
        sandbox_var = tk.BooleanVar(value=self.config.get("sandbox_plugins", True))
        ttk.Checkbutton(
            security_frame, text="Run plugins in sandbox mode",
            variable=sandbox_var
        ).pack(anchor=tk.W, padx=5, pady=5)
        
        # Save button
        ttk.Button(
            settings_frame, text="Save Settings",
            command=lambda: self.save_plugin_settings(
                plugin_dir_var.get(),
                auto_update_var.get(),
                verify_var.get(),
                sandbox_var.get()
            )
        ).pack(anchor=tk.E, padx=10, pady=10)
        
        # Close button at bottom
        ttk.Button(
            manager_window, text="Close",
            command=manager_window.destroy
        ).pack(anchor=tk.E, padx=10, pady=10)
    
    def save_plugin_settings(self, plugin_dir: str, auto_update: bool, verify: bool, sandbox: bool):
        """Save plugin settings to configuration"""
        self.config["plugins_directory"] = plugin_dir
        self.config["auto_update_plugins"] = auto_update
        self.config["verify_plugins"] = verify
        self.config["sandbox_plugins"] = sandbox
        
        self.save_config()
        
        self.show_message(
            "Settings Saved",
            "Plugin settings have been saved.",
            "info"
        )
        
        # Reload plugins if directory changed
        if plugin_dir != self.plugin_manager.plugin_dir:
            self.plugin_manager.set_plugin_dir(plugin_dir)
            self.plugin_manager.reload_plugins()
    
    def configure_plugin(self):
        """Configure the selected plugin"""
        selected = self.plugin_tree.selection()
        if not selected:
            self.show_message(
                "No Plugin Selected",
                "Please select a plugin to configure.",
                "warning"
            )
            return
            
        # Get the plugin name from the selected item
        plugin_name = self.plugin_tree.item(selected[0], 'values')[0]
        
        # In a real app, display plugin-specific configuration dialog
        self.show_message(
            "Configuration",
            f"Configure plugin '{plugin_name}' (Not implemented in sample)",
            "info"
        )
    
    def toggle_plugin(self, enable: bool):
        """Enable or disable the selected plugin"""
        selected = self.plugin_tree.selection()
        if not selected:
            self.show_message(
                "No Plugin Selected",
                "Please select a plugin to toggle.",
                "warning"
            )
            return
            
        # Get the plugin name from the selected item
        plugin_name = self.plugin_tree.item(selected[0], 'values')[0]
        status = "enabled" if enable else "disabled"
        
        # In a real app, enable or disable the plugin
        self.show_message(
            "Plugin Status",
            f"Plugin '{plugin_name}' has been {status} (Not implemented in sample)",
            "info"
        )
    
    def uninstall_plugin(self):
        """Uninstall the selected plugin"""
        selected = self.plugin_tree.selection()
        if not selected:
            self.show_message(
                "No Plugin Selected",
                "Please select a plugin to uninstall.",
                "warning"
            )
            return
            
        # Get the plugin name from the selected item
        plugin_name = self.plugin_tree.item(selected[0], 'values')[0]
        
        # Confirm uninstallation
        confirm = messagebox.askyesno(
            "Confirm Uninstallation",
            f"Are you sure you want to uninstall the plugin '{plugin_name}'?"
        )
        
        if confirm:
            # In a real app, uninstall the plugin
            self.show_message(
                "Plugin Uninstalled",
                f"Plugin '{plugin_name}' has been uninstalled (Not implemented in sample)",
                "info"
            )
    
    def update_plugin(self):
        """Update the selected plugin"""
        selected = self.plugin_tree.selection()
        if not selected:
            self.show_message(
                "No Plugin Selected",
                "Please select a plugin to update.",
                "warning"
            )
            return
            
        # Get the plugin name from the selected item
        plugin_name = self.plugin_tree.item(selected[0], 'values')[0]
        
        # In a real app, check for and install updates
        self.show_message(
            "Plugin Update",
            f"Plugin '{plugin_name}' is up to date (Not implemented in sample)",
            "info"
        )
    
    def install_plugin_dialog(self):
        """Show dialog to install plugin from file"""
        plugin_file = filedialog.askopenfilename(
            title="Install Plugin",
            filetypes=[
                ("Python files", "*.py"),
                ("ZIP archives", "*.zip"),
                ("All files", "*.*")
            ]
        )
        
        if plugin_file:
            # In a real app, validate and install the plugin
            plugin_name = os.path.basename(plugin_file)
            
            self.show_message(
                "Plugin Installation",
                f"Plugin '{plugin_name}' has been installed (Not implemented in sample)",
                "info"
            )
    
    def install_plugin_from_repo(self):
        """Install selected plugin from repository"""
        self.show_message(
            "Plugin Installation",
            "Plugin installation from repository not implemented in sample",
            "info"
        )
    
    def refresh_plugin_list(self):
        """Refresh the list of available plugins"""
        self.show_message(
            "Refresh List",
            "Plugin list refresh not implemented in sample",
            "info"
        )
    
    def run_plugin(self, plugin_id: str):
        """
        Run a specific plugin
        
        Args:
            plugin_id: ID of the plugin to run
        """
        # In a real app, execute the plugin with proper parameters
        self.show_message(
            "Run Plugin",
            f"Running plugin '{plugin_id}' (Not implemented in sample)",
            "info"
        )
    
    def plugin_settings_dialog(self):
        """Show plugin settings dialog"""
        # In a real implementation, this might show a dialog to configure
        # global plugin settings or select which plugins to use
        self.plugin_manager_dialog()
    
    # Search and results methods
    def start_search(self):
        """Start the search process"""
        if not self.target_var.get():
            self.show_message(
                "Missing Target",
                "Please enter a target to search for.",
                "warning"
            )
            return
        
        if self.search_running:
            self.show_message(
                "Search in Progress",
                "A search is already running. Please wait for it to complete or cancel it.",
                "warning"
            )
            return
        
        # Set search state
        self.search_running = True
        self.status_var.set("Search started...")
        
        # Show progress bar
        self.show_progress(True)
        
        # Gather search parameters
        search_params = {
            "target": self.target_var.get(),
            "target_type": self.target_type_var.get(),
            "location": self.location_var.get(),
            "profile": self.profile_var.get(),
            "depth": self.depth_var.get(),
            "limit": self.limit_var.get(),
            "sources": {source: var.get() for source, var in self.source_vars.items()}
        }
        
        # Add date range if enabled
        if self.enable_time_var.get():
            search_params["start_date"] = self.start_date_var.get()
            search_params["end_date"] = self.end_date_var.get()
        
        # Start search in a background thread
        threading.Thread(
            target=self._run_search,
            args=(search_params,),
            daemon=True
        ).start()
    
    def _run_search(self, params: Dict[str, Any]):
        """
        Run the search in a background thread
        
        Args:
            params: Search parameters
        """
        try:
            # In a real app, this would call the search engine with parameters
            # For this sample, we'll simulate a search with a delay
            
            # Simulated search progress
            total_steps = 10
            for i in range(total_steps):
                # Update progress
                progress = (i + 1) * 100 / total_steps
                self.root.after(0, lambda p=progress: self.update_progress(p))
                
                # Simulate work
                import time
                time.sleep(0.5)
            
            # Simulated results (in a real app, this would be actual search results)
            results = [
                {
                    "item": f"Result {i+1} for {params['target']}",
                    "source": ["Twitter", "Facebook", "LinkedIn", "Instagram", "Public Records"][i % 5],
                    "type": ["Profile", "Post", "Image", "Document", "Contact"][i % 5],
                    "date": "2023-05-15",
                    "confidence": ["High", "Medium", "Low"][i % 3]
                }
                for i in range(20)
            ]
            
            # Save results to project if open
            if self.current_project:
                self.project_manager.update_project_results(results)
            
            # Store results locally
            self.results_data = results
            
            # Update UI in main thread
            self.root.after(0, self._search_complete)
            
        except Exception as e:
            logger.error(f"Search error: {e}", exc_info=True)
            self.root.after(0, lambda: self._search_error(str(e)))
        finally:
            # Make sure we reset the search state even if there's an error
            self.search_running = False
            
    def _search_complete(self):
        """Handle successful search completion"""
        # Update UI
        self.status_var.set(f"Search completed. Found {len(self.results_data)} results.")
        self.show_progress(False)
        
        # Populate results tree
        self.populate_results_tree()
        
        # Switch to results tab
        self.notebook.select(2)  # Results tab (index 2)
    
    def _search_error(self, error_message: str):
        """Handle search error"""
        # Update UI
        self.status_var.set("Search failed")
        self.show_progress(False)
        
        # Show error message
        self.show_message(
            "Search Error",
            f"Failed to complete search: {error_message}",
            "error"
        )
    
    def populate_results_tree(self):
        """Populate the results tree with current results data"""
        # Clear existing results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        # Add results to tree
        for result in self.results_data:
            self.results_tree.insert(
                "", tk.END,
                text=result.get("item", "Unknown"),
                values=(
                    result.get("source", "Unknown"),
                    result.get("type", "Unknown"),
                    result.get("date", "Unknown"),
                    result.get("confidence", "Low")
                )
            )
        
        # Update available sources for filtering
        self.update_filter_sources()
    
    def update_filter_sources(self):
        """Update source filter dropdown with available sources"""
        sources = set()
        
        # Collect all unique sources from results
        for result in self.results_data:
            source = result.get("source", "Unknown")
            if source:
                sources.add(source)
        
        # Get sorted list of sources
        source_list = sorted(list(sources))
        
        # Update combobox values
        if source_list:
            self.filter_source_combo['values'] = ["All"] + source_list
        else:
            self.filter_source_combo['values'] = ["All"]
            
        # Reset to "All"
        self.filter_source_var.set("All")
    
    def apply_filter(self):
        """Apply filter to results view"""
        filter_text = self.filter_var.get().lower()
        filter_source = self.filter_source_var.get()
        
        # Clear current display
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Apply filters
        for result in self.results_data:
            # Check source filter
            if filter_source != "All" and result.get("source") != filter_source:
                continue
                
            # Check text filter
            if filter_text and filter_text not in result.get("item", "").lower():
                continue
                
            # Add result to tree
            self.results_tree.insert(
                "", tk.END,
                text=result.get("item", "Unknown"),
                values=(
                    result.get("source", "Unknown"),
                    result.get("type", "Unknown"),
                    result.get("date", "Unknown"),
                    result.get("confidence", "Low")
                )
            )
        
        # Update status bar
        filtered_count = len(self.results_tree.get_children())
        total_count = len(self.results_data)
        self.status_var.set(f"Showing {filtered_count} of {total_count} results")
    
    def clear_filter(self):
        """Clear filters and show all results"""
        self.filter_var.set("")
        self.filter_source_var.set("All")
        self.populate_results_tree()
    
    def view_result_details(self, item_id=None):
        """
        View details for a specific result
        
        Args:
            item_id: Optional tree item ID. If None, use selection.
        """
        # Get selected item if not specified
        if item_id is None:
            selected = self.results_tree.selection()
            if not selected:
                self.show_message(
                    "No Selection",
                    "Please select a result to view.",
                    "warning"
                )
                return
            item_id = selected[0]
        
        # Get item text and values
        item_text = self.results_tree.item(item_id, 'text')
        item_values = self.results_tree.item(item_id, 'values')
        
        # Find corresponding data
        result = None
        for r in self.results_data:
            if r.get("item") == item_text:
                result = r
                break
        
        if not result:
            self.show_message(
                "Error",
                "Could not find result details.",
                "error"
            )
            return
            
        # Create details dialog
        details_window = tk.Toplevel(self.root)
        details_window.title("Result Details")
        details_window.geometry("600x400")
        details_window.transient(self.root)
        details_window.grab_set()
        
        # Details header
        ttk.Label(
            details_window, 
            text=item_text,
            font=("TkDefaultFont", 14, "bold")
        ).pack(pady=10)
        
        # Information frame
        info_frame = ttk.LabelFrame(details_window, text="Information")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add fields in a grid
        fields = [
            ("Source", result.get("source", "Unknown")),
            ("Type", result.get("type", "Unknown")),
            ("Date", result.get("date", "Unknown")),
            ("Confidence", result.get("confidence", "Low")),
            # Add any additional fields here
        ]
        
        for i, (label, value) in enumerate(fields):
            ttk.Label(info_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            ttk.Label(info_frame, text=value).grid(row=i, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Additional details
        details_frame = ttk.LabelFrame(details_window, text="Details")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Details text widget
        details_text = tk.Text(details_frame, wrap=tk.WORD)
        details_scroll = ttk.Scrollbar(details_frame, command=details_text.yview)
        details_text.configure(yscrollcommand=details_scroll.set)
        
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        details_text.pack(fill=tk.BOTH, expand=True)
        
        # Insert details (in a real app, this would include all result data)
        details_text.insert(tk.END, f"Details for {item_text}\n\n")
        details_text.insert(tk.END, f"This is a simulated result entry for demonstration purposes.\n\n")
        details_text.insert(tk.END, f"In a real application, this would contain the full details of the result item, including any metadata, content, links, and other associated information.\n\n")
        details_text.insert(tk.END, f"Source: {result.get('source', 'Unknown')}\n")
        details_text.insert(tk.END, f"Type: {result.get('type', 'Unknown')}\n")
        details_text.insert(tk.END, f"Date: {result.get('date', 'Unknown')}\n")
        details_text.insert(tk.END, f"Confidence: {result.get('confidence', 'Low')}\n")
        
        # Make text read-only
        details_text.configure(state=tk.DISABLED)
        
        # Actions frame
        actions_frame = ttk.Frame(details_window)
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            actions_frame, text="Close",
            command=details_window.destroy
        ).pack(side=tk.RIGHT)
        
        ttk.Button(
            actions_frame, text="Export",
            command=lambda: self.export_result_details(result)
        ).pack(side=tk.RIGHT, padx=5)
    
    def export_result_details(self, result: Dict[str, Any]):
        """
        Export details of a specific result
        
        Args:
            result: Result data to export
        """
        # Create file dialog
        file_path = filedialog.asksaveasfilename(
            title="Export Result",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(result, f, indent=4)
                    
                self.show_message(
                    "Export Complete",
                    f"Result exported to {file_path}",
                    "info"
                )
            except Exception as e:
                logger.error(f"Failed to export result: {e}", exc_info=True)
                self.show_message(
                    "Export Error",
                    f"Failed to export result: {e}",
                    "error"
                )
    
    def remove_result(self, item_id):
        """
        Remove a result from the results list
        
        Args:
            item_id: Tree item ID to remove
        """
        # Get item text
        item_text = self.results_tree.item(item_id, 'text')
        
        # Confirm removal
        confirm = messagebox.askyesno(
            "Confirm Removal",
            f"Are you sure you want to remove '{item_text}' from results?"
        )
        
        if not confirm:
            return
            
        # Remove from results data
        self.results_data = [r for r in self.results_data if r.get("item") != item_text]
        
        # Remove from tree
        self.results_tree.delete(item_id)
        
        # Update project if open
        if self.current_project:
            self.project_manager.update_project_results(self.results_data)
            
        # Update status
        self.status_var.set(f"Result removed. {len(self.results_data)} results remaining.")
    
    def copy_selected(self):
        """Copy selected result data to clipboard"""
        selected = self.results_tree.selection()
        if not selected:
            return
            
        # Get item text
        item_text = self.results_tree.item(selected[0], 'text')
        
        # Copy to clipboard
        self.root.clipboard_clear()
        self.root.clipboard_append(item_text)
        
        self.status_var.set(f"Copied: {item_text}")
    
    def select_all(self):
        """Select all results in the tree"""
        for item in self.results_tree.get_children():
            self.results_tree.selection_add(item)
    
    def find_in_results(self):
        """Show dialog to find text in results"""
        search_text = tk.simpledialog.askstring(
            "Find in Results",
            "Enter text to find:"
        )
        
        if not search_text:
            return
            
        # Clear current selection
        for item in self.results_tree.selection():
            self.results_tree.selection_remove(item)
            
        # Set filter text
        self.filter_var.set(search_text)
        
        # Apply filter
        self.apply_filter()
    
    # Visualization methods
    def generate_visualization(self):
        """Generate visualization based on selected options"""
        viz_type = self.viz_var.get()
        data_source = self.data_source_var.get()
        
        if not self.results_data:
            self.show_message(
                "No Data",
                "There is no data to visualize.",
                "warning"
            )
            return
            
        # Get filtered data
        filtered_data = self._get_filtered_data_for_visualization()
        
        if not filtered_data:
            self.show_message(
                "No Data",
                "No data matches your filter criteria.",
                "warning"
            )
            return
            
        # Show progress
        self.status_var.set(f"Generating {viz_type} visualization...")
        self.show_progress(True)
        
        # Generate visualization in a thread
        threading.Thread(
            target=self._generate_visualization_thread,
            args=(viz_type, filtered_data),
            daemon=True
        ).start()
    
    def _get_filtered_data_for_visualization(self) -> List[Dict[str, Any]]:
        """
        Get filtered data for visualization based on current settings
        
        Returns:
            Filtered list of result data
        """
        # Start with all data
        filtered_data = self.results_data[:]
        
        # Filter by source
        data_source = self.data_source_var.get()
        if data_source != "All Results":
            if data_source == "Social Media Only":
                social_sources = ["Twitter", "Facebook", "LinkedIn", "Instagram"]
                filtered_data = [r for r in filtered_data if r.get("source") in social_sources]
            elif data_source == "Public Records Only":
                public_sources = ["Public Records", "Government Records"]
                filtered_data = [r for r in filtered_data if r.get("source") in public_sources]
                
        # Filter by date range if enabled
        if self.use_date_range_var.get():
            # In a real app, parse dates and filter based on them
            pass
            
        return filtered_data
    
    def _generate_visualization_thread(self, viz_type: str, data: List[Dict[str, Any]]):
        """
        Generate visualization in a background thread
        
        Args:
            viz_type: Type of visualization to generate
            data: Data to visualize
        """
        try:
            import time
            # Simulate processing delay
            time.sleep(1)
            
            # In a real app, generate the actual visualization here
            # For this sample, we'll just use a placeholder
            
            self.root.after(0, lambda: self._show_visualization(viz_type))
            
        except Exception as e:
            logger.error(f"Visualization error: {e}", exc_info=True)
            self.root.after(0, lambda: self._visualization_error(str(e)))
        finally:
            self.root.after(0, lambda: self.show_progress(False))
    
    def _show_visualization(self, viz_type: str):
        """
        Show the generated visualization
        
        Args:
            viz_type: Type of visualization that was generated
        """
        # Hide placeholder
        self.viz_placeholder.pack_forget()
        
        # Configure canvas
        self.viz_canvas.delete("all")  # Clear canvas
        self.viz_canvas.config(width=600, height=400)
        
        # Draw placeholder visualization
        if viz_type == "Network Graph":
            self._draw_network_graph()
        elif viz_type == "Timeline":
            self._draw_timeline()
        elif viz_type == "Heatmap":
            self._draw_heatmap()
        elif viz_type == "Word Cloud":
            self._draw_word_cloud()
        elif viz_type == "Relationship Diagram":
            self._draw_relationship_diagram()
        
        # Show canvas
        self.viz_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Update status
        self.status_var.set(f"{viz_type} visualization created.")
    
    def _visualization_error(self, error_message: str):
        """Handle visualization error"""
        # Show placeholder
        self.viz_placeholder.pack(expand=True)
        
        # Hide canvas
        self.viz_canvas.pack_forget()
        
        # Show error message
        self.show_message(
            "Visualization Error",
            f"Failed to generate visualization: {error_message}",
            "error"
        )
        
        # Update status
        self.status_var.set("Visualization failed.")
    
    def _draw_network_graph(self):
        """Draw a placeholder network graph"""
        # Get canvas dimensions
        width = self.viz_canvas.winfo_width()
        height = self.viz_canvas.winfo_height()
        
        # Draw nodes
        nodes = 8
        node_size = 20
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 3
        
        # Create nodes in a circle
        node_positions = []
        for i in range(nodes):
            angle = 2 * 3.14159 * i / nodes
            x = center_x + radius * 0.8 * -1 * (i % 2 * 2 - 1) * 0.8 * (i % 3) / 3 * 0.6
            y = center_y + radius * 0.8 * (i % 4) / 4 * 0.7
            node_positions.append((x, y))
            self.viz_canvas.create_oval(x-node_size/2, y-node_size/2, x+node_size/2, y+node_size/2, fill="#4287f5")
        
        # Create lines between nodes
        for i in range(nodes):
            for j in range(i+1, nodes):
                # Only connect some nodes
                if (i + j) % 3 == 0:
                    self.viz_canvas.create_line(node_positions[i][0], node_positions[i][1], 
                                             node_positions[j][0], node_positions[j][1],
                                             width=2, fill="#aaaaaa")
        
        # Add a title
        self.viz_canvas.create_text(width/2, 20, text="Network Graph Visualization", font=("TkDefaultFont", 12, "bold"))
    
    def _draw_timeline(self):
        """Draw a placeholder timeline"""
        # Get canvas dimensions
        width = self.viz_canvas.winfo_width()
        height = self.viz_canvas.winfo_height()
        
        # Draw timeline axis
        margin = 50
        axis_y = height - margin
        self.viz_canvas.create_line(margin, axis_y, width-margin, axis_y, width=2)
        
        # Draw time markers
        num_markers = 5
        marker_width = (width - 2 * margin) / (num_markers - 1)
        
        for i in range(num_markers):
            x = margin + i * marker_width
            self.viz_canvas.create_line(x, axis_y, x, axis_y + 10, width=2)
            self.viz_canvas.create_text(x, axis_y + 20, text=f"2023-{i+1:02d}")
        
        # Draw events
        for i in range(10):
            x = margin + (width - 2 * margin) * i / 10
            y = axis_y - 10 - random.randint(10, 100)
            self.viz_canvas.create_oval(x-5, y-5, x+5, y+5, fill="#ff7700")
            self.viz_canvas.create_line(x, y+5, x, axis_y, width=1, dash=(4, 4))
            
        # Add a title
        self.viz_canvas.create_text(width/2, 20, text="Timeline Visualization", font=("TkDefaultFont", 12, "bold"))
    
    def _draw_heatmap(self):
        """Draw a placeholder heatmap"""
        # Get canvas dimensions
        width = self.viz_canvas.winfo_width()
        height = self.viz_canvas.winfo_height()
        
        # Draw grid
        margin = 50
        grid_width = width - 2 * margin
        grid_height = height - 2 * margin
        
        rows, cols = 8, 8
        cell_width = grid_width / cols
        cell_height = grid_height / rows
        
        for row in range(rows):
            for col in range(cols):
                # Generate a color intensity based on position
                intensity = (row + col) / (rows + cols)
                color = self._get_heatmap_color(intensity)
                
                # Draw cell
                x1 = margin + col * cell_width
                y1 = margin + row * cell_height
                x2 = x1 + cell_width
                y2 = y1 + cell_height
                
                self.viz_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                
        # Add a title
        self.viz_canvas.create_text(width/2, 20, text="Heatmap Visualization", font=("TkDefaultFont", 12, "bold"))
    
    def _get_heatmap_color(self, intensity: float) -> str:
        """
        Get a color hex code for a heatmap based on intensity
        
        Args:
            intensity: Value between 0 and 1
            
        Returns:
            Hex color code
        """
        # Convert to a color from blue (cold) to red (hot)
        r = int(255 * intensity)
        g = int(255 * (1 - abs(2 * intensity - 1)))
        b = int(255 * (1 - intensity))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _draw_word_cloud(self):
        """Draw a placeholder word cloud"""
        # Get canvas dimensions
        width = self.viz_canvas.winfo_width()
        height = self.viz_canvas.winfo_height()
        
        # Sample words with sizes
        words = [
            ("Social Media", 36),
            ("Profile", 24),
            ("Location", 32),
            ("Email", 18),
            ("Contact", 20),
            ("Image", 16),
            ("Document", 22),
            ("Public", 28),
            ("Post", 26),
            ("Network", 30)
        ]
        
        # Draw words at random positions
        import random
        random.seed(42)  # For reproducibility
        
        for word, size in words:
            x = margin = 50
            y = margin = 50
            x = random.randint(100, width - 100)
            y = random.randint(100, height - 100)
            
            self.viz_canvas.create_text(x, y, text=word, font=("TkDefaultFont", size))
            
        # Add a title
        self.viz_canvas.create_text(width/2, 20, text="Word Cloud Visualization", font=("TkDefaultFont", 12, "bold"))
    
    def _draw_relationship_diagram(self):
        """Draw a placeholder relationship diagram"""
        # Get canvas dimensions
        width = self.viz_canvas.winfo_width()
        height = self.viz_canvas.winfo_height()
        
        # Central node
        center_x = width / 2
        center_y = height / 2
        
        self.viz_canvas.create_oval(center_x-30, center_y-30, center_x+30, center_y+30, fill="#4287f5")
        self.viz_canvas.create_text(center_x, center_y, text="Target", fill="white", font=("TkDefaultFont", 10, "bold"))
        
        # Related nodes
        related_items = ["Email", "Phone", "Address", "Social", "Work", "Family"]
        node_radius = 20
        
        for i, item in enumerate(related_items):
            angle = 2 * 3.14159 * i / len(related_items)
            distance = 150
            
            x = center_x + distance * 0.8 * math.cos(angle)
            y = center_y + distance * 0.8 * math.sin(angle)
            
            # Draw connection
            self.viz_canvas.create_line(center_x, center_y, x, y, width=2, fill="#aaaaaa")
            
            # Draw node
            self.viz_canvas.create_oval(x-node_radius, y-node_radius, x+node_radius, y+node_radius, fill="#f542a7")
            self.viz_canvas.create_text(x, y, text=item, fill="white", font=("TkDefaultFont", 9))
            
        # Add a title
        self.viz_canvas.create_text(width/2, 20, text="Relationship Diagram", font=("TkDefaultFont", 12, "bold"))
    
    def export_visualization(self):
        """Export the current visualization"""
        if not hasattr(self, 'viz_canvas') or not self.viz_canvas.winfo_ismapped():
            self.show_message(
                "No Visualization",
                "There is no visualization to export.",
                "warning"
            )
            return
            
        # Create file dialog
        file_path = filedialog.asksaveasfilename(
            title="Export Visualization",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # In a real app, this would capture the canvas as an image
                self.show_message(
                    "Export Failed",
                    "Visualization export not implemented in this sample.",
                    "warning"
                )
                
            except Exception as e:
                logger.error(f"Failed to export visualization: {e}", exc_info=True)
                self.show_message(
                    "Export Error",
                    f"Failed to export visualization: {e}",
                    "error"
                )
    
    # Report methods
    def generate_report(self):
        """Generate report based on selected options"""
        report_type = self.report_type_var.get()
        report_format = self.report_format_var.get()
        
        if not self.results_data:
            self.show_message(
                "No Data",
                "There is no data for the report.",
                "warning"
            )
            return
        
        # Show progress
        self.status_var.set(f"Generating {report_type} in {report_format} format...")
        self.show_progress(True)
        
        # Generate report in a thread
        threading.Thread(
            target=self._generate_report_thread,
            args=(report_type, report_format),
            daemon=True
        ).start()
    
    def _generate_report_thread(self, report_type: str, report_format: str):
        """
        Generate report in a background thread
        
        Args:
            report_type: Type of report to generate
            report_format: Format of the report
        """
        try:
            import time
            # Simulate processing delay
            time.sleep(1)
            
            # In a real app, generate the actual report here
            # For this sample, we'll just use a placeholder
            
            self.root.after(0, lambda: self._show_report_preview(report_type, report_format))
            
        except Exception as e:
            logger.error(f"Report generation error: {e}", exc_info=True)
            self.root.after(0, lambda: self._report_error(str(e)))
        finally:
            self.root.after(0, lambda: self.show_progress(False))
    
    def _show_report_preview(self, report_type: str, report_format: str):
        """
        Show report preview
        
        Args:
            report_type: Type of report that was generated
            report_format: Format of the report
        """
        # Hide placeholder
        self.report_preview_label.pack_forget()
        
        # Configure text widget
        self.report_preview.delete(1.0, tk.END)
        
        # Add report content
        self.report_preview.insert(tk.END, f"{report_type}\n", "title")
        self.report_preview.insert(tk.END, f"Format: {report_format}\n\n", "subtitle")
        
        # Add report sections
        self.report_preview.insert(tk.END, "Executive Summary\n\n", "section")
        self.report_preview.insert(tk.END, "This report provides an analysis of the search results for the specified target. ")
        self.report_preview.insert(tk.END, "The search yielded a total of ")
        self.report_preview.insert(tk.END, f"{len(self.results_data)} results ", "highlight")
        self.report_preview.insert(tk.END, "across multiple data sources.\n\n")
        
        self.report_preview.insert(tk.END, "Key Findings\n\n", "section")
        self.report_preview.insert(tk.END, "• Found social media profiles on multiple platforms\n")
        self.report_preview.insert(tk.END, "• Identified public records associated with the target\n")
        self.report_preview.insert(tk.END, "• Discovered relationships with other entities\n")
        self.report_preview.insert(tk.END, "• Located potential contact information\n\n")
        
        self.report_preview.insert(tk.END, "Results Breakdown\n\n", "section")
        
        # Create results summary by source
        sources = {}
        for result in self.results_data:
            source = result.get("source", "Unknown")
            sources[source] = sources.get(source, 0) + 1
            
        for source, count in sources.items():
            self.report_preview.insert(tk.END, f"{source}: {count} results\n")
            
        self.report_preview.insert(tk.END, "\n")
        
        # Add disclaimer
        self.report_preview.insert(tk.END, "Note: This is a sample report for demonstration purposes only.\n")
        
        # Configure text tags
        self.report_preview.tag_configure("title", font=("TkDefaultFont", 16, "bold"), justify="center")
        self.report_preview.tag_configure("subtitle", font=("TkDefaultFont", 10), justify="center")
        self.report_preview.tag_configure("section", font=("TkDefaultFont", 12, "bold"))
        self.report_preview.tag_configure("highlight", font=("TkDefaultFont", 10, "bold"))
        
        # Show report preview
        self.report_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.report_preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Update status
        self.status_var.set(f"{report_type} report generated.")
    
    def _report_error(self, error_message: str):
        """Handle report generation error"""
        # Update UI
        self.status_var.set("Report generation failed")
        
        # Show error message
        self.show_message(
            "Report Error",
            f"Failed to generate report: {error_message}",
            "error"
        )
    
    def view_recent_reports(self):
        """View list of recently generated reports"""
        # In a real app, this would show a list of saved reports
        self.show_message(
            "Recent Reports",
            "Recent reports feature not implemented in this sample.",
            "info"
        )
    
    # Utility methods
    def show_progress(self, show: bool):
        """Show or hide progress bar"""
        if show:
            self.progress_var.set(0)
            self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        else:
            self.progress_bar.pack_forget()
    
    def update_progress(self, progress: float):
        """Update progress bar value"""
        self.progress_var.set(progress)
        # Force update the display
        self.root.update_idletasks()
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Remove invalid characters from filename
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Replace invalid characters with underscores
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
            
        # Remove leading/trailing whitespace and periods
        filename = filename.strip().strip('.')
        
        return filename
    
    # General UI methods
    def show_preferences(self):
        """Show application preferences dialog"""
        # Create preferences dialog
        prefs_window = tk.Toplevel(self.root)
        prefs_window.title("Preferences")
        prefs_window.geometry("500x400")
        prefs_window.transient(self.root)
        prefs_window.grab_set()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(prefs_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General preferences tab
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        
        # Appearance preferences tab
        appearance_frame = ttk.Frame(notebook)
        notebook.add(appearance_frame, text="Appearance")
        
        # Data preferences tab
        data_frame = ttk.Frame(notebook)
        notebook.add(data_frame, text="Data")
        
        # General preferences
        ttk.Label(general_frame, text="General Settings").pack(anchor=tk.W, padx=10, pady=10)
        
        # Output directory
        dir_frame = ttk.Frame(general_frame)
        dir_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dir_frame, text="Output Directory:").pack(side=tk.LEFT)
        
        output_dir_var = tk.StringVar(value=self.config.get("output_directory", ""))
        dir_entry = ttk.Entry(dir_frame, textvariable=output_dir_var, width=30)
        dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(
            dir_frame, text="Browse",
            command=lambda: output_dir_var.set(filedialog.askdirectory(
                initialdir=output_dir_var.get()
            ))
        ).pack(side=tk.LEFT, padx=5)
        
        # Auto-save option
        auto_save_var = tk.BooleanVar(value=self.config.get("auto_save", True))
        ttk.Checkbutton(
            general_frame, text="Auto-save projects",
            variable=auto_save_var
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Update check
        auto_update_var = tk.BooleanVar(value=self.config.get("auto_check_updates", True))
        ttk.Checkbutton(
            general_frame, text="Automatically check for updates",
            variable=auto_update_var
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Appearance preferences
        ttk.Label(appearance_frame, text="Appearance Settings").pack(anchor=tk.W, padx=10, pady=10)
        
        # Theme selection
        theme_frame = ttk.Frame(appearance_frame)
        theme_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)
        
        theme_var = tk.StringVar(value=self.config.get("theme", "system"))
        themes = ["system", "light", "dark", "classic", "custom"]
        theme_combo = ttk.Combobox(theme_frame, textvariable=theme_var, values=themes, state="readonly", width=15)
        theme_combo.pack(side=tk.LEFT, padx=5)
        
        # Font size
        font_frame = ttk.Frame(appearance_frame)
        font_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(font_frame, text="Font Size:").pack(side=tk.LEFT)
        
        font_size_var = tk.IntVar(value=self.config.get("font_size", 10))
        font_size_spin = ttk.Spinbox(font_frame, from_=8, to=20, textvariable=font_size_var, width=5)
        font_size_spin.pack(side=tk.LEFT, padx=5)
        
        # Data preferences
        ttk.Label(data_frame, text="Data Settings").pack(anchor=tk.W, padx=10, pady=10)
        
        # Max results
        max_results_frame = ttk.Frame(data_frame)
        max_results_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(max_results_frame, text="Max Results Per Search:").pack(side=tk.LEFT)
        
        max_results_var = tk.IntVar(value=self.config.get("max_results", 1000))
        max_results_spin = ttk.Spinbox(max_results_frame, from_=100, to=10000, increment=100, textvariable=max_results_var, width=7)
        max_results_spin.pack(side=tk.LEFT, padx=5)
        
        # Cache data
        cache_var = tk.BooleanVar(value=self.config.get("cache_data", True))
        ttk.Checkbutton(
            data_frame, text="Cache search results on disk",
            variable=cache_var
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Cache expiration
        cache_exp_frame = ttk.Frame(data_frame)
        cache_exp_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(cache_exp_frame, text="Cache Expiration (days):").pack(side=tk.LEFT)
        
        cache_exp_var = tk.IntVar(value=self.config.get("cache_expiration_days", 30))
        cache_exp_spin = ttk.Spinbox(cache_exp_frame, from_=1, to=365, textvariable=cache_exp_var, width=5)
        cache_exp_spin.pack(side=tk.LEFT, padx=5)
        
        # API keys section
        api_frame = ttk.LabelFrame(data_frame, text="API Keys")
        api_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Manage API keys button
        ttk.Button(
            api_frame, text="Manage API Keys",
            command=self.show_api_keys_dialog
        ).pack(padx=10, pady=10)
        
        # OK/Cancel buttons
        button_frame = ttk.Frame(prefs_window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            button_frame, text="OK",
            command=lambda: self.save_preferences(
                prefs_window,
                output_dir_var.get(),
                auto_save_var.get(),
                auto_update_var.get(),
                theme_var.get(),
                font_size_var.get(),
                max_results_var.get(),
                cache_var.get(),
                cache_exp_var.get()
            )
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame, text="Cancel",
            command=prefs_window.destroy
        ).pack(side=tk.RIGHT, padx=5)
    
    def save_preferences(self, window, output_dir: str, auto_save: bool, 
                         auto_update: bool, theme: str, font_size: int,
                         max_results: int, cache_data: bool, cache_expiration: int):
        """
        Save preferences and close dialog
        
        Args:
            window: Preferences window to close
            output_dir: Output directory path
            auto_save: Auto-save setting
            auto_update: Auto-update check setting
            theme: UI theme
            font_size: Font size
            max_results: Maximum results per search
            cache_data: Whether to cache data
            cache_expiration: Cache expiration in days
        """
        try:
            # Update config
            self.config["output_directory"] = output_dir
            self.config["auto_save"] = auto_save
            self.config["auto_check_updates"] = auto_update
            self.config["theme"] = theme
            self.config["font_size"] = font_size
            self.config["max_results"] = max_results
            self.config["cache_data"] = cache_data
            self.config["cache_expiration_days"] = cache_expiration
            
            # Save to disk
            self.save_config()
            
            # Apply theme if changed
            self.apply_theme()
            
            # Close dialog
            window.destroy()
            
            # Show confirmation
            self.status_var.set("Preferences saved")
            
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}", exc_info=True)
            self.show_message(
                "Error",
                f"Failed to save preferences: {e}",
                "error"
            )
    
    def show_api_keys_dialog(self):
        """Show dialog to manage API keys"""
        # Create API keys dialog
        api_window = tk.Toplevel(self.root)
        api_window.title("API Keys")
        api_window.geometry("500x400")
        api_window.transient(self.root)
        api_window.grab_set()
        
        # API keys list frame
        list_frame = ttk.Frame(api_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Get current API keys
        api_keys = self.config.get("api_keys", {})
        
        # Create treeview for API keys
        columns = ("service", "key", "status")
        api_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        
        # Configure columns
        api_tree.heading("service", text="Service")
        api_tree.heading("key", text="API Key")
        api_tree.heading("status", text="Status")
        
        api_tree.column("service", width=150)
        api_tree.column("key", width=200)
        api_tree.column("status", width=80)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=api_tree.yview)
        api_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Pack tree and scrollbar
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        api_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Populate with API keys - mask the actual key values for security
        for service, key in api_keys.items():
            # Show only first 4 and last 4 characters of key, rest as asterisks
            masked_key = key[:4] + "****" + key[-4:] if len(key) > 8 else "****"
            api_tree.insert("", tk.END, values=(service, masked_key, "Valid"))
        
        # Buttons frame
        buttons_frame = ttk.Frame(api_window)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Add button
        ttk.Button(
            buttons_frame, text="Add Key",
            command=lambda: self.add_api_key(api_tree)
        ).pack(side=tk.LEFT, padx=5)
        
        # Edit button
        ttk.Button(
            buttons_frame, text="Edit Key",
            command=lambda: self.edit_api_key(api_tree)
        ).pack(side=tk.LEFT, padx=5)
        
        # Remove button
        ttk.Button(
            buttons_frame, text="Remove Key",
            command=lambda: self.remove_api_key(api_tree)
        ).pack(side=tk.LEFT, padx=5)
        
        # Close button
        ttk.Button(
            buttons_frame, text="Close",
            command=api_window.destroy
        ).pack(side=tk.RIGHT, padx=5)
    
    def add_api_key(self, tree):
        """
        Add a new API key
        
        Args:
            tree: API keys treeview
        """
        # Create add key dialog
        key_window = tk.Toplevel(self.root)
        key_window.title("Add API Key")
        key_window.geometry("400x150")
        key_window.transient(self.root)
        key_window.grab_set()
        
        # Service name
        ttk.Label(key_window, text="Service:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        service_var = tk.StringVar()
        ttk.Entry(key_window, textvariable=service_var, width=30).grid(row=0, column=1, padx=10, pady=10)
        
        # API key
        ttk.Label(key_window, text="API Key:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        key_var = tk.StringVar()
        ttk.Entry(key_window, textvariable=key_var, width=30, show="*").grid(row=1, column=1, padx=10, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(key_window)
        button_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        
        ttk.Button(
            button_frame, text="Save",
            command=lambda: self.save_api_key(key_window, tree, service_var.get(), key_var.get())
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, text="Cancel",
            command=key_window.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def save_api_key(self, window, tree, service: str, key: str):
        """
        Save API key to configuration
        
        Args:
            window: Dialog window to close
            tree: API keys treeview to update
            service: Service name
            key: API key value
        """
        if not service:
            self.show_message("Error", "Service name cannot be empty", "error")
            return
            
        if not key:
            self.show_message("Error", "API key cannot be empty", "error")
            return
        
        try:
            # Update config
            api_keys = self.config.get("api_keys", {})
            api_keys[service] = key
            self.config["api_keys"] = api_keys
            
            # Save config
            self.save_config()
            
            # Update tree
            masked_key = key[:4] + "****" + key[-4:] if len(key) > 8 else "****"
            tree.insert("", tk.END, values=(service, masked_key, "Valid"))
            
            # Close dialog
            window.destroy()
            
        except Exception as e:
            logger.error(f"Failed to save API key: {e}", exc_info=True)
            self.show_message("Error", f"Failed to save API key: {e}", "error")
    
    def edit_api_key(self, tree):
        """
        Edit selected API key
        
        Args:
            tree: API keys treeview
        """
        selected = tree.selection()
        if not selected:
            self.show_message("No Selection", "Please select an API key to edit", "warning")
            return
            
        # Get selected service
        service = tree.item(selected[0], "values")[0]
        
        # Get current key for this service
        api_keys = self.config.get("api_keys", {})
        current_key = api_keys.get(service, "")
        
        # Create edit key dialog
        key_window = tk.Toplevel(self.root)
        key_window.title(f"Edit API Key for {service}")
        key_window.geometry("400x150")
        key_window.transient(self.root)
        key_window.grab_set()
        
        # Service name (disabled)
        ttk.Label(key_window, text="Service:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        service_var = tk.StringVar(value=service)
        ttk.Entry(key_window, textvariable=service_var, state="disabled", width=30).grid(row=0, column=1, padx=10, pady=10)
        
        # API key
        ttk.Label(key_window, text="API Key:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        key_var = tk.StringVar(value=current_key)
        ttk.Entry(key_window, textvariable=key_var, width=30, show="*").grid(row=1, column=1, padx=10, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(key_window)
        button_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        
        ttk.Button(
            button_frame, text="Update",
            command=lambda: self.update_api_key(key_window, tree, selected[0], service, key_var.get())
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, text="Cancel",
            command=key_window.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def update_api_key(self, window, tree, item_id, service: str, key: str):
        """
        Update API key in configuration
        
        Args:
            window: Dialog window to close
            tree: API keys treeview to update
            item_id: Tree item ID
            service: Service name
            key: New API key value
        """
        if not key:
            self.show_message("Error", "API key cannot be empty", "error")
            return
        
        try:
            # Update config
            api_keys = self.config.get("api_keys", {})
            api_keys[service] = key
            self.config["api_keys"] = api_keys
            
            # Save config
            self.save_config()
            
            # Update tree
            masked_key = key[:4] + "****" + key[-4:] if len(key) > 8 else "****"
            tree.item(item_id, values=(service, masked_key, "Valid"))
            
            # Close dialog
            window.destroy()
            
        except Exception as e:
            logger.error(f"Failed to update API key: {e}", exc_info=True)
            self.show_message("Error", f"Failed to update API key: {e}", "error")
    
    def remove_api_key(self, tree):
        """
        Remove selected API key
        
        Args:
            tree: API keys treeview
        """
        selected = tree.selection()
        if not selected:
            self.show_message("No Selection", "Please select an API key to remove", "warning")
            return
            
        # Get selected service
        service = tree.item(selected[0], "values")[0]
        
        # Confirm removal
        confirm = messagebox.askyesno(
            "Confirm Removal",
            f"Are you sure you want to remove the API key for '{service}'?"
        )
        
        if not confirm:
            return
        
        try:
            # Update config
            api_keys = self.config.get("api_keys", {})
            if service in api_keys:
                del api_keys[service]
                self.config["api_keys"] = api_keys
                
                # Save config
                self.save_config()
                
                # Update tree
                tree.delete(selected[0])
                
        except Exception as e:
            logger.error(f"Failed to remove API key: {e}", exc_info=True)
            self.show_message("Error", f"Failed to remove API key: {e}", "error")
    
    def show_about(self):
        """Show about dialog with application information"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About CreepyAI")
        about_window.geometry("400x300")
        about_window.transient(self.root)
        about_window.grab_set()
        
        # App title
        ttk.Label(
            about_window, 
            text="CreepyAI OSINT Assistant",
            font=("TkDefaultFont", 16, "bold")
        ).pack(pady=10)
        
        # Version
        ttk.Label(
            about_window,
            text="Version 1.0.0"
        ).pack()
        
        # Description
        ttk.Label(
            about_window,
            text="A comprehensive tool for OSINT research,\ndata collection, and analysis.",
            justify=tk.CENTER
        ).pack(pady=10)
        
        # Copyright
        ttk.Label(
            about_window,
            text="© 2023 CreepyAI Team. All rights reserved."
        ).pack(pady=10)
        
        # Website link
        link_frame = ttk.Frame(about_window)
        link_frame.pack(pady=5)
        
        ttk.Label(
            link_frame,
            text="Visit our website:"
        ).pack(side=tk.LEFT)
        
        website_label = ttk.Label(
            link_frame,
            text="creepyai.example.com",
            foreground="blue",
            cursor="hand2"
        )
        website_label.pack(side=tk.LEFT, padx=5)
        website_label.bind("<Button-1>", lambda e: webbrowser.open("https://creepyai.example.com"))
        
        # Close button
        ttk.Button(
            about_window,
            text="Close",
            command=about_window.destroy
        ).pack(pady=20)
    
    def show_documentation(self, event=None):
        """Show documentation in web browser"""
        # In a real app, this would open actual documentation
        try:
            webbrowser.open("https://creepyai.example.com/docs")
            self.status_var.set("Documentation opened in web browser")
        except Exception as e:
            logger.error(f"Failed to open documentation: {e}")
            self.show_message(
                "Documentation Error",
                "Failed to open documentation. Please visit our website for help.",
                "error"
            )
    
    def show_logs(self):
        """Show application logs"""
        log_path = "creepyai.log"
        
        try:
            # Check if log file exists
            if not os.path.exists(log_path):
                self.show_message(
                    "No Logs",
                    "No log file found.",
                    "warning"
                )
                return
                
            # Create logs viewer dialog
            logs_window = tk.Toplevel(self.root)
            logs_window.title("Application Logs")
            logs_window.geometry("800x600")
            logs_window.transient(self.root)
            
            # Create text widget for logs
            logs_text = tk.Text(logs_window, wrap=tk.NONE)
            
            # Add scrollbars
            y_scroll = ttk.Scrollbar(logs_window, orient=tk.VERTICAL, command=logs_text.yview)
            x_scroll = ttk.Scrollbar(logs_window, orient=tk.HORIZONTAL, command=logs_text.xview)
            logs_text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
            
            # Pack everything
            y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            logs_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Load log file
            with open(log_path, 'r') as f:
                logs_content = f.read()
                
            # Insert log content and make read-only
            logs_text.insert(tk.END, logs_content)
            logs_text.configure(state=tk.DISABLED)
            
            # Scroll to end
            logs_text.see(tk.END)
            
            # Buttons
            button_frame = ttk.Frame(logs_window)
            button_frame.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Button(
                button_frame, text="Refresh",
                command=lambda: self.refresh_logs(logs_text, log_path)
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                button_frame, text="Clear Logs",
                command=lambda: self.clear_logs(logs_text, log_path)
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                button_frame, text="Close",
                command=logs_window.destroy
            ).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            logger.error(f"Failed to show logs: {e}", exc_info=True)
            self.show_message(
                "Error",
                f"Failed to show logs: {e}",
                "error"
            )
    
    def refresh_logs(self, logs_text, log_path):
        """
        Refresh log content in the viewer
        
        Args:
            logs_text: Text widget to update
            log_path: Path to log file
        """
        try:
            # Clear current content
            logs_text.configure(state=tk.NORMAL)
            logs_text.delete(1.0, tk.END)
            
            # Load log file
            with open(log_path, 'r') as f:
                logs_content = f.read()
                
            # Insert log content and make read-only
            logs_text.insert(tk.END, logs_content)
            logs_text.configure(state=tk.DISABLED)
            
            # Scroll to end
            logs_text.see(tk.END)
            
        except Exception as e:
            logger.error(f"Failed to refresh logs: {e}")
            self.show_message(
                "Error",
                f"Failed to refresh logs: {e}",
                "error"
            )
    
    def clear_logs(self, logs_text, log_path):
        """
        Clear log file
        
        Args:
            logs_text: Text widget to update
            log_path: Path to log file
        """
        try:
            # Confirm clear
            confirm = messagebox.askyesno(
                "Clear Logs",
                "Are you sure you want to clear all logs?\nThis cannot be undone."
            )
            
            if not confirm:
                return
                
            # Clear log file
            with open(log_path, 'w') as f:
                f.write("")
                
            # Update text widget
            logs_text.configure(state=tk.NORMAL)
            logs_text.delete(1.0, tk.END)
            logs_text.configure(state=tk.DISABLED)
            
            self.status_var.set("Logs cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear logs: {e}")
            self.show_message(
                "Error",
                f"Failed to clear logs: {e}",
                "error"
            )
    
    def check_for_updates(self):
        """Check for application updates"""
        # In a real app, this would contact a server to check for updates
        self.status_var.set("Checking for updates...")
        
        # Simulate update check with a short delay
        def check_updates_task():
            # Simulate network delay
            import time
            time.sleep(1.5)
            
            # In a real app, this would compare versions with a server
            # For this sample, we'll just simulate no updates
            self.root.after(0, lambda: self._show_update_result(False))
        
        # Run in thread to avoid freezing UI
        threading.Thread(target=check_updates_task, daemon=True).start()
    
    def _show_update_result(self, update_available, version=None):
        """
        Show update check result
        
        Args:
            update_available: Whether an update is available
            version: New version info if update is available
        """
        if update_available:
            # Show update available message with option to download
            result = messagebox.askyesno(
                "Update Available",
                f"A new version ({version}) is available. Would you like to download it now?",
                icon="info"
            )
            
            if result:
                # In a real app, this would open download URL or start updater
                webbrowser.open("https://creepyai.example.com/download")
                self.status_var.set("Opening download page...")
            else:
                self.status_var.set("Update available, but download was skipped")
        else:
            # Show up to date message
            messagebox.showinfo(
                "No Updates Available",
                "You are running the latest version of CreepyAI."
            )
            self.status_var.set("No updates available")
    
    def confirm_exit(self):
        """Ask for confirmation before exiting the application"""
        # Check if there's unsaved work
        has_unsaved_changes = False
        
        if self.current_project and self.project_manager.has_unsaved_changes():
            has_unsaved_changes = True
        
        if has_unsaved_changes:
            # Ask to save changes
            result = messagebox.askyesnocancel(
                "Exit CreepyAI",
                "You have unsaved changes. Would you like to save before exiting?",
                icon="warning"
            )
            
            if result is None:  # Cancel
                return
            elif result:  # Yes, save
                saved = self.save_project()
                if not saved:
                    # Save failed, ask if still want to exit
                    if not messagebox.askyesno(
                        "Save Failed",
                        "Failed to save project. Exit anyway?",
                        icon="warning"
                    ):
                        return
        else:
            # No unsaved changes, just confirm
            if not messagebox.askyesno(
                "Exit CreepyAI",
                "Are you sure you want to exit?",
                icon="question"
            ):
                return
        
        # Save application state
        self.save_config()
        
        # Exit the application
        self.root.destroy()

# Class definition for ProjectManager
class ProjectManager:
    """Manages CreepyAI projects"""
    
    def __init__(self, app):
        """
        Initialize the project manager with reference to main app
        
        Args:
            app: Main application instance
        """
        self.app = app
        self.project_data = None
        self.unsaved_changes = False
    
    def create_project(self, name: str, project_path: str) -> bool:
        """
        Create a new project at specified path
        
        Args:
            name: Project name
            project_path: Project directory path
            
        Returns:
            True if project created successfully
        """
        try:
            # Create project directory if needed
            if not os.path.exists(project_path):
                os.makedirs(project_path, exist_ok=True)
            
            # Create basic project structure
            self.project_data = {
                "name": name,
                "created": self.get_timestamp(),
                "modified": self.get_timestamp(),
                "target": {},
                "results": [],
                "notes": [],
                "settings": {
                    "auto_save": True,
                    "create_backups": True
                }
            }
            
            # Save initial project file
            return self.save_project(project_path)
            
        except Exception as e:
            logger.error(f"Failed to create project: {e}", exc_info=True)
            return False
    
    def load_project(self, project_path: str) -> bool:
        """
        Load project from specified path
        
        Args:
            project_path: Project directory path
            
        Returns:
            True if project loaded successfully
        """
        try:
            # Check if project directory exists
            if not os.path.isdir(project_path):
                logger.error(f"Project directory does not exist: {project_path}")
                return False
            
            # Check for project file
            project_file = os.path.join(project_path, "project.json")
            if not os.path.isfile(project_file):
                logger.error(f"Project file not found: {project_file}")
                return False
            
            # Load project data
            with open(project_file, 'r') as f:
                self.project_data = json.load(f)
                
            # Reset unsaved changes flag
            self.unsaved_changes = False
                
            logger.info(f"Project loaded: {project_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load project: {e}", exc_info=True)
            return False
    
    def save_project(self, project_path: str = None) -> bool:
        """
        Save project to specified path
        
        Args:
            project_path: Optional project directory path
            
        Returns:
            True if project saved successfully
        """
        # Ensure we have project data
        if not self.project_data:
            logger.error("No project data to save")
            return False
            
        try:
            # Update modified timestamp
            self.project_data["modified"] = self.get_timestamp()
            
            # Save project file
            project_file = os.path.join(project_path, "project.json")
            
            # Create backup if setting enabled
            if self.get_project_setting("create_backups", True) and os.path.isfile(project_file):
                backup_file = f"{project_file}.bak"
                try:
                    shutil.copy2(project_file, backup_file)
                except Exception as e:
                    logger.warning(f"Failed to create backup: {e}")
                    
            # Save project data
            with open(project_file, 'w') as f:
                json.dump(self.project_data, f, indent=2)
                
            # Reset unsaved changes flag
            self.unsaved_changes = False
                
            logger.info(f"Project saved: {project_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save project: {e}", exc_info=True)
            return False
    
    def create_backup(self) -> bool:
        """Create a backup of the current project"""
        # Ensure we have project data and path
        if not self.project_data or not self.app.current_project:
            return False
        
        try:
            # Create backups directory
            backups_dir = os.path.join(self.app.current_project, "backups")
            os.makedirs(backups_dir, exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = self.get_timestamp(file_safe=True)
            backup_file = os.path.join(backups_dir, f"backup_{timestamp}.json")
            
            # Save current data to backup file
            with open(backup_file, 'w') as f:
                json.dump(self.project_data, f, indent=2)
                
            logger.info(f"Project backup created: {backup_file}")
            
            # Show success message
            self.app.show_message(
                "Backup Created", 
                f"Project backup created: {os.path.basename(backup_file)}",
                "info"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}", exc_info=True)
            return False
    
    def export_project(self, export_path: str) -> bool:
        """
        Export project to a ZIP file
        
        Args:
            export_path: Path to save exported ZIP file
            
        Returns:
            True if export successful
        """
        # Ensure we have project data and path
        if not self.project_data or not self.app.current_project:
            return False
        
        try:
            # Create zip file
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Walk through project directory and add all files
                for root, _, files in os.walk(self.app.current_project):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.app.current_project)
                        zipf.write(file_path, arcname)
                        
            logger.info(f"Project exported to: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export project: {e}", exc_info=True)
            return False
    
    def rename_project(self, new_name: str) -> bool:
        """
        Rename current project
        
        Args:
            new_name: New name for project
            
        Returns:
            True if renamed successfully
        """
        # Ensure we have project data
        if not self.project_data:
            logger.error("No project data to rename")
            return False
            
        try:
            # Update project name
            self.project_data["name"] = new_name
            
            # Mark as having unsaved changes
            self.unsaved_changes = True
            
            # Save changes right away if auto-save is enabled
            if self.get_project_setting("auto_save", True) and self.app.current_project:
                self.save_project(self.app.current_project)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to rename project: {e}", exc_info=True)
            return False
    
    def close_project(self):
        """Close current project"""
        self.project_data = None
        self.unsaved_changes = False
    
    def update_project_results(self, results: List[Dict[str, Any]]) -> bool:
        """
        Update project results data
        
        Args:
            results: New results list
            
        Returns:
            True if update successful
        """
        # Ensure we have project data
        if not self.project_data:
            logger.error("No project data to update")
            return False
            
        try:
            # Update results
            self.project_data["results"] = results
            
            # Mark as having unsaved changes
            self.unsaved_changes = True
            
            # Save changes right away if auto-save is enabled
            if self.get_project_setting("auto_save", True) and self.app.current_project:
                self.save_project(self.app.current_project)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to update project results: {e}", exc_info=True)
            return False
    
    def has_unsaved_changes(self) -> bool:
        """Check if project has unsaved changes"""
        return self.unsaved_changes
    
    def get_project_metadata(self) -> Dict[str, Any]:
        """Get project metadata"""
        if not self.project_data:
            return {}
            
        return {
            "name": self.project_data.get("name", "Unnamed"),
            "created": self.project_data.get("created", "Unknown"),
            "modified": self.project_data.get("modified", "Unknown")
        }
    
    def get_project_setting(self, key: str, default=None) -> Any:
        """
        Get a project setting value
        
        Args:
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        if not self.project_data or "settings" not in self.project_data:
            return default
            
        return self.project_data["settings"].get(key, default)
    
    def set_project_setting(self, key: str, value: Any) -> bool:
        """
        Set a project setting value
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            True if successful
        """
        # Ensure we have project data
        if not self.project_data:
            logger.error("No project data to update")
            return False
            
        try:
            # Ensure settings dict exists
            if "settings" not in self.project_data:
                self.project_data["settings"] = {}
                
            # Update setting
            self.project_data["settings"][key] = value
            
            # Mark as having unsaved changes
            self.unsaved_changes = True
            
            # Save changes right away if auto-save is enabled
            if self.get_project_setting("auto_save", True) and self.app.current_project:
                self.save_project(self.app.current_project)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to set project setting: {e}", exc_info=True)
            return False
    
    def get_timestamp(self, file_safe=False) -> str:
        """
        Get current timestamp
        
        Args:
            file_safe: Whether to format for filenames
            
        Returns:
            Formatted timestamp
        """
        if file_safe:
            return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Class definition for PluginManager
class PluginManager:
    """Manages CreepyAI plugins"""
    
    def __init__(self, app):
        """
        Initialize the plugin manager
        
        Args:
            app: Main application instance
        """
        self.app = app
        self.plugin_dir = app.config.get("plugins_directory", "plugins")
        self.plugins = {}
        self.load_plugins()
    
    def load_plugins(self) -> int:
        """
        Load all plugins from plugin directory
        
        Returns:
            Number of plugins loaded
        """
        # Clear current plugins
        self.plugins = {}
        
        # Ensure plugin directory exists
        if not os.path.isdir(self.plugin_dir):
            try:
                os.makedirs(self.plugin_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create plugins directory: {e}")
                return 0
        
        # This is just a placeholder implementation
        # In a real app, this would dynamically load plugin modules
        
        # Add some sample plugins
        self.plugins = {
            "social_media": {
                "name": "Social Media Finder",
                "version": "1.0.0",
                "description": "Searches social media platforms",
                "status": "Active"
            },
            "email_finder": {
                "name": "Email Finder",
                "version": "1.1.2",
                "description": "Finds email addresses",
                "status": "Active"
            },
            "image_search": {
                "name": "Image Search",
                "version": "0.9.5",
                "description": "Searches for images",
                "status": "Active"
            }
        }
        
        logger.info(f"Loaded {len(self.plugins)} plugins")
        return len(self.plugins)
    
    def reload_plugins(self) -> int:
        """
        Reload all plugins
        
        Returns:
            Number of plugins loaded
        """
        return self.load_plugins()
    
    def get_plugins(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all loaded plugins
        
        Returns:
            Dictionary of plugin information
        """
        return self.plugins
    
    def set_plugin_dir(self, plugin_dir: str) -> None:
        """Set plugin directory path"""
        self.plugin_dir = plugin_dir


# Main function to run the application
def main():
    """Run the CreepyAI GUI application"""
    root = tk.Tk()
    gui = CreepyAIGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
``` 