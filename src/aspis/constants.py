"""Single-source constants for ASPIS.

Plain, static facts shared across modules. Anything configurable at runtime
belongs in :mod:`aspis.settings`; this module holds the fixed names the engine
is built around, so they are defined exactly once.
"""

from __future__ import annotations

#: Folder that marks a directory as an ASPIS project (the project "brain").
BRAIN_DIR = ".aspis"

#: Subfolder under the brain where lifecycle hook scripts live, grouped by event.
#: Lifecycle hooks are transient (removed after bootstrap), so they share the
#: hooks folder rather than a separate top-level dir.
HOOKS_DIR = "hooks"

#: Runtime tools ASPIS can export to. New runtimes are added here.
RUNTIMES = ("opencode", "claude")

#: Leads promoted from ``subagent`` to ``primary`` after a successful bootstrap.
#: Every agent ships as a subagent so a fresh project has a single entry point
#: (``project-lead``, which is always primary and is *not* listed here). Once the
#: project is live, these become directly selectable — yielding exactly five
#: primaries: project, system, planning, build, and review leads.
PROMOTE_TO_PRIMARY = ("system-lead", "planning-lead", "build-lead", "reviewer")
