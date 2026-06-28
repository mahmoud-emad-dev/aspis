"""Template rendering — the single shared placeholder helper.

ASPIS keeps content in static files and fills small ``{placeholder}`` slots at
render time. This is the ONE place substitution happens, so every caller (brain
scaffold, root files, exported assets) behaves identically. Only ``{identifier}``
tokens are touched; unknown ones are left as-is (so a template can carry slots
filled at a later stage, e.g. bootstrap), and any other braces pass through
untouched.

Used by: the brain scaffold + root-file writers and exported-asset rendering.
"""

from __future__ import annotations

import re

# Matches a {placeholder} whose name is a Python-style identifier.
_PLACEHOLDER = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def render(template: str, /, **values: object) -> str:
    """Replace ``{name}`` placeholders in *template* from *values*.

    Placeholders without a matching value are left unchanged.
    """
    mapping = {key: str(value) for key, value in values.items()}

    def _replace(match: re.Match[str]) -> str:
        name = match.group(1)
        return mapping.get(name, match.group(0))

    return _PLACEHOLDER.sub(_replace, template)
