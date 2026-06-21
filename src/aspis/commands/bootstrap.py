"""``aspis bootstrap`` — make an initialized project live (onboarding)."""

from __future__ import annotations

import argparse
from pathlib import Path

from aspis import manifest
from aspis.engine import build_engine
from aspis.operations import register_all


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``bootstrap`` verb on the given subparsers action."""
    parser = subparsers.add_parser(
        "bootstrap", help="Make an initialized project live (onboarding wizard)."
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="Project directory (default: current)."
    )
    parser.add_argument("--name", default=None, help="Project name.")
    parser.add_argument("--goal", default=None, help="One-line project goal/definition.")
    parser.add_argument("--stack", default=None, help="Main stack (default: detected).")
    parser.add_argument("--plan", default=None, help="Path to a plan file (optional).")
    parser.add_argument(
        "-y", "--yes", action="store_true", help="Skip prompts; use detected defaults."
    )
    parser.add_argument("--write", action="store_true", help="Apply changes (default: dry-run).")
    parser.add_argument(
        "--check", action="store_true", help="Only report whether the project is bootstrapped."
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    """Run bootstrap, or with --check just report the bootstrapped state."""
    root = Path(args.path).resolve()

    if args.check:
        done = manifest.is_bootstrapped(root)
        print(f"{'bootstrapped' if done else 'NOT bootstrapped'}: {root}")
        if not done:
            print("Run `aspis bootstrap --write` to bootstrap.")
        return 0 if done else 1

    engine = build_engine()
    register_all(engine)
    try:
        ctx = engine.run(
            "bootstrap",
            root,
            name=args.name,
            goal=args.goal,
            stack=args.stack,
            plan=args.plan,
            yes=bool(args.yes),
            write=bool(args.write),
        )
    except RuntimeError as exc:
        print(f"error: {exc}")
        return 1

    header = "BOOTSTRAPPED" if args.write else "DRY-RUN (pass --write to apply)"
    print(f"{header} — bootstrap {ctx.root}")
    for message in ctx.messages:
        print(f"  {message}")
    if not args.write:
        print("\nNothing was written (dry-run). Re-run with --write to apply:")
        print("  aspis bootstrap --write")
        return 0

    print("\nProject is live. Next:")
    print("  1. aspis models --sync   # review/assign the model each agent uses")
    print("  2. open AGENTS.md        # the project goal + how the agents operate")
    print("  3. start your runtime    # ask the project-lead to plan your first feature")
    print("  4. aspis status          # check project state anytime")
    return 0
