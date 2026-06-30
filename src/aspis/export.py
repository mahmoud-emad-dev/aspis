"""Export — plan and write a project's runtime assets from a profile.

Given a resolved profile and the bundled catalog, the planner computes what to
copy or render per runtime (dry-run, no writes); the writer performs it. Agents
and commands are rendered through the runtime adapters; skills/templates/hooks/
scripts are copied. Runtime-independent assets (templates/hooks/scripts) land
once under ``.aspis/``; runtime assets land under each ``.<runtime>/``.

Purpose:
    Translate a profile into concrete copy/render actions and execute them
    safely. When ``force=False`` (the default), writes are hash-protected
    through ``aspis.protect``: each target is classified as ADD, UNCHANGED,
    UNKNOWN, UPDATE, PROTECT or CONFLICT by comparing the live file hash, the
    recorded snapshot hash, and the hash of what the catalog would produce.
    The resulting decision determines whether the writer overwrites, preserves,
    or refuses the target. ``--force`` preserves the legacy skip-if-exists
    behavior and overwrites unconditionally.

Responsibilities:
    - Plan exports from a catalog and profile (``plan_export``).
    - Classify and perform write actions (``write_export``).
    - Maintain the per-target export snapshot at ``.aspis/current/export-snapshot.json``.
    - Append an audit log entry for every decided action to
      ``.aspis/current/export-log.jsonl``.
    - Acquire a per-target lockfile during writes to prevent concurrent exports.

Does Not:
    - Implement the pure decision truth table (that lives in ``aspis.protect``).
    - Modify the rendering or copy mechanics (``_apply`` is unchanged).
    - Route runtime hooks through the decision engine (deferred follow-up).

Used By:
    CLI export command and any automation that applies a profile to a project.
"""

from __future__ import annotations

import ctypes
import datetime
import errno
import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from aspis import assetkinds, manifest, project, transform
from aspis.catalog import split_frontmatter
from aspis.inventory import load_inventory
from aspis.profiles import Profile
from aspis.protect import DecisionKind, decide, sha256_text
from aspis.runtimes import get_adapter

#: The frontmatter ``model:`` line (top-level key, first occurrence). Used to carry a live
#: file's already-baked model across a re-export so export never re-routes a live model.
_MODEL_LINE = re.compile(r"^model:.*$", re.MULTILINE)


def _preserve_model_line(rendered: str, live_path: Path) -> str:
    """Return *rendered* with its ``model:`` line replaced by the live file's, if any.

    A re-export resolves the model from the *current* config, which may differ from what
    is baked into the live agent file. When models are frozen, we keep the live model:
    read the live file's ``model:`` line and substitute it into the freshly rendered text,
    so structure syncs while the routed model is untouched. A no-op when either side lacks
    a ``model:`` line (e.g. a brand-new agent being added has no live file yet).
    """
    if not live_path.is_file():
        return rendered
    live = _MODEL_LINE.search(live_path.read_text(encoding="utf-8"))
    if live is None or _MODEL_LINE.search(rendered) is None:
        return rendered
    return _MODEL_LINE.sub(lambda _m: live.group(0), rendered, count=1)


def _is_bootstrap_package(action: ExportAction) -> bool:
    """True when *action* deploys a transient bootstrap-onboarding asset.

    The bootstrap agent, the ``project-onboarding`` skill, and the shared
    ``workflows/bootstrap.md`` — the package that self-erases at go-live. Once a project is
    bootstrapped these must never be re-exported, so a live project keeps zero residue.
    """
    name = action.source.name
    return (
        (action.kind == "agents" and name == "bootstrap.md")
        or (action.kind == "skills" and name == "project-onboarding")
        or (action.kind == "workflows" and name == "bootstrap.md")
    )


class ProtectionError(RuntimeError):
    """Raised when ``--strict`` is set and a CONFLICT or PROTECT (LIVE-CUSTOMIZED)
    decision is encountered during an ``--apply`` run (FR-010)."""


@dataclass(frozen=True)
class ExportAction:
    """One planned copy/render step."""

    kind: str
    runtime: str
    source: Path
    target: str
    op: str  # render-agent | render-command | copy


@dataclass
class ExportPlan:
    """The full set of actions plus anything that could not be exported."""

    actions: list[ExportAction] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    skipped_by_scope: list[str] = field(default_factory=list)
    catalog_root: Path | None = None  # carried so the writer can emit runtime hooks


def _asset_meta(source: Path, kind: str) -> tuple[str, set[str]]:
    """Return ``(export_scope, runtime_lock)`` from an agent/command's frontmatter.

    ``runtime_lock`` is the set of runtimes the asset is restricted to; an empty
    set means "all runtimes". Non-renderable kinds carry no scope metadata.
    """
    if kind not in ("agents", "commands") or not source.is_file():
        return "all", set()
    frontmatter, _ = split_frontmatter(source.read_text(encoding="utf-8"))
    scope = frontmatter.get("export_scope", "all")
    return scope, set(frontmatter.get("runtimes", []))


def plan_export(catalog_root: Path, profile: Profile) -> ExportPlan:
    """Compute the export actions for *profile* against *catalog_root* (no writes)."""
    plan = ExportPlan(catalog_root=catalog_root)
    for kind, rel in profile.assets():
        source = catalog_root / rel
        if not source.exists():
            plan.missing.append(rel)
            continue
        scope, runtime_lock = _asset_meta(source, kind)
        if scope == "project-only":
            plan.skipped_by_scope.append(rel)
            continue

        per_runtime = assetkinds.is_per_runtime(kind)
        runtimes = profile.runtimes if per_runtime else ("",)
        for runtime in runtimes:
            # Honour runtime-lock: a locked asset skips runtimes outside its set.
            if runtime_lock and runtime not in runtime_lock:
                plan.skipped_by_scope.append(f"{rel} ({runtime})")
                continue
            # Honour the runtime capability model: drop a kind a runtime can't accept.
            if per_runtime and not get_adapter(runtime).supports(kind):
                plan.skipped_by_scope.append(f"{rel} ({runtime}: unsupported)")
                continue
            target = assetkinds.target(kind, runtime, rel)
            plan.actions.append(ExportAction(kind, runtime, source, target, assetkinds.op(kind)))
    return plan


def _load_snapshot(target_root: Path, *, reset: bool = False) -> dict:
    """Load the export snapshot for *target_root*.

    Returns ``{"version": 1, "paths": {}}`` when the snapshot file is absent.
    If the file exists but is not valid JSON, raises ``ProtectionError`` unless
    *reset* is ``True``, in which case the corrupted snapshot is discarded and
    an empty snapshot is returned.
    """
    path = target_root / ".aspis" / "current" / "export-snapshot.json"
    if not path.exists():
        return {"version": 1, "paths": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        if reset:
            return {"version": 1, "paths": {}}
        raise ProtectionError(
            f"{path} is corrupted ({exc}); use --reset-snapshot to discard it"
        ) from exc
    if not isinstance(data, dict):
        if reset:
            return {"version": 1, "paths": {}}
        raise ProtectionError(f"{path} is corrupted; use --reset-snapshot to discard it")
    data.setdefault("paths", {})
    return data


def _save_snapshot(target_root: Path, snapshot: dict) -> None:
    """Atomically write *snapshot* to ``.aspis/current/export-snapshot.json``."""
    dest = target_root / ".aspis" / "current" / "export-snapshot.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=str(dest.parent), suffix=".tmp")
    # os.fdopen takes ownership of fd on success; if it fails, fd is still ours.
    try:
        fh = os.fdopen(fd, "w", encoding="utf-8")
    except Exception:
        os.close(fd)
        os.unlink(tmp_path)
        raise
    try:
        with fh:
            json.dump(snapshot, fh, indent=2)
            fh.write("\n")
        os.replace(tmp_path, dest)
    except Exception:
        # fh (and thus fd) is already closed by the `with` block above; only
        # clean up the orphaned temp file. Do NOT os.close(fd) here — that would
        # double-close a descriptor os.fdopen owns.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _append_log(target_root: Path, entries: list[dict]) -> None:
    """Append *entries* to ``.aspis/current/export-log.jsonl`` (one JSON object per line)."""
    path = target_root / ".aspis" / "current" / "export-log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry) + "\n")


def _log_entry(
    path: str,
    kind: str,
    action: str,
    *,
    live: str | None = None,
    snapshot: str | None = None,
    regen: str | None = None,
) -> dict:
    """Build one audit-log record — the single shape written to ``export-log.jsonl``."""
    return {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "path": path,
        "kind": kind,
        "action": action,
        "hashes": {"live": live, "snapshot": snapshot, "regen": regen},
    }


def _hash_file(path: Path) -> str | None:
    """Return the normalized SHA-256 hash of *path* if it is a file, else ``None``."""
    if path.is_file():
        return sha256_text(path.read_text(encoding="utf-8"))
    return None


def _render_agent_text(
    action: ExportAction,
    project_config: dict,
    inventory,
    live_path: Path,
    *,
    preserve_models: bool,
    strip_bootstrap: bool,
) -> str:
    """Render an agent for *action*, then apply the two export-safety transforms.

    The single place agent text is produced for both the decision hash and the write, so
    ``_regen_hash`` and ``_apply`` can never diverge. ``strip_bootstrap`` removes the gate
    + bootstrap frontmatter (so a live project never re-grows it); ``preserve_models`` keeps
    the live file's already-baked ``model:`` line (so a re-export never re-routes a model).
    """
    inv = inventory.get(action.runtime) if isinstance(inventory, dict) else inventory
    text = transform.render_agent(
        action.source.read_text(encoding="utf-8"),
        action.runtime,
        project_config=project_config,
        inventory=inv,
    )
    if strip_bootstrap:
        from aspis.operations.bootstrap import strip_bootstrap_text

        text = strip_bootstrap_text(text)
    if preserve_models:
        text = _preserve_model_line(text, live_path)
    return text


def _regen_hash(
    action: ExportAction,
    project_config: dict,
    inventory,
    target_root: Path,
    *,
    preserve_models: bool = False,
    strip_bootstrap: bool = False,
) -> str | None:
    """Return the hash of what the catalog would write for *action*.

    For file copies this is the hash of the source file. For render actions it
    is the hash of the rendered text (using the same transforms as ``_apply``).
    Directory copies are outside hash protection and return ``None``.
    """
    if action.op == "copy":
        if action.source.is_dir():
            return None
        return sha256_text(action.source.read_text(encoding="utf-8"))
    if action.op == "render-agent":
        text = _render_agent_text(
            action,
            project_config,
            inventory,
            target_root / action.target,
            preserve_models=preserve_models,
            strip_bootstrap=strip_bootstrap,
        )
        return sha256_text(text)
    if action.op == "render-command":
        text = transform.render_command(action.source.read_text(encoding="utf-8"), action.runtime)
        return sha256_text(text)
    return None


def _pid_alive(pid: int) -> bool:
    """Best-effort cross-platform check whether *pid* is currently running."""
    if os.name == "posix":
        try:
            os.kill(pid, 0)
        except OSError as exc:
            if exc.errno == errno.ESRCH:
                return False
            # EPERM means the process exists but we cannot signal it.
            return True
        except Exception:
            return True
        return True

    # Windows
    try:
        SYNCHRONIZE = 0x00100000
        WAIT_TIMEOUT = 0x00000102
        handle = ctypes.windll.kernel32.OpenProcess(SYNCHRONIZE, False, pid)
        if not handle:
            return False
        try:
            result = ctypes.windll.kernel32.WaitForSingleObject(handle, 0)
            return result == WAIT_TIMEOUT
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    except Exception:
        return True


def _acquire_lock(lock_path: Path) -> None:
    """Acquire an exclusive lockfile at *lock_path*, taking over stale locks."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            break
        except FileExistsError:
            existing_pid = None
            try:
                existing_pid = int(lock_path.read_text(encoding="utf-8").strip())
            except Exception:
                pass
            held_by_other = (
                existing_pid is not None
                and existing_pid != os.getpid()
                and _pid_alive(existing_pid)
            )
            if held_by_other:
                raise ProtectionError(
                    f"export already in progress (lock held by PID {existing_pid})"
                ) from None
            lock_path.unlink(missing_ok=True)

    try:
        os.write(fd, str(os.getpid()).encode("utf-8"))
    finally:
        os.close(fd)


def _release_lock(lock_path: Path) -> None:
    """Release the lockfile at *lock_path* if it exists."""
    if lock_path.exists():
        try:
            lock_path.unlink()
        except OSError:
            pass


def write_export(
    plan: ExportPlan,
    target_root: Path,
    *,
    force: bool = False,
    write: bool = False,
    apply: bool = False,
    strict: bool = False,
    scope: str | None = None,
    force_conflicts: bool = False,
    reset_snapshot: bool = False,
    preserve_models: bool = False,
) -> list[str]:
    """Perform (or, with ``write=False``, describe) the planned actions.

    When ``force=False`` (the default), each target is classified by
    ``aspis.protect.decide`` and only ADD, UPDATE (when ``apply=True``), and
    CONFLICT (when ``apply=True`` and ``force_conflicts=True``) cause writes.
    UNKNOWN and PROTECT targets are preserved, and CONFLICT or PROTECT with
    ``strict=True`` raises ``ProtectionError`` (FR-010). Snapshots and audit
    logs are only persisted when a real write occurs (``write=True`` or
    ``apply=True``).

    ``force=True`` bypasses the decision engine and preserves the legacy
    skip-if-exists behavior, overwriting all existing targets.

    Two export-safety transforms run regardless of the write path. When
    ``preserve_models`` is set (``aspis export``/``init``, but never
    ``aspis models --apply``), each rendered agent keeps the live file's already-baked
    ``model:`` line, so a structural re-export never re-routes a frozen model. When the
    project is already bootstrapped (``manifest.is_bootstrapped``), the bootstrap gate +
    delegate are stripped from rendered agents, the transient onboarding package is skipped,
    and any lingering package residue is removed — so a live project never re-grows bootstrap.
    """
    # The target's own settings override model routing — project.yaml plus the
    # authoritative per-agent assignments in agent-models.yaml (aspis models --sync).
    project_config = project.load_effective_config(target_root)
    # Detected runtime inventory (None when detection has not run here) — lets render
    # emit the model strings the machine can actually run. Loaded once for all actions.
    inventory = load_inventory(target_root)
    # Once live, bootstrap must leave no trace — strip its prose and skip its package.
    bootstrapped = manifest.is_bootstrapped(target_root)
    performed: list[str] = []

    if scope is not None and not any(a.target.startswith(scope) for a in plan.actions):
        return [f"scope '{scope}' matched no actions"]

    effective_write = write or apply
    lock_path = target_root / ".aspis" / "current" / "export.lock"
    if effective_write:
        _acquire_lock(lock_path)

    try:
        if force:
            _write_force(
                plan,
                target_root,
                project_config,
                inventory,
                performed,
                effective_write=effective_write,
                scope=scope,
                reset_snapshot=reset_snapshot,
                preserve_models=preserve_models,
                bootstrapped=bootstrapped,
            )
        else:
            _write_decide(
                plan,
                target_root,
                project_config,
                inventory,
                performed,
                effective_write=effective_write,
                apply=apply,
                strict=strict,
                scope=scope,
                force_conflicts=force_conflicts,
                reset_snapshot=reset_snapshot,
                preserve_models=preserve_models,
                bootstrapped=bootstrapped,
            )

        # A live project keeps zero bootstrap residue: drop any leftover package files.
        if bootstrapped:
            _remove_bootstrap_residue(target_root, performed, effective_write=effective_write)

        # Each runtime emits its own scope-guard wiring (adapter-owned placement).
        if plan.catalog_root is not None:
            hook_write = write or apply
            for runtime in sorted({action.runtime for action in plan.actions if action.runtime}):
                performed.extend(
                    get_adapter(runtime).emit_runtime_hooks(
                        plan.catalog_root, target_root, force=force, write=hook_write
                    )
                )
        return performed
    finally:
        _release_lock(lock_path)


def _remove_bootstrap_residue(
    target_root: Path, performed: list[str], *, effective_write: bool
) -> None:
    """Delete any transient onboarding-package files still present in a live project.

    Reuses the bootstrap subsystem's own definition of the package so the two stay in
    lockstep. Idempotent: on a clean project the package list is empty and this is a no-op.
    """
    from aspis.operations.bootstrap import bootstrap_package

    for path in bootstrap_package(target_root):
        performed.append(f"remove (bootstrap done): {path.relative_to(target_root).as_posix()}")
        if effective_write:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()


def _write_force(
    plan: ExportPlan,
    target_root: Path,
    project_config: dict,
    inventory,
    performed: list[str],
    *,
    effective_write: bool,
    scope: str | None,
    reset_snapshot: bool,
    preserve_models: bool = False,
    bootstrapped: bool = False,
) -> None:
    """Legacy force path: overwrite (or skip if not force) every in-scope action."""
    if effective_write:
        snapshot = _load_snapshot(target_root, reset=reset_snapshot)
        paths = snapshot.setdefault("paths", {})
        log_entries: list[dict] = []
    else:
        snapshot = None
        paths = None
        log_entries = []

    for action in plan.actions:
        if scope is not None and not action.target.startswith(scope):
            continue
        if bootstrapped and _is_bootstrap_package(action):
            performed.append(f"skip (bootstrap done): {action.target}")
            continue

        destination = target_root / action.target
        performed.append(f"{action.op}: {action.target}")
        if effective_write:
            destination.parent.mkdir(parents=True, exist_ok=True)
            _apply(
                action,
                destination,
                project_config,
                inventory,
                preserve_models=preserve_models,
                strip_bootstrap=bootstrapped,
            )
            if destination.is_file():
                target_posix = action.target
                live_hash = _hash_file(destination)
                if live_hash is not None and paths is not None:
                    paths[target_posix] = live_hash
                    log_entries.append(_log_entry(target_posix, "FORCE", "wrote", live=live_hash))

    if effective_write and snapshot is not None:
        _save_snapshot(target_root, snapshot)
        _append_log(target_root, log_entries)


def _write_decide(
    plan: ExportPlan,
    target_root: Path,
    project_config: dict,
    inventory,
    performed: list[str],
    *,
    effective_write: bool,
    apply: bool,
    strict: bool,
    scope: str | None,
    force_conflicts: bool,
    reset_snapshot: bool,
    preserve_models: bool = False,
    bootstrapped: bool = False,
) -> None:
    """Hash-protected decide path: only safe changes are written."""
    snapshot = _load_snapshot(target_root, reset=reset_snapshot)
    paths = snapshot.setdefault("paths", {})
    log_entries: list[dict] = []

    for action in plan.actions:
        if scope is not None and not action.target.startswith(scope):
            continue
        if bootstrapped and _is_bootstrap_package(action):
            performed.append(f"skip (bootstrap done): {action.target}")
            continue

        destination = target_root / action.target
        target_posix = action.target
        regen_hash = _regen_hash(
            action,
            project_config,
            inventory,
            target_root,
            preserve_models=preserve_models,
            strip_bootstrap=bootstrapped,
        )

        if regen_hash is None:
            # Directory copies use legacy skip-if-exists and are not hash-protected.
            # (This branch is only reached when force=False — _write_force handles
            # the force path — so no force check is needed here.)
            if destination.exists():
                performed.append(f"skip (exists): {action.target}")
                continue
            performed.append(f"{action.op}: {action.target}")
            if effective_write:
                destination.parent.mkdir(parents=True, exist_ok=True)
                _apply(action, destination, project_config, inventory)
            continue

        live_hash = _hash_file(destination)
        snapshot_hash = paths.get(target_posix)
        decision = decide(live_hash, snapshot_hash, regen_hash)

        if decision.kind == DecisionKind.ADD:
            should_write = effective_write
            action_str = "wrote"
        elif decision.kind == DecisionKind.UNCHANGED:
            should_write = False
            action_str = "skipped"
        elif decision.kind == DecisionKind.UNKNOWN:
            should_write = False
            # Record the live hash so a future run can classify this file as
            # UNCHANGED/UPDATE/PROTECT instead of UNKNOWN forever. This means the
            # snapshot records files we *observed*, not only files we wrote — a
            # deliberate choice so an externally-created file becomes tracked on
            # the next run instead of staying UNKNOWN indefinitely.
            if live_hash is not None:
                paths[target_posix] = live_hash
            action_str = "preserved"
        elif decision.kind == DecisionKind.UPDATE:
            should_write = apply
            action_str = "wrote"
        elif decision.kind == DecisionKind.PROTECT:
            should_write = False
            action_str = "protected"
        else:  # CONFLICT
            should_write = apply and force_conflicts
            action_str = "wrote" if should_write else "conflict"

        if should_write:
            performed.append(f"{action.op}: {action.target}")
            if effective_write:
                destination.parent.mkdir(parents=True, exist_ok=True)
                _apply(
                    action,
                    destination,
                    project_config,
                    inventory,
                    preserve_models=preserve_models,
                    strip_bootstrap=bootstrapped,
                )
                paths[target_posix] = regen_hash
        else:
            hint = (
                " (use --force-conflicts to overwrite)"
                if decision.kind is DecisionKind.CONFLICT
                else ""
            )
            performed.append(f"{decision.kind.value}: {action.target}{hint}")

        log_entries.append(
            _log_entry(
                target_posix,
                decision.kind.value,
                action_str,
                live=live_hash,
                snapshot=snapshot_hash,
                regen=regen_hash,
            )
        )

        if strict and decision.kind in (DecisionKind.CONFLICT, DecisionKind.PROTECT):
            if effective_write:
                _save_snapshot(target_root, snapshot)
                _append_log(target_root, log_entries)
            if decision.kind is DecisionKind.CONFLICT:
                raise ProtectionError(
                    f"conflict on {action.target}: both user and catalog changed "
                    f"(use --force-conflicts to overwrite)"
                )
            raise ProtectionError(
                f"protected on {action.target}: user-customized file skipped "
                f"(use --force to overwrite)"
            )

    if effective_write:
        _save_snapshot(target_root, snapshot)
        _append_log(target_root, log_entries)


def _apply(
    action: ExportAction,
    destination: Path,
    project_config: dict,
    inventory=None,
    *,
    preserve_models: bool = False,
    strip_bootstrap: bool = False,
) -> None:
    """Execute a single export action against *destination*."""
    if action.op == "render-agent":
        text = _render_agent_text(
            action,
            project_config,
            inventory,
            destination,
            preserve_models=preserve_models,
            strip_bootstrap=strip_bootstrap,
        )
        destination.write_text(text, encoding="utf-8", newline="\n")
    elif action.op == "render-command":
        text = transform.render_command(action.source.read_text(encoding="utf-8"), action.runtime)
        destination.write_text(text, encoding="utf-8", newline="\n")
    elif action.source.is_dir():
        shutil.copytree(action.source, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(action.source, destination)
