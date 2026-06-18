"""Single-source constants for ASPIS.

Plain, static facts shared across modules. Anything configurable at runtime
belongs in :mod:`aspis.settings`; this module holds the fixed names the engine
is built around, so they are defined exactly once.
"""

from __future__ import annotations

#: Folder that marks a directory as an ASPIS project (the project "brain").
BRAIN_DIR = ".asps"

#: Subfolder under the brain holding Type-1 lifecycle hook scripts, grouped by event.
LIFECYCLE_DIR = "lifecycle"

#: Runtime tools ASPIS can export to. New runtimes are added here.
RUNTIMES = ("opencode", "claude")
