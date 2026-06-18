"""Runtime adapter registry.

One adapter per runtime tool. To add a runtime: create the module and add its
adapter here — the transformer and exporter look runtimes up through this
registry, so nothing else changes.
"""

from __future__ import annotations

from aspis.runtimes.base import RuntimeAdapter
from aspis.runtimes.claude import ClaudeAdapter
from aspis.runtimes.opencode import OpenCodeAdapter

_ADAPTERS: dict[str, RuntimeAdapter] = {
    adapter.name: adapter for adapter in (OpenCodeAdapter(), ClaudeAdapter())
}


def get_adapter(runtime: str) -> RuntimeAdapter:
    """Return the adapter for *runtime* (raises KeyError if unknown)."""
    if runtime not in _ADAPTERS:
        known = ", ".join(sorted(_ADAPTERS))
        raise KeyError(f"unknown runtime: {runtime} (known: {known})")
    return _ADAPTERS[runtime]


def available_runtimes() -> tuple[str, ...]:
    """Return the registered runtime names."""
    return tuple(_ADAPTERS)
