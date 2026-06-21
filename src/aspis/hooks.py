"""Type-1 lifecycle hooks — operational scripts run around operations.

These are OUR scripts (distinct from the runtime tools' own hooks). For an event
like ``pre-init`` the runner discovers files under
``<root>/<brain>/<lifecycle>/<event>/`` and runs them in sorted order. Discovery
is convention-driven, so adding a hook means dropping a file in the folder — no
code change. Pre-hooks block the operation on failure; post-hooks only warn.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from aspis.lifecycle import Context
from aspis.settings import get_settings


class HookError(RuntimeError):
    """Raised when a blocking (pre-) hook exits non-zero."""


def _command_for(script: Path) -> list[str] | None:
    """Return the command to run *script*, or None if no interpreter is available.

    Python hooks run with the active interpreter (cross-platform). Shell hooks
    run only when their interpreter is on PATH — Windows-first means ``.ps1`` via
    PowerShell, POSIX means ``.sh`` via bash.
    """
    suffix = script.suffix.lower()
    if suffix == ".py":
        return [sys.executable, str(script)]
    if suffix == ".sh" and shutil.which("bash"):
        return ["bash", str(script)]
    if suffix == ".ps1":
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if shell:
            return [shell, "-File", str(script)]
    return None


class HookRunner:
    """Discovers and runs the Type-1 lifecycle hooks for an event."""

    def __call__(self, event: str, ctx: Context) -> None:
        """Run every hook registered for *event*, recording results on *ctx*."""
        settings = get_settings()
        event_dir = ctx.root / settings.brain_dir / settings.hooks_dir / event
        if not event_dir.is_dir():
            return

        block = event.startswith("pre-")
        records = ctx.results.setdefault("hooks", {}).setdefault(event, [])

        for script in sorted(event_dir.iterdir()):
            if not script.is_file():
                continue

            command = _command_for(script)
            if command is None:
                ctx.log(f"hook skipped (no interpreter): {script.name}")
                continue

            outcome = self._run_one(command, script, event, ctx)
            records.append(outcome)

            if outcome["exit_code"] != 0:
                message = f"hook failed: {script.name} (exit {outcome['exit_code']})"
                ctx.log(message)
                if block:
                    raise HookError(message)

    def _run_one(self, command: list[str], script: Path, event: str, ctx: Context) -> dict:
        """Run one hook script and return a record of its outcome."""
        env = {
            **os.environ,
            "ASPIS_ROOT": str(ctx.root),
            "ASPIS_OPERATION": ctx.operation,
            "ASPIS_EVENT": event,
        }
        completed = subprocess.run(
            command,
            cwd=str(ctx.root),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        return {
            "hook": script.name,
            "exit_code": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
