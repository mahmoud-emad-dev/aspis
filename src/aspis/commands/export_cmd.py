"""``aspis export`` — re-export a project's runtime assets from the catalog.

A **thin wrapper** over the same ``plan_export`` / ``write_export`` pipeline that
``aspis init`` uses. Reconciles with init: identical planner + writer, single
source of truth. The only init steps ``export`` deliberately does NOT do are
brain scaffolding, root-file seeding, git init, and the first commit — those
belong to a one-time ``init``, not to repeated re-exports.

- ``aspis export`` (or ``--dry-run``): plan the export, print it, write nothing.
- ``aspis export --apply``: execute the plan under hash protection (UPDATEs land,
  user-edited PROTECT/CONFLICT files are preserved, or refused with ``--strict``).
- ``aspis export --force``: bypass protection and overwrite every target.
- ``aspis export --runtime <name>``: scope to one runtime (default: the
  profile's runtimes that already have a directory in the project, so a Claude
  init is not re-clobbered when you ``--apply`` from an OpenCode shell).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from aspis import resources
from aspis.constants import BRAIN_DIR
from aspis.export import ProtectionError, plan_export, write_export
from aspis.profiles import Profile, load_merged
from aspis.runtimes import get_adapter


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``export`` verb on the given subparsers action."""
    parser = subparsers.add_parser(
        "export",
        help="Re-export the catalog's runtime assets into this project "
        "(dry-run by default; reconciles with `aspis init`).",
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="Project directory (default: current)."
    )
    parser.add_argument(
        "--profile", default="base", help="Profile to export (default: base)."
    )
    parser.add_argument("--runtime", help="Scope to a single runtime (default: profile's).")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Plan without writing (default).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute the export plan under hash protection (UPDATEs land, "
        "PROTECT/CONFLICT files are preserved; use --force or --force-conflicts to overwrite).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass hash protection — overwrite every target (legacy escape hatch).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Raise on CONFLICT or PROTECT (exit non-zero).",
    )
    parser.add_argument(
        "--force-conflicts",
        action="store_true",
        help="Overwrite files that are CONFLICT (both user and catalog changed).",
    )
    parser.set_defaults(func=_run)


def _resolve_profile(name: str, runtimes: list[str] | None) -> Profile:
    """Load *name* from the bundled profiles; narrow its runtimes if *runtimes* given."""
    profile = load_merged(name, resources.data_dir() / "profiles")
    if runtimes:
        profile = profile.model_copy(update={"runtimes": list(runtimes)})
    return profile


def _run(args: argparse.Namespace) -> int:
    """Plan the export; with ``--apply``/``--force`` execute it via the writer init uses."""
    root = Path(args.path).resolve()

    if not (root / BRAIN_DIR).is_dir():
        print("not an ASPIS project (no .aspis/) -- run `aspis init` first.")
        return 1

    if args.force_conflicts and args.strict:
        print("error: --force-conflicts and --strict are contradictory "
              "(one permits conflicts, one forbids them).")
        return 2

    apply = bool(args.apply or args.force)  # --force implies writing
    profile = _resolve_profile(args.profile, [args.runtime] if args.runtime else None)

    # Restrict to runtimes the project actually carries on disk, so re-exporting
    # from a different shell (e.g. OpenCode on a Claude project) does not stomp
    # a runtime's tree that was never installed here.
    present = [r for r in profile.runtimes if (root / get_adapter(r).runtime_dir).is_dir()]
    if present:
        profile = profile.model_copy(update={"runtimes": present})
    if not profile.runtimes:
        print(
            "no runtime directories present (no .opencode / .claude / ...) "
            "-- run `aspis init` first."
        )
        return 1

    plan = plan_export(resources.catalog_dir(), profile)

    try:
        performed = write_export(
            plan,
            root,
            force=bool(args.force),
            write=apply,
            apply=bool(args.apply),
            strict=bool(args.strict),
            force_conflicts=bool(args.force_conflicts),
        )
    except ProtectionError as exc:
        print(f"error: {exc}")
        return 1

    header = "WROTE" if apply else "DRY-RUN (pass --apply to execute)"
    runtimes = ", ".join(profile.runtimes) or "(none)"
    print(f"{header} — export {root}  [profile={profile.name}, runtimes={runtimes}]")
    for line in performed:
        print(f"  {line}")
    for missing in plan.missing:
        print(f"  missing reference (skipped): {missing}")
    for skipped in plan.skipped_by_scope:
        print(f"  out of scope (skipped): {skipped}")

    if not apply:
        print("\nNothing was written (dry-run). Re-run with --apply to execute:")
        print(f"  aspis export {args.path} --apply")
        return 0

    return 0
