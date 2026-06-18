"""Single-source constants for ASPIS.

Plain, static facts shared across modules. Anything configurable at runtime
belongs in :mod:`aspis.settings`; this module holds the fixed names the engine
is built around, so they are defined exactly once.
"""

from __future__ import annotations

#: Folder that marks a directory as an ASPIS project (the project "brain").
BRAIN_DIR = ".asps"

#: Subfolder under the brain where lifecycle hook scripts live, grouped by event.
#: Lifecycle hooks are transient (removed after bootstrap), so they share the
#: hooks folder rather than a separate top-level dir.
HOOKS_DIR = "hooks"

#: Runtime tools ASPIS can export to. New runtimes are added here.
RUNTIMES = ("opencode", "claude")
