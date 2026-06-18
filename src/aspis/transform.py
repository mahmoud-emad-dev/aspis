"""Catalog → runtime transformation.

Thin dispatcher: parse a catalog asset, then hand it to the chosen runtime's
adapter. The transformer holds no runtime-specific logic — that lives in the
adapter modules — so new runtimes plug in via the registry without changing
this file.
"""

from __future__ import annotations

from aspis.catalog import parse_agent, parse_command
from aspis.runtimes import get_adapter


def render_agent(catalog_text: str, runtime: str) -> str:
    """Render a catalog agent's markdown for *runtime*."""
    return get_adapter(runtime).render_agent(parse_agent(catalog_text))


def render_command(catalog_text: str, runtime: str) -> str:
    """Render a catalog command's markdown for *runtime*."""
    return get_adapter(runtime).render_command(parse_command(catalog_text))
