"""Best-effort subprocess runner for the lifecycle operations.

Purpose:
    init and bootstrap shell out to helper scripts, git, and external runtime
    tools (e.g. ``opencode models``). Those steps are best-effort: their output
    is discarded and a failure must never abort the operation. But an external
    tool can wedge, so every such call is bounded by a timeout — turning a
    possible "hang forever" into a clean, logged skip.

Responsibilities:
    - Run a command with output captured (never inherited) and a hard timeout.
    - Never raise: a non-zero exit, a missing executable, or a timeout all
      resolve to ``False`` so the caller simply continues.

Does Not:
    - Interpret or surface the subprocess output — callers that need stdout use
      ``subprocess``/``gitops`` directly; this is only for fire-and-forget steps.

Used By:
    aspis.operations.init, aspis.operations.bootstrap.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

#: Seconds a single best-effort step may run before it is abandoned. Generous
#: enough for a slow brain-fill or model sync on a large repo, short enough that
#: a wedged external tool (the known ``opencode models`` hang) cannot stall a
#: bootstrap indefinitely.
STEP_TIMEOUT = 120


def run_quiet(
    cmd: list[str], *, cwd: Path | str | None = None, timeout: int = STEP_TIMEOUT
) -> bool:
    """Run *cmd* with output discarded; return ``True`` only on a clean exit.

    Never raises. A non-zero exit, a missing executable (``OSError``), or a
    timeout (``TimeoutExpired``) all return ``False`` so a best-effort step can
    be skipped without aborting the operation.
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd is not None else None,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0
