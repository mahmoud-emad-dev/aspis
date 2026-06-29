"""setup-workflow — the thin orchestration over the init/bootstrap operations (F-020).

Turns first-run into one guided experience: after ``aspis init``, it reads the
pre-bootstrap decision state, tells the user exactly where the project is and what to do
next (continue onboarding / skip / open a runtime / stop), and records progress so an
interrupted run resumes instead of restarting. It only *sequences and presents* — each
operation still owns its own work; this module makes no project changes beyond the
onboarding-status marker in the decision state.
"""

from __future__ import annotations

from pathlib import Path

from aspis.operations import pre_bootstrap as pb

#: The recommended next action per project state (the state machine drives the UX).
_NEXT = {
    pb.EMPTY: "init",
    pb.EXISTING_CODE: "init",
    pb.INCOMPLETE: "recover",
    pb.LEGACY: "recover",
    pb.INITIALIZED: "onboard",
    pb.BOOTSTRAPPED: "ready",
}

#: Best-effort command to *continue inside* a detected runtime (its CLI executable). GUI/
#: desktop runtimes without a CLI fall back to their name; refined from runtime defs later.
_LAUNCH = {"opencode": "opencode", "claude": "claude"}

#: Onboarding lifecycle statuses recorded for resume.
PENDING, IN_PROGRESS, SKIPPED, COMPLETE = "pending", "in_progress", "skipped", "complete"


def next_step(state: dict) -> str:
    """The recommended next action: ``init`` | ``recover`` | ``onboard`` | ready (``done``)."""
    return (
        "done"
        if state.get("project_state") == pb.BOOTSTRAPPED
        else _NEXT.get(state.get("project_state", ""), "init")
    )


def options(state: dict) -> list[tuple[str, str]]:
    """The decision-screen choices for the current state (key, human label)."""
    step = next_step(state)
    if step == "onboard":
        return [
            ("continue", "Continue onboarding now — make the project live"),
            ("skip", "Skip for now — project stays valid; bootstrap later"),
            ("runtime", "Open a runtime and continue there"),
            ("stop", "Stop after scaffold"),
        ]
    if step == "done":
        return [("work", "Project is live — start working")]
    if step == "recover":
        return [("recover", "Recover/upgrade the ASPIS brain"), ("stop", "Stop")]
    return [("init", "Run `aspis init --write` to scaffold"), ("stop", "Stop")]


def launch_commands(state: dict) -> dict[str, str]:
    """Exact command to continue in each detected runtime (best-effort)."""
    available = (state.get("runtimes") or {}).get("available") or []
    return {name: _LAUNCH.get(name, name) for name in available}


def mark(root: Path, status: str, **extra) -> Path:
    """Record the onboarding status (and any extra) in the decision state, for resume."""
    state = pb.load_state(root)
    onboarding = state.get("onboarding") or {}
    onboarding["status"] = status
    onboarding.update(extra)
    state["onboarding"] = onboarding
    return pb.save_state(root, state)


def render(state: dict) -> str:
    """The guided decision screen: where the project is, what was detected, what to do next."""
    stack = state.get("stack") or {}
    runtimes = (state.get("runtimes") or {}).get("available") or []
    rules = state.get("rules") or {}
    plans = state.get("plan_files") or []
    launch = launch_commands(state)
    lines = [
        "ASPIS — setup",
        f"  project state : {state.get('project_state', '?')}",
        f"  stack         : {stack.get('value', 'unknown')} "
        f"({stack.get('confidence', '?')} confidence)",
        f"  runtimes      : {', '.join(runtimes) or 'none detected on PATH'}",
        f"  rules         : system={rules.get('system')} project={rules.get('project')} "
        f"user={rules.get('user_present')}",
        f"  plan files    : {', '.join(plans) or 'none found'}",
        "",
        f"Next: {next_step(state)}",
    ]
    for _key, label in options(state):
        lines.append(f"  - {label}")
    if launch:
        lines.append("")
        lines.append("Open a runtime to continue there:")
        for name, cmd in launch.items():
            lines.append(f"  {name}: {cmd}    (starts with project-lead → delegates to bootstrap)")
    return "\n".join(lines)


def resume_point(state: dict) -> str:
    """Where to resume from the recorded onboarding status (so a run never restarts).

    ``complete`` → done; ``skipped`` → skipped; ``pending``/``in_progress`` → the
    state-derived next step.
    """
    status = (state.get("onboarding") or {}).get("status") or PENDING
    if status == COMPLETE:
        return "done"
    if status == SKIPPED:
        return "skipped"
    return next_step(state)


def guide(root: Path) -> tuple[dict, str]:
    """Resolve the decision state read-only and render the guidance; return (state, text)."""
    state = pb.resolve(Path(root))
    return state, render(state)
