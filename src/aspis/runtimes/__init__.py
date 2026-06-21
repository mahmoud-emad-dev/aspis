"""Runtime adapter registry — auto-discovering.

Every module in this package (except ``base``) is scanned for
:class:`~aspis.runtimes.base.RuntimeAdapter` subclasses, which are registered by
their ``name``. So adding a runtime is just dropping a ``<name>.py`` module that
defines an adapter — no edit here, no edit to the transformer.
"""

from __future__ import annotations

import importlib
import pkgutil

from aspis.runtimes.base import RuntimeAdapter


def _discover() -> dict[str, RuntimeAdapter]:
    """Import sibling modules and register every concrete RuntimeAdapter found."""
    adapters: dict[str, RuntimeAdapter] = {}
    for info in pkgutil.iter_modules(__path__):
        if info.name == "base":
            continue
        module = importlib.import_module(f"{__name__}.{info.name}")
        for value in vars(module).values():
            is_adapter = (
                isinstance(value, type)
                and issubclass(value, RuntimeAdapter)
                and value is not RuntimeAdapter
            )
            if is_adapter:
                adapter = value()
                adapters[adapter.name] = adapter
    return adapters


_ADAPTERS: dict[str, RuntimeAdapter] = _discover()


def get_adapter(runtime: str) -> RuntimeAdapter:
    """Return the adapter for *runtime* (raises KeyError if unknown)."""
    if runtime not in _ADAPTERS:
        known = ", ".join(sorted(_ADAPTERS))
        raise KeyError(f"unknown runtime: {runtime} (known: {known})")
    return _ADAPTERS[runtime]


def available_runtimes() -> tuple[str, ...]:
    """Return the registered runtime names."""
    return tuple(_ADAPTERS)


def runtime_dirs() -> tuple[str, ...]:
    """Return every runtime's on-disk project dir (e.g. ``.claude``, ``.opencode``)."""
    return tuple(adapter.runtime_dir for adapter in _ADAPTERS.values())


def mode_runtime() -> str | None:
    """Return the name of the runtime that expresses agent ``mode`` (or ``None``).

    The one runtime whose leads can be promoted from subagent to primary; callers
    resolve it here instead of hardcoding a runtime name.
    """
    for adapter in _ADAPTERS.values():
        if adapter.supports_mode:
            return adapter.name
    return None
