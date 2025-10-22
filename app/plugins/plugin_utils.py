"""Utility helpers for working with CreepyAI plugins."""

from __future__ import annotations

import importlib.util
import inspect
import logging
import os
import sys
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, Type

logger = logging.getLogger("creepyai.plugins.utils")


def get_plugin_metadata(plugin_instance: Any) -> Dict[str, Any]:
    """Return a metadata dictionary for ``plugin_instance``.

    The helper mirrors :meth:`app.plugins.plugin_base.PluginBase.get_metadata`
    but works with any object that exposes the expected attributes.
    """

    return {
        "name": getattr(plugin_instance, "name", plugin_instance.__class__.__name__),
        "description": getattr(plugin_instance, "description", ""),
        "version": getattr(plugin_instance, "version", "1.0.0"),
        "author": getattr(plugin_instance, "author", "Unknown"),
        "enabled": getattr(plugin_instance, "enabled", True),
    }


def _load_module_from_path(module_path: str, module_name: str) -> Optional[ModuleType]:
    """Load and return a module from ``module_path``.

    The helper returns ``None`` when the module cannot be loaded and logs a
    meaningful error for debugging purposes.
    """

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        logger.error("Could not create module spec for %s", module_path)
        return None

    module = importlib.util.module_from_spec(spec)
    # ``sys.modules`` registration ensures that imports performed by the module
    # itself resolve correctly during execution.
    sys.modules[module_name] = module

    try:
        spec.loader.exec_module(module)  # type: ignore[assignment]
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Failed to import plugin module %s: %s", module_path, exc)
        return None

    return module


def scan_for_plugin_classes(module_path: str, base_class: Type | None = None) -> List[Type]:
    """Discover plugin classes defined in ``module_path``.

    Args:
        module_path: Path to the Python file to inspect.
        base_class: Optional base class that discovered plugins must inherit
            from.

    Returns:
        A list containing each matching class.
    """

    if not os.path.exists(module_path):
        logger.error("Plugin module does not exist: %s", module_path)
        return []

    module_name = f"creepyai_plugin_{hash(module_path)}"
    module = _load_module_from_path(module_path, module_name)
    if module is None:
        return []

    plugin_classes: List[Type] = []
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ != module.__name__:
            continue

        if base_class is not None:
            try:
                if not issubclass(obj, base_class) or obj is base_class:
                    continue
            except TypeError:
                continue

        plugin_classes.append(obj)

    return plugin_classes


def validate_plugin(plugin: Any) -> Tuple[bool, List[str]]:
    """Validate ``plugin`` and return ``(is_valid, errors)``."""

    errors: List[str] = []
    required_attrs = ["name", "description", "version", "author"]
    for attr in required_attrs:
        if not hasattr(plugin, attr):
            errors.append(f"Missing required attribute: {attr}")

    required_methods = ["initialize", "execute"]
    for method in required_methods:
        if not hasattr(plugin, method) or not callable(getattr(plugin, method)):
            errors.append(f"Missing required method: {method}")

    return len(errors) == 0, errors


def discover_plugins(directory: str, base_class: Type | None = None) -> Dict[str, Type]:
    """Scan ``directory`` for plugin modules and return discovered classes."""

    if not os.path.isdir(directory):
        logger.error("Plugin directory does not exist or is not a directory: %s", directory)
        return {}

    discovered: Dict[str, Type] = {}
    for filename in os.listdir(directory):
        if not filename.endswith(".py") or filename.startswith("__"):
            continue

        module_path = os.path.join(directory, filename)
        for plugin_class in scan_for_plugin_classes(module_path, base_class):
            discovered[plugin_class.__name__] = plugin_class

    return discovered


def import_plugin_module(module_path: str) -> Optional[ModuleType]:
    """Import and return a plugin module located at ``module_path``."""

    if not os.path.exists(module_path):
        logger.error("Plugin module does not exist: %s", module_path)
        return None

    module_name = os.path.splitext(os.path.basename(module_path))[0]
    return _load_module_from_path(module_path, f"creepyai_plugin_{module_name}")


def get_plugin_config_path(plugin_name: str) -> str:
    """Return the configuration path associated with ``plugin_name``."""

    from app.core.config import Configuration

    config = Configuration()
    project_root = config.get_project_root()

    candidate_paths = [
        os.path.join(project_root, "configs", "plugins", f"{plugin_name}.conf"),
        os.path.join(project_root, "plugins", "configs", f"{plugin_name}.conf"),
    ]

    for path in candidate_paths:
        if os.path.exists(path):
            return path

    # Return the default location inside ``configs/plugins`` when no dedicated
    # configuration file has been created yet.
    return candidate_paths[0]

