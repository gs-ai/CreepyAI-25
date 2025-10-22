"""Advanced plugin cataloguing infrastructure for CreepyAI.

This module provides a manifest builder that understands the structure of
``app.plugins`` and any user supplied plugin directories.  It extracts rich
metadata for every plugin, persists the information to a cache on disk and can
reconstruct lazily loadable descriptors without executing the heavy discovery
logic repeatedly.  The catalog becomes the single source of truth for the rest
of the application which drastically improves startup times while surfacing
actionable diagnostics for broken plugins.
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import inspect
import json
import logging
import sys
import types
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence


LOGGER = logging.getLogger(__name__)


MANIFEST_SCHEMA_VERSION = 1
_CACHED_FALSE = object()


def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


@dataclass(frozen=True)
class PluginDescriptor:
    """Serializable description of a plugin module.

    The descriptor keeps enough information to lazily import and instantiate the
    plugin class without relying on global state.  It is light-weight so it can
    be stored inside the JSON manifest while still exposing convenience helpers
    for the runtime ``PluginManager``.
    """

    identifier: str
    module: str
    class_name: str
    category: str
    path: str
    fingerprint: str
    info: Dict[str, Any] = field(default_factory=dict)
    load_error: Optional[str] = None
    is_package_module: bool = True

    def as_dict(self) -> Dict[str, Any]:
        """Return a JSON friendly representation."""

        return {
            "identifier": self.identifier,
            "module": self.module,
            "class_name": self.class_name,
            "category": self.category,
            "path": self.path,
            "fingerprint": self.fingerprint,
            "info": self.info,
            "load_error": self.load_error,
            "is_package_module": self.is_package_module,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "PluginDescriptor":
        return cls(
            identifier=payload["identifier"],
            module=payload["module"],
            class_name=payload["class_name"],
            category=payload["category"],
            path=payload["path"],
            fingerprint=payload["fingerprint"],
            info=payload.get("info", {}),
            load_error=payload.get("load_error"),
            is_package_module=payload.get("is_package_module", True),
        )

    # ------------------------------------------------------------------
    # Runtime helpers
    # ------------------------------------------------------------------
    def instantiate(self) -> Any:
        """Instantiate the plugin class described by this descriptor."""

        module = self._import()
        try:
            plugin_class = self._resolve_class(module)
        except AttributeError as exc:  # pragma: no cover - defensive guard
            raise ImportError(f"Unable to resolve class {self.class_name!r}") from exc

        return plugin_class()

    def _import(self) -> types.ModuleType:
        """Import the target module regardless of where it lives on disk."""

        if self.is_package_module:
            return importlib.import_module(self.module)

        spec = importlib.util.spec_from_file_location(self.module, self.path)
        if not spec or not spec.loader:
            raise ImportError(f"Cannot create import spec for {self.path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[self.module] = module
        spec.loader.exec_module(module)
        return module

    def _resolve_class(self, module: types.ModuleType) -> type:
        """Fetch the plugin class from an imported module."""

        target = module
        for part in self.class_name.split("."):
            target = getattr(target, part)

        if not isinstance(target, type):  # pragma: no cover - defensive guard
            raise AttributeError(f"Resolved attribute {self.class_name!r} is not a class")
        return target


class PluginCatalog:
    """Builds, caches and exposes ``PluginDescriptor`` instances."""

    def __init__(
        self,
        roots: Iterable[str | Path],
        *,
        base_package: str = "app.plugins",
        cache_path: Optional[str | Path] = None,
    ) -> None:
        self.roots: List[Path] = []
        for root in roots:
            path = Path(root).resolve()
            if path.exists():
                self.roots.append(path)

        if not self.roots:
            raise ValueError("At least one plugin root must exist")

        self.base_package = base_package
        package_module = importlib.import_module(base_package)
        self.package_root = Path(package_module.__file__).resolve().parent

        if cache_path is None:
            cache_dir = Path.home() / ".creepyai" / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_path = cache_dir / "plugin_catalog.json"

        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def load(self, *, force_refresh: bool = False) -> List[PluginDescriptor]:
        if not force_refresh:
            descriptors = self._load_cache()
            if descriptors is not None:
                return descriptors

        descriptors = list(self._build_descriptors())
        self._store_cache(descriptors)
        return descriptors

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------
    def _load_cache(self) -> Optional[List[PluginDescriptor]]:
        if not self.cache_path.exists():
            return None

        try:
            payload = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - corrupted cache
            LOGGER.warning("Failed to read plugin catalog cache: %s", exc)
            return None

        if payload.get("schema_version") != MANIFEST_SCHEMA_VERSION:
            return None

        cached_roots = [Path(root) for root in payload.get("roots", [])]
        if set(map(str, cached_roots)) != set(map(str, self.roots)):
            return None

        entries = payload.get("entries", [])
        if not entries:
            return None

        # Validate fingerprints
        for entry in entries:
            path = Path(entry["path"])
            if not path.exists():
                return None
            if self._fingerprint(path) != entry.get("fingerprint"):
                return None

        return [PluginDescriptor.from_dict(entry) for entry in entries]

    def _store_cache(self, descriptors: Sequence[PluginDescriptor]) -> None:
        payload = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "generated_at": _now_iso(),
            "roots": [str(root) for root in self.roots],
            "entries": [descriptor.as_dict() for descriptor in descriptors],
        }
        self.cache_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    # ------------------------------------------------------------------
    # Descriptor construction
    # ------------------------------------------------------------------
    def _build_descriptors(self) -> Iterator[PluginDescriptor]:
        discovered: Dict[str, PluginDescriptor] = {}

        for path in self._iter_plugin_files():
            identifier = self._identifier_from_path(path)
            if identifier in discovered:
                LOGGER.debug("Duplicate plugin identifier %s for %s", identifier, path)
                continue

            descriptor = self._build_descriptor(path, identifier)
            discovered[identifier] = descriptor
            yield descriptor

    def _iter_plugin_files(self) -> Iterator[Path]:
        for root in self.roots:
            for candidate in sorted(root.rglob("*.py")):
                if candidate.name.startswith("__"):
                    continue
                yield candidate

    def _build_descriptor(self, path: Path, identifier: str) -> PluginDescriptor:
        module_name, is_package = self._module_name_for_path(path)
        fingerprint = self._fingerprint(path)
        category = self._category_from_path(path)

        info: Dict[str, Any] = {}
        load_error: Optional[str] = None
        class_name = ""

        try:
            module = self._import_probe(module_name, path, is_package)
            plugin_class = self._locate_plugin_class(module)
            if plugin_class is None:
                raise RuntimeError("No plugin class found")

            class_name = plugin_class.__qualname__
            info, load_error = self._extract_metadata(plugin_class)
        except Exception as exc:  # pragma: no cover - exercised in integration tests
            load_error = f"{type(exc).__name__}: {exc}"
            class_name = class_name or "Plugin"

        return PluginDescriptor(
            identifier=identifier,
            module=module_name,
            class_name=class_name,
            category=category,
            path=str(path),
            fingerprint=fingerprint,
            info=info,
            load_error=load_error,
            is_package_module=is_package,
        )

    def _import_probe(self, module_name: str, path: Path, is_package: bool) -> types.ModuleType:
        if is_package:
            return importlib.import_module(module_name)

        spec = importlib.util.spec_from_file_location(module_name, path)
        if not spec or not spec.loader:
            raise ImportError(f"Cannot import {module_name} from {path}")

        module = importlib.util.module_from_spec(spec)
        loader = spec.loader
        assert loader is not None
        loader.exec_module(module)
        return module

    def _locate_plugin_class(self, module: types.ModuleType) -> Optional[type]:
        from app.plugins.base_plugin import BasePlugin  # Lazy import to avoid cycles

        # Prioritise a top-level ``Plugin`` symbol.
        if hasattr(module, "Plugin") and isinstance(module.Plugin, type):
            return module.Plugin

        candidates: List[type] = []
        for attr in module.__dict__.values():
            if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                if attr.__module__ == module.__name__:
                    candidates.append(attr)

        if not candidates:
            return None

        # Prefer the first class defined in the module to maintain backwards
        # compatibility with older plugins that expose multiple helpers.
        candidates.sort(key=lambda cls: getattr(cls, "__qualname__", cls.__name__))
        return candidates[0]

    def _extract_metadata(self, plugin_class: type) -> tuple[Dict[str, Any], Optional[str]]:
        info: Dict[str, Any] = {}
        load_error: Optional[str] = None

        instance = self._instantiate_safely(plugin_class)
        if isinstance(instance, Exception):
            return info, f"{type(instance).__name__}: {instance}"

        try:
            if hasattr(instance, "get_info"):
                retrieved = instance.get_info()  # type: ignore[misc]
                if isinstance(retrieved, dict):
                    info.update(retrieved)
        except Exception as exc:
            load_error = f"get_info failed: {exc}"

        info.setdefault("name", getattr(instance, "name", plugin_class.__name__))
        info.setdefault("description", getattr(instance, "description", ""))
        info.setdefault("version", getattr(instance, "version", "0.0"))
        info.setdefault("author", getattr(instance, "author", "Unknown"))

        try:
            if hasattr(instance, "get_configuration_options"):
                options = instance.get_configuration_options()  # type: ignore[misc]
                if isinstance(options, list):
                    info["configuration_options"] = options
        except Exception as exc:
            load_error = f"get_configuration_options failed: {exc}"

        return info, load_error

    def _instantiate_safely(self, plugin_class: type) -> Any | Exception:
        try:
            signature = inspect.signature(plugin_class)
            for parameter in signature.parameters.values():
                if (
                    parameter.default is inspect.Signature.empty
                    and parameter.kind
                    in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD)
                ):
                    raise TypeError(
                        f"Plugin class {plugin_class.__qualname__} requires arguments"
                    )
        except (TypeError, ValueError):
            # The inspection failed which likely means we can still attempt to instantiate.
            pass

        try:
            return plugin_class()
        except Exception as exc:  # pragma: no cover - instantiation failure is recorded in manifest
            return exc

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _module_name_for_path(self, path: Path) -> tuple[str, bool]:
        try:
            relative = path.relative_to(self.package_root)
        except ValueError:
            module_name = self._ephemeral_module_name(path)
            return module_name, False

        parts = list(relative.parts)
        if parts[-1] == "__init__.py":
            parts = parts[:-1]
        else:
            parts[-1] = parts[-1][:-3]

        module_name = ".".join([self.base_package, *parts]) if parts else self.base_package
        return module_name, True

    def _ephemeral_module_name(self, path: Path) -> str:
        digest = hashlib.sha1(str(path).encode("utf-8")).hexdigest()
        return f"creepyai_external_plugin_{digest}"

    def _category_from_path(self, path: Path) -> str:
        categories = {"social_media", "location_services", "data_extraction", "tools", "other"}
        for part in path.parts:
            if part in categories:
                return part
        return "uncategorized"

    def _identifier_from_path(self, path: Path) -> str:
        if path.name == "__init__.py":
            return path.parent.name.lower()
        return path.stem.lower()

    def _fingerprint(self, path: Path) -> str:
        stat = path.stat()
        digest = hashlib.sha256()
        digest.update(str(stat.st_mtime_ns).encode("utf-8"))
        digest.update(str(stat.st_size).encode("utf-8"))
        digest.update(str(path).encode("utf-8"))
        return digest.hexdigest()

