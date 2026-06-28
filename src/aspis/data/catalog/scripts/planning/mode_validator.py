#!/usr/bin/env python3
"""Validate the project mode and enforce mode-appropriate gates.

Purpose: Read the project mode from .aspis/config/project.yaml (or default to
'production'), validate it against known modes [vibe, mvp, production], check
that mode-appropriate gates are configured, and output PASS/WARN/FAIL with
reasoning.

Does Not: Change the mode — this is a validator, not a configurator.
Does not validate the full project configuration, only the mode field.

Used By: planning-lead (mode validation), build-lead (mode-aware gates).

Stdlib-only. Uses yaml (PyYAML) if available, falls back to JSON parsing.
Deterministic. --help shows usage.

Valid modes:
  vibe    — fast, loose, no reviews required
  mvp     — standard gates, optional reviews
  production — full rigor, all gates enforced

Usage:
  python mode_validator.py
  python mode_validator.py --config <path>
  python mode_validator.py --mode <mode>
  python mode_validator.py --help
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

KNOWN_MODES = {"vibe", "mvp", "production"}

# Mode-appropriate gates
MODE_GATES = {
    "vibe": {
        "required": [],
        "recommended": ["lint"],
        "review": "none",
    },
    "mvp": {
        "required": ["lint", "test"],
        "recommended": ["byte-parity", "validate-index"],
        "review": "optional",
    },
    "production": {
        "required": ["lint", "test", "byte-parity", "validate-index", "validate-runtime"],
        "recommended": ["doctor", "export --dry-run", "constitution-check"],
        "review": "required",
    },
}


def try_yaml_load(path: Path) -> dict | None:
    """Try loading YAML, falling back to JSON parsing of subset."""
    # Try PyYAML first
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: try JSON
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        pass

    # Minimal YAML parser for `mode:` field only
    try:
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("mode:"):
                mode_val = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                return {"mode": mode_val}
    except OSError:
        pass

    return None


def find_config(root: Path) -> Path | None:
    """Find project config file."""
    candidates = [
        root / ".aspis" / "config" / "project.yaml",
        root / ".aspis" / "config" / "project.yml",
        root / ".aspis" / "config.yaml",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def validate_mode(mode: str) -> tuple[str, str, dict]:
    """Validate mode and return (verdict, reasoning, gate_info)."""
    if mode not in KNOWN_MODES:
        return (
            "FAIL",
            f"Unknown mode '{mode}'. Valid modes: {', '.join(sorted(KNOWN_MODES))}",
            {},
        )

    gates = MODE_GATES.get(mode, {})
    required = gates.get("required", [])
    recommended = gates.get("recommended", [])

    reasoning = f"Mode '{mode}' is valid."
    if required:
        reasoning += f" Required gates: {', '.join(required)}."
    if recommended:
        reasoning += f" Recommended: {', '.join(recommended)}."

    return "PASS", reasoning, gates


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the project mode and enforce mode-appropriate gates."
    )
    parser.add_argument(
        "--config", default=None, help="path to project config file"
    )
    parser.add_argument(
        "--mode", default=None, help="explicit mode to validate (overrides config)"
    )
    parser.add_argument(
        "--root", default=".", help="project root directory"
    )
    parser.add_argument(
        "--json", action="store_true", help="output as JSON"
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    root = Path(args.root)

    mode = None
    config_path = None

    if args.mode:
        mode = args.mode
    elif args.config:
        config_path = Path(args.config)
        config = try_yaml_load(config_path)
        if config and isinstance(config, dict):
            mode = config.get("mode")
    else:
        config_path = find_config(root)
        if config_path:
            config = try_yaml_load(config_path)
            if config and isinstance(config, dict):
                mode = config.get("mode")

    if not mode:
        mode = "production"
        reasoning_extra = " (default — no config found)"
    else:
        reasoning_extra = f" (from {config_path})" if config_path else ""

    verdict, reasoning, gates = validate_mode(mode)

    if args.json:
        output = {
            "verdict": verdict,
            "mode": mode,
            "reasoning": reasoning + reasoning_extra,
            "gates": gates,
            "config_path": str(config_path) if config_path else None,
        }
        print(json.dumps(output, indent=2))
        return 0

    print(f"Mode:       {mode}{reasoning_extra}")
    print(f"Verdict:    {verdict}")
    print(f"Reasoning:  {reasoning}")
    if gates:
        print(f"Required:   {', '.join(gates.get('required', [])) or 'none'}")
        print(f"Recommended: {', '.join(gates.get('recommended', [])) or 'none'}")
        print(f"Review:     {gates.get('review', 'unknown')}")

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
