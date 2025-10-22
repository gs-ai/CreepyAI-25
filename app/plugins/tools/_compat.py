"""Helper utilities for compatibility modules in :mod:`app.plugins.tools`."""

from __future__ import annotations

from importlib import import_module
import runpy
import sys
from types import ModuleType
from typing import Callable

_BASE_PACKAGE = "app.plugins"


def _copy_public_attributes(source: ModuleType, destination: ModuleType) -> None:
    """Populate ``destination`` with attributes from ``source``."""

    source_dict = source.__dict__
    dest_dict = destination.__dict__

    for name, value in source_dict.items():
        if name.startswith("_"):
            if name in {"__all__", "__doc__", "__annotations__", "__getattr__", "__dir__"}:
                dest_dict[name] = value
            continue
        dest_dict[name] = value

    dest_dict.setdefault("__annotations__", source_dict.get("__annotations__", {}))
    dest_dict.setdefault("__doc__", source.__doc__)
    dest_dict["__wrapped_module__"] = source

    if "__all__" not in dest_dict:
        if "__all__" in source_dict:
            dest_dict["__all__"] = list(source_dict["__all__"])  # type: ignore[index]
        else:
            dest_dict["__all__"] = [
                name for name in source_dict if not name.startswith("_")
            ]

    dest_dict["__package__"] = destination.__name__.rsplit(".", 1)[0]

    if hasattr(source, "__path__"):
        dest_dict["__path__"] = list(getattr(source, "__path__"))

    if "__getattr__" not in dest_dict:
        def _getattr(name: str) -> object:
            try:
                return getattr(source, name)
            except AttributeError as exc:  # pragma: no cover - defensive path
                raise AttributeError(
                    f"module {destination.__name__!r} has no attribute {name!r}"
                ) from exc

        dest_dict["__getattr__"] = _getattr

    if "__dir__" not in dest_dict:
        def _dir() -> list[str]:
            exported = destination.__dict__.get("__all__")
            if isinstance(exported, (list, tuple, set)):
                return sorted(exported)
            return sorted(name for name in source_dict if not name.startswith("_"))

        dest_dict["__dir__"] = _dir


def alias_module(current_module_name: str, *, base_package: str = _BASE_PACKAGE) -> Callable[[], None]:
    """Alias ``current_module_name`` to the real implementation under ``base_package``."""

    proxy_module = sys.modules[current_module_name]
    target_basename = current_module_name.rsplit(".", 1)[-1]
    target_module = import_module(f"{base_package}.{target_basename}")

    _copy_public_attributes(target_module, proxy_module)

    def _run_main() -> None:
        runpy.run_module(target_module.__name__, run_name="__main__")

    return _run_main
