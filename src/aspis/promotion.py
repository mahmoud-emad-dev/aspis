"""Lead promotion — flip post-bootstrap leads from subagent to primary.

Every agent ships as ``mode: subagent`` so a freshly initialized project has a
single entry point: ``project-lead`` (always primary). Once bootstrap proves the
project is live, the leads in :data:`PROMOTE_TO_PRIMARY` become directly
selectable, yielding exactly five primaries.

Only the runtime that expresses ``mode`` in agent frontmatter can be promoted, so
promotion edits that runtime's rendered ``agents`` files (today OpenCode's); which
runtime that is comes from the adapter capability (``supports_mode``), never a
hardcoded name. The edit is frontmatter-only and idempotent — an already-primary
lead is left untouched, so re-running bootstrap is safe.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from aspis.constants import PROMOTE_TO_PRIMARY
from aspis.runtimes import get_adapter, mode_runtime

# The first ``mode:`` line in a frontmatter block; groups keep prefix + trailing.
_MODE_RE = re.compile(r"^(mode:[ \t]*)(\S+)(.*)$", re.MULTILINE)


@dataclass
class PromotionResult:
    """What promotion did: which leads were flipped, already primary, or absent."""

    promoted: list[str] = field(default_factory=list)
    already: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)


def promote_leads(
    target_root: Path, *, runtime: str | None = None, write: bool = False
) -> PromotionResult:
    """Flip the post-bootstrap leads to ``primary`` in *target_root*'s runtime dir.

    *runtime* defaults to the runtime that expresses ``mode`` (``mode_runtime()``);
    if no runtime does, there is nothing to promote and an empty result is returned.
    """
    result = PromotionResult()
    runtime = runtime or mode_runtime()
    if runtime is None:
        return result
    agents_dir = target_root / get_adapter(runtime).runtime_dir / "agents"
    for name in PROMOTE_TO_PRIMARY:
        path = agents_dir / f"{name}.md"
        if not path.is_file():
            result.missing.append(name)
            continue
        text = path.read_text(encoding="utf-8")
        match = _MODE_RE.search(text)
        if match is None:
            result.missing.append(name)
            continue
        if match.group(2) == "primary":
            result.already.append(name)
            continue
        result.promoted.append(name)
        if write:
            path.write_text(_MODE_RE.sub(r"\g<1>primary\g<3>", text, count=1), encoding="utf-8")
    return result
