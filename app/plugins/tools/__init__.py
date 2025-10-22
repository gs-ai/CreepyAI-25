"""Compatibility package providing legacy plugin tooling imports.

Historically the ``app.plugins.tools`` package duplicated a large portion of the
primary ``app.plugins`` modules. Those copies diverged over time and even became
syntactically invalid, so we now defer to the canonical implementations and
keep this namespace as a thin compatibility layer.
"""

from importlib import import_module as _import_module
from pkgutil import iter_modules as _iter_modules
from types import ModuleType as _ModuleType
from typing import Iterable as _Iterable
import sys as _sys

_BASE_PACKAGE = "app.plugins"
_TOOLS_PACKAGE = __name__

def _available_modules() -> _Iterable[str]:
    base_pkg = _import_module(_BASE_PACKAGE)
    for info in _iter_modules(base_pkg.__path__):
        if info.name == "tools":
            continue
        yield info.name


def __getattr__(name: str) -> _ModuleType:
    if name.startswith("_"):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    try:
        module = _import_module(f"{_BASE_PACKAGE}.{name}")
    except ModuleNotFoundError as exc:  # pragma: no cover - defensive guard
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc

    _sys.modules[f"{_TOOLS_PACKAGE}.{name}"] = module
    return module


def __dir__() -> list[str]:
    base_attrs = {"__dir__", "__doc__", "__getattr__"}
    base_attrs.update(globals().keys())
    base_attrs.update(_available_modules())
    return sorted(attr for attr in base_attrs if not attr.startswith("_"))


__all__ = [name for name in _available_modules()]
