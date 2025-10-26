"""
Main application engine for CreepyAI.

This module defines the ``Engine`` singleton that orchestrates
configuration loading, plugin management and execution. It aims to
provide a resilient entry point for the application by catching
unexpected errors and emitting structured logging messages.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional


logger = logging.getLogger("creepyai.engine")


class Engine:
    """Central coordinator for CreepyAI.

    The ``Engine`` is implemented as a singleton to ensure that there is
    exactly one active instance within a running process. It is responsible
    for loading configuration, initialising the plugin manager, and
    executing plugins on demand. Errors encountered during these
    operations are logged rather than propagated to the caller to
    prevent the entire application from crashing.
    """

    _instance: Optional["Engine"] = None

    def __new__(cls) -> "Engine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        # Prevent reinitialisation of the singleton instance
        if self._initialized:
            return

        # Configure logger
        logger.setLevel(logging.INFO)
        logger.debug("Engine logger configured at INFO level")

        self._initialized = True
        self.config: Dict[str, Any] = {}
        self.plugin_manager: Optional["PluginManager"] = None
        self.root_path: Path = Path()

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialise the engine with the given configuration.

        Parameters
        ----------
        config : dict
            Application configuration dictionary.

        Returns
        -------
        bool
            ``True`` on success, ``False`` otherwise.
        """
        try:
            self.config = config
            # Resolve application root path using path_utils helper.  Do not
            # import this at module scope to avoid circular import issues.
            from app.core.path_utils import get_app_root

            self.root_path = Path(get_app_root())
            logger.info("CreepyAI Engine initialised with root: %s", self.root_path)

            if config.get("plugins", {}).get("enabled", True):
                if not self._initialize_plugins():
                    logger.error("Failed to initialise plugin manager")
                    return False

            return True
        except Exception as exc:
            logger.exception("Engine initialisation failed: %s", exc)
            return False

    def _initialize_plugins(self) -> bool:
        """Set up the plugin manager and load available plugins.

        Returns
        -------
        bool
            ``True`` if the manager was created and plugins loaded successfully.
        """
        try:
            # Lazy import to avoid recursive imports
            from app.plugins.plugin_manager import PluginManager
        except ImportError:
            logger.exception("Could not import PluginManager class")
            return False

        try:
            self.plugin_manager = PluginManager()
            self.plugin_manager.initialize()
            self.plugin_manager.load_plugins()
            logger.info("Loaded %d plugins", len(self.plugin_manager.plugins))
            return True
        except Exception as exc:
            logger.exception("Failed to initialise plugins: %s", exc)
            return False

    def run_plugin(self, plugin_name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a plugin by its identifier.

        Parameters
        ----------
        plugin_name : str
            Identifier or alias of the plugin to execute.
        *args : tuple
            Positional arguments forwarded to the plugin ``run`` method.
        **kwargs : dict
            Keyword arguments forwarded to the plugin ``run`` method.

        Returns
        -------
        Any
            The result returned by the plugin’s ``run`` method, or ``None``
            if the plugin was not found or raised an exception.
        """
        if self.plugin_manager is None:
            logger.error("Plugin manager not initialised")
            return None

        plugin = self.plugin_manager.get_plugin(plugin_name)
        if plugin is None:
            logger.error("Plugin '%s' not found", plugin_name)
            return None

        # Some plugins implement ``run`` while others may define ``execute``;
        # prefer ``run`` and fall back to ``execute`` for backwards compatibility.
        callable_attr = getattr(plugin, "run", None) or getattr(plugin, "execute", None)
        if not callable(callable_attr):
            logger.error("Plugin '%s' has no runnable interface", plugin_name)
            return None

        try:
            return callable_attr(*args, **kwargs)
        except Exception as exc:
            logger.exception("Error executing plugin '%s': %s", plugin_name, exc)
            return None

    def shutdown(self) -> None:
        """Clean up resources held by the engine.

        Currently this method only logs the shutdown. It can be extended
        to close database connections or release other resources when such
        facilities are introduced.
        """
        logger.info("Shutting down CreepyAI engine")


# Backwards compatibility alias
CreepyAIEngine = Engine