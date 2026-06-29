"""ASPIS CLI command registry.

Each verb lives in its own module that exposes a ``register(subparsers)``
function. To add a command: create the module, then add it to
``COMMAND_MODULES`` below. The CLI entry point (:mod:`aspis.cli`) loops over
this tuple, so it never needs to change when a verb is added.
"""

from __future__ import annotations

from aspis.commands import (
    artifact,
    bootstrap,
    byte_parity,
    commit,
    commits,
    context,
    doctor,
    drift,
    export_cmd,
    findings,
    gitignore,
    governance,
    heal,
    init,
    mode,
    models,
    preflight,
    stack,
    status,
    subsystem,
    testledger,
    uninstall,
    validate_index,
    validate_runtime,
)

#: Command modules, in the order their verbs appear in ``aspis --help``.
COMMAND_MODULES = (
    init,
    bootstrap,
    byte_parity,
    export_cmd,
    status,
    mode,
    models,
    gitignore,
    commit,
    commits,
    artifact,
    subsystem,
    stack,
    heal,
    testledger,
    preflight,
    context,
    findings,
    drift,
    doctor,
    governance,
    uninstall,
    validate_index,
    validate_runtime,
)
