"""``aspis byte-parity`` — read-only catalog self-consistency check.

For every agent the bundled base profile would render, this command renders
the catalog source in-memory and reports CLEAN / CONFLICT / PROTECT per the
protection engine's contract:

- **CLEAN** — renders without error, every required frontmatter field is
  present, every ``skills:`` and ``delegates:`` entry resolves to a real
  catalog asset, and the rendered text hashes deterministically.
- **CONFLICT** — render failed, a required field is missing, or a reference
  does not resolve.
- **PROTECT** — would fire only when a live file already exists and would be
  skipped by a future export. The catalog-only check (no live files
  consulted) never produces it; the status name is reported for engine
  contract completeness.

Thin wrapper over the existing rendering and protection engine — no
re-implementation of either. The regen hash uses
:func:`aspis.transform.render_agent` + :func:`aspis.protect.sha256_text`, the
same public functions ``aspis.export._regen_hash`` calls. Live catalog ↔
runtime parity is verified after the owner runs ``aspis export``; this
verb never writes the live file, the export snapshot, or the audit log.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING

from aspis.catalog import split_frontmatter
from aspis.export import ExportAction, plan_export
from aspis.inventory import load_inventory
from aspis.profiles import load_profile
from aspis.project import is_project, load_effective_config
from aspis.protect import DecisionKind, decide, sha256_text
from aspis.resources import catalog_dir, data_dir
from aspis.runtimes import get_adapter
from aspis.transform import render_agent

if TYPE_CHECKING:
    from aspis.runtimes.base import RuntimeInventory


#: Frontmatter keys every catalog agent must declare. ``name`` and ``model``
#: drive rendering; ``description`` and ``mode`` are surfaced to humans.
_REQUIRED_FIELDS: tuple[str, ...] = (
    "name",
    "description",
    "mode",
    "model",
)


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``byte-parity`` verb on the given subparsers action."""
    parser = subparsers.add_parser(
        "byte-parity",
        help=(
            "Read-only catalog self-consistency check (renders every agent "
            "in-memory; reports CLEAN/CONFLICT/PROTECT)."
        ),
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help=(
            "Project directory (default: current). Used to resolve the "
            "project's local config + inventory; the catalog itself is "
            "always the bundled one."
        ),
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    catalog = catalog_dir()

    # 1. Build the profile from the bundled base, mirroring models.py: keep
    #    only runtimes the project already has a directory for, so we never
    #    render into a runtime the project never asked for.
    profile = load_profile(data_dir() / "profiles" / "base.yaml")
    present = [r for r in profile.runtimes if (root / get_adapter(r).runtime_dir).is_dir()]
    if present:
        profile = profile.model_copy(update={"runtimes": present})

    # 2. Resolve project config + detected inventory the same way the export
    #    engine does. Both are safe to omit when the directory is not an ASPIS
    #    project: ``load_effective_config`` is skipped, ``load_inventory``
    #    returns ``None``, and the renderer falls back to the tier map.
    if is_project(root):
        project_config = load_effective_config(root)
        inventory = load_inventory(root)
    else:
        project_config = {}
        inventory = None

    # 3. Plan, then keep only render-agent actions — copy actions have no
    #    "render" semantics and are outside the parity contract.
    plan = plan_export(catalog, profile)
    render_actions = [a for a in plan.actions if a.op == "render-agent"]

    if not render_actions:
        print("no renderable agents in the profile — nothing to check.")
        return 0

    # 4. Pre-index the catalog so we can validate refs cheaply per agent.
    skill_dirs = _index_skill_dirs(catalog)
    agent_stems = _index_agent_stems(catalog)

    print("Byte-parity check — catalog self-consistency")
    print()

    clean = 0
    issues = 0
    for action in render_actions:
        status, reason = _check_agent(
            action, project_config, inventory, skill_dirs, agent_stems,
        )
        agent_name = action.source.stem
        suffix = f"  ({reason})" if reason else ""
        print(f"Agent: {agent_name} — {status}{suffix}")
        if status == "CLEAN":
            clean += 1
        else:
            issues += 1

    total = len(render_actions)
    print()
    print(f"{clean}/{total} agents CLEAN. {issues} issues.")
    return 0 if issues == 0 else 1


def _index_skill_dirs(catalog: Path) -> set[str]:
    """Catalog skill names = subdirectory names of ``catalog/skills/``."""
    skills_root = catalog / "skills"
    if not skills_root.is_dir():
        return set()
    return {p.name for p in skills_root.iterdir() if p.is_dir()}


def _index_agent_stems(catalog: Path) -> set[str]:
    """Catalog agent names = the file stems of ``catalog/agents/*.md``."""
    agents_root = catalog / "agents"
    if not agents_root.is_dir():
        return set()
    return {p.stem for p in agents_root.glob("*.md")}


def _check_agent(
    action: ExportAction,
    project_config: dict,
    inventory: "dict[str, RuntimeInventory] | None",
    skill_dirs: set[str],
    agent_stems: set[str],
) -> tuple[str, str]:
    """Classify a single render-agent action; return ``(status, reason)``.

    ``reason`` is empty on CLEAN, otherwise a short human-readable
    explanation of the failure. The renderer is the same one ``export``
    uses, so a CLEAN here means a future ``aspis export`` will produce
    the same content byte-for-byte for this agent.
    """
    source = action.source
    try:
        text = source.read_text(encoding="utf-8")
    except OSError as exc:
        return "CONFLICT", f"unreadable: {exc}"

    # --- frontmatter shape -------------------------------------------------
    frontmatter, _ = split_frontmatter(text)
    missing = [f for f in _REQUIRED_FIELDS if f not in frontmatter]
    if missing:
        return "CONFLICT", f"missing frontmatter: {', '.join(missing)}"

    # --- reference resolution ---------------------------------------------
    for skill in frontmatter.get("skills") or ():
        if skill not in skill_dirs:
            return "CONFLICT", f"broken skill ref: {skill!r}"
    for delegate in frontmatter.get("delegates") or ():
        if delegate not in agent_stems:
            return "CONFLICT", f"broken delegate ref: {delegate!r}"

    # --- render in-memory + hash via the same public pipeline ---------------
    # load_inventory returns a {runtime: RuntimeInventory} map; render wants
    # this runtime's single entry (None when detection has not run here).
    # Mirrors the index dance in export._regen_hash / _apply.
    inv = inventory.get(action.runtime) if isinstance(inventory, dict) else inventory
    try:
        rendered = render_agent(
            text,
            action.runtime,
            project_config=project_config,
            inventory=inv,
        )
        regen_hash = sha256_text(rendered)
    except Exception as exc:  # noqa: BLE001 — renderer raises anything on a bad catalog
        return "CONFLICT", f"render failed: {exc.__class__.__name__}: {exc}"

    # --- classify against the protection engine contract -------------------
    # Catalog self-consistency: there is no live file and no snapshot entry
    # (byte-parity is read-only — it never queries them), so the decision is
    # ADD → which we collapse to CLEAN. PROTECT only ever appears when a
    # live file is present and would be skipped by a future export; we
    # keep the branch in the schema for forward compatibility, but the
    # catalog-only check never produces it.
    decision = decide(live_hash=None, snapshot_hash=None, regen_hash=regen_hash)
    if decision.kind is DecisionKind.ADD:
        return "CLEAN", ""
    return "CONFLICT", f"unexpected decision: {decision.kind.value}"
