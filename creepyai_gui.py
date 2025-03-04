import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import json
import os
import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='creepyai.log'
)
logger = logging.getLogger('CreepyAI GUI')

class CreepyAIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CreepyAI - OSINT Assistant")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Load configuration
        self.config = self.load_config()
        
        # Set up the main frame
        self.setup_ui()
        
        # Current project
        self.current_project = None
        
        # Search state
        self.search_running = False

    def load_config(self):
        """Load configuration from file"""
        config_path = os.path.expanduser("~/.config/creepyai/config.json")
        default_config = {
            "api_keys": {},
            "output_directory": os.path.expanduser("~/Documents/CreepyAI"),
            "plugins_directory": os.path.expanduser("~/.config/creepyai/plugins")
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                # Create default config
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            messagebox.showerror("Configuration Error", f"Error loading configuration: {e}")
            return default_config

    def setup_ui(self):
        """Set up the user interface"""
        # Create menu
        self.create_menu()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_search_tab()
        self.create_results_tab()
        self.create_analysis_tab()
        self.create_reports_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Search", command=self.new_search, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Project", command=self.open_project, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Results", command=self.save_results, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export Data", command=self.export_data, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Preferences", command=self.show_preferences)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Projects menu
        projects_menu = tk.Menu(menubar, tearoff=0)
        projects_menu.add_command(label="Create New Project", command=self.create_project)
        projects_menu.add_command(label="Open Existing Project", command=self.open_project)
        projects_menu.add_command(label="Project Settings", command=self.project_settings)
        menubar.add_cascade(label="Projects", menu=projects_menu)
        
        # Plugins menu
        plugins_menu = tk.Menu(menubar, tearoff=0)
        plugins_menu.add_command(label="Plugin Manager", command=self.plugin_manager)
        plugins_menu.add_command(label="Install Plugin", command=self.install_plugin)
        plugins_menu.add_separator()
        plugins_menu.add_command(label="Plugin Settings", command=self.plugin_settings)
        menubar.add_cascade(label="Plugins", menu=plugins_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="View Logs", command=self.show_logs)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-n>", lambda event: self.new_search())
        self.root.bind("<Control-o>", lambda event: self.open_project())
        self.root.bind("<Control-s>", lambda event: self.save_results())
        self.root.bind("<Control-e>", lambda event: self.export_data())
        self.root.bind("<F1>", lambda event: self.show_documentation())

    def create_dashboard_tab(self):
        """Create the dashboard tab"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Welcome message
        ttk.Label(
            dashboard_frame, 
            text="Welcome to CreepyAI OSINT Assistant", 
            font=("TkDefaultFont", 16)
        ).pack(pady=20)
        
        # Quick actions frame
        actions_frame = ttk.LabelFrame(dashboard_frame, text="Quick Actions")
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Button(actions_frame, text="New Search", command=self.new_search).grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(actions_frame, text="Recent Projects", command=self.show_recent_projects).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(actions_frame, text="Import Data", command=self.import_data).grid(row=0, column=2, padx=10, pady=10)
        ttk.Button(actions_frame, text="Generate Report", command=self.generate_report).grid(row=0, column=3, padx=10, pady=10)
        
        # Recent activity
        recent_frame = ttk.LabelFrame(dashboard_frame, text="Recent Activity")
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Placeholder for recent activity
        ttk.Label(recent_frame, text="No recent activity").pack(pady=20)

    def create_search_tab(self):
        """Create the search tab"""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="Search")
        
        # Search configuration
        config_frame = ttk.LabelFrame(search_frame, text="Search Configuration")
        config_frame.pack(fill=tk.X, expand=False, padx=20, pady=10)
        
        # Target input
        ttk.Label(config_frame, text="Target:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.target_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.target_var, width=50).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Location input
        ttk.Label(config_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.location_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.location_var, width=50).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Profile selection
        ttk.Label(config_frame, text="Profile:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.profile_var = tk.StringVar()
        profiles = ["Basic", "Professional", "Comprehensive", "Social Media", "Custom"]
        ttk.Combobox(config_frame, textvariable=self.profile_var, values=profiles, state="readonly").grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=5
        )
        self.profile_var.set("Basic")
        
        # Sources frame
        sources_frame = ttk.LabelFrame(search_frame, text="Data Sources")
        sources_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Data source checkboxes
        self.source_vars = {}
        sources = ["Social Media", "Public Records", "Professional Networks", "News Articles", "Image Search"]
        
        for i, source in enumerate(sources):
            self.source_vars[source] = tk.BooleanVar(value=True)
            ttk.Checkbutton(
                sources_frame, text=source, variable=self.source_vars[source]
            ).grid(row=i//3, column=i%3, sticky=tk.W, padx=20, pady=5)
        
        # Search button
        ttk.Button(
            search_frame, 
            text="Start Search", 
            command=self.start_search
        ).pack(pady=20)

    def create_results_tab(self):
        """Create the results tab"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Results")
        
        # Results control panel
        control_frame = ttk.Frame(results_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(control_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.filter_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Apply", command=self.apply_filter).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(results_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)
        
        # Results treeview
        self.results_tree = ttk.Treeview(results_frame, columns=("Source", "Type", "Date", "Confidence"))
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
        y_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        x_scroll = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Pack everything
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Export panel
        export_frame = ttk.Frame(results_frame)
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(export_frame, text="Export Results", command=self.export_data).pack(side=tk.RIGHT, padx=5)

    def create_analysis_tab(self):
        """Create the analysis tab"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="Analysis")
        
        # Visualization options
        options_frame = ttk.LabelFrame(analysis_frame, text="Visualization Options")
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Visualization type
        ttk.Label(options_frame, text="Visualization:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.viz_var = tk.StringVar()
        viz_types = ["Network Graph", "Timeline", "Heatmap", "Word Cloud", "Relationship Diagram"]
        ttk.Combobox(options_frame, textvariable=self.viz_var, values=viz_types, state="readonly", width=30).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5
        )
        self.viz_var.set("Network Graph")
        
        # Data source
        ttk.Label(options_frame, text="Data Source:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.data_source_var = tk.StringVar()
        data_sources = ["All Results", "Social Media Only", "Public Records Only", "Custom Selection"]
        ttk.Combobox(options_frame, textvariable=self.data_source_var, values=data_sources, state="readonly", width=30).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5
        )
        self.data_source_var.set("All Results")
        
        # Generate button
        ttk.Button(options_frame, text="Generate Visualization", command=self.generate_visualization).grid(
            row=2, column=0, columnspan=2, pady=10
        )
        
        # Visualization area
        viz_area = ttk.LabelFrame(analysis_frame, text="Visualization")
        viz_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Placeholder for visualization
        ttk.Label(viz_area, text="Select options and generate visualization to view results").pack(pady=100)

    def create_reports_tab(self):
        """Create the reports tab"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reports")
        
        # Report options
        options_frame = ttk.LabelFrame(reports_frame, text="Report Options")
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Report type
        ttk.Label(options_frame, text="Report Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.report_type_var = tk.StringVar()
        report_types = ["Executive Summary", "Full Technical Report", "Data Sheet", "Custom Report"]
        ttk.Combobox(options_frame, textvariable=self.report_type_var, values=report_types, state="readonly", width=30).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5
        )
        self.report_type_var.set("Executive Summary")
        
        # Include visualizations
        self.include_viz_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include Visualizations", variable=self.include_viz_var).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5
        )
        
        # Include raw data
        self.include_raw_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Include Raw Data", variable=self.include_raw_var).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5
        )
        
        # Generate button
        ttk.Button(options_frame, text="Generate Report", command=self.generate_report).grid(
            row=2, column=0, columnspan=2, pady=10
        )
        
        # Report preview area
        preview_area = ttk.LabelFrame(reports_frame, text="Report Preview")
        preview_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Placeholder for preview
        ttk.Label(preview_area, text="Generate a report to preview").pack(pady=100)

    # Action methods
    def new_search(self):
        """Start a new search"""
        self.notebook.select(1)  # Switch to search tab
        self.target_var.set("")
        self.location_var.set("")
        self.profile_var.set("Basic")

    def open_project(self):
        """Open an existing project"""
        project_path = filedialog.askdirectory(title="Open CreepyAI Project")
        if project_path:
            try:
                # Load project details
                self.current_project = project_path
                self.status_var.set(f"Project opened: {os.path.basename(project_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open project: {e}")

    def save_results(self):
        """Save current results"""
        if not self.current_project:
            self.create_project()
            if not self.current_project:  # User canceled
                return
                
        try:
            # Save logic would go here
            self.status_var.set("Results saved successfully")
            messagebox.showinfo("Success", "Results saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {e}")

    def export_data(self):
        """Export data to file"""
        file_types = [
            ("CSV files", "*.csv"),
            ("JSON files", "*.json"),
            ("Excel files", "*.xlsx"),
            ("PDF files", "*.pdf"),
            ("All files", "*.*")
        ]
        export_file = filedialog.asksaveasfilename(
            title="Export Data",
            filetypes=file_types,
            defaultextension=".csv"
        )
        if export_file:
            try:
                # Export logic would go here
                self.status_var.set(f"Data exported to {export_file}")
                messagebox.showinfo("Success", f"Data exported to {export_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {e}")

    def create_project(self):
        """Create a new project"""
        project_name = tk.simpledialog.askstring("New Project", "Enter project name:")
        if not project_name:
            return
            
        project_path = os.path.join(self.config["output_directory"], project_name)
        try:
            os.makedirs(project_path, exist_ok=True)
            self.current_project = project_path
            self.status_var.set(f"Project created: {project_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project: {e}")

    def show_preferences(self):
        """Show preferences dialog"""
        prefs_window = tk.Toplevel(self.root)
        prefs_window.title("Preferences")
        prefs_window.geometry("500x400")
        prefs_window.transient(self.root)
        prefs_window.grab_set()
        
        # Create preference tabs
        prefs_notebook = ttk.Notebook(prefs_window)
        prefs_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General tab
        general_frame = ttk.Frame(prefs_notebook)
        prefs_notebook.add(general_frame, text="General")
        
        # Output directory
        ttk.Label(general_frame, text="Output Directory:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        output_var = tk.StringVar(value=self.config["output_directory"])
        ttk.Entry(general_frame, textvariable=output_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(general_frame, text="Browse", command=lambda: output_var.set(
            filedialog.askdirectory(initialdir=output_var.get())
        )).grid(row=0, column=2, padx=5, pady=5)
        
        # API Keys tab
        api_frame = ttk.Frame(prefs_notebook)
        prefs_notebook.add(api_frame, text="API Keys")
        
        # Add API key entries
        row = 0
        api_vars = {}
        for service, key in self.config["api_keys"].items():
            ttk.Label(api_frame, text=f"{service}:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            api_vars[service] = tk.StringVar(value=key)
            ttk.Entry(api_frame, textvariable=api_vars[service], width=40, show="*").grid(row=row, column=1, padx=5, pady=5)
            row += 1
        
        # Save button
        ttk.Button(prefs_window, text="Save", command=prefs_window.destroy).pack(pady=10)

    def start_search(self):
        """Start the search process"""
        if not self.target_var.get():
            messagebox.showerror("Error", "Target is required")
            return
            
        if self.search_running:
            messagebox.showinfo("Search in Progress", "A search is already running")
            return
            
        self.search_running = True
        self.status_var.set("Search started...")
        
        # Start search in a separate thread to keep UI responsive
        threading.Thread(target=self._run_search, daemon=True).start()

    def _run_search(self):
        """Run the search in background thread"""
        try:
            # Simulate search process
            import time
            for i in range(10):
                time.sleep(0.5)  # Simulate work
                self.status_var.set(f"Searching... ({i+1}/10)")
            
            # Update UI with results
            self.root.after(0, self._update_results)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Search Error", str(e)))
        finally:
            self.search_running = False
            self.root.after(0, lambda: self.status_var.set("Search completed"))

    def _update_results(self):
        """Update results in UI thread"""
        # Clear existing results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        # Add sample results
        self.results_tree.insert("", tk.END, text="John Smith Twitter Profile", values=("Twitter", "Profile", "2023-05-15", "High"))
        self.results_tree.insert("", tk.END, text="john.smith@example.com", values=("Email", "Contact", "2023-05-15", "Medium"))
        self.results_tree.insert("", tk.END, text="LinkedIn: John Smith", values=("LinkedIn", "Profile", "2023-05-15", "High"))
        self.results_tree.insert("", tk.END, text="555-123-4567", values=("Phone", "Contact", "2023-05-15", "Medium"))
        
        # Switch to results tab
        self.notebook.select(2)  # Results tab

    def apply_filter(self):
        """Apply filter to results"""
        filter_text = self.filter_var.get().lower()
        if not filter_text:
            return
            
        # Filter logic would go here
        self.status_var.set(f"Filter applied: {filter_text}")

    def generate_visualization(self):
        """Generate visualization based on selected options"""
        viz_type = self.viz_var.get()
        data_source = self.data_source_var.get()
        
        self.status_var.set(f"Generating {viz_type} visualization...")
        # Visualization generation logic would go here

    def generate_report(self):
        """Generate report based on selected options"""
        report_type = self.report_type_var.get()
        include_viz = self.include_viz_var.get()
        include_raw = self.include_raw_var.get()
        
        self.status_var.set(f"Generating {report_type} report...")
        # Report generation logic would go here
        
    # Additional helper methods
    def show_recent_projects(self):
        """Show recent projects dialog"""
        # Implementation would go here
        pass
        
    def import_data(self):
        """Import data from file"""
        import_file = filedialog.askopenfilename(
            title="Import Data",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )
        if import_file:
            # Import logic would go here
            pass

    # Missing method implementations
    def project_settings(self):
        """Show project settings dialog"""
        if not self.current_project:
            messagebox.showinfo("No Project", "Please open a project first")
            return
            
        messagebox.showinfo("Project Settings", f"Settings for project: {os.path.basename(self.current_project)}")
    
    def plugin_manager(self):
        """Show plugin manager dialog"""
        messagebox.showinfo("Plugin Manager", "Plugin manager not yet implemented")
    
    def install_plugin(self):
        """Show install plugin dialog"""
        plugin_file = filedialog.askopenfilename(
            title="Install Plugin",
            filetypes=[("Python files", "*.py"), ("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        if plugin_file:
            messagebox.showinfo("Plugin Installation", f"Plugin installation from {plugin_file} simulated")
    
    def plugin_settings(self):
        """Show plugin settings dialog"""
        messagebox.showinfo("Plugin Settings", "Plugin settings not yet implemented")
        
    def show_documentation(self):
        """Show documentation"""
        messagebox.showinfo("Documentation", "Documentation not yet implemented")
        
    def show_logs(self):
        """Show application logs"""
        log_window = tk.Toplevel(self.root)
        log_window.title("Application Logs")
        log_window.geometry("700x500")
        log_window.transient(self.root)
        
        # Create a text widget with scrollbar
        log_frame = ttk.Frame(log_window)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        log_text = tk.Text(log_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, command=log_text.yview)
        log_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Try to load and display log contents
        try:
            with open("creepyai.log", "r") as f:
                log_text.insert(tk.END, f.read())
        except Exception as e:
            log_text.insert(tk.END, f"Error loading log file: {e}")
        
        log_text.config(state=tk.DISABLED)  # Make read-only
        
    def show_about(self):
        """Show about dialog"""
        about_text = """
        CreepyAI - OSINT Assistant
        
        Version: 1.0.0
        
        An open-source intelligence gathering and analysis tool.
        
        © 2023 CreepyAI Team
        """
        messagebox.showinfo("About CreepyAI", about_text)

# Add this to the end of the file to allow direct execution
if __name__ == "__main__":
    root = tk.Tk()
    app = CreepyAIGUI(root)
    root.mainloop()