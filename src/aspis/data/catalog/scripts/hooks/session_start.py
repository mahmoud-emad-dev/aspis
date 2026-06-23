#!/usr/bin/env python3
"""Session-start notice — surface open findings when a session begins (F-014 T-12).

Wired to Claude `SessionStart` and OpenCode's session-start plugin event. Its stdout is
informational (Claude injects it into the session context); it never blocks — always exit 0.
Stdlib-only, so it runs under the baked interpreter with no third-party dependency.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import _config  # noqa: E402
import _git  # noqa: E402
import findings  # noqa: E402


def main() -> int:
    _config.force_utf8_stdio()
    root = _git.repo_root()
    items = findings.load(root)
    if items:
        print(
            f"[aspis] {len(items)} open finding(s) — run `aspis preflight` / `aspis findings` "
            "and resolve before editing:"
        )
        for finding in items[:5]:
            print(f"  - [{finding.get('kind', '?')}] {finding.get('detail', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
