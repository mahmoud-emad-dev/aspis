"""Project-layer helpers: identifying an ASPIS project and reading its settings.

A directory is an ASPIS project when it contains the brain folder (``.aspis/``) —
the durable, tool-neutral memory for that project. Project-tunable settings live in
``.aspis/config/project.yaml`` (the default build mode, model overrides); machine
state lives in the manifest. Keeping both in one place means every command agrees
on what "a project" means and where its settings are.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from aspis.constants import BRAIN_DIR

#: The build modes a project may default to (matches config/modes.yaml).
VALID_MODES = ("vibe", "mvp", "production")

#: Project-relative path to the human-editable settings file.
PROJECT_CONFIG_REL = Path(BRAIN_DIR) / "config" / "project.yaml"


def is_project(root: Path) -> bool:
    """Return True if ``root`` contains an ASPIS brain folder."""
    return (root / BRAIN_DIR).is_dir()


def config_path(root: Path) -> Path:
    """Return the path to the project's settings file."""
    return root / PROJECT_CONFIG_REL


def load_project_config(root: Path) -> dict:
    """Return the parsed project settings, or ``{}`` when none exist."""
    path = config_path(root)
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def default_mode(root: Path, *, fallback: str = "production") -> str:
    """Return the project's default build mode, falling back when unset."""
    mode = load_project_config(root).get("mode")
    return mode if mode in VALID_MODES else fallback


def set_mode(root: Path, mode: str) -> None:
    """Set the project's default build mode, preserving the file's other content.

    Replaces the ``mode:`` line in place (keeping comments) when present, else
    creates the file with a single ``mode:`` key.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"unknown mode {mode!r}; expected one of {VALID_MODES}")
    path = config_path(root)
    if path.is_file():
        lines = path.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if line.strip().startswith("mode:") and not line.lstrip().startswith("#"):
                lines[i] = f"mode: {mode}"
                break
        else:
            lines.insert(0, f"mode: {mode}")
        text = "\n".join(lines) + "\n"
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        text = f"mode: {mode}\n"
    path.write_text(text, encoding="utf-8", newline="\n")
