"""Environment health checks behind ``aspis doctor``.

Each check is a small function that takes the project root and returns a
:class:`Check`. ``run_checks`` runs them all. The CLI command is just a printer
over this — adding a check is a one-line edit to ``CHECKS`` with no branching
logic to maintain (checks-as-data, not an if-chain).
"""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from aspis import __version__
from aspis.project import is_project

#: Minimum Python the engine supports (kept in step with requires-python).
MIN_PYTHON = (3, 11)


@dataclass(frozen=True)
class Check:
    """The outcome of a single health check.

    ``status`` is one of ``"ok"``, ``"warn"``, or ``"fail"``. Only ``"fail"``
    makes ``aspis doctor`` exit non-zero.
    """

    name: str
    status: str
    detail: str


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def check_python(_: Path) -> Check:
    """Verify the running Python meets the minimum supported version."""
    current = sys.version_info[:2]
    running = f"{current[0]}.{current[1]}"
    if current >= MIN_PYTHON:
        return Check("python", "ok", f"Python {running}")
    needed = f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
    return Check("python", "fail", f"Python {running} (need >= {needed})")


def check_aspis(_: Path) -> Check:
    """Report the installed ASPIS version (always informational)."""
    return Check("aspis", "ok", f"aspis {__version__}")


def check_git(_: Path) -> Check:
    """Check that Git is on PATH — the file-first workflow depends on it."""
    found = shutil.which("git")
    if found:
        return Check("git", "ok", found)
    return Check("git", "warn", "git not found on PATH")


def check_project(root: Path) -> Check:
    """Report whether ``root`` is an ASPIS project (informational)."""
    if is_project(root):
        return Check("project", "ok", f"ASPIS project at {root}")
    return Check("project", "warn", "not an ASPIS project (run `aspis init`)")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

#: Every check doctor runs, in display order.
CHECKS = (check_python, check_aspis, check_git, check_project)


def run_checks(root: Path) -> list[Check]:
    """Run every registered check against ``root`` and return the results."""
    return [check(root) for check in CHECKS]
