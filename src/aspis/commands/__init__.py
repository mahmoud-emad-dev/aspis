"""ASPIS CLI command registry.

Each verb lives in its own module that exposes a ``register(subparsers)``
function. To add a command: create the module, then add it to
``COMMAND_MODULES`` below. The CLI entry point (:mod:`aspis.cli`) loops over
this tuple, so it never needs to change when a verb is added.
"""

from __future__ import annotations

from aspis.commands import bootstrap, commit, doctor, gitignore, init, mode, status

#: Command modules, in the order their verbs appear in ``aspis --help``.
COMMAND_MODULES = (init, bootstrap, status, mode, gitignore, commit, doctor)
