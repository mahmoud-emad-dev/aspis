"""The ``init`` operation — scaffold a project and export its runtime assets.

Registered on the lifecycle engine, so it runs as
``pre-init hooks → init_core → post-init hooks``. The core itself is pure
orchestration over the export engine, the brain scaffold, and the root-file
templates — no runtime-specific logic lives here.
"""

from __future__ import annotations

import subprocess
import sys

from aspis import detect, resources
from aspis.constants import BRAIN_DIR
from aspis.export import plan_export, write_export
from aspis.lifecycle import Context, Engine
from aspis.profiles import Profile, load_profile, merge
from aspis.runtimes import get_adapter
from aspis.templating import render


def _load_profile(name: str) -> Profile:
    """Load *name* merged under the shared base profile."""
    profiles_dir = resources.data_dir() / "profiles"
    base = load_profile(profiles_dir / "base.yaml")
    if name == "base":
        return base
    return merge(base, load_profile(profiles_dir / f"{name}.yaml"))


def init_core(ctx: Context) -> None:
    """Export catalog assets, scaffold the brain, and write the root files."""
    write = bool(ctx.options.get("write"))
    force = bool(ctx.options.get("force"))

    profile = _load_profile(ctx.options.get("profile") or "base")
    if ctx.options.get("runtimes"):
        profile = profile.model_copy(update={"runtimes": list(ctx.options["runtimes"])})
    project_name = ctx.options.get("name") or ctx.root.name

    # New/empty vs existing-code projects follow different workflows; record which.
    ctx.log(f"mode: {detect.project_mode(ctx.root)}")

    # 1) Export catalog assets selected by the profile.
    plan = plan_export(resources.catalog_dir(), profile)
    for line in write_export(plan, ctx.root, force=force, write=write):
        ctx.log(line)
    for missing in plan.missing:
        ctx.log(f"missing reference (skipped): {missing}")

    # 2) Scaffold the brain, 3) ship helper scripts, 4) root files, 5) init git,
    # 6) arm the git hooks.
    _scaffold_brain(ctx, write=write)
    _ship_scripts(ctx, write=write)
    _seed_authored_files(ctx, project_name, write=write, force=force)
    _write_root_files(ctx, project_name, profile, write=write, force=force)
    if not ctx.options.get("no_git"):
        _git_init(ctx, write=write)
        _install_git_hooks(ctx, write=write)
        _commit_scaffold(ctx, write=write)


def _commit_scaffold(ctx: Context, *, write: bool) -> None:
    """Commit the freshly scaffolded brain as init's own first commit.

    init owns its commit (not bootstrap): a just-initialized project lands with a clean
    first commit of *only* the ASPIS files, so bootstrap later makes a single, separate
    commit of its fill. On an existing repo the user's own code is never swept in.
    """
    from aspis import gitops

    if not write or not gitops.has_git(ctx.root):
        return
    if gitops.commit_owned(ctx.root, "chore: initialize ASPIS project"):
        ctx.log("commit init scaffolding")


def _ship_scripts(ctx: Context, *, write: bool) -> None:
    """Copy the self-contained helper scripts (context, planning, hooks, …) into the project.

    Every group folder under ``catalog/scripts/`` ships to ``.aspis/scripts/<group>/``,
    recursively, so a new script category — and any data files it carries (e.g. the
    gitignore offline cache) — is added by dropping a folder, no code change here.
    """
    root = resources.catalog_dir() / "scripts"
    groups = (p for p in sorted(root.iterdir()) if p.is_dir() and not p.name.startswith("_"))
    for group in groups:
        dest = ctx.root / BRAIN_DIR / "scripts" / group.name
        for source in sorted(group.rglob("*")):
            if not source.is_file() or "__pycache__" in source.parts or source.suffix == ".pyc":
                continue
            target = dest / source.relative_to(group)
            ctx.log(f"ship {target.relative_to(ctx.root).as_posix()}")
            if write:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def _scaffold_brain(ctx: Context, *, write: bool) -> None:
    """Create the empty brain directories, each kept by a ``.gitkeep``.

    A ``.gitkeep`` is only planted while the directory is genuinely empty — on a
    re-init over a populated brain, a directory that already holds content is left
    untouched (its content already makes git track it; a ``.gitkeep`` there would
    just be stale junk the cleanup hook has to reap).
    """
    for brain_dir in resources.brain_dirs():
        directory = ctx.root / brain_dir
        keep = directory / ".gitkeep"
        if keep.exists():
            continue
        if directory.is_dir() and any(directory.iterdir()):
            continue
        ctx.log(f"scaffold {brain_dir}/.gitkeep")
        if write:
            directory.mkdir(parents=True, exist_ok=True)
            keep.write_text("", encoding="utf-8", newline="\n")


def _seed_authored_files(ctx: Context, project_name: str, *, write: bool, force: bool) -> None:
    """Seed hand-grown brain files that agents maintain, never clobbering an existing one.

    Unlike CURRENT_STATE/CODE_MAP (generated, untracked), these are authored over time:
    the as-built architecture and the file-purpose config the registry reads. Init only
    plants a skeleton.
    """
    seeds = {
        ".aspis/context/ARCHITECTURE.md": render(
            resources.template("context/ARCHITECTURE.md"), project_name=project_name
        ),
        ".aspis/config/purposes.json": resources.scaffold("purposes.json"),
        ".aspis/.gitignore": resources.scaffold("brain.gitignore"),
    }
    for rel, content in seeds.items():
        destination = ctx.root / rel
        if destination.exists() and not force:
            ctx.log(f"skip (exists): {rel}")
            continue
        ctx.log(f"write {rel}")
        if write:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8", newline="\n")


def _write_root_files(
    ctx: Context, project_name: str, profile: Profile, *, write: bool, force: bool
) -> None:
    """Write AGENTS.md, .gitignore, and each target runtime's own root guide.

    AGENTS.md is the universal guide every project gets; a runtime that declares a
    ``root_guide`` (e.g. Claude's CLAUDE.md) adds its own — asked of the adapter, so
    no runtime is named here.
    """
    files = {
        "AGENTS.md": render(resources.scaffold("AGENTS.md"), project_name=project_name),
        ".gitignore": resources.scaffold("gitignore"),
    }
    for runtime in profile.runtimes:
        guide = get_adapter(runtime).root_guide
        if guide:
            files[guide] = render(resources.scaffold(guide), project_name=project_name)

    for name, content in files.items():
        destination = ctx.root / name
        if destination.exists() and not force:
            ctx.log(f"skip (exists): {name}")
            continue
        ctx.log(f"write {name}")
        if write:
            destination.write_text(content, encoding="utf-8", newline="\n")


def _git_init(ctx: Context, *, write: bool) -> None:
    """Initialize a git repo when the target has none."""
    if (ctx.root / ".git").exists():
        return
    ctx.log("git init")
    if write:
        subprocess.run(["git", "init", "-q"], cwd=str(ctx.root), capture_output=True, check=False)


def _install_git_hooks(ctx: Context, *, write: bool) -> None:
    """Arm the git hooks by running the shipped installer (writes .git/hooks wrappers)."""
    installer = ctx.root / BRAIN_DIR / "scripts" / "hooks" / "install.py"
    if not (ctx.root / ".git").exists():
        return
    ctx.log("install git hooks (.git/hooks)")
    if write and installer.is_file():
        subprocess.run(
            [sys.executable, str(installer), str(ctx.root)],
            cwd=str(ctx.root),
            capture_output=True,
            check=False,
        )


def register(engine: Engine) -> None:
    """Register the init operation on *engine*."""
    engine.register("init", init_core)
