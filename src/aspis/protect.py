"""Protect — content-hash-based per-file write decision engine.

Purpose:
    A pure 6-way hash-based decision engine for safe catalog export. Classify
    every export target by comparing three hashes (live, snapshot, regen) into
    one of 6 categories (ADD, UNCHANGED, UNKNOWN, UPDATE, PROTECT, CONFLICT).
    The caller decides what to do with each ``Decision`` — this module never
    touches the filesystem.

Responsibilities:
    - Define the ``DecisionKind`` enum and the ``Decision`` record.
    - Hash text (with BOM/CRLF normalization) and raw bytes via SHA-256.
    - Resolve a single (live, snapshot, regen) hash triple into a ``Decision``
      through a pure ordered truth table (``decide``).
    - Fan the decision out across a whole runtime (``plan_runtime``) and
      aggregate the results (``summary``).

Does Not:
    - Perform file I/O — callers compute the hashes and pass them in.
    - Know about runtimes, profiles, or asset kinds.
    - Make policy decisions (write/skip/refuse) — it only classifies.

Used By:
    src/aspis/export.py (the ``write_export`` function).
"""

from __future__ import annotations

import enum
import hashlib
from dataclasses import dataclass


class DecisionKind(enum.Enum):
    """The 6 mutually-exclusive outcomes of comparing three hashes."""

    ADD = "ADD"            # No live file exists.
    UNCHANGED = "UNCHANGED"  # Live hash == regen hash (file matches catalog).
    UNKNOWN = "UNKNOWN"    # Live exists, no snapshot entry (no history).
    UPDATE = "UPDATE"      # Live == snapshot (pristine) -> safe to overwrite.
    PROTECT = "PROTECT"    # Live != snapshot, regen == snapshot (user edited).
    CONFLICT = "CONFLICT"  # All three hashes differ (both user and catalog changed).


@dataclass(frozen=True)
class Decision:
    """The outcome of ``decide`` plus the three hashes that produced it.

    All hash fields are SHA-256 hex strings or ``None`` (when the corresponding
    input was absent). Carrying the inputs back out keeps the decision
    self-describing for audit logs and dry-run output without re-hashing.
    """

    kind: DecisionKind
    live_hash: str | None = None
    snapshot_hash: str | None = None
    regen_hash: str | None = None


def sha256_text(text: str) -> str:
    """SHA-256 hex digest after stripping a leading UTF-8 BOM and normalizing CRLF->LF.

    Normalization prevents false PROTECT decisions from editor-added BOMs and
    Windows/Linux line-ending differences: the same logical content hashes the
    same regardless of how it was serialized. A bare CR (``\\r`` not followed by
    ``\\n``) is intentionally *not* normalized — only the CRLF pair is.
    """
    if text.startswith("\ufeff"):
        text = text[1:]
    text = text.replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    """SHA-256 hex digest of raw bytes with no normalization.

    For binary files (images, etc.) where any byte-level transformation would
    corrupt the content. The digest is over the exact bytes passed in.
    """
    return hashlib.sha256(data).hexdigest()


def decide(
    live_hash: str | None,
    snapshot_hash: str | None,
    regen_hash: str | None,
) -> Decision:
    """Pure 6-case truth table. All parameters are hex strings or ``None``.

    Evaluated in order (first match wins):

    1. ``live_hash is None`` -> ADD (no live file).
    2. ``live_hash == regen_hash`` -> UNCHANGED (file matches catalog).
    3. ``snapshot_hash is None`` -> UNKNOWN (live exists, no history).
    4. ``live_hash == snapshot_hash`` -> UPDATE (pristine, safe to overwrite).
    5. ``regen_hash == snapshot_hash`` -> PROTECT (user edited, catalog unchanged).
    6. fallthrough -> CONFLICT (both user and catalog changed).

    The order matters: case 1 fires before case 3 (a missing live file is ADD
    even if a snapshot exists), and case 2 fires before case 3 (a live file that
    already matches the catalog is UNCHANGED even with no snapshot record).
    """
    # 1. No live file -> ADD.
    if live_hash is None:
        return Decision(DecisionKind.ADD, live_hash, snapshot_hash, regen_hash)
    # 2. Live matches what the catalog would produce -> UNCHANGED.
    if live_hash == regen_hash:
        return Decision(DecisionKind.UNCHANGED, live_hash, snapshot_hash, regen_hash)
    # 3. Live exists but no snapshot record -> UNKNOWN.
    if snapshot_hash is None:
        return Decision(DecisionKind.UNKNOWN, live_hash, snapshot_hash, regen_hash)
    # 4. Live matches snapshot (pristine) -> safe to UPDATE.
    if live_hash == snapshot_hash:
        return Decision(DecisionKind.UPDATE, live_hash, snapshot_hash, regen_hash)
    # 5. Catalog unchanged from snapshot, but live differs -> PROTECT user edit.
    if regen_hash == snapshot_hash:
        return Decision(DecisionKind.PROTECT, live_hash, snapshot_hash, regen_hash)
    # 6. All three differ -> CONFLICT.
    return Decision(DecisionKind.CONFLICT, live_hash, snapshot_hash, regen_hash)


def plan_runtime(
    snapshot: dict[str, str],
    live_hashes: dict[str, str | None],
    regen_hashes: dict[str, str],
) -> dict[str, Decision]:
    """Fan-out: call ``decide`` for every path in the union of the three dicts.

    A path present in the snapshot or regen but absent from ``live_hashes`` gets
    ``live_hash=None`` (-> ADD), which is exactly the "no live file" case. The
    result is keyed by the same path strings the caller supplied.
    """
    all_paths = set(snapshot) | set(live_hashes) | set(regen_hashes)
    return {
        path: decide(
            live_hashes.get(path),
            snapshot.get(path),
            regen_hashes.get(path),
        )
        for path in all_paths
    }


def summary(decisions: dict[str, Decision]) -> dict[DecisionKind, int]:
    """Aggregate counts by ``DecisionKind``.

    Returns all 6 keys (zero for any kind that did not occur) so callers can
    render a complete summary line without probing for missing keys.
    """
    counts = {kind: 0 for kind in DecisionKind}
    for decision in decisions.values():
        counts[decision.kind] += 1
    return counts