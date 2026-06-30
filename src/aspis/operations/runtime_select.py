"""Runtime detection + selection for ``aspis init`` (F-020).

When the user does not pass ``--runtime``, init should not silently guess: it
detects which *supported* runtimes are actually installed on this machine and lets
the user pick one or more. If none of the supported runtimes is installed, init
never installs anything — it points at OpenCode (the free default) and asks before
proceeding.

This module is the pure, side-effect-free, unit-testable half: which runtimes we
support, which are installed, how the menu reads, and how a raw answer parses. The
interactive loop (``input()``/``print()``) lives in ``commands/init.py``; the
``init`` operation itself stays deterministic and offline (its FIXED contract).
"""

from __future__ import annotations

from aspis import resources, runtime_inventory

#: Where to get a runtime when the machine has none we support. OpenCode is free and
#: cross-platform, so it is the one we offer to default to (after the user confirms).
DEFAULT_RUNTIME = "opencode"
OPENCODE_URL = "https://opencode.ai"
OPENCODE_INSTALL = "npm install -g opencode-ai"


def supported() -> list[str]:
    """Every runtime ASPIS can export to, sorted (discovered from data, never hardcoded)."""
    return sorted(resources.runtime_defs())


def installed(detected: dict[str, str | None] | None = None) -> list[str]:
    """The supported runtimes whose CLI is present on this machine, sorted."""
    return runtime_inventory.available(detected)


def menu(
    supported_runtimes: list[str], installed_runtimes: list[str]
) -> list[tuple[int, str, bool]]:
    """Numbered menu rows ``(number, runtime, is_installed)`` for display."""
    present = set(installed_runtimes)
    return [(i, name, name in present) for i, name in enumerate(supported_runtimes, start=1)]


def render_menu(rows: list[tuple[int, str, bool]]) -> str:
    """Render the selection menu the user sees."""
    lines = ["Which agent runtime(s) should this project use? You can pick more than one."]
    for number, name, is_installed in rows:
        tag = "installed" if is_installed else "not installed"
        lines.append(f"  {number}) {name:<10} [{tag}]")
    lines.append("")
    lines.append("Enter numbers or names, comma/space separated (e.g. '1' or 'opencode claude').")
    return "\n".join(lines)


def parse_selection(raw: str, supported_runtimes: list[str]) -> list[str]:
    """Parse a raw answer (numbers and/or names) into a validated, de-duplicated list.

    Tokens may be 1-based menu numbers or runtime names; unknown tokens are ignored.
    The result follows ``supported_runtimes`` order. An empty/garbage answer yields ``[]``
    so the caller can fall back to its default.
    """
    chosen: set[str] = set()
    for token in raw.replace(",", " ").split():
        if token.isdigit():
            index = int(token) - 1
            if 0 <= index < len(supported_runtimes):
                chosen.add(supported_runtimes[index])
        elif token in supported_runtimes:
            chosen.add(token)
    return [name for name in supported_runtimes if name in chosen]


def install_hint() -> str:
    """The message shown when no supported runtime is installed (URL + command)."""
    return (
        "No supported agent runtime was found on this machine.\n"
        f"Install OpenCode (free, cross-platform):  {OPENCODE_URL}\n"
        f"  e.g.  {OPENCODE_INSTALL}\n"
        "(Claude Code is also supported if you already have it.)"
    )
