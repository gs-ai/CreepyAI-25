"""Helpers for adapting legacy plugins to the modern CreepyAI API."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, Protocol

logger = logging.getLogger(__name__)


class LegacyPluginProtocol(Protocol):
    """Subset of attributes expected from legacy plugins."""

    name: str
    description: str

    def run(self, *args: Any, **kwargs: Any) -> Any: ...  # pragma: no cover - protocol


@dataclass
class PluginDescriptor:
    """Lightweight description used during adaptation."""

    name: str
    description: str
    original: Any


class PluginCompatibilityLayer:
    """Manage adapters that turn legacy plugin objects into modern ones."""

    def __init__(self) -> None:
        self._adapters: Dict[str, Callable[[Any], Any]] = {}

    # Public API -----------------------------------------------------
    def register_adapter(self, class_name: str, factory: Callable[[Any], Any]) -> None:
        """Register a callable that wraps instances of ``class_name``."""

        self._adapters[class_name] = factory
        logger.debug("Registered compatibility adapter for %s", class_name)

    def adapt(self, plugin: Any) -> Any:
        """Return a compatible plugin instance for ``plugin``."""

        class_name = plugin.__class__.__name__
        factory = self._adapters.get(class_name)
        if factory:
            logger.debug("Adapting %s via registered factory", class_name)
            return factory(plugin)
        return self._wrap_generic(plugin)

    # Convenience helpers -------------------------------------------
    def describe(self, plugin: Any) -> PluginDescriptor:
        """Return a :class:`PluginDescriptor` for ``plugin``."""

        name = getattr(plugin, "name", plugin.__class__.__name__)
        description = getattr(plugin, "description", "Legacy plugin")
        return PluginDescriptor(name=name, description=description, original=plugin)

    # Internal implementation --------------------------------------
    @staticmethod
    def _wrap_generic(plugin: Any) -> Any:
        """Wrap ``plugin`` with a modern interface when no adapter is registered."""

        layer = globals().get("_default_layer")
        if isinstance(layer, PluginCompatibilityLayer):
            descriptor = layer.describe(plugin)
        else:  # pragma: no cover - defensive fallback
            descriptor = PluginCompatibilityLayer().describe(plugin)

        class GenericWrapper:
            def __init__(self, wrapped: Any, info: PluginDescriptor) -> None:
                self._wrapped = wrapped
                self._info = info

            def get_info(self) -> Dict[str, str]:
                return {
                    "name": self._info.name,
                    "description": self._info.description,
                }

            def configure(self, *args: Any, **kwargs: Any) -> bool:
                return True

            def run(self, *args: Any, **kwargs: Any) -> Any:
                if hasattr(self._wrapped, "run"):
                    return self._wrapped.run(*args, **kwargs)
                if hasattr(self._wrapped, "execute"):
                    return self._wrapped.execute(*args, **kwargs)
                if hasattr(self._wrapped, "collect_locations"):
                    target = args[0] if args else ""
                    return self._wrapped.collect_locations(target)
                logger.warning("Legacy plugin %s has no executable entry point", self._info.name)
                return None

        return GenericWrapper(plugin, descriptor)


_default_layer = PluginCompatibilityLayer()


def register_adapter(class_name: str, factory: Callable[[Any], Any]) -> None:
    """Register a compatibility adapter on the default layer."""

    _default_layer.register_adapter(class_name, factory)


def adapt_plugin(plugin: Any) -> Any:
    """Adapt ``plugin`` using the default compatibility layer."""

    return _default_layer.adapt(plugin)


def describe_plugin(plugin: Any) -> PluginDescriptor:
    """Return a description of ``plugin`` using the default layer."""

    return _default_layer.describe(plugin)


__all__ = [
    "PluginCompatibilityLayer",
    "PluginDescriptor",
    "adapt_plugin",
    "describe_plugin",
    "register_adapter",
]
