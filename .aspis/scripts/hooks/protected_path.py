#!/usr/bin/env python3
"""Protected-path validation — PreToolUse hook (R-008 surface, F-018 T-044).

Writes to certain paths change architecture, rules, permissions, or
security posture and therefore require explicit governance approval (R-008).
This hook is the *gate* the runtime fires before a write/edit; it returns
one of:

- ``GOVERNANCE_REQUIRED`` — the target matches a protected path. The runtime
  should block (or, in warn mode, surface) the write until the owner has
  approved the change.
- ``ALLOW`` — the target is not on the protected list; no gate is needed.

Protected surfaces:
- ``.opencode/``     — opencode runtime config (cross-runtime parity)
- ``.claude/``       — claude runtime config (PreToolUse hooks, etc.)
- ``.aspis/rules/``  — system / project rule files
- ``.aspis/config/project.yaml`` — the project configuration of record

Stdlib only (``pathlib``, ``sys``, ``argparse``).
"""
from __future__ import annotations

import argparse
from pathlib import Path

# Protected paths. A trailing ``/`` means "everything under this directory";
# no trailing slash means "this exact file only". A path that *equals* a
# directory protection (e.g. the user passes ``.claude``) is not treated as
# a write target — a file path always has something under the directory.
PROTECTED_PATHS: tuple[str, ...] = (
    ".opencode/",
    ".claude/",
    ".aspis/rules/",
    ".aspis/config/project.yaml",
)


def _normalize(path: str) -> str:
    """Return *path* in forward-slash repo-relative form.

    Absolute paths are made relative to the current working directory when
    possible; otherwise they pass through unchanged so the prefix check
    still does the right thing on Windows-style paths.
    """
    p = Path(path)
    if p.is_absolute():
        try:
            return p.resolve().relative_to(Path.cwd()).as_posix()
        except ValueError:
            return p.as_posix()
    return p.as_posix()


def check_path(path: str) -> tuple[str, str]:
    """Return ``(verdict, reason)`` for *path*.

    A directory protection (``".opencode/"``) matches any path *under* the
    directory, but not the directory itself (a write target always names a
    file inside it). An exact-file protection (``.aspis/config/project.yaml``)
    matches only that exact relative path.
    """
    norm = _normalize(path)
    for protected in PROTECTED_PATHS:
        if protected.endswith("/"):
            if norm.startswith(protected):
                return (
                    "GOVERNANCE_REQUIRED",
                    f"path '{norm}' is under protected '{protected}' (R-008)",
                )
        else:
            if norm == protected:
                return (
                    "GOVERNANCE_REQUIRED",
                    f"path '{norm}' is the protected file '{protected}' (R-008)",
                )
    return "ALLOW", f"path '{norm}' is not on the protected list"


def main() -> int:
    """CLI entry point: parse ``--path`` and print the verdict."""
    parser = argparse.ArgumentParser(
        description=(
            "Check whether a file write target is on a protected path. "
            "Returns ALLOW or GOVERNANCE_REQUIRED."
        ),
    )
    parser.add_argument(
        "--path",
        required=True,
        help="File path to check (relative or absolute).",
    )
    args = parser.parse_args()

    verdict, reason = check_path(args.path)
    print(f"{verdict} — {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
