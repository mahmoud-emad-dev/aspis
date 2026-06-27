#!/usr/bin/env python3
"""Shared console helper for the self-contained planning scripts.

Purpose:
    Keep the planning scripts' output UTF-8 safe so they never crash printing a
    non-ASCII character (an arrow, a check mark) under a legacy console — most
    notably Windows' cp1252, where the default stdout codec cannot encode them.

Does Not:
    Parse arguments or do any planning work — it only configures the streams.

Used By:
    feature_scaffold.py, prereq_validate.py, task_compile.py
"""

from __future__ import annotations

import sys


def force_utf8_stdio() -> None:
    """Make stdout/stderr emit UTF-8 on legacy consoles (mirrors ``aspis.cli``).

    Best-effort: streams without ``reconfigure`` (such as a test capture buffer)
    are left untouched.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass
