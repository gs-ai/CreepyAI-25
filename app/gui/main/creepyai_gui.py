#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import functools
import queue
import threading
from app.resources.icons import Icons
import creepy.creepy_resources_rc as creepy_resources_rc
import os
import logging
import datetime
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QMessageBox, QFileDialog,
    QProgressDialog, QMenu, QAction, QLabel, QStatusBar,
    QToolBar, QDialog, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QSettings, QTimer
from PyQt5.QtGui import QIcon

# Import internal modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.analysis import (
    DEFAULT_PROMPT_TEMPLATE,
    LocalLLMAnalyzer,
    SUPPORTED_LOCAL_LLM_MODELS,
    get_default_history_dir,
    load_recent_history,
    load_social_media_records,
    persist_analysis_result,
)
from app.core.config_manager import ConfigManager
from app.gui.LLMAnalysisDialog import LLMAnalysisDialog
from app.models.Database import Database
from app.models.Location import Location
from app.models.Project import Project
from utilities.PluginManager import PluginManager
from utilities.WebScrapingUtility import WebScrapingUtility
from utilities.GeocodingUtility import GeocodingUtility
from utilities.ExportUtils import ExportManager
from utilities.webengine_compat import setup_webengine_options

# Import UI components
from ui.PersonProjectWizard import PersonProjectWizard
from ui.PluginsConfig import PluginsConfigDialog
from ui.FilterLocationsDateDialog import FilterLocationsDateDialog
from ui.FilterLocationsPointDialog import FilterLocationsPointDialog
from ui.AboutDialog import AboutDialog
from ui.VerifyDeleteDialog import VerifyDeleteDialog
from ui.creepy_map_view import CreepyMapView

logger = logging.getLogger(__name__)

_ICON_STYLESHEET: Optional[str] = None


def _load_icon_stylesheet() -> Optional[str]:
    """Load the shared icon stylesheet once and cache it for reuse."""

    global _ICON_STYLESHEET

    if _ICON_STYLESHEET is not None:
        return _ICON_STYLESHEET

    style_path = Path(__file__).resolve().parents[2] / "resources" / "styles" / "icons.css"
    try:
        _ICON_STYLESHEET = style_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.debug("Icon stylesheet not found at %s", style_path)
        _ICON_STYLESHEET = None
    except Exception:
        logger.exception("Failed to load icon stylesheet from %s", style_path)
        _ICON_STYLESHEET = None

    return _ICON_STYLESHEET

class CreepyMainWindow(QMainWindow):
    """Main window for the CreepyAI application."""

    def __init__(self, config_manager=None, parent=None, load_plugins: bool = True):
        super().__init__(parent)

        if config_manager is None:
            config_manager = ConfigManager()

        self._apply_icon_styles()

        self.setWindowTitle("CreepyAI - Geolocation Intelligence")
        self.resize(1200, 800)

        # Initialize components
        self.config_manager = config_manager
        self.database = Database()
        self.plugin_manager = PluginManager()
        self._load_plugins = load_plugins
        if load_plugins:
            self.plugin_manager.load_plugins()
        self.geocoder = GeocodingUtility(self.config_manager)
        self.export_manager = ExportManager()
        
        # Initialize recent projects list
        self.recent_projects = []
        self.load_recent_projects()
        
        # Set up UI components
        self._setup_ui()
        
        # Initialize data structures
        self.current_project = None
        self.current_target = None
        self.locations = []
        
        # Configure plugins with database and config
        if load_plugins:
            self.plugin_manager.configure_plugins(self.config_manager, self.database)
        
        # Load settings
        self.load_settings()
        
        logger.info("Main window initialized")
        
        # Check for export dependencies
        QApplication.instance().processEvents()
        self.check_export_dependencies()

        # Background analysis management
        self._analysis_job_running = False
        self._background_refresh_queue: "queue.Queue[Dict[str, object]]" = queue.Queue()
        self._background_refresh_thread: Optional[threading.Thread] = None
        self._dataset_watch_state: Dict[str, Tuple[float, float]] = {}
        self._analysis_refresh_timer = QTimer(self)
        self._analysis_refresh_timer.setSingleShot(False)
        self._analysis_refresh_timer.timeout.connect(self._background_refresh_tick)
        self._setup_background_tasks()

    def _setup_ui(self):
        """Set up the user interface."""
        try:
            # Set up central widget
            self.map_view = CreepyMapView(self)
            self.setCentralWidget(self.map_view)
            
            # Create toolbars
            self._create_toolbars()
            
            # Create status bar
            self.statusbar = QStatusBar()
            self.setStatusBar(self.statusbar)
            self.status_location_count = QLabel("No locations loaded")
            self.statusbar.addPermanentWidget(self.status_location_count)
            
            # Create menus
            self._create_menus()
        
        except Exception as e:
            logger.error(f"Failed to set up UI: {e}")
            QMessageBox.critical(self, "Error", f"Failed to set up UI: {e}")

    def _apply_icon_styles(self) -> None:
        """Apply the shared icon stylesheet if it exists."""
        style_path = Path(__file__).resolve().parents[2] / "resources" / "styles" / "icons.css"
        try:
            stylesheet = style_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.debug("Icon stylesheet not found at %s", style_path)
        except Exception:
            logger.exception("Failed to load icon stylesheet from %s", style_path)
        else:
            self.setStyleSheet(stylesheet)
    
    def _create_toolbars(self):
        """Create application toolbars."""
        # Main toolbar
        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setObjectName("MainToolbar")  # Fix: Set objectName for toolbar
        self.main_toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(Qt.TopToolBarArea, self.main_toolbar)
        
        # Project actions
        self.action_new_project = QAction(Icons.get_icon("new_project"), "New Project", self)
        self.action_new_project.triggered.connect(self.create_new_project)
        self.main_toolbar.addAction(self.action_new_project)
        
        self.action_open_project = QAction(Icons.get_icon("open_project"), "Open Project", self)
        self.action_open_project.triggered.connect(self.open_project)
        self.main_toolbar.addAction(self.action_open_project)
        
        self.action_save_project = QAction(Icons.get_icon("save_project"), "Save Project", self)
        self.action_save_project.triggered.connect(self.save_project)
        self.main_toolbar.addAction(self.action_save_project)
        
        self.main_toolbar.addSeparator()
        
        # Analysis actions
        self.action_analyze = QAction(Icons.get_icon("analyze"), "Analyze Data", self)
        self.action_analyze.triggered.connect(self.analyze_data)
        self.main_toolbar.addAction(self.action_analyze)
        
        self.action_export = QAction(Icons.get_icon("export"), "Export Data", self)
        self.action_export.triggered.connect(self.export_project)
        self.main_toolbar.addAction(self.action_export)
        
        self.main_toolbar.addSeparator()
        
        # Filter actions
        self.action_filter_date = QAction(Icons.get_icon("filter_date"), "Filter by Date", self)
        self.action_filter_date.triggered.connect(self.filter_by_date)
        self.main_toolbar.addAction(self.action_filter_date)
        
        self.action_filter_location = QAction(Icons.get_icon("filter_location"), "Filter by Location", self)
        self.action_filter_location.triggered.connect(self.filter_by_location)
        self.main_toolbar.addAction(self.action_filter_location)
        
        self.action_clear_filters = QAction(Icons.get_icon("clear_filters"), "Clear Filters", self)
        self.action_clear_filters.triggered.connect(self.clear_filters)
        self.main_toolbar.addAction(self.action_clear_filters)
    
    def _create_menus(self):
        """Create application menus."""
        # File menu
        self.file_menu = self.menuBar().addMenu("&File")
        
        self.file_menu.addAction(self.action_new_project)
        self.file_menu.addAction(self.action_open_project)
        self.file_menu.addAction(self.action_save_project)
        
        self.file_menu.addSeparator()
        
        # Recent projects submenu
        self.recent_projects_menu = QMenu("Recent Projects", self)
        self.file_menu.addMenu(self.recent_projects_menu)
        self._update_recent_projects_menu()
        
        self.file_menu.addSeparator()
        
        # Export submenu
        self.export_menu = QMenu("Export", self)
        self.action_export_kml = QAction("Export to KML", self)
        self.action_export_kml.triggered.connect(lambda: self.export_project("kml"))
        self.export_menu.addAction(self.action_export_kml)
        
        self.action_export_csv = QAction("Export to CSV", self)
        self.action_export_csv.triggered.connect(lambda: self.export_project("csv"))
        self.export_menu.addAction(self.action_export_csv)
        
        self.action_export_html = QAction("Export to HTML Map", self)
        self.action_export_html.triggered.connect(lambda: self.export_project("html"))
        self.export_menu.addAction(self.action_export_html)
        
        self.action_export_json = QAction("Export to JSON", self)
        self.action_export_json.triggered.connect(lambda: self.export_project("json"))
        self.export_menu.addAction(self.action_export_json)
        
        self.file_menu.addMenu(self.export_menu)
        
        self.file_menu.addSeparator()
        
        # Exit action
        self.action_exit = QAction("E&xit", self)
        self.action_exit.triggered.connect(self.close)
        self.file_menu.addAction(self.action_exit)
        
        # Analysis menu
        self.analysis_menu = self.menuBar().addMenu("&Analysis")
        
        self.analysis_menu.addAction(self.action_analyze)
        
        self.analysis_menu.addSeparator()
        
        self.analysis_menu.addAction(self.action_filter_date)
        self.analysis_menu.addAction(self.action_filter_location)
        self.analysis_menu.addAction(self.action_clear_filters)
        
        # Tools menu
        self.tools_menu = self.menuBar().addMenu("&Tools")
        
        self.action_plugins_config = QAction("Plugin Configuration", self)
        self.action_plugins_config.triggered.connect(self.configure_plugins)
        self.tools_menu.addAction(self.action_plugins_config)
        
        self.action_settings = QAction("Settings", self)
        self.action_settings.triggered.connect(self.show_settings)
        self.tools_menu.addAction(self.action_settings)
    
    def create_new_project(self):
        """Create a new project."""
        wizard = PersonProjectWizard(self.plugin_manager)
        if wizard.exec_():
            project_data = wizard.get_project_data()
            self.current_project = Project(
                name=project_data.get('name', ''),
                description=project_data.get('description', ''),
                project_dir=project_data.get('directory', '')
            )
            for target in project_data.get('targets', []):
                self.current_project.add_target(target)
            self.save_project()
            self.update_project_ui()
            if project_data.get('analyze_now', False):
                self.analyze_data()
            self.statusbar.showMessage(f"Created new project: {self.current_project.name}")
    
    def open_project(self):
        """Open an existing project."""
        project_dir = QFileDialog.getExistingDirectory(self, "Open Project Directory")
        if not project_dir:
            return
        project_file = os.path.join(project_dir, 'project.json')
        if not os.path.exists(project_file):
            QMessageBox.warning(self, "Invalid Project", "The selected directory does not contain a valid CreepyAI project.")
            return
        self.current_project = Project.load(project_dir)
        if not self.current_project:
            QMessageBox.critical(self, "Project Error", "Failed to load the project. Please see the log for details.")
            return
        self.update_project_ui()
        self.statusbar.showMessage(f"Opened project: {self.current_project.name}")
    
    def save_project(self):
        """Save the current project."""
        if not self.current_project:
            return
        if not self.current_project.project_dir:
            project_dir = QFileDialog.getExistingDirectory(self, "Select Project Directory")
            if not project_dir:
                return
            self.current_project.set_project_dir(project_dir)
        if self.current_project.save():
            self.statusbar.showMessage(f"Project saved: {self.current_project.name}")
        else:
            QMessageBox.critical(self, "Save Error", "Failed to save the project. Please see the log for details.")
    
    def update_project_ui(self):
        """Update UI with current project data."""
        if not self.current_project:
            self.statusbar.showMessage("No project loaded")
            return
        self.statusbar.showMessage(f"Project: {self.current_project.name}\nDescription: {self.current_project.description}\nLocations: {self.current_project.locations.count()}")
    
    def filter_by_date(self):
        """Show filter by date dialog."""
        if not self.current_project or self.current_project.locations.count() == 0:
            QMessageBox.information(self, "No Data", "No location data available to filter.")
            return
        dialog = FilterLocationsDateDialog(self.current_project, self)
        if dialog.exec_():
            self.statusbar.showMessage("Date filter applied")
    
    def filter_by_location(self):
        """Show filter by location point dialog."""
        if not self.current_project or self.current_project.locations.count() == 0:
            QMessageBox.information(self, "No Data", "No location data available to filter.")
            return
        dialog = FilterLocationsPointDialog(self.current_project, self)
        if dialog.exec_():
            self.statusbar.showMessage("Location filter applied")
    
    def clear_filters(self):
        """Clear all filters."""
        self.statusbar.showMessage("Filters cleared")
    
    def show_about(self):
        """Show about dialog."""
        dialog = AboutDialog(self)
        dialog.exec_()

    def _build_analysis_settings(self) -> Dict[str, object]:
        """Collect analysis settings from the configuration manager."""

        default_temperature = 0.2
        default_tone = "objective"
        default_depth = "balanced"
        prompt_template = DEFAULT_PROMPT_TEMPLATE
        overrides_list: List[Dict[str, object]] = []
        selected_models: List[str] = []
        max_records = 75
        history_override: Optional[str] = None
        base_data_dir: Optional[Path] = None

        if self.config_manager:
            temp_value = self.config_manager.get('analysis.default_temperature', default_temperature)
            try:
                default_temperature = float(temp_value)
            except (TypeError, ValueError):
                default_temperature = 0.2

            tone_value = self.config_manager.get('analysis.default_tone', default_tone)
            if tone_value:
                default_tone = str(tone_value)

            depth_value = self.config_manager.get('analysis.default_depth', default_depth)
            if depth_value:
                default_depth = str(depth_value)

            template_value = self.config_manager.get('analysis.prompt_template', prompt_template)
            if template_value:
                prompt_template = str(template_value)

            overrides_value = self.config_manager.get('analysis.model_overrides', [])
            if isinstance(overrides_value, list):
                overrides_list = overrides_value

            models_value = self.config_manager.get('analysis.models', [])
            if isinstance(models_value, list):
                selected_models = [str(model).strip() for model in models_value if str(model).strip()]

            history_override = self.config_manager.get('analysis.history_dir', '')
            data_dir_value = self.config_manager.get('data_dir', '')
            if data_dir_value:
                base_data_dir = Path(str(data_dir_value))

            max_records_value = self.config_manager.get('analysis.max_records', max_records)
            try:
                max_records = int(max_records_value)
            except (TypeError, ValueError):
                max_records = 75

        if history_override:
            history_dir = Path(str(history_override))
        else:
            history_dir = get_default_history_dir(base_data_dir)

        model_settings: Dict[str, Dict[str, object]] = {}
        ordered_models: List[str] = []

        for entry in overrides_list:
            model_name = str(entry.get('model', '')).strip()
            if not model_name:
                continue

            config: Dict[str, object] = {}
            try:
                if entry.get('temperature') is not None:
                    config['temperature'] = float(entry['temperature'])
            except (TypeError, ValueError):
                pass

            tone_override = entry.get('tone')
            if tone_override:
                config['tone'] = str(tone_override)

            depth_override = entry.get('depth')
            if depth_override:
                config['depth'] = str(depth_override)

            prompt_override = entry.get('prompt_override')
            if prompt_override:
                config['prompt_template'] = str(prompt_override)

            if config:
                model_settings[model_name] = config

            ordered_models.append(model_name)

        if selected_models:
            ordered_models = selected_models + [model for model in ordered_models if model not in selected_models]

        if not ordered_models:
            ordered_models = [
                str(item.get('name'))
                for item in SUPPORTED_LOCAL_LLM_MODELS
                if item.get('name')
            ]

        unique_models: List[str] = []
        for name in ordered_models:
            if name and name not in unique_models:
                unique_models.append(name)

        return {
            'temperature': default_temperature,
            'tone': default_tone,
            'depth': default_depth,
            'prompt_template': prompt_template,
            'model_settings': model_settings,
            'models': unique_models,
            'history_dir': history_dir,
            'max_records': max_records,
        }

    def _setup_background_tasks(self) -> None:
        """Configure timers and cached signatures for dataset refresh tasks."""

        if not hasattr(self, "_analysis_refresh_timer"):
            return

        self._analysis_refresh_timer.stop()
        self._dataset_watch_state.clear()
        self._prime_dataset_watch_state()

        if self._should_enable_background_refresh():
            interval_minutes = self._get_refresh_interval_minutes()
            self._analysis_refresh_timer.start(interval_minutes * 60 * 1000)
            logger.info("Background dataset refresh enabled (interval=%s minutes)", interval_minutes)
        else:
            logger.info("Background dataset refresh disabled")

    def _should_enable_background_refresh(self) -> bool:
        if not getattr(self, "config_manager", None):
            return False
        return bool(self.config_manager.get('analysis.auto_refresh_enabled', False))

    def _get_refresh_interval_minutes(self) -> int:
        default_interval = 30
        if not getattr(self, "config_manager", None):
            return default_interval

        value = self.config_manager.get('analysis.auto_refresh_interval_minutes', default_interval)
        try:
            interval = int(value)
        except (TypeError, ValueError):
            interval = default_interval
        return max(1, interval)

    def _prime_dataset_watch_state(self) -> None:
        try:
            from app.plugins.social_media import SOCIAL_MEDIA_PLUGINS
        except Exception as exc:
            logger.debug("Unable to prime dataset watcher: %s", exc)
            return

        for slug in SOCIAL_MEDIA_PLUGINS:
            self._refresh_watch_state_for(slug)

    def _refresh_watch_state_for(self, slug: str) -> None:
        try:
            from app.plugins.social_media import SOCIAL_MEDIA_PLUGINS
            from app.plugins.social_media.base import ArchiveSocialMediaPlugin
        except Exception as exc:
            logger.debug("Unable to refresh dataset state: %s", exc)
            return

        plugin_cls = SOCIAL_MEDIA_PLUGINS.get(slug)
        if not plugin_cls:
            return

        plugin: ArchiveSocialMediaPlugin = plugin_cls()
        data_dir = Path(plugin.get_data_directory())
        signature = self._calculate_data_signature(data_dir, plugin.dataset_filename)
        dataset_path = data_dir / plugin.dataset_filename

        try:
            dataset_mtime = float(dataset_path.stat().st_mtime)
        except OSError:
            dataset_mtime = 0.0

        self._dataset_watch_state[slug] = (signature, dataset_mtime)

    def _calculate_data_signature(self, path: Path, dataset_filename: str) -> float:
        try:
            path = path.expanduser()
        except Exception:
            pass

        if not path.exists():
            return 0.0

        if path.is_file():
            try:
                return float(path.stat().st_mtime)
            except OSError:
                return 0.0

        latest = 0.0
        dataset_filename = dataset_filename or ""

        try:
            for child in path.rglob("*"):
                if dataset_filename and child.name == dataset_filename:
                    continue

                try:
                    mtime = float(child.stat().st_mtime)
                except OSError:
                    continue

                if mtime > latest:
                    latest = mtime
        except OSError:
            return latest

        return latest

    def _detect_archive_changes(self) -> List[str]:
        changed: List[str] = []

        try:
            from app.plugins.social_media import SOCIAL_MEDIA_PLUGINS
            from app.plugins.social_media.base import ArchiveSocialMediaPlugin
        except Exception as exc:
            logger.debug("Unable to detect archive changes: %s", exc)
            return changed

        for slug, plugin_cls in SOCIAL_MEDIA_PLUGINS.items():
            plugin: ArchiveSocialMediaPlugin = plugin_cls()
            data_dir = Path(plugin.get_data_directory())
            signature = self._calculate_data_signature(data_dir, plugin.dataset_filename)
            dataset_path = data_dir / plugin.dataset_filename

            try:
                dataset_mtime = float(dataset_path.stat().st_mtime)
            except OSError:
                dataset_mtime = 0.0

            previous = self._dataset_watch_state.get(slug)
            if previous is None:
                self._dataset_watch_state[slug] = (signature, dataset_mtime)
                continue

            previous_signature, _previous_dataset_mtime = previous

            should_refresh = False
            if dataset_mtime == 0.0 and signature > 0.0:
                should_refresh = True
            elif signature > previous_signature and signature > dataset_mtime:
                should_refresh = True

            if should_refresh:
                changed.append(slug)

            self._dataset_watch_state[slug] = (signature, dataset_mtime)

        return changed

    def _background_refresh_tick(self) -> None:
        self._consume_background_results()

        if not self._should_enable_background_refresh():
            return

        if self._background_refresh_thread is not None and self._background_refresh_thread.is_alive():
            return

        changed = self._detect_archive_changes()
        if not changed:
            return

        self._background_refresh_thread = threading.Thread(
            target=self._run_background_refresh,
            args=(changed,),
            daemon=True,
        )
        self._background_refresh_thread.start()

    def _run_background_refresh(self, slugs: List[str]) -> None:
        try:
            from app.data_collection.social_media_data_collector import SocialMediaDataCollector
        except Exception as exc:
            logger.exception("Unable to start dataset collector: %s", exc)
            self._background_refresh_queue.put({"error": str(exc), "slugs": slugs})
            QTimer.singleShot(0, self._process_background_queue)
            self._background_refresh_thread = None
            return

        try:
            collector = SocialMediaDataCollector()
            datasets = collector.collect(plugin_slugs=slugs)
            run_analysis = bool(
                getattr(self, "config_manager", None)
                and self.config_manager.get('analysis.auto_run_after_refresh', False)
            )
            self._background_refresh_queue.put(
                {
                    "datasets": datasets,
                    "slugs": slugs,
                    "run_analysis": run_analysis,
                }
            )
        except Exception as exc:
            logger.exception("Background dataset refresh failed: %s", exc)
            self._background_refresh_queue.put({"error": str(exc), "slugs": slugs})
        finally:
            self._background_refresh_thread = None
            QTimer.singleShot(0, self._process_background_queue)

    def _process_background_queue(self) -> None:
        self._consume_background_results()

    def _consume_background_results(self) -> None:
        updated = False

        while True:
            try:
                result = self._background_refresh_queue.get_nowait()
            except queue.Empty:
                break

            error = result.get("error")
            if error:
                logger.warning("Background dataset refresh issue: %s", error)
                if hasattr(self, "statusbar") and self.statusbar:
                    self.statusbar.showMessage(f"Dataset refresh error: {error}", 10000)
                continue

            slugs = result.get("slugs") or []
            for slug in slugs:
                self._refresh_watch_state_for(slug)

            datasets = result.get("datasets") or {}
            if datasets and hasattr(self, "statusbar") and self.statusbar:
                refreshed = ", ".join(sorted(datasets.keys()))
                self.statusbar.showMessage(f"Refreshed datasets for {refreshed}", 10000)

            run_analysis = bool(result.get("run_analysis"))
            if run_analysis and self.current_project:
                if not self._analysis_job_running:
                    QTimer.singleShot(0, functools.partial(self.analyze_data, False, auto_trigger=True))
                else:
                    if hasattr(self, "statusbar") and self.statusbar:
                        self.statusbar.showMessage("Analysis already running; skipping auto-run.", 10000)
            elif run_analysis and not self.current_project and hasattr(self, "statusbar") and self.statusbar:
                self.statusbar.showMessage("Datasets refreshed. Open a project to run analysis.", 10000)

            updated = True

        if updated and self._should_enable_background_refresh() and not self._analysis_refresh_timer.isActive():
            self._analysis_refresh_timer.start(self._get_refresh_interval_minutes() * 60 * 1000)

    def analyze_data(self, checked=False, *, auto_trigger: bool = False):
        """Perform analysis on the project data using local LLMs."""

        if not self.current_project:
            message = "Open or create a project before running analysis."
            if auto_trigger and hasattr(self, "statusbar") and self.statusbar:
                self.statusbar.showMessage(message, 10000)
            else:
                QMessageBox.information(self, "No Project", message)
            return

        if self._analysis_job_running:
            if not auto_trigger:
                QMessageBox.information(self, "Analysis Running", "An analysis task is already in progress.")
            return

        try:
            settings = self._build_analysis_settings()
            records = load_social_media_records(limit_per_plugin=settings['max_records'])
        except Exception as exc:
            logger.exception("Failed to load curated datasets: %s", exc)
            message = f"Failed to load curated datasets: {exc}"
            if auto_trigger and hasattr(self, "statusbar") and self.statusbar:
                self.statusbar.showMessage(message, 10000)
            else:
                QMessageBox.critical(self, "Analysis Error", message)
            return

        if not records:
            message = "No curated social media datasets were found. Collect new data before running analysis."
            if auto_trigger and hasattr(self, "statusbar") and self.statusbar:
                self.statusbar.showMessage(message, 10000)
            else:
                QMessageBox.information(
                    self,
                    "No Curated Data",
                    message,
                )
            return

        self._analysis_job_running = True

        analyzer = LocalLLMAnalyzer(
            models=settings['models'],
            max_records=settings['max_records'],
            temperature=settings['temperature'],
            prompt_template=settings['prompt_template'],
            default_tone=settings['tone'],
            default_depth=settings['depth'],
            model_settings=settings['model_settings'],
        )

        subject = self.current_project.name or "Investigation"
        focus = self.current_project.description or None

        progress = QProgressDialog("Running local LLM analysis...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.setMinimumDuration(0)
        progress.show()
        QApplication.processEvents()

        try:
            result = analyzer.analyze_subject(subject, records, focus=focus)
        except Exception as exc:
            logger.exception("Local LLM analysis failed: %s", exc)
            QMessageBox.critical(self, "Analysis Error", f"Local LLM analysis failed: {exc}")
            progress.close()
            self._analysis_job_running = False
            return
        finally:
            progress.close()

        self._analysis_job_running = False

        history_dir: Path = settings['history_dir']
        saved_entry = None
        try:
            saved_entry = persist_analysis_result(history_dir, result)
            result['integrity'] = saved_entry.integrity
            result['history_path'] = str(saved_entry.file_path)
        except Exception as exc:
            logger.exception("Failed to persist analysis result: %s", exc)
            QMessageBox.warning(
                self,
                "History Warning",
                f"Analysis completed but saving the result failed: {exc}",
            )

        history_entries = load_recent_history(history_dir, limit=10)
        if saved_entry is not None:
            history_entries = [saved_entry] + [
                entry for entry in history_entries if entry.file_path != saved_entry.file_path
            ]

        dialog = LLMAnalysisDialog(self)
        dialog.set_analysis_results(result, history_entries, saved_entry)
        dialog.exec_()

        if saved_entry is not None and hasattr(self, 'statusbar') and self.statusbar:
            self.statusbar.showMessage(f"Analysis saved to {saved_entry.file_path}", 10000)
    
    def export_project(self, format="kml"):
        """Export project data."""
        if not self.current_project or self.current_project.locations.count() == 0:
            QMessageBox.information(self, "No Data", "No location data available to export.")
            return
        file_formats = {
            "kml": "KML Files (*.kml)",
            "csv": "CSV Files (*.csv)",
            "html": "HTML Files (*.html)",
            "json": "JSON Files (*.json)"
        }
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Project", f"{self.current_project.name}.{format}", file_formats[format])
        if not file_path:
            return
        success = self.export_manager.export_locations(self.current_project.locations, file_path, format)
        if success:
            self.statusbar.showMessage(f"Data exported to {file_path}")
        else:
            QMessageBox.critical(self, "Export Error", "Failed to export data. See log for details.")
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.current_project and self.current_project.is_modified():
            reply = QMessageBox.question(self, "Save Project", "The current project has unsaved changes. Save before closing?", QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
            if reply == QMessageBox.Save:
                self.save_project()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        self.save_settings()
        event.accept()
    
    def save_settings(self):
        """Save application settings."""
        settings = QSettings("CreepyAI", "CreepyAI")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue("recentProjects", self.recent_projects)
    
    def load_settings(self):
        """Load application settings."""
        settings = QSettings("CreepyAI", "CreepyAI")
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        state = settings.value("windowState")
        if state:
            self.restoreState(state)
        self.recent_projects = settings.value("recentProjects", [])
    
    def check_export_dependencies(self):
        """Check for export-related dependencies and notify the user if any are missing."""
        missing_features = []
        try:
            import simplekml
        except ImportError:
            missing_features.append({'name': 'KML Export', 'package': 'simplekml', 'importance': 'optional'})
        if missing_features:
            feature_list = "\n".join([f"- {f['name']} (requires {f['package']})" for f in missing_features])
            QMessageBox.information(self, "Limited Functionality", f"Some features have limited functionality due to missing dependencies:\n\n{feature_list}\n\nYou can install these packages using:\npip install simplekml\n\nOr run the dependency installer:\npython core/install_dependencies.py --optional")
            for feature in missing_features:
                logger.warning(f"Missing dependency: {feature['package']} - {feature['name']} will be limited")

    def _update_recent_projects_menu(self):
        """Update the recent projects menu with recent project paths."""
        # Clear existing actions
        self.recent_projects_menu.clear()
        
        # If no recent projects, add disabled action
        if not self.recent_projects:
            action = QAction("No Recent Projects", self)
            action.setEnabled(False)
            self.recent_projects_menu.addAction(action)
            return
        
        # Add recent projects
        for project_path in self.recent_projects:
            if os.path.exists(project_path):
                project_name = os.path.basename(project_path)
                action = QAction(project_name, self)
                action.setData(project_path)
                action.triggered.connect(lambda checked, path=project_path: self.open_recent_project(path))
                self.recent_projects_menu.addAction(action)
        
        # Add separator and clear action
        if self.recent_projects:
            self.recent_projects_menu.addSeparator()
            clear_action = QAction("Clear Recent Projects", self)
            clear_action.triggered.connect(self.clear_recent_projects)
            self.recent_projects_menu.addAction(clear_action)

    def open_recent_project(self, project_path):
        """Open a project from the recent projects list."""
        if os.path.exists(project_path):
            self.current_project = Project.load(project_path)
            if self.current_project:
                # Update UI
                self.update_project_ui()
                # Add to recent projects (moves to top of list)
                self._add_to_recent_projects(project_path)
            else:
                # Remove from recent projects if it failed to load
                self._remove_from_recent_projects(project_path)
        else:
            # Remove from recent projects if it doesn't exist
            self._remove_from_recent_projects(project_path)
            QMessageBox.warning(self, "Project Not Found", f"The project at {project_path} no longer exists.")

    def _add_to_recent_projects(self, project_path):
        """Add a project to the recent projects list."""
        # Remove if already in the list
        if project_path in self.recent_projects:
            self.recent_projects.remove(project_path)
        # Add to the beginning of the list
        self.recent_projects.insert(0, project_path)
        # Limit to 10 recent projects
        self.recent_projects = self.recent_projects[:10]
        # Update menu
        self._update_recent_projects_menu()

    def _remove_from_recent_projects(self, project_path):
        """Remove a project from the recent projects list."""
        if project_path in self.recent_projects:
            self.recent_projects.remove(project_path)
            # Update menu
            self._update_recent_projects_menu()

    def clear_recent_projects(self):
        """Clear the recent projects list."""
        self.recent_projects = []
        self._update_recent_projects_menu()

    def load_recent_projects(self):
        """Load recent projects from settings or config."""
        try:
            # Try to load from config manager if available
            if hasattr(self, 'config_manager') and self.config_manager:
                self.recent_projects = self.config_manager.get('recent_projects', [])
            else:
                self.recent_projects = []
        except Exception as e:
            logging.error(f"Failed to load recent projects: {e}")
            self.recent_projects = []

    def configure_plugins(self):
        """Open plugin configuration dialog"""
        try:
            from ui.PluginsConfig import PluginsConfigDialog
            config_dialog = PluginsConfigDialog(self.plugin_manager, parent=self)
            config_dialog.exec_()
        except Exception as e:
            logger.error(f"Error opening plugin configuration: {str(e)}")
            QMessageBox.warning(self, "Plugin Configuration Error", 
                               f"Could not open plugin configuration: {str(e)}")

    def show_settings(self):
        """Open application settings dialog"""
        try:
            from app.gui.SettingsDialog import SettingsDialog
            settings_dialog = SettingsDialog(self.config_manager, parent=self)
            if settings_dialog.exec_() == QDialog.Accepted:
                self._setup_background_tasks()
                if hasattr(self, "statusbar") and self.statusbar:
                    self.statusbar.showMessage("Settings updated", 5000)
        except Exception as e:
            logger.error(f"Error opening settings: {str(e)}")
            QMessageBox.warning(self, "Settings Error",
                               f"Could not open settings: {str(e)}")



class CreepyAIGUI(CreepyMainWindow):
    """Compatibility wrapper exposing the legacy CreepyAI GUI class name."""

    def __init__(
        self,
        engine=None,
        config_manager=None,
        parent=None,
        load_plugins: bool = True,
    ):
        self.engine = engine
        if config_manager is None and engine is not None:
            config_manager = getattr(engine, "config_manager", None)
            if config_manager is None:
                config_manager = getattr(engine, "settings_manager", None)
        super().__init__(config_manager=config_manager, parent=parent, load_plugins=load_plugins)


def launch_gui(
    config_path: Optional[str] = None,
    app_root: Optional[str] = None,
    load_plugins: bool = True,
) -> int:
    """Launch the CreepyAI Qt application."""

    if app_root and app_root not in sys.path:
        sys.path.insert(0, app_root)

    try:
        setup_webengine_options()
    except Exception:
        logger.exception("Failed to configure Qt WebEngine options")

    config_manager = ConfigManager(config_path)

    qt_app = QApplication.instance()
    if qt_app is None:
        qt_app = QApplication(sys.argv)

    window = CreepyMainWindow(config_manager=config_manager, load_plugins=load_plugins)
    window.show()

    return qt_app.exec_()


__all__ = ["CreepyMainWindow", "CreepyAIGUI", "launch_gui"]
