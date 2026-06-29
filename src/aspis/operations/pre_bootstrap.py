"""Pre-bootstrap resolution — the read-only truth-gathering before bootstrap (F-020).

Runs after ``init`` and before ``bootstrap``. It classifies the project **state**,
inventories the runtimes on this machine, computes the **stack with a confidence**,
locates the rule layers, and detects any **plan file** the user dropped — then records
all of it in ``.aspis/current/bootstrap_state.json`` (resumable). It makes **no**
side-effecting changes beyond that single state file: bootstrap consumes this decision
state, it does not re-derive it. Detection is reused from ``detect`` / ``runtime_inventory``
(never duplicated); subscription/model resolution is reserved for the models subsystem.
"""

from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path

from aspis import detect, manifest, paths, project, runtime_inventory
from aspis.constants import BRAIN_DIR

#: Resumable decision state, relative to a project root.
STATE_REL = Path(BRAIN_DIR) / "current" / "bootstrap_state.json"

#: The (default, overridable) machine-wide user-rules file — a human-editable markdown.
#: The structured (yaml/json) rules are the rules subsystem's later job.
USER_RULES_ENV = "ASPIS_USER_RULES"

#: A dropped plan file is recognised by a common name + a document extension, in the
#: project root or ``docs/`` (the locations users actually use).
_PLAN_NAME = re.compile(r"(plan|arch|architecture|spec|prd|roadmap|design)", re.IGNORECASE)
_PLAN_EXT = {".md", ".markdown", ".rst", ".txt", ".html", ".htm", ".pdf", ".docx", ".doc"}

#: The six project states the workflow needs to route on.
EMPTY = "empty"
EXISTING_CODE = "existing-code"
INITIALIZED = "initialized-not-onboarded"
INCOMPLETE = "incomplete-aspis"
LEGACY = "legacy-aspis"
BOOTSTRAPPED = "bootstrapped"


def state_path(root: Path) -> Path:
    """Where the decision state lives for *root*."""
    return root / STATE_REL


def load_state(root: Path) -> dict:
    """Return the recorded decision state, or ``{}`` when absent/unreadable."""
    path = state_path(root)
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(root: Path, data: dict) -> Path:
    """Write *data* as the decision state; return its path."""
    path = state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def project_state(root: Path) -> str:
    """Classify the project for routing (the six-state machine)."""
    if not root.is_dir():
        return EMPTY
    if project.is_project(root):
        if manifest.is_bootstrapped(root):
            return BOOTSTRAPPED
        brain = root / BRAIN_DIR
        if (brain / "context").is_dir() and (brain / "index").is_dir():
            return INITIALIZED
        return INCOMPLETE
    if (root / ".asps").is_dir():  # the old ASPS engine's brain dir
        return LEGACY
    return EXISTING_CODE if detect.project_mode(root) == "existing" else EMPTY


def stack_record(root: Path) -> dict:
    """The detected stack + confidence: one marker hit = high, several = medium, none = unknown."""
    found = detect.detect_stacks(root)
    confidence = "high" if len(found) == 1 else "medium" if found else "unknown"
    return {
        "value": detect.normalize_stack(" ".join(found)) or "unknown",
        "confidence": confidence,
        "source": "detected",
        "candidates": found,
    }


def _user_rules_path() -> str:
    """The configurable machine-wide user-rules markdown path (env override, else config home)."""
    return os.environ.get(USER_RULES_ENV) or str(paths.config_home() / "rules.md")


def rule_layers(root: Path) -> dict:
    """Which rule layers are present (system/project in the brain; user on the machine)."""
    rules = root / BRAIN_DIR / "rules"
    user_path = _user_rules_path()
    return {
        "system": (rules / "system-rules.md").is_file(),
        "project": (rules / "project-rules.md").is_file(),
        "user_path": user_path,
        "user_present": Path(user_path).is_file(),
    }


def plan_files(root: Path) -> list[str]:
    """Plan files the user dropped (common name + doc extension) in the root or ``docs/``."""
    out: list[str] = []
    for base in (root, root / "docs"):
        if not base.is_dir():
            continue
        for path in sorted(base.iterdir()):
            if path.is_file() and path.suffix.lower() in _PLAN_EXT and _PLAN_NAME.search(path.stem):
                out.append(path.relative_to(root).as_posix())
    return out


def runtimes() -> dict:
    """Runtime presence + declared capabilities on this machine (reuses runtime_inventory)."""
    detected = runtime_inventory.detect_runtimes()
    names = runtime_inventory.available(detected)
    return {
        "available": names,
        "detected": {name: bool(path) for name, path in sorted(detected.items())},
        "capabilities": {name: runtime_inventory.capabilities(name) for name in names},
        # Subscription / model availability is resolved by the models subsystem (F-021);
        # the seam is reserved here so its resolver can fill it without a schema change.
        "subscriptions": None,
    }


def resolve(root: Path, *, write: bool = True) -> dict:
    """Gather the decision state read-only; record it when the project has a brain.

    Preserves any existing ``onboarding`` block so an interrupted run resumes rather than
    restarts. Writes only the state file (never any other project file).
    """
    root = Path(root)
    previous = load_state(root)
    state = {
        "version": 1,
        "generated": datetime.now(UTC).isoformat(timespec="seconds"),
        "project_state": project_state(root),
        "stack": stack_record(root),
        "runtimes": runtimes(),
        "rules": rule_layers(root),
        "plan_files": plan_files(root),
        "onboarding": previous.get("onboarding") or {"status": "pending"},
    }
    if write and project.is_project(root):
        save_state(root, state)
    return state
