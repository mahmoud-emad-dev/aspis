"""ASPIS lifecycle engine.

Every operation runs as ``pre-<op> hooks → core logic → post-<op> hooks``.
Operations register a core callable; the engine is generic and knows nothing
about init or bootstrap specifically, so new operations, events, or hooks are
added without changing this module.

A :class:`Context` flows through all three stages, so the core logic and the
post hooks can read whatever earlier stages produced (e.g. a pre-hook report).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Context:
    """Mutable state carried through one operation run."""

    operation: str
    root: Path
    options: dict = field(default_factory=dict)
    results: dict = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)

    def log(self, message: str) -> None:
        """Record a human-readable progress line."""
        self.messages.append(message)


#: A core handler runs an operation's real logic against the context.
CoreHandler = Callable[[Context], object]

#: A hook runner executes the Type-1 hooks registered for an event.
HookRun = Callable[[str, Context], None]


def _no_hooks(event: str, ctx: Context) -> None:
    """Default hook runner: do nothing (used until a real runner is wired in)."""
    return None


@dataclass(frozen=True)
class Operation:
    """A registered lifecycle operation (e.g. ``init``, ``bootstrap``)."""

    name: str
    core: CoreHandler


class Engine:
    """Registry and runner for lifecycle operations."""

    def __init__(self, run_hooks: HookRun = _no_hooks) -> None:
        self._operations: dict[str, Operation] = {}
        self._run_hooks = run_hooks

    def register(self, name: str, core: CoreHandler) -> None:
        """Register *core* as the handler for operation *name*."""
        if name in self._operations:
            raise ValueError(f"operation already registered: {name}")
        self._operations[name] = Operation(name=name, core=core)

    def run(self, name: str, root: Path | str, /, **options: object) -> Context:
        """Run *name* as pre-hooks → core → post-hooks and return the context."""
        if name not in self._operations:
            raise KeyError(f"unknown operation: {name}")

        operation = self._operations[name]
        ctx = Context(operation=name, root=Path(root), options=dict(options))

        self._run_hooks(f"pre-{name}", ctx)
        operation.core(ctx)
        self._run_hooks(f"post-{name}", ctx)
        return ctx
