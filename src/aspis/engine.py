"""Engine assembly — wire the lifecycle runner to the Type-1 hook runner.

This is the one place that connects the generic :class:`~aspis.lifecycle.Engine`
to the real :class:`~aspis.hooks.HookRunner`. Operations (init, bootstrap, ...)
register themselves onto the engine returned here.
"""

from __future__ import annotations

from aspis.hooks import HookRunner
from aspis.lifecycle import Engine


def build_engine() -> Engine:
    """Return an Engine that runs discovered Type-1 lifecycle hooks."""
    return Engine(run_hooks=HookRunner())
