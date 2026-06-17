"""ASPIS — the shield for autonomous software production.

A file-first, deterministic software-production system. This package is the
engine; project state lives in plain files under ``.asps/``.
"""

# Single source of truth for the version. ``pyproject.toml`` reads it from here
# via ``[tool.hatch.version]`` so the number is never duplicated.
__version__ = "0.0.1"
