#!/usr/bin/env python3
"""cross_ref_agents.py — Validate cross-agent consistency of F-016 reference specs.

Purpose:
    Read all agent reference spec files in
    ``.aspis/features/F-016-agent-system-architecture/Research/ref/`` and check
    that the agent system is internally coherent. Catches the four classes of
    cross-agent drift that an adversarial reviewer would otherwise have to find
    by hand:

        1. Overlapping responsibilities  — two agents claim the same job.
        2. Orphaned delegation edges     — an agent delegates to a name that
                                           does not exist (and is not on the
                                           known-future roster).
        3. Unresolved skill references   — a backtick-quoted skill is mentioned
                                           that no spec defines.
        4. Open clarification markers    — ``[NEEDS CLARIFICATION]`` is left in
                                           a spec instead of being resolved.

    Deterministic — no LLM, no network. Output is exit 0 when clean, exit 1
    when any finding is reported. Designed to be wired into CI and to be run
    from a reviewer agent as a pre-review gate.

Does Not:
    - Edit any spec file.
    - Render or evaluate markdown (parsing only — the tables and tokens are
      regex-extracted, not AST-built).
    - Replace the live reviewer agent; this script is the deterministic
      first-pass before the LLM adversarial audit.

Used By:
    - F-016 review work (T-02, T-05, T-14, T-18, T-40).
    - The planning lead and reviewer lead at any point they want a quick
      consistency read on the agent roster.
    - CI: ``python .aspis/scripts/planning/cross_ref_agents.py --scope leads``.

Usage:
    python3 .aspis/scripts/planning/cross_ref_agents.py --scope leads
    python3 .aspis/scripts/planning/cross_ref_agents.py --scope all
    python3 .aspis/scripts/planning/cross_ref_agents.py --scope build-lead,fix-lead
    python3 .aspis/scripts/planning/cross_ref_agents.py --ref-dir <other> --scope leads
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Roster — the agents ASPIS knows about. Three tiers:
#   - LEADS  : the 8 L1/L2 specialists with full specs in the F-016 ref folder.
#   - LEAVES : the 3 L3 leaf workers (committer, general-builder, project-explorer)
#              that the leads delegate to. Lighter specs land in --scope all.
#   - FUTURE : agents referenced in planning prose whose specs are not yet
#              produced. References to these are EXPECTED and never flagged as
#              orphaned edges; instead they are reported as INFO.
# ---------------------------------------------------------------------------

LEAD_AGENTS: tuple[str, ...] = (
    "project-lead",
    "planning-lead",
    "build-lead",
    "reviewer",
    "system-lead",
    "fix-lead",
    "test-lead",
    "research-lead",
)

LEAF_AGENTS: tuple[str, ...] = (
    "committer",
    "general-builder",
    "project-explorer",
)

# Future / planned agents. Sourced from each spec's "Future subagents" /
# "Missing skills" / "New subagents" section. Adding a name here tells the
# script: "this name appears in the spec, it is intentionally not built
# yet, do not flag references to it as orphans." Keep this list current as
# the specs evolve — when the F-016 review finds a name that the spec
# lists as future but the script does not, the right fix is to add the
# name here, not to let the script keep flagging it.
FUTURE_AGENTS: frozenset[str] = frozenset(
    {
        # planning-lead — subagents for the planning pipeline
        "governance",
        "clarify",
        "task-decomposer",
        "idea-capture",
        "prd-writer",
        "scope-estimator",
        "constitution-checker",
        "research-request-writer",
        "dependency-analyzer",
        # research-lead — subagents for the knowledge layer
        "codebase-explorer",
        "docs-fetcher",
        "web-researcher",
        "cache-manager",
        # fix-lead — subagents for the recovery pipeline
        "bug-triager",
        "gate-fixer",
        # build-lead — subagent for review routing
        "sub-reviewer",
        # system-lead — subagents for the runtime layer (from §10 "Future
        # subagents" table)
        "runtime-validator",
        "drift-auditor",
        "permission-auditor",
        "export-verifier",
        "catalog-synchronizer",
        "opencode-author",
        "claude-author",
        # test-lead — stack-specialized testers (future)
        "test-author",
        "python-tester",
        "api-tester",
        "db-tester",
        "ui-tester",
        "cli-tester",
        "security-tester",
    }
)

# The full known-agent set. A delegation edge that points outside this set is
# an orphan (HIGH finding) — the most important signal this script emits.
KNOWN_AGENTS: frozenset[str] = frozenset(LEAD_AGENTS) | frozenset(LEAF_AGENTS) | FUTURE_AGENTS

# Bootstrap skill registry — skills that are named in prose but live in a
# catalog or skill folder, not in any of the in-scope specs. Read by the
# "skill resolution" check so the script can detect a typo even when the
# misspelled name appears only once in the corpus. Kept deliberately small —
# the script also harvests additional skills from the in-scope specs
# themselves (see ``build_skill_registry``).
BOOTSTRAP_SKILLS: frozenset[str] = frozenset(
    {
        "clean-tree-precondition",
        "deterministic-first",
        "commit-message",
        "commit-splitting",
    }
)

# ---------------------------------------------------------------------------
# Markdown-table parsing
#
# The specs follow a consistent pattern: a heading, then a markdown pipe table
# with a header row, a ``|---|---|`` separator, and data rows. We extract
# tables by line index — cheap, no full markdown AST — and treat each cell
# as a string with leading/trailing whitespace stripped.
# ---------------------------------------------------------------------------

_TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$")


def is_table_row(line: str) -> bool:
    """True if *line* looks like a markdown table row (starts with ``|``)."""
    return line.lstrip().startswith("|")


def parse_table_row(line: str) -> list[str]:
    """Split a table row into cells. ``| a | b | c |`` -> ``['a', 'b', 'c']``."""
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def find_tables(text: str) -> Iterable[tuple[int, int, list[str], list[list[str]]]]:
    """Yield ``(start_line, header_line, headers, rows)`` for every markdown table.

    The ``start_line`` is the header line; the rows are the data rows that
    follow the separator. The ``header_line`` is the index of the header row
    (1-based for human-friendly messages).
    """
    lines = text.splitlines()
    i = 0
    while i < len(lines) - 1:
        # A table starts with a row that has at least 2 cells and is followed
        # by a separator of the form ``|---|---|``.
        if is_table_row(lines[i]) and _TABLE_SEPARATOR.match(lines[i + 1]):
            headers = parse_table_row(lines[i])
            rows: list[list[str]] = []
            j = i + 2
            while j < len(lines) and is_table_row(lines[j]):
                rows.append(parse_table_row(lines[j]))
                j += 1
            if rows:  # ignore empty tables (just a header + separator)
                yield (i, i + 1, headers, rows)
            i = j
        else:
            i += 1


# ---------------------------------------------------------------------------
# Skill reference extraction
#
# A skill reference is a backtick-quoted kebab-case token with at least one
# hyphen: `` `prestart-checks` ``, `` `context-ladder` ``. We deliberately
# exclude:
#   - tools (``read``, ``write``, ``edit``, ``bash``) — no hyphen;
#   - paths (start with ``.``, ``/`` or contain ``/``);
#   - commands with wildcards (contain ``*`` or spaces);
#   - file extensions / dotted names (``ruff check``);
#   - agent names (filtered against KNOWN_AGENTS).
# ---------------------------------------------------------------------------

_SKILL_TOKEN = re.compile(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`")


def extract_skill_tokens(text: str) -> list[tuple[str, int]]:
    """Yield ``(name, 1-based_line)`` for every backtick-quoted kebab-case token.

    A token is only emitted when it is the **whole** content of its
    backticks — i.e. it is not a substring of a longer identifier like
    ``aspis validate-runtime*`` (where ``validate-runtime`` is a
    subcommand, not a skill) and not a CLI command prefixed by a tool
    name. The check looks for an opening backtick immediately before the
    match start; if there is one, the token is the only content of the
    backticks. This filters out model IDs and CLI verb fragments that
    happen to look like skill names.
    """
    for match in _SKILL_TOKEN.finditer(text):
        # Reject matches that are not the entire backtick content. A
        # legitimate skill reference looks like `` `foo-bar` `` — the
        # character right before the match is the opening backtick. If
        # the preceding character is anything else (typically a letter
        # or digit from a multi-token command like ``aspis validate-*``),
        # the matched token is a subcommand fragment, not a skill.
        start = match.start()
        if start == 0 or text[start - 1] != "`":
            continue
        name = match.group(1)
        line = text.count("\n", 0, start) + 1
        yield (name, line)


def is_agent_name(token: str) -> bool:
    """True if *token* names a known agent (lead, leaf, or future)."""
    return token in KNOWN_AGENTS


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

SEVERITY_HIGH = "HIGH"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_LOW = "LOW"
SEVERITY_INFO = "INFO"

# Exit-code policy: HIGH or MEDIUM findings fail the run. LOW and INFO do
# not — they are reported so reviewers can see them, but they do not block
# the gate. This matches the spec's "Exit 1 on FAIL" rule while letting
# housekeeping signals (future-agent references, near-match soft hits) flow
# without breaking the build.
FAILING_SEVERITIES: frozenset[str] = frozenset({SEVERITY_HIGH, SEVERITY_MEDIUM})


@dataclass
class Finding:
    """One issue produced by a check. ``file_path`` is the spec the finding came from."""

    file_path: str
    line: int
    severity: str
    check: str
    message: str

    def render(self) -> str:
        return f"{self.file_path}:{self.line}: {self.severity}: {self.check}: {self.message}"


# ---------------------------------------------------------------------------
# Spec loading
# ---------------------------------------------------------------------------


@dataclass
class ParsedSpec:
    """A spec file with the parts the script needs cached on it.

    ``responsibilities`` is a list of ``(line, text)`` — the responsibility
    text and the line where it lives, used for overlap detection.
    ``delegations`` is a list of ``(line, agent_name)`` — every delegation
    edge the spec declares, used to find orphaned edges.
    ``declared_skills`` is the set of skill names that appear in a
    ``Responsibilities → Skills`` table — these are the SKILLS the spec
    actually claims. The script uses them to seed the skill registry.
    ``skill_refs`` is the list of backtick-quoted kebab-case tokens found
    anywhere in the file (excluding agent names), used to find unresolved
    skill references — the body of the spec may mention a skill that no
    Skills table declares, and that is the typo we are looking for.
    ``clarifications`` is the list of ``[NEEDS CLARIFICATION]`` markers.
    """

    name: str
    path: Path
    text: str
    lines: list[str]
    responsibilities: list[tuple[int, str]] = field(default_factory=list)
    declared_skills: set[str] = field(default_factory=set)
    delegations: list[tuple[int, str]] = field(default_factory=list)
    skill_refs: list[tuple[int, str]] = field(default_factory=list)
    clarifications: list[tuple[int, str]] = field(default_factory=list)


# Patterns that mark a section as "delegation-related" — its tables and
# `#### name (L<level>)` headings are scanned for delegate names. The
# patterns match common phrasings seen in the 8 lead specs.
_DELEGATION_HEADINGS = (
    re.compile(r"^\s*#{2,}\s+.*[Tt]ask\s*[/·\s]+[Dd]elegation", re.MULTILINE),
    re.compile(r"^\s*#{1,}\s+.*[Dd]elegation\s+[Mm]ap", re.MULTILINE),
    re.compile(r"^\s*#{2,}\s+.*[Ee]xisting\s+[Dd]elegates", re.MULTILINE),
    re.compile(r"^\s*#{2,}\s+.*[Nn]ew\s+[Ss]ubagents", re.MULTILINE),
    re.compile(r"^\s*#{2,}\s+[Rr]eceives\s+from", re.MULTILINE),
    re.compile(r"^\s*#{2,}\s+[Ss]ends\s+to", re.MULTILINE),
    re.compile(r"^\s*#{2,}\s+[Rr]outing\s+[Tt]able", re.MULTILINE),
    re.compile(r"^\s*#{2,}\s+[Ss]ubagents", re.MULTILINE),
    re.compile(r"^\s*#{2,}\s+[Pp]er-delegate\s+[Pp]rofiles", re.MULTILINE),
)
# Inline delegate headings like ``#### build-lead (L2 primary)`` or
# ``#### project-explorer (L3 leaf)`` — present in the per-delegate profile
# sections of the L1 / L2 specs.
_DELEGATE_SUBHEADING = re.compile(r"^\s*#{3,4}\s+`?([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`?\s*\((L[123])", re.MULTILINE)
# Backtick-quoted agent names in plain prose, used as a fallback for specs
# whose delegation map is mostly prose (e.g. "delegates to `general-builder`").
_PROSE_DELEGATE = re.compile(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`\s*\((L[123])", re.MULTILINE)


def _section_offsets(text: str, patterns: Iterable[re.Pattern[str]]) -> list[tuple[int, int, int]]:
    """Return ``(heading_offset, body_start_offset, body_end_offset)`` triples.

    The body of a section is the text between its heading and the next
    heading of equal or shallower depth.
    """
    out: list[tuple[int, int, int]] = []
    for pattern in patterns:
        for match in pattern.finditer(text):
            heading_text = match.group(0).lstrip()
            depth = 0
            while depth < len(heading_text) and heading_text[depth] == "#":
                depth += 1
            # Use ``match.end()`` (the offset just after the matched text)
            # as the start of the body. Using ``text.find('\\n', heading_offset)``
            # would find the leading newline (the match often starts there
            # because the patterns allow leading ``\\s*``), not the trailing
            # one. The match itself is the correct boundary.
            heading_offset = match.start()
            body_start = _section_body_offset_after(text, match.end())
            body_end = _next_heading_offset(text, body_start, depth)
            out.append((heading_offset, body_start, body_end))
    return out


# Column headers in delegation tables. We look for tables where the first
# column is one of these names — those are the rows we treat as delegation
# edges. (The "Task" column is filtered out via the cell content.)
_DELEGATION_TABLE_HEADERS = frozenset(
    {
        "delegate",
        "delegates",
        "delegation",
        "from",
        "to",
        "subagent",
        "caller",
        "name",
    }
)


def _is_delegation_table(headers: list[str]) -> bool:
    """True if the first column of a table is a delegate / subagent column."""
    if not headers:
        return False
    return headers[0].strip().lower() in _DELEGATION_TABLE_HEADERS


def _extract_agent_from_cell(cell: str) -> str | None:
    """Return the agent name from a delegation-table cell, or None.

    The cell format varies — most use `` `name` `` backticks, but the "From"
    column in fix-lead.md uses bare bolded names like ``**build-lead**``.
    """
    # Backtick-quoted: `name`
    match = re.search(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`", cell)
    if match:
        return match.group(1)
    # Bolded: **name**
    match = re.search(r"\*\*([a-z][a-z0-9]*(?:-[a-z0-9]+)+)\*\*", cell)
    if match:
        return match.group(1)
    return None


# Heading pattern that scopes responsibility parsing. The check is strict:
# only tables that appear UNDER a heading mentioning "Responsibilities" (in
# either the L1 spec style ``## N · Responsibilities → Skills`` or the
# shorter ``## Responsibilities → Skills`` form) count as responsibility
# tables. This keeps the bash allowlist ("Pattern | Purpose | Read/Write")
# out of the responsibility overlap check.
_RESPONSIBILITY_HEADING = re.compile(
    r"^\s*#{1,6}\s+.*[Rr]esponsibilities?\b.*[→\->].*[Ss]kills?\b",
    re.MULTILINE,
)
# Fallback heading for specs whose first section is "Current skills" or
# "Missing skills" (reviewer.md, system-lead.md) without a "Responsibilities
# → Skills" header. These sections still carry the role's responsibility list.
_SKILLS_HEADING = re.compile(
    r"^\s*#{1,6}\s+.*\b(?:[Cc]urrent\s+skills|[Mm]issing\s+skills|"
    r"[Ss]kills?\s+NOT\s+in\b|[Rr]ecommended\s+skill\s+additions)\b",
    re.MULTILINE,
)


def _section_body_offset_after(text: str, after_offset: int) -> int:
    """Return the body-start offset (1 past the line containing *after_offset*).

    ``after_offset`` should be the position just after the heading text
    (typically ``match.end()``). We advance past the trailing newline to
    land on the first line of the body.
    """
    line_end = text.find("\n", after_offset)
    return (line_end + 1) if line_end != -1 else len(text)


def _next_heading_offset(text: str, body_start: int, depth: int) -> int:
    """Return the offset of the next heading at the same or shallower depth."""
    lines = text[body_start:].splitlines()
    running_offset = body_start
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("#"):
            # Count the leading '#' characters in the stripped line. The
            # previous implementation used ``len(line) - len(line.lstrip())``
            # which is the leading-whitespace count, not the hash count —
            # wrong for unindented headings, the very case we hit most.
            line_depth = len(stripped) - len(stripped.lstrip("#"))
            if 0 < line_depth <= depth:
                return running_offset
        running_offset += len(line) + 1
    return len(text)


def _offsets_for_heading(text: str, pattern: re.Pattern[str]) -> list[tuple[int, int, int]]:
    """Return ``(heading_offset, body_start_offset, body_end_offset)`` triples."""
    out: list[tuple[int, int, int]] = []
    for match in pattern.finditer(text):
        # Determine heading depth (number of leading '#' chars). The matched
        # text may include leading whitespace (because the patterns all start
        # with ``\s*``); strip it before counting the hashes, or the depth
        # is computed from the wrong characters and the section boundaries
        # are nonsense.
        heading_text = match.group(0).lstrip()
        depth = 0
        while depth < len(heading_text) and heading_text[depth] == "#":
            depth += 1
        heading_offset = match.start()
        body_start = _section_body_offset_after(text, match.end())
        body_end = _next_heading_offset(text, body_start, depth)
        out.append((heading_offset, body_start, body_end))
    return out


def parse_spec(path: Path) -> ParsedSpec:
    """Parse one reference spec into the parts the validators need."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    name = path.stem  # e.g. "build-lead"
    spec = ParsedSpec(name=name, path=path, text=text, lines=lines)

    # --- Responsibilities --------------------------------------------------
    # Only the tables under "Responsibilities → Skills" (or the "Current
    # skills" / "Missing skills" / "Skills NOT in X's set" / "Recommended
    # skill additions" sections) count. The bash allowlist and routing
    # tables are explicitly excluded — they have a "Purpose" column that
    # would otherwise be misread as a responsibility.
    responsibility_sections: list[tuple[int, int, int]] = []
    responsibility_sections.extend(_offsets_for_heading(text, _RESPONSIBILITY_HEADING))
    responsibility_sections.extend(_offsets_for_heading(text, _SKILLS_HEADING))

    responsibility_headers = {"responsibility", "what it does", "purpose", "what it does."}
    skill_header_names = {"skill"}
    for header_line, _sep_line, headers, rows in find_tables(text):
        if not headers:
            continue
        # Find the table's character offset (start of the header line).
        header_offset = sum(len(line) + 1 for line in lines[: max(header_line - 1, 0)])
        in_responsibility_section = any(
            body_start <= header_offset < body_end
            for _, body_start, body_end in responsibility_sections
        )
        if not in_responsibility_section:
            continue
        lower_headers = [h.strip().lower() for h in headers]
        resp_idx = next(
            (i for i, h in enumerate(lower_headers) if h in responsibility_headers),
            None,
        )
        if resp_idx is None:
            continue
        skill_idx = next(
            (i for i, h in enumerate(lower_headers) if h in skill_header_names),
            None,
        )
        for row_index, row in enumerate(rows):
            if resp_idx >= len(row):
                continue
            text_cell = row[resp_idx].strip()
            if not text_cell:
                continue
            line_no = header_line + 2 + row_index + 1
            spec.responsibilities.append((line_no, text_cell))
            if skill_idx is not None and skill_idx < len(row):
                skill_cell = row[skill_idx].strip()
                skill_name = skill_cell.strip("`").strip()
                if skill_name and "-" in skill_name:
                    spec.declared_skills.add(skill_name)

    # --- Declared skills (broader scan) ------------------------------------
    # Some specs list their skills in a procedure table (e.g. the
    # "## 2 · The 4-Step Procedure" table in research-lead.md has columns
    # ``# | Step | Skill | Output``). That table is NOT under a
    # "Responsibilities → Skills" heading, so the previous block missed
    # it. Here we sweep every table in the file and pick up any column
    # whose header is "Skill" (case-insensitive). The bash allowlist and
    # routing tables do not have a "Skill" column, so the sweep is safe.
    for header_line, _sep_line, headers, rows in find_tables(text):
        lower_headers = [h.strip().lower() for h in headers]
        skill_idx = next(
            (i for i, h in enumerate(lower_headers) if h in skill_header_names),
            None,
        )
        if skill_idx is None:
            continue
        for row in rows:
            if skill_idx >= len(row):
                continue
            cell = row[skill_idx].strip()
            for skill_name in _split_skill_cell(cell):
                spec.declared_skills.add(skill_name)

    # --- Delegations --------------------------------------------------------
    # 1) Tables with a "Delegate" / "From" / "To" / "Subagent" first column
    #    inside a heading that looks like a delegation section.
    delegation_sections = _section_offsets(text, _DELEGATION_HEADINGS)
    for header_line, _sep_line, headers, rows in find_tables(text):
        if not _is_delegation_table(headers):
            continue
        # Translate the table's 1-based header line to a character offset and
        # ask whether any delegation section covers it. This keeps the bash
        # allowlist ("Pattern | Purpose") and routing tables ("Intent |
        # Delegate to") out of the delegation check, the same way the
        # responsibility check keeps those tables out of the overlap check.
        header_offset = sum(len(line) + 1 for line in lines[: max(header_line - 1, 0)])
        in_section = any(
            body_start <= header_offset < body_end
            for _, body_start, body_end in delegation_sections
        )
        if not in_section:
            continue
        for row_index, row in enumerate(rows):
            if not row:
                continue
            cell = row[0]
            agent = _extract_agent_from_cell(cell)
            if agent is None:
                continue
            line_no = header_line + 2 + row_index + 1
            spec.delegations.append((line_no, agent))

    # 2) Per-delegate sub-headings like ``#### build-lead (L2 primary)`` —
    #    common in the project-lead and planning-lead Delegation Maps.
    for match in _DELEGATE_SUBHEADING.finditer(text):
        agent = match.group(1)
        line = text.count("\n", 0, match.start()) + 1
        spec.delegations.append((line, agent))

    # 3) Prose mentions: `` `agent` (L<level>) `` — used in escalation
    #    tables and use-case bodies.
    for match in _PROSE_DELEGATE.finditer(text):
        agent = match.group(1)
        line = text.count("\n", 0, match.start()) + 1
        spec.delegations.append((line, agent))

    # Deduplicate delegations while preserving the first occurrence.
    seen: set[tuple[int, str]] = set()
    deduped: list[tuple[int, str]] = []
    for line, agent in spec.delegations:
        key = (line, agent)
        if key in seen:
            continue
        seen.add(key)
        deduped.append((line, agent))
    spec.delegations = deduped

    # --- Skill references (body tokens, not just skill tables) ------------
    # Tokens that are KNOWN agent names (the lead / leaf / future roster)
    # are filtered out — they are agent names, not skills. Tokens that
    # appear in this spec's delegation list are also filtered out — they
    # are already covered by the orphan check, and we don't want a typo'd
    # delegate to produce both an orphan and an unresolved-skill finding
    # for the same line.
    delegation_agents = {agent for _, agent in spec.delegations}
    for token, line in extract_skill_tokens(text):
        if is_agent_name(token):
            continue
        if token in delegation_agents:
            continue
        spec.skill_refs.append((line, token))
    # Deduplicate.
    seen_skills: set[tuple[int, str]] = set()
    deduped_skills: list[tuple[int, str]] = []
    for line, token in spec.skill_refs:
        key = (line, token)
        if key in seen_skills:
            continue
        seen_skills.add(key)
        deduped_skills.append((line, token))
    spec.skill_refs = deduped_skills

    # --- [NEEDS CLARIFICATION] markers -------------------------------------
    # A real unresolved marker is ``[NEEDS CLARIFICATION: <question>...]`` —
    # it carries the actual question after the colon. Bare mentions like
    # ``[NEEDS CLARIFICATION]`` in prose (rule descriptions, audit checklists)
    # are NOT flagged: they refer to the rule, they are not the rule broken.
    # Pattern: a colon followed by at least one non-bracket character before
    # the closing bracket. Anything without that question text is treated as
    # a description, not a marker.
    for match in re.finditer(r"\[NEEDS CLARIFICATION:\s+[^\]]{2,}\]", text):
        line = text.count("\n", 0, match.start()) + 1
        spec.clarifications.append((line, match.group(0)))

    return spec


def _split_skill_cell(cell: str) -> list[str]:
    """Split a skill cell that may contain multiple skills into a list.

    Skill cells in the F-016 specs take three forms:
      1. `` `foo-bar` `` — single skill
      2. `` `foo-bar`, `baz-qux` `` — comma-separated list
      3. `` `foo-bar` + `baz-qux` `` — plus-joined (e.g. "step 3 uses
         root-cause-analysis AND context-ladder")
    We strip backticks and split on the joiners. Cells that do not look
    like skill names (no hyphen) are dropped — they are likely fragments
    of prose the parser picked up by accident.
    """
    text = cell.replace("`", "")
    parts = re.split(r"\s*\+\s*|\s*,\s*", text)
    out: list[str] = []
    for part in parts:
        name = part.strip()
        if name and "-" in name and re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
            out.append(name)
    return out


# ---------------------------------------------------------------------------
# Skill registry
# ---------------------------------------------------------------------------


def build_skill_registry(specs: list[ParsedSpec]) -> frozenset[str]:
    """Return the union of all skill names known to the corpus.

    Sources, in priority order:
      1. The static ``BOOTSTRAP_SKILLS`` — skills that live in the catalog
         or skill folder rather than in the in-scope specs.
      2. ``spec.declared_skills`` — every skill that appears in a
         ``Responsibilities → Skills`` / ``Current skills`` /
         ``Missing skills`` / ``Recommended skill additions`` table of
         any in-scope spec. These are the SKILLS the specs CLAIM; tokens
         that appear only in body prose are NOT included here, so a body
         mention of an unknown token will still surface as an unresolved
         skill.

    The registry deliberately does NOT include body-only tokens. If it
    did, typos like ``this-is-a-typpo`` would register themselves just by
    being mentioned, defeating the unresolved-skill check.
    """
    skills: set[str] = set(BOOTSTRAP_SKILLS)
    for spec in specs:
        skills.update(spec.declared_skills)
    return frozenset(skills)


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

# Threshold for "near-match" responsibility overlap. A pair of responsibilities
# with SequenceMatcher ratio above this counts as an overlap. 0.72 catches
# rewrites ("Validate a system change" vs "Validate the change") without
# screaming on every shared word.
_OVERLAP_THRESHOLD = 0.72


def _normalise(text: str) -> str:
    """Lowercase + collapse whitespace + strip leading bullets/dashes."""
    text = text.lower()
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -:.")


def check_responsibility_overlap(specs: list[ParsedSpec]) -> list[Finding]:
    """Flag pairs of responsibilities (across specs) that are very similar."""
    findings: list[Finding] = []
    flat: list[tuple[ParsedSpec, int, str, str]] = []
    for spec in specs:
        for line, text in spec.responsibilities:
            flat.append((spec, line, text, _normalise(text)))
    n = len(flat)
    for i in range(n):
        spec_a, line_a, text_a, norm_a = flat[i]
        if not norm_a:
            continue
        for j in range(i + 1, n):
            spec_b, line_b, text_b, norm_b = flat[j]
            if spec_a.name == spec_b.name:
                continue  # overlap within the same spec is normal
            if not norm_b:
                continue
            # Exact match.
            if norm_a == norm_b:
                findings.append(
                    Finding(
                        file_path=spec_b.path.name,
                        line=line_b,
                        severity=SEVERITY_MEDIUM,
                        check="overlap",
                        message=(
                            f"responsibility duplicates {spec_a.path.name}:{line_a} — "
                            f"both claim: {text_a!r}"
                        ),
                    )
                )
                continue
            # Near-match.
            ratio = SequenceMatcher(None, norm_a, norm_b).ratio()
            if ratio >= _OVERLAP_THRESHOLD:
                findings.append(
                    Finding(
                        file_path=spec_b.path.name,
                        line=line_b,
                        severity=SEVERITY_LOW,
                        check="overlap",
                        message=(
                            f"responsibility near-duplicates "
                            f"{spec_a.path.name}:{line_a} (similarity {ratio:.2f}) — "
                            f"{text_a!r} vs {text_b!r}"
                        ),
                    )
                )
    return findings


def check_delegation_edges(specs: list[ParsedSpec]) -> list[Finding]:
    """Flag delegation edges that point to an agent outside KNOWN_AGENTS."""
    findings: list[Finding] = []
    for spec in specs:
        for line, agent in spec.delegations:
            if agent in KNOWN_AGENTS:
                continue
            findings.append(
                Finding(
                    file_path=spec.path.name,
                    line=line,
                    severity=SEVERITY_HIGH,
                    check="orphan",
                    message=(
                        f"delegation edge points to unknown agent {agent!r} — "
                        f"add it to LEAD_AGENTS, LEAF_AGENTS, or FUTURE_AGENTS in this script"
                    ),
                )
            )
    return findings


def check_skill_resolution(
    specs: list[ParsedSpec], registry: frozenset[str]
) -> list[Finding]:
    """Flag skill references that the registry does not know about."""
    findings: list[Finding] = []
    for spec in specs:
        for line, token in spec.skill_refs:
            if token in registry:
                continue
            findings.append(
                Finding(
                    file_path=spec.path.name,
                    line=line,
                    severity=SEVERITY_LOW,
                    check="unresolved-skill",
                    message=(
                        f"skill {token!r} is referenced but never defined in any "
                        f"in-scope spec — add to a Skills table or to BOOTSTRAP_SKILLS"
                    ),
                )
            )
    return findings


def check_clarification_markers(specs: list[ParsedSpec]) -> list[Finding]:
    """Flag any ``[NEEDS CLARIFICATION]`` marker left in a spec."""
    findings: list[Finding] = []
    for spec in specs:
        for line, marker in spec.clarifications:
            findings.append(
                Finding(
                    file_path=spec.path.name,
                    line=line,
                    severity=SEVERITY_HIGH,
                    check="clarification",
                    message=f"unresolved {marker!r} — must be answered or removed before sign-off",
                )
            )
    return findings


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def render_findings(findings: list[Finding]) -> str:
    """Render findings in the ``FILE:LINE: SEVERITY: check: message`` format."""
    if not findings:
        return "  (no findings)"
    lines = [f"  {f.render()}" for f in findings]
    return "\n".join(lines)


def summarise(findings: list[Finding]) -> str:
    """Render the ``N findings (X HIGH, Y MEDIUM, Z LOW, W INFO)`` line."""
    by_sev: dict[str, int] = {
        SEVERITY_HIGH: 0,
        SEVERITY_MEDIUM: 0,
        SEVERITY_LOW: 0,
        SEVERITY_INFO: 0,
    }
    for f in findings:
        by_sev[f.severity] = by_sev.get(f.severity, 0) + 1
    return (
        f"{len(findings)} findings "
        f"({by_sev[SEVERITY_HIGH]} HIGH, "
        f"{by_sev[SEVERITY_MEDIUM]} MEDIUM, "
        f"{by_sev[SEVERITY_LOW]} LOW, "
        f"{by_sev[SEVERITY_INFO]} INFO)"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments. See module docstring for usage examples."""
    parser = argparse.ArgumentParser(
        prog="cross_ref_agents.py",
        description=(
            "Validate cross-agent consistency of F-016 reference specs. "
            "Catches overlapping responsibilities, orphaned delegation edges, "
            "unresolved skill references, and unresolved "
            "[NEEDS CLARIFICATION] markers."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 .aspis/scripts/planning/cross_ref_agents.py --scope leads\n"
            "  python3 .aspis/scripts/planning/cross_ref_agents.py --scope all\n"
            "  python3 .aspis/scripts/planning/cross_ref_agents.py "
            "--scope build-lead,fix-lead\n"
        ),
    )
    parser.add_argument(
        "--scope",
        default="leads",
        help=(
            "Which specs to validate. 'leads' (default) reads the 8 lead "
            "specs only. 'all' also reads the 3 leaf specs "
            "(committer, general-builder, project-explorer) if they exist. "
            "A comma-separated list of names reads just those specs "
            "(e.g. 'build-lead,fix-lead')."
        ),
    )
    parser.add_argument(
        "--ref-dir",
        default=None,
        help=(
            "Path to the ref/ folder. Defaults to "
            "<repo>/.aspis/features/F-016-agent-system-architecture/Research/ref/. "
            "Use this to point at a different feature's specs."
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-finding output; print only the summary line.",
    )
    return parser.parse_args(argv)


def default_ref_dir(script_path: Path) -> Path:
    """Resolve the default ref/ folder relative to *script_path*."""
    # <repo>/.aspis/scripts/planning/cross_ref_agents.py
    # -> <repo>/.aspis/features/F-016-agent-system-architecture/Research/ref/
    return (
        script_path.resolve().parent.parent.parent
        / "features"
        / "F-016-agent-system-architecture"
        / "Research"
        / "ref"
    )


def resolve_specs(ref_dir: Path, scope: str) -> list[Path]:
    """Map a --scope value to the list of spec files to read."""
    if scope == "leads":
        wanted = list(LEAD_AGENTS)
    elif scope == "all":
        wanted = list(LEAD_AGENTS) + list(LEAF_AGENTS)
    else:
        wanted = [name.strip() for name in scope.split(",") if name.strip()]
    found: list[Path] = []
    missing: list[str] = []
    for name in wanted:
        path = ref_dir / f"{name}.md"
        if path.is_file():
            found.append(path)
        else:
            missing.append(name)
    return found, missing, wanted


def main(argv: list[str] | None = None) -> int:
    """CLI entry point — returns the process exit code (0 or 1)."""
    args = parse_args(argv)

    # UTF-8 stdio so we can print arrows / box-drawing chars on Windows
    # consoles that default to cp1252.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass

    script_path = Path(__file__).resolve()
    ref_dir = (
        Path(args.ref_dir).resolve()
        if args.ref_dir
        else default_ref_dir(script_path)
    )
    if not ref_dir.is_dir():
        print(f"error: ref directory not found: {ref_dir}", file=sys.stderr)
        return 1

    spec_paths, missing, wanted = resolve_specs(ref_dir, args.scope)
    print(f"cross_ref_agents.py — scope: {args.scope}")
    print(f"  ref dir: {ref_dir}")
    print(f"  specs requested: {len(wanted)} | found: {len(spec_paths)} | missing: {len(missing)}")
    if missing:
        print(f"  missing specs (skipped): {', '.join(missing)}")
    if not spec_paths:
        print("error: no spec files resolved", file=sys.stderr)
        return 1

    specs = [parse_spec(path) for path in sorted(spec_paths)]
    print(f"  loaded {len(specs)} spec(s): {', '.join(s.name for s in specs)}")

    # Build the skill registry from the loaded specs.
    skill_registry = build_skill_registry(specs)
    print(f"  skill registry: {len(skill_registry)} skill(s) known")

    # Run the four checks in order. The order is stable so the output of a
    # second run is diff-able against the first.
    print("")
    print("Check 1: responsibility overlap")
    overlap = check_responsibility_overlap(specs)
    if not args.quiet:
        print(render_findings(overlap))

    print("")
    print("Check 2: orphaned delegation edges")
    orphans = check_delegation_edges(specs)
    if not args.quiet:
        print(render_findings(orphans))

    print("")
    print("Check 3: unresolved skill references")
    unresolved = check_skill_resolution(specs, skill_registry)
    if not args.quiet:
        print(render_findings(unresolved))

    print("")
    print("Check 4: [NEEDS CLARIFICATION] markers")
    clarifications = check_clarification_markers(specs)
    if not args.quiet:
        print(render_findings(clarifications))

    all_findings = overlap + orphans + unresolved + clarifications
    failing = [f for f in all_findings if f.severity in FAILING_SEVERITIES]
    print("")
    print(f"summary: {summarise(all_findings)}")
    if not failing:
        print("verdict: PASS (no HIGH or MEDIUM findings)")
        return 0
    print(f"verdict: FAIL ({len(failing)} finding(s) at HIGH or MEDIUM severity)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
