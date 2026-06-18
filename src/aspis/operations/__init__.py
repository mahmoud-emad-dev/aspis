"""Lifecycle operations registry.

Each operation registers its core handler on the engine. To add an operation
(e.g. bootstrap), create its module and call its ``register`` here.
"""

from __future__ import annotations

from aspis.lifecycle import Engine
from aspis.operations import init as _init


def register_all(engine: Engine) -> None:
    """Register every built-in operation on *engine*."""
    _init.register(engine)
