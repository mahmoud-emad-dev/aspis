"""``aspis drift`` — catalog vs. live runtime frontmatter drift detection.

Walks every agent in the catalog and, for every exported runtime, compares
the catalog frontmatter field-by-field against the live agent file the
runtime adapter produced. Surfaces per-agent, per-field differences with
``agent:field`` evidence so a maintainer can see exactly which field on
which agent has gone stale. Exits non-zero when any drift is detected, so
the "catalog is the source of truth" claim is machine-enforced, not just
asserted in prose. Stdlib-only at the algorithmic level — only the
project's own ``aspis.catalog.split_frontmatter`` and
``aspis.resources.catalog_dir`` are imported, both already proven on the
catalog files.

The ``model`` field is reported as a raw string mismatch even though the
catalog stores a tier (``standard``) and the runtimes store a vendor id
(``opencode-go/deepseek-v4-pro``). The two forms are intentionally
different — the catalog is the tier, the runtime is the resolved vendor
— so the line is informational, not a bug. Treat it as a sanity check
that the field is rendered at all.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from aspis.catalog import split_frontmatter
from aspis.resources import catalog_dir

#: Frontmatter fields the catalog is the source of truth for. Order is
#: preserved in drift reports so the diff reads top-to-bottom like the
#: agent file itself. ``runtimes`` is checked at the file-presence level,
#: not against a frontmatter field, but it stays in the tuple so a reader
#: of this module sees the full set of compared fields in one place.
_COMPARE_FIELDS: tuple[str, ...] = (
    "name",
    "description",
    "mode",
    "model",
    "temperature",
    "tools",
    "skills",
    "delegates",
    "runtimes",
)

#: Status labels — ASCII-safe for any console.
_LABEL_OK = "OK"
_LABEL_DRIFT = "DRIFT"
_LABEL_MISSING = "MISSING"
_LABEL_STALE = "STALE"


# --- Runtime projection -----------------------------------------------------

def _project_opencode(frontmatter: dict) -> dict[str, Any]:
    """Project opencode's frontmatter into the catalog-schema field set.

    opencode's permission block encodes tools/skills/delegates/bash as
    nested keys with ``"allow"`` / ``"deny"`` string values, not as flat
    lists. This function reverses the encoding so the comparison is
    field-shaped, not syntax-shaped: a missing tool reads as a missing
    element of the ``tools`` list, not as a different YAML structure.
    """
    out: dict[str, Any] = {}
    if "description" in frontmatter:
        out["description"] = frontmatter["description"]
    if "mode" in frontmatter:
        out["mode"] = frontmatter["mode"]
    if "model" in frontmatter:
        out["model"] = frontmatter["model"]
    if "temperature" in frontmatter:
        out["temperature"] = frontmatter["temperature"]

    perm = frontmatter.get("permission") or {}
    tools: list[str] = []
    delegates: list[str] = []
    skills: list[str] = []
    for top_name, top_policy in perm.items():
        if not isinstance(top_policy, dict):
            # Scalar allow/deny (e.g. ``webfetch: deny``, ``read: allow``).
            # ``webfetch`` and ``websearch`` are not tools in the catalog
            # sense — they're network-policy toggles, not capability
            # tokens — so they are excluded from the tools projection.
            if top_policy == "allow" and top_name not in ("webfetch", "websearch"):
                tools.append(top_name)
            continue
        if top_name == "task":
            for sub, pol in top_policy.items():
                if pol == "allow" and sub != "*":
                    delegates.append(sub)
        elif top_name == "skill":
            for sub, pol in top_policy.items():
                if pol == "allow" and sub != "*":
                    skills.append(sub)
        elif top_name == "bash":
            # ``bash`` is a dict of command patterns; its presence means
            # the tool is in use regardless of pattern policy.
            tools.append("bash")
    out["tools"] = sorted(tools)
    out["delegates"] = sorted(delegates)
    out["skills"] = sorted(skills)
    return out


def _project_claude(frontmatter: dict) -> dict[str, Any]:
    """Project claude's frontmatter into the catalog-schema field set.

    Claude drops ``mode``/``temperature``/``delegates``/``skills`` (it
    has no syntax for them), so those are simply absent from the
    projection — comparing them would always report a phantom drift
    that's by design. ``tools`` is lower-cased so the catalog's
    canonical ``read`` token can be compared against Claude's
    vendor-specific ``Read``.
    """
    out: dict[str, Any] = {}
    if "name" in frontmatter:
        out["name"] = frontmatter["name"]
    if "description" in frontmatter:
        out["description"] = frontmatter["description"]
    if "model" in frontmatter:
        out["model"] = frontmatter["model"]
    raw_tools = frontmatter.get("tools")
    if isinstance(raw_tools, list):
        out["tools"] = sorted(str(t).lower() for t in raw_tools)
    return out


# --- Comparison helpers -----------------------------------------------------

def _values_differ(catalog_value: Any, runtime_value: Any) -> bool:
    """Return True iff the catalog value and the runtime projection differ.

    Lists are compared as sorted sequences so order is irrelevant — the
    catalog and the runtime are free to sort their own lists. Scalars
    are compared with ``!=`` so ``0.1`` matches ``0.1`` and
    ``"primary"`` matches ``"primary"``.
    """
    if isinstance(catalog_value, list):
        if not isinstance(runtime_value, list):
            return True
        return sorted(catalog_value) != sorted(runtime_value)
    if isinstance(runtime_value, list):
        # Catalog scalar, runtime list — not equal in any sane ordering.
        return sorted(runtime_value) != [catalog_value]
    return catalog_value != runtime_value


def _format_value(value: Any) -> str:
    """Render a comparison value compactly for the report line."""
    if isinstance(value, list):
        return "[" + ", ".join(str(v) for v in sorted(value)) + "]"
    return repr(value)


# --- Per-agent, per-runtime check -------------------------------------------

def _check_agent(
    agent_name: str,
    catalog_frontmatter: dict,
    live_path: Path,
    runtime: str,
) -> list[str]:
    """Return the list of drift messages for one agent in one runtime.

    ``[]`` means the agent's live frontmatter matches the catalog
    projection for every compared field. The message format is
    ``"<agent>:<field> catalog=... runtime=..."`` so the user can grep
    the report and jump straight to the wrong field.
    """
    try:
        text = live_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{agent_name}@{runtime} unreadable: {exc}"]

    live_frontmatter, _ = split_frontmatter(text)
    if not live_frontmatter:
        return [f"{agent_name}@{runtime} has no parseable frontmatter"]

    # Dispatch by runtime via a table, not an ``if runtime ==`` chain
    # (constitution #4/#9). F-020 can move each projection onto its adapter.
    projector = {"opencode": _project_opencode, "claude": _project_claude}.get(runtime)
    if projector is None:
        return [f"{agent_name}@{runtime} unknown runtime"]
    projection = projector(live_frontmatter)

    drifts: list[str] = []
    for field in _COMPARE_FIELDS:
        if field == "runtimes":
            # Run-time-list field — checked at the file-presence level
            # in the caller, not against a frontmatter field.
            continue
        catalog_value = catalog_frontmatter.get(field)
        runtime_value = projection.get(field)
        if runtime_value is None:
            # Runtime doesn't render this field (by design). Not drift.
            continue
        if _values_differ(catalog_value, runtime_value):
            drifts.append(
                f"{agent_name}:{field} "
                f"catalog={_format_value(catalog_value)} "
                f"runtime={_format_value(runtime_value)}"
            )
    return drifts


# --- CLI verb ---------------------------------------------------------------

def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``drift`` verb."""
    parser = subparsers.add_parser(
        "drift",
        help=(
            "Compare catalog agent frontmatter against the live runtime "
            "export (per-field, per-agent)."
        ),
    )
    parser.add_argument(
        "--runtime",
        default="all",
        choices=("opencode", "claude", "all"),
        help=(
            "Scope to one runtime or scan both. Default: all. The catalog "
            "is the source of truth; the live runtime is the thing that "
            "may have drifted."
        ),
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """Walk every catalog agent and report per-field drift.

    Returns 0 when every agent matches its live counterpart in every
    selected runtime; 1 if any drift is detected. The summary line
    always prints so callers can parse it.
    """
    project_root = Path.cwd()
    catalog_root = catalog_dir()
    agents_dir = catalog_root / "agents"
    if not agents_dir.is_dir():
        print(f"agents directory not found: {agents_dir}")
        return 1

    runtime_dirs: dict[str, Path] = {
        "opencode": project_root / ".opencode" / "agents",
        "claude": project_root / ".claude" / "agents",
    }
    runtime_keys: tuple[str, ...] = (
        ("opencode", "claude") if args.runtime == "all" else (args.runtime,)
    )

    # Discover runtimes whose agents dir simply doesn't exist on disk.
    # When EVERY selected runtime is absent there is nothing to compare
    # against — the project has never been exported. Report that clearly
    # and exit cleanly so the caller knows this is a pre-condition, not a
    # failure.
    live_runtime_keys: list[str] = []
    missing_rt: list[str] = []
    for runtime in runtime_keys:
        if runtime_dirs[runtime].is_dir():
            live_runtime_keys.append(runtime)
        else:
            missing_rt.append(runtime)

    if not live_runtime_keys:
        joined = ", ".join(missing_rt)
        print(f"no live runtime ({joined}) — run aspis export first")
        return 0

    agent_files = sorted(agents_dir.glob("*.md"))
    total = len(agent_files)
    drifted_pairs = 0
    drifted_agents: set[str] = set()
    total_drift_messages = 0

    for path in agent_files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(
                f"Agent: {path.stem} — {_LABEL_DRIFT} "
                f"(catalog unreadable: {exc})"
            )
            drifted_pairs += 1
            drifted_agents.add(path.stem)
            total_drift_messages += 1
            continue

        catalog_frontmatter, _ = split_frontmatter(text)
        agent_name = catalog_frontmatter.get("name") or path.stem
        raw_runtimes = catalog_frontmatter.get("runtimes")
        declared_runtimes = (
            raw_runtimes if isinstance(raw_runtimes, (list, tuple)) else ()
        )

        for runtime in live_runtime_keys:
            live_path = runtime_dirs[runtime] / f"{agent_name}.md"
            # ``declared_runtimes`` is empty (= "all") or contains this
            # runtime name → the catalog claims this runtime for the
            # agent. Otherwise it doesn't.
            expected = not declared_runtimes or runtime in declared_runtimes
            exists = live_path.is_file()

            if expected and not exists:
                # Catalog claims this runtime (or claims all) but the
                # live file is missing — that's drift in the
                # "export was skipped" direction.
                print(
                    f"Agent: {agent_name} @ {runtime} — {_LABEL_MISSING} "
                    f"(expected {live_path})"
                )
                drifted_pairs += 1
                drifted_agents.add(agent_name)
                total_drift_messages += 1
                continue

            if not expected and exists:
                # Live file exists but the catalog doesn't claim this
                # runtime — stale export, drift in the other direction.
                print(
                    f"Agent: {agent_name} @ {runtime} — {_LABEL_STALE} "
                    f"(live file exists but not declared in catalog "
                    f"runtimes={list(declared_runtimes)})"
                )
                drifted_pairs += 1
                drifted_agents.add(agent_name)
                total_drift_messages += 1
                continue

            if not exists:
                # Not expected, not present — fine.
                continue

            # Expected and exists — compare fields.
            drifts = _check_agent(agent_name, catalog_frontmatter, live_path, runtime)
            if drifts:
                joined = "; ".join(drifts)
                print(
                    f"Agent: {agent_name} @ {runtime} — {_LABEL_DRIFT} "
                    f"({joined})"
                )
                drifted_pairs += 1
                drifted_agents.add(agent_name)
                total_drift_messages += len(drifts)
            else:
                print(f"Agent: {agent_name} @ {runtime} — {_LABEL_OK}")

    in_sync = total - len(drifted_agents)
    print(
        f"\n{in_sync}/{total} agents in sync. "
        f"{total_drift_messages} drift messages across "
        f"{len(drifted_agents)} agent(s) and {drifted_pairs} runtime pair(s)."
    )
    return 0 if drifted_pairs == 0 else 1


if __name__ == "__main__":
    # Allow ``python -m aspis.commands.drift`` for ad-hoc runs in
    # addition to the normal ``aspis drift`` dispatch path. Build a
    # real parser here so ``--help`` triggers argparse's standard help
    # exit (code 0), not the verb's own exit code.
    parser = argparse.ArgumentParser(
        prog="aspis drift",
        description=(
            "Compare catalog agent frontmatter against the live runtime "
            "export (per-field, per-agent)."
        ),
    )
    parser.add_argument(
        "--runtime",
        default="all",
        choices=("opencode", "claude", "all"),
        help=(
            "Scope to one runtime or scan both. Default: all. The catalog "
            "is the source of truth; the live runtime is the thing that "
            "may have drifted."
        ),
    )
    raise SystemExit(_run(parser.parse_args()))
