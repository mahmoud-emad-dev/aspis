"""``aspis governance`` — the R-008 human-gate ledger.

Why: protected paths (system rules, runtime config, agent permissions, ...) cannot
be edited by an automated agent without a human's signed approval (R-008 — Human
gate, see :file:`.aspis/rules/system-rules.md`). This CLI keeps an append-only YAML
ledger at ``.aspis/state/approval-ledger.yaml`` of every approval ever issued, and
offers read-only diagnostics so an agent can ask *before* it writes: "would this
write be allowed right now?".

Subcommands (all five plus one diagnostic):

- ``request``  — declare intent to write a protected path; prints the exact
  ``approve`` command the human should run. Does NOT modify the ledger.
- ``approve``  — record a human approval (the R-008 gate). Appends a new entry.
- ``audit``    — query the ledger by time / approver / path glob.
- ``revoke``   — flip a prior approval to ``revoked``. Append-only: the original
  entry is mutated in place (status + ``revocation`` block) — nothing is deleted.
- ``ledger``   — read-only health summary: path, entry count, oldest/newest stamps.
- ``check``    — diagnostic: would a write to ``--path`` be allowed right now?

Exit codes follow governance.md §6: 0 = ok, 2 = validation error, 3 = not found
or already revoked, 4 = blocked by gate, 5 = path not protected.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Append-only ledger location. Created on first write. NEVER hand-edit.
LEDGER_REL = Path(".aspis/state/approval-ledger.yaml")

#: Sidecar lock file. Held only during read-modify-write of the ledger.
LOCK_REL = Path(".aspis/state/approval-ledger.lock")

#: A lock older than this is considered stale and may be broken by the next writer.
LOCK_STALE_SECONDS = 60

#: Canonical set of protected glob patterns. A path is protected iff it matches
#: ANY pattern here. Source: governance.md §3 (single source of truth for R-008).
PROTECTED_PATHS: list[str] = [
    "rules/**",
    ".aspis/rules/**",
    ".aspis/config/hooks.yaml",
    ".aspis/config/modes.yaml",
    ".aspis/config/constitution-checks.yaml",
    ".aspis/config/capabilities.yaml",
    ".aspis/config/agent-capabilities.yaml",
    ".aspis/config/commit-convention.yaml",
    "profiles/defaults.yaml",
    ".opencode/agents/**",
    ".claude/agents/**",
    ".claude/settings.json",
    "**/permissions*.yaml",
    ".aspis/current/active_feature.json",
]

#: Regex metacharacters that need escaping in a glob fragment.
_REGEX_META = ".^$+(){}[]|\\"

# ---------------------------------------------------------------------------
# Path matching
# ---------------------------------------------------------------------------


def _normalize(path: str) -> str:
    """Return ``path`` with POSIX separators — portable for glob matching."""
    return str(path).replace("\\", "/")


def _build_glob_body(pattern: str) -> str:
    """Convert a glob fragment to a regex body (no anchors).

    - ``**`` matches zero or more chars, including ``/`` (any depth).
    - ``*``  matches zero or more chars in a single segment (no ``/``).
    - ``?``  matches exactly one char in a single segment (no ``/``).
    - All other regex metacharacters are escaped.
    """
    i = 0
    n = len(pattern)
    out: list[str] = []
    while i < n:
        c = pattern[i]
        if c == "*":
            if i + 1 < n and pattern[i + 1] == "*":
                out.append(".*")
                i += 2
            else:
                out.append("[^/]*")
                i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        elif c in _REGEX_META:
            out.append("\\" + c)
            i += 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _glob_to_regex(pattern: str) -> str:
    """Convert a glob pattern to an anchored, compiled regex source string.

    A leading ``**/`` is treated as "any depth, including the root" so
    ``**/foo`` matches ``foo``, ``a/foo``, and ``a/b/foo``. Without this
    special-case, ``**/foo`` would only match paths under at least one segment.

    The built-in :py:meth:`pathlib.PurePath.match` is unsuitable for this: its
    right-anchored ``**`` does not match a leaf file at any depth, and its
    left-anchored ``**/`` does not match the root.
    """
    if pattern.startswith("**/"):
        return "^(?:.*/)?" + _build_glob_body(pattern[3:]) + "$"
    return "^" + _build_glob_body(pattern) + "$"


def _matches(candidate: str, pattern: str) -> bool:
    """Return True if ``candidate`` (POSIX) matches the glob ``pattern``."""
    return bool(re.match(_glob_to_regex(pattern), _normalize(candidate)))


def is_protected(path: str, patterns: list[str] | None = None) -> bool:
    """Return True if ``path`` matches any pattern in the protected set.

    Public so an editor / hook can ask the same question without re-implementing
    the matching rules.
    """
    pats = patterns if patterns is not None else PROTECTED_PATHS
    return any(_matches(path, p) for p in pats)

# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------


def _now_utc() -> datetime:
    """Timezone-aware UTC ``datetime`` — used for ``expiry`` comparisons."""
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    """ISO 8601 UTC stamp, ``...Z`` form — the format written to the ledger."""
    return _now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(value: str | None) -> datetime | None:
    """Parse a permissive ISO 8601 / ``...Z`` timestamp; return None on failure."""
    if not value:
        return None
    s = str(value).strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _is_expired(entry: dict[str, Any], now: datetime) -> bool:
    """True if the entry's ``expiry`` is in the past (or equals now)."""
    expiry = entry.get("expiry")
    if not expiry:
        return False
    exp = _parse_iso(str(expiry))
    if exp is None:
        return False
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    return exp <= now

# ---------------------------------------------------------------------------
# Ledger I/O
# ---------------------------------------------------------------------------


def _read_ledger(ledger: Path) -> list[dict[str, Any]]:
    """Read the ledger; return ``[]`` if absent or unreadable."""
    if not ledger.is_file():
        return []
    try:
        data = yaml.safe_load(ledger.read_text(encoding="utf-8")) or {}
    except (yaml.YAMLError, OSError) as exc:
        print(f"[warn] could not read {ledger}: {exc}", file=sys.stderr)
        return []
    entries = data.get("entries", [])
    return entries if isinstance(entries, list) else []


def _write_ledger(ledger: Path, entries: list[dict[str, Any]]) -> None:
    """Write the ledger atomically: build in a sibling ``.tmp``, then replace."""
    ledger.parent.mkdir(parents=True, exist_ok=True)
    payload = yaml.dump(
        {"entries": entries},
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )
    tmp = ledger.with_suffix(ledger.suffix + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, ledger)


def _next_id(entries: list[dict[str, Any]]) -> str:
    """Monotonic, zero-padded ID — the next entry is the existing count + 1."""
    return f"APRV-{len(entries) + 1:03d}"


class _LockError(RuntimeError):
    """Raised when the ledger lock is held by another writer."""


def _acquire_lock(lock: Path) -> None:
    """Create the lock file atomically. Stale (>60s) locks are broken first.

    Raises :class:`_LockError` if a fresh lock is already held.
    """
    lock.parent.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            # Check staleness — a crashed writer may have left a lock behind.
            try:
                age = _now_utc().timestamp() - lock.stat().st_mtime
            except OSError:
                age = 0
            if age > LOCK_STALE_SECONDS:
                try:
                    lock.unlink()
                except FileNotFoundError:
                    pass
                except OSError as exc:
                    raise _LockError(f"could not break stale lock {lock}: {exc}") from exc
                # Loop and try to re-acquire.
                continue
            raise _LockError(
                f"ledger is locked ({lock}, age={int(age)}s); another writer is active"
            ) from None
        else:
            os.write(fd, _now_iso().encode("utf-8"))
            os.close(fd)
            return


def _release_lock(lock: Path) -> None:
    """Remove the lock file, swallowing ``FileNotFoundError`` (already gone)."""
    try:
        lock.unlink()
    except FileNotFoundError:
        pass
    except OSError as exc:
        print(f"[warn] could not remove lock {lock}: {exc}", file=sys.stderr)


def _entry_covers(entry: dict[str, Any], path: str) -> bool:
    """Return True if ``entry``'s approved scope covers the (POSIX) ``path``."""
    scope = entry.get("scope") or {}
    for approved in scope.get("paths") or []:
        approved_s = str(approved)
        # Both directions — the approved pattern may be a glob OR a literal.
        if _matches(path, approved_s) or _matches(approved_s, path):
            return True
    return False


def _find_active_approval(
    entries: list[dict[str, Any]], path: str, now: datetime
) -> dict[str, Any] | None:
    """First active (non-revoked, non-expired) entry that covers ``path``."""
    for entry in entries:
        if entry.get("status") != "active":
            continue
        if _is_expired(entry, now):
            continue
        if _entry_covers(entry, path):
            return entry
    return None

# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------


def _request(args: argparse.Namespace) -> int:
    """Print the exact ``approve`` command a human should run; do not touch the ledger."""
    paths = list(args.paths or [])
    if not paths:
        print("request needs at least one --path", file=sys.stderr)
        return 2
    quoted = " ".join(p if " " not in p else f'"{p}"' for p in paths)
    reason = (args.reason or "").strip() or "<reason>"
    print("To write the protected path(s), a human must run:\n")
    print(
        f"  aspis governance approve --paths {quoted} \\\n"
        f"      --reason \"{reason}\" \\\n"
        f"      --approver <human-identity-handle>"
    )
    return 0


def _approve(args: argparse.Namespace) -> int:
    """Record a human approval; appends a new ledger entry. R-008 requires ``--approver``."""
    if not args.paths:
        print("approve needs at least one --paths entry", file=sys.stderr)
        return 2
    if not args.approver or not args.approver.strip():
        print("approve requires --approver (R-008 Human gate)", file=sys.stderr)
        return 2
    if not args.reason or not args.reason.strip():
        print("approve requires a non-empty --reason", file=sys.stderr)
        return 2
    if args.expiry and _parse_iso(args.expiry) is None:
        print(f"approve --expiry must be ISO 8601 (got {args.expiry!r})", file=sys.stderr)
        return 2

    if args.glob_approval:
        # Per the spec: warn but do not block — the CLI flag is the confirmation.
        print(
            "[warn] --glob-approval is DANGEROUS: the approval will match any path "
            "under the given glob. Confirm this is intentional.",
            file=sys.stderr,
        )

    ledger = Path.cwd() / LEDGER_REL
    lock = Path.cwd() / LOCK_REL
    try:
        _acquire_lock(lock)
    except _LockError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    try:
        entries = _read_ledger(ledger)
        entry: dict[str, Any] = {
            "id": _next_id(entries),
            "timestamp": _now_iso(),
            "approver": args.approver.strip(),
            "scope": {
                "paths": [_normalize(p) for p in args.paths],
                "reason": args.reason,
            },
            "expiry": args.expiry,
            "status": "active",
            "glob_approval": bool(args.glob_approval),
            "applied": [],
            "revocation": {
                "revoked_at": None,
                "revoked_by": None,
                "reason": None,
            },
        }
        entries.append(entry)
        _write_ledger(ledger, entries)
    finally:
        _release_lock(lock)

    print(
        f"approved: {entry['id']} by {entry['approver']} "
        f"({len(entry['scope']['paths'])} path(s), status=active)"
    )
    return 0


def _audit(args: argparse.Namespace) -> int:
    """Read the ledger, apply filters, and print matching entries. Exit 0 always."""
    ledger = Path.cwd() / LEDGER_REL
    entries = _read_ledger(ledger)

    if args.since:
        cutoff = _parse_iso(args.since)
        if cutoff is None:
            print(f"audit --since must be ISO 8601 (got {args.since!r})", file=sys.stderr)
            return 2
        if cutoff.tzinfo is None:
            cutoff = cutoff.replace(tzinfo=timezone.utc)
        entries = [
            e for e in entries
            if (lambda ts: ts is not None and ts >= cutoff)(_parse_iso(str(e.get("timestamp", ""))))
        ]

    if getattr(args, "until", None):
        cutoff = _parse_iso(args.until)
        if cutoff is None:
            print(f"audit --until must be ISO 8601 (got {args.until!r})", file=sys.stderr)
            return 2
        if cutoff.tzinfo is None:
            cutoff = cutoff.replace(tzinfo=timezone.utc)
        entries = [
            e for e in entries
            if (lambda ts: ts is not None and ts <= cutoff)(_parse_iso(str(e.get("timestamp", ""))))
        ]

    if args.approver:
        want = args.approver.strip()
        entries = [e for e in entries if e.get("approver") == want]

    if getattr(args, "status", None):
        now = _now_utc()

        def _status_of(e: dict) -> str:
            if e.get("status") == "revoked":
                return "revoked"
            exp = _parse_iso(str(e.get("expiry") or ""))
            if exp is not None:
                if exp.tzinfo is None:
                    exp = exp.replace(tzinfo=timezone.utc)
                if exp < now:
                    return "expired"
            return "active"

        entries = [e for e in entries if _status_of(e) == args.status]

    if getattr(args, "path_filters", None):
        filters = [_normalize(p) for p in args.path_filters]
        entries = [
            e for e in entries
            if any(_matches(p, fp) or _matches(fp, p)
                   for p in (e.get("scope") or {}).get("paths") or []
                   for fp in filters)
        ]

    if not entries:
        print("(no matching entries)")
        return 0

    for e in entries:
        eid = e.get("id", "?")
        ts = e.get("timestamp", "?")
        apv = e.get("approver", "?")
        st = e.get("status", "?")
        scope = e.get("scope") or {}
        paths = scope.get("paths") or []
        print(f"  {eid}  {ts}  {apv}  [{st}]  {', '.join(paths)}")
    print(f"\n{len(entries)} matching entr{'y' if len(entries) == 1 else 'ies'}.")
    return 0


def _revoke(args: argparse.Namespace) -> int:
    """Flip a prior approval to ``revoked`` (append-only, in-place state change)."""
    if not args.id or not args.id.strip():
        print("revoke needs --id (e.g. APRV-001)", file=sys.stderr)
        return 2
    if not args.reason or not args.reason.strip():
        print("revoke requires a non-empty --reason", file=sys.stderr)
        return 2

    target_id = args.id.strip()
    ledger = Path.cwd() / LEDGER_REL
    lock = Path.cwd() / LOCK_REL
    try:
        _acquire_lock(lock)
    except _LockError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    try:
        entries = _read_ledger(ledger)
        for entry in entries:
            if entry.get("id") == target_id:
                if entry.get("status") == "revoked":
                    print(f"already revoked: {target_id}", file=sys.stderr)
                    return 3
                # --approver optional: default to the original approver (spec §6).
                revoker = (
                    args.approver.strip()
                    if args.approver and args.approver.strip()
                    else entry.get("approver", "unknown")
                )
                entry["status"] = "revoked"
                entry["revocation"] = {
                    "revoked_at": _now_iso(),
                    "revoked_by": revoker,
                    "reason": args.reason,
                }
                _write_ledger(ledger, entries)
                print(f"revoked: {target_id} by {revoker}")
                return 0
        print(f"not found: {target_id}", file=sys.stderr)
        return 3
    finally:
        _release_lock(lock)


def _ledger(args: argparse.Namespace) -> int:
    """Print ledger health: path, entry count, oldest / newest timestamps."""
    ledger = Path.cwd() / LEDGER_REL
    entries = _read_ledger(ledger)
    print(f"path:   {ledger}")
    print(f"exists: {ledger.is_file()}")
    print(f"count:  {len(entries)}")
    if entries:
        stamps = sorted(
            (str(e.get("timestamp") or "") for e in entries),
        )
        # ``sorted`` is lexicographic; ISO 8601 is sortable as a string.
        print(f"oldest: {stamps[0]}")
        print(f"newest: {stamps[-1]}")
        active = sum(1 for e in entries if e.get("status") == "active")
        revoked = sum(1 for e in entries if e.get("status") == "revoked")
        print(f"active:  {active}")
        print(f"revoked: {revoked}")
    return 0


def _check(args: argparse.Namespace) -> int:
    """Diagnostic: would a write to ``--path`` be allowed right now?

    Exit codes: 0 = allowed, 4 = blocked (no active approval), 5 = not protected.
    """
    path = args.path
    if not path:
        print("check needs --path", file=sys.stderr)
        return 2
    if not is_protected(path):
        print(f"not protected: {path}")
        return 5

    ledger = Path.cwd() / LEDGER_REL
    entries = _read_ledger(ledger)
    approval = _find_active_approval(entries, _normalize(path), _now_utc())
    if approval is None:
        print(f"blocked: {path} is protected and has no active approval.")
        print(f"  run: aspis governance request --path {path} --reason <why>")
        return 4

    print(
        f"allowed: {path} — approval {approval.get('id')} by "
        f"{approval.get('approver')} at {approval.get('timestamp')}"
    )
    return 0

# ---------------------------------------------------------------------------
# Parser registration
# ---------------------------------------------------------------------------


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``governance`` verb on the top-level subparsers action."""
    parser = subparsers.add_parser(
        "governance",
        help="R-008 human gate: approve, audit, check protected-path writes.",
    )
    sub = parser.add_subparsers(dest="gov_command", metavar="<subcommand>")

    # request
    req = sub.add_parser("request", help="Declare intent to write a protected path.")
    req.add_argument(
        "--path", dest="paths", required=True, action="append",
        help="Protected path(s) you intend to write (repeatable).",
    )
    req.add_argument("--reason", help="Human-readable reason for the write (optional).")
    req.set_defaults(func=_request)

    # approve
    app = sub.add_parser("approve", help="Record a human approval (R-008 gate).")
    app.add_argument(
        "--paths", required=True, nargs="+",
        help="Exact paths being approved (space-separated).",
    )
    app.add_argument("--reason", required=True, help="Human-readable justification.")
    app.add_argument(
        "--approver", required=True,
        help="Human's identity handle (REQUIRED — R-008 gate).",
    )
    app.add_argument("--expiry", help="ISO 8601 UTC expiry (default: permanent).")
    app.add_argument(
        "--glob-approval", action="store_true",
        help="Allow glob patterns in --paths (DANGEROUS — prints a warning).",
    )
    app.set_defaults(func=_approve)

    # audit
    aud = sub.add_parser("audit", help="Query the approval ledger.")
    aud.add_argument("--since", help="ISO 8601 filter: at/after this timestamp.")
    aud.add_argument("--until", help="ISO 8601 filter: at/before this timestamp.")
    aud.add_argument("--approver", help="Filter by approver handle.")
    aud.add_argument(
        "--status", choices=("active", "revoked", "expired"),
        help="Filter by entry status.",
    )
    aud.add_argument(
        "--path", action="append", dest="path_filters",
        help="Filter by path glob (repeatable).",
    )
    aud.set_defaults(func=_audit)

    # revoke
    rev = sub.add_parser("revoke", help="Revoke a prior approval (append-only).")
    rev.add_argument("--id", required=True, help="APRV-NNN to revoke.")
    rev.add_argument("--reason", required=True, help="Why this approval is being revoked.")
    rev.add_argument(
        "--approver",
        help="Who is revoking (optional — defaults to the original approver).",
    )
    rev.set_defaults(func=_revoke)

    # ledger
    led = sub.add_parser("ledger", help="Show ledger health + entry count.")
    led.set_defaults(func=_ledger)

    # check
    chk = sub.add_parser("check", help="Diagnostic: would this write be allowed?")
    chk.add_argument("--path", required=True, help="Path to check.")
    chk.set_defaults(func=_check)
