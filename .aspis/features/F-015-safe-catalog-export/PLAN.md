# F-015: Safe Catalog Export — Architecture Plan

**Feature:** F-015 — Exporter Hardening (Safe Catalog Export)
**Mode:** Production (full architecture, small tasks, independent review, full testing)
**Status:** Architecture (P3) — ready for task decomposition

---

## 1. Approach

Add a **content-hash-based protection engine** (`protect.py`) that decides per-file
whether to write, skip, or protect during export. The existing single-guard
(`destination.exists() and not force → skip`) is replaced by a **pure 6-way
decision function** that compares three hashes (live file, snapshot record, catalog
regeneration) and classifies every action as ADD / UNCHANGED / UNKNOWN / UPDATE /
PROTECT / CONFLICT. A JSON snapshot records what was last written; a JSON audit log
records every write decision. The `--force` flag keeps full backward compatibility.
The `models --apply` bug (hard-coded `force=True`) is fixed by routing through the
same decide flow.

The design follows the architecture constitution: a new module carries the
protection logic (Local Change), the decision function is runtime-agnostic (Plugin
First), and hash comparison is a deterministic function (Automation before
Intelligence). No staging area, no clobber classification, no per-runtime lock
files — all dead weight from the old repo is deliberately excluded.

---

## 2. Structure

### 2.1 New file: `src/aspis/protect.py` (pure protection engine)

```
src/aspis/protect.py          (~141 lines)  NEW
```

**Purpose:** Content-hash-based per-file write decision — pure data in, pure data
out. No file I/O, no diff computation, no runtime awareness.

**Module docstring requirement:** The module must carry a top docstring with
Purpose / Responsibilities / Does Not / Used By per the constitution's file rules.

**Public interface:**

```python
class DecisionKind(enum.Enum):
    ADD = "ADD"            # No live file exists
    UNCHANGED = "UNCHANGED"  # Live hash == regen hash
    UNKNOWN = "UNKNOWN"    # Live exists, no snapshot entry
    UPDATE = "UPDATE"      # Live == snapshot (pristine) → safe to overwrite
    PROTECT = "PROTECT"    # Live != snapshot, regen == snapshot (user edited,
                           #   catalog unchanged)
    CONFLICT = "CONFLICT"  # All three hashes differ

@dataclass(frozen=True)
class Decision:
    kind: DecisionKind
    live_hash: str | None = None
    snapshot_hash: str | None = None
    regen_hash: str | None = None

def sha256_text(text: str) -> str:
    """SHA-256 hex digest after stripping UTF-8 BOM and normalizing CRLF→LF."""
    if text.startswith("\ufeff"):
        text = text[1:]
    text = text.replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_bytes(data: bytes) -> str:
    """SHA-256 hex digest of raw bytes. No normalization. For binary files."""
    return hashlib.sha256(data).hexdigest()

def decide(
    live_hash: str | None,
    snapshot_hash: str | None,
    regen_hash: str | None,
) -> Decision:
    """Pure 6-case truth table. All parameters are hex strings or None."""

def plan_runtime(
    snapshot: dict[str, str],
    live_hashes: dict[str, str | None],
    regen_hashes: dict[str, str],
) -> dict[str, Decision]:
    """Fan-out: call decide() for every path in the union of keys."""

def summary(decisions: dict[str, Decision]) -> dict[DecisionKind, int]:
    """Aggregate counts by DecisionKind."""
```

**Decision table (evaluated in order):**

| # | Condition | DecisionKind | Action |
|---|---|---|---|
| 1 | `live_hash is None` | ADD | Write regen, record in snapshot |
| 2 | `live_hash == regen_hash` | UNCHANGED | Skip |
| 3 | `snapshot_hash is None` | UNKNOWN | Preserve live, record live_hash in snapshot |
| 4 | `live_hash == snapshot_hash` | UPDATE | Write regen, record in snapshot |
| 5 | `regen_hash == snapshot_hash` | PROTECT | Skip (protect live) |
| 6 | *(fallthrough)* | CONFLICT | Refuse without `--force-conflicts` |

**Key adaptation from old repo:**
- `UNTRACKED` renamed to `UNKNOWN` (clearer semantics: "we don't know the history")
- `sha256_text` strips UTF-8 BOM and normalizes CRLF→LF before hashing (prevents
  false PROTECT on Windows line-ending mismatch and on editor-added BOMs)
- `sha256_bytes` hashes raw bytes with no normalization, for binary files
- `decide()` is pure — no file I/O inside it (caller computes hashes)
- Snapshot keys are always `Path.as_posix()` — never use `str(path)` for the
  snapshot key

### 2.2 Changed file: `src/aspis/export.py`

```
src/aspis/export.py           (+120 lines, ~258 total)  CHANGED
```

**Changes to `write_export()`:**

New signature:
```python
def write_export(
    plan: ExportPlan,
    target_root: Path,
    *,
    force: bool = False,           # existing — bypass all protection
    write: bool = False,            # existing — perform writes (vs dry-run)
    apply: bool = False,            # NEW — alias for write in models context
    strict: bool = False,           # NEW — exit non-zero on CONFLICT
    scope: str | None = None,       # NEW — filter by catalog source path prefix
    force_conflicts: bool = False,  # NEW — overwrite on CONFLICT decisions
    reset_snapshot: bool = False,   # NEW — ignore corrupted snapshot
) -> list[str]:
```

**Flow (when `force=False`):**

0. **Acquire lock:** create `.aspis/current/export.lock` using
   `os.open(O_CREAT | O_EXCL | O_RDWR)`. If it exists, check if the PID is
   alive; if dead, allow takeover. Release lock on completion (delete the file).

1. **Load snapshot** from `{target_root}/.aspis/current/export-snapshot.json`
   - If absent → empty `{"version": 1, "paths": {}}`
   - If corrupted and not `reset_snapshot` → refuse with clear error
   - If corrupted and `reset_snapshot` → treat as empty

2. **Filter by scope** (if `scope is not None`):
   - Keep only actions where `action.target` starts with `scope` (target path = the
     project-relative path the file will be written to)

3. **For each action, compute three hashes:**
   - **regen_hash:** `sha256_text(source.read_text())` — what the catalog says
   - **live_hash:** `sha256_text(destination.read_text())` if destination exists,
     else `None`
   - **snapshot_hash:** from snapshot `paths[target_posix]` or `None`

4. **Call `protect.decide(live_hash, snapshot_hash, regen_hash)`**

5. **Dispatch per DecisionKind:**
   | Kind | Action |
   |---|---|
   | ADD | Write file, `snapshot[path] = regen_hash` |
   | UNCHANGED | Skip, log |
   | UNKNOWN | Preserve live, `snapshot[path] = live_hash` |
   | UPDATE | Write file, `snapshot[path] = regen_hash` |
   | PROTECT | Skip, log "protected (user-modified)" |
   | CONFLICT | Skip unless `force_conflicts`; log "conflict (both changed)" |

5a. **Runtime hook outputs (emit_runtime_hooks)** are also tracked in the
    snapshot. Every file `write_export` writes — whether from `plan.actions`
    or from `emit_runtime_hooks` — is protected by the same decide flow.

6. **After all actions:** Ensure `.aspis/current/` exists before writing:
   `path.parent.mkdir(parents=True, exist_ok=True)`. Then write snapshot
   **atomically** using `tempfile.mkstemp(dir=parent, suffix='.tmp')` +
   `os.fdopen` + `os.replace` (NOT `NamedTemporaryFile` — it holds the file
   open on Windows) to prevent partial writes from concurrent runs

7. **Append audit entries** to `{target_root}/.aspis/current/export-log.jsonl`
   (JSONL format — one JSON object per line, true append-only, O(1) per entry)

8. **When `force=True`:** skip the decide loop entirely — overwrite every
   destination (exact existing behavior preserved for backward compat)

9. **When `strict=True` and any CONFLICT:** raise a `ProtectionError`
   (caught by CLI → non-zero exit)

10. **Return:** list of performed action strings (existing format, extended with
    hash info in dry-run mode)

**Helper functions added to export.py:**

```python
def _load_snapshot(target_root: Path) -> dict:
    """Load export-snapshot.json or return empty. Raise on corruption
    unless reset_snapshot."""

def _save_snapshot(target_root: Path, snapshot: dict) -> None:
    """Atomic write: tempfile + os.replace."""

def _append_log(target_root: Path, entries: list[dict]) -> None:
    """Append entries to export-log.json."""

def _hash_file(path: Path) -> str | None:
    """sha256_text of file content, or None if file doesn't exist."""

def _regen_hash(source: Path, op: str) -> str:
    """Hash of what would be written: for copy ops, hash the source;
    for render ops, hash the rendered output."""
```

**No change to `plan_export()` or `_apply()`.** The core pipeline is untouched.

### 2.3 Changed file: `src/aspis/commands/init.py`

```
src/aspis/commands/init.py    (+30 lines, ~96 total)  CHANGED
```

**New CLI flags added to `register()`:**

```python
parser.add_argument("--dry-run", action="store_true",
    help="Show what would happen (default).")
parser.add_argument("--apply", action="store_true",
    help="Apply changes (synonym for --write).")
parser.add_argument("--strict", action="store_true",
    help="Refuse on CONFLICT (exit non-zero).")
parser.add_argument("--scope", default=None,
    help="Export only assets whose target path starts with this prefix (e.g. .opencode/agents/).")
parser.add_argument("--force-conflicts", action="store_true",
    help="Overwrite files even when both catalog and user changed the file.")
parser.add_argument("--reset-snapshot", action="store_true",
    help="Discard a corrupt snapshot and rebuild it.")
```

**Flag interaction matrix:**

| Flag Combination | Valid? | Behavior |
|---|---|---|
| *(none)* | ✅ | Dry-run with full decision output |
| `--dry-run` | ✅ | Explicit dry-run (same as default) |
| `--write` | ✅ | Apply changes with protection |
| `--apply` | ✅ | Synonym for `--write` |
| `--write --force` | ✅ | `force` supersedes — overwrite everything, skip decide |
| `--write --force-conflicts` | ✅ | Apply, overriding CONFLICTs only |
| `--write --strict` | ✅ | Apply, fail on CONFLICT |
| `--write --scope=agents/` | ✅ | Apply only to matching assets |
| `--write --reset-snapshot` | ✅ | Reset corrupt snapshot, then apply |
| `--force --force-conflicts` | ⚠️ | Redundant but harmless — `force` already overwrites everything |
| `--force --strict` | ⚠️ | Redundant but harmless — `force` bypasses all protection |
| `--force-conflicts --strict` | ❌ | Contradictory: one permits, one forbids |
| `--write --dry-run` | ⚠️ | `--write` wins (dry-run is default; explicit `--write` overrides) |

**`_run()` updated to pass new flags through to `write_export`:**
```python
write_export(plan, ctx.root, force=force, write=write,
             apply=apply, strict=strict, scope=scope,
             force_conflicts=force_conflicts, reset_snapshot=reset_snapshot)
```

**Dry-run output format** (when `write=False`):
```
DRY-RUN — init /path/to/project
  [ADD]         .opencode/agents/planning-lead.md       (live=—        snap=—        regen=abc123)
  [UNCHANGED]   .opencode/agents/system-lead.md         (live=def456   snap=def456    regen=def456)
  [UNKNOWN]     .aspis/templates/custom.md              (live=ghi789   snap=—         regen=jkl012)
  [UPDATE]      .opencode/agents/build-lead.md          (live=abc123   snap=abc123    regen=new456)
  [PROTECT]     .opencode/agents/reviewer.md            (live=usr789   snap=orig456   regen=orig456)
  [CONFLICT]    .opencode/commands/custom.md            (live=usr123   snap=old456    regen=new789)

SUMMARY: 3 ADD, 15 UNCHANGED, 1 UNKNOWN, 2 UPDATE, 1 PROTECT, 1 CONFLICT
```

### 2.3a Changed file: `src/aspis/operations/init.py`

```
src/aspis/operations/init.py   (+8 lines, ~55 total)  CHANGED
```

**Read new flags from `ctx.options` and forward to `write_export()`:**

The current implementation reads `ctx.options.get("write")` and
`ctx.options.get("force")` at line ~34-35 and calls
`write_export(plan, ctx.root, force=force, write=write)` at line ~47. This file
must also read the new flags from `ctx.options` and pass them to `write_export`:

```python
write_export(plan, ctx.root, force=force, write=write,
             apply=ctx.options.get("apply", False),
             strict=ctx.options.get("strict", False),
             scope=ctx.options.get("scope"),
             force_conflicts=ctx.options.get("force_conflicts", False),
             reset_snapshot=ctx.options.get("reset_snapshot", False))
```

(Inherits the same options dict shape as the CLI layer.)

### 2.4 Changed file: `src/aspis/commands/models.py`

```
src/aspis/commands/models.py   (1 line changed)  CHANGED
```

**Line 230 — fix the hard-coded `force=True` bug:**

```python
# OLD (line 230):
write_export(ExportPlan(actions=live, catalog_root=None), root, force=True, write=True)

# NEW:
write_export(ExportPlan(actions=live, catalog_root=None), root, apply=True, write=True)
```

`apply=True` routes through the decide flow. Since `models --apply` re-renders
agents that already exist on disk with a catalog that may have changed, the
decision engine will correctly:
- **UPDATE** agents whose live content matches the snapshot (pristine, safe to
  overwrite)
- **PROTECT** agents the user has hand-edited (live ≠ snapshot, but catalog
  unchanged)
- **CONFLICT** agents where both the catalog and user changed

**`--force` flag added as escape hatch:**

Add `--force` flag to `aspis models --apply` as an escape hatch. When `--force`
is passed, use `force=True` instead of `apply=True` (old behavior — overwrites
everything, including user-edited agents). Without `--force`, `models --apply`
uses `apply=True` (new protected behavior).

### 2.5 New brain files (generated, gitignored)

```
.aspis/current/export-snapshot.json    NEW  (generated, gitignored)
.aspis/current/export-log.jsonl        NEW  (generated, gitignored)
```

**`export-snapshot.json` format:**
```json
{
  "version": 1,
  "paths": {
    ".opencode/agents/planning-lead.md": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ".opencode/commands/plan.md": "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a",
    ".aspis/templates/planning/SPEC.md": "6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d"
  }
}
```

- `version`: integer, incremented on format changes
- `paths`: posix-relative path → SHA-256 hex digest
- Atomic write via tempfile + `os.replace` (concurrent-run safe)

**`export-log.jsonl` format (JSONL — one JSON object per line, no array wrapper):**
```jsonl
{"timestamp": "2026-06-24T14:30:00.123456", "path": ".opencode/agents/planning-lead.md", "kind": "UPDATE", "action": "wrote", "hashes": {"live": "abc123...", "snapshot": "abc123...", "regen": "def456..."}}
```

- `timestamp`: ISO 8601 with microseconds (UTC)
- `kind`: DecisionKind value
- `action`: `"wrote"` | `"skipped"` | `"preserved"` | `"protected"` | `"conflict"`
- `hashes`: the three hashes at decision time
- One JSON object per line — true append-only, O(1) per entry

### 2.6 Brain `.gitignore` update

```
.aspis/.gitignore    DATA UPDATE  (add 2 lines)
```

Add entries to ignore generated export state:
```
current/export-snapshot.json
current/export-log.jsonl
```

This is a scaffolding data change (not product code) — the `resources/scaffold/brain.gitignore`
catalog entry is updated.

---

## 3. Technical Context

- **Language:** Python 3.12+
- **Key dependencies:** `hashlib` (stdlib), `json` (stdlib), `tempfile` + `os.replace`
  (stdlib), `pathlib` (stdlib) — zero new dependencies
- **Storage:** Two JSON files under `.aspis/current/` (the existing brain `current/`
  directory, currently empty)
- **Concurrency:** Atomic `os.replace` for snapshot writes; `export-log.json` is
  append-only (best-effort; concurrent appends may interleave entries which is
  acceptable for an audit log)
- **Backward compatibility:** `--force` preserves exact existing behavior; existing
  callers that pass `force=True` (e.g., bootstrap operations) continue to work
  unchanged

---

## 4. Steps and Gates

### Step 1: Create `src/aspis/protect.py` — the pure engine

**Files:** `src/aspis/protect.py` (new)
**Gate:** `pytest tests/test_protect.py -x -q` — 16+ tests covering the full
decision table, CRLF normalization, edge cases (None hashes, empty strings,
BOM handling)
**Depends on:** nothing

### Step 2: Add snapshot/log helpers to `src/aspis/export.py`

**Files:** `src/aspis/export.py` (add `_load_snapshot`, `_save_snapshot`,
`_append_log`, `_hash_file`, `_regen_hash`)
**Gate:** `pytest tests/test_export_snapshot.py -x -q` — test load/save
round-trip, corruption detection, reset_snapshot behavior, atomic write
**Depends on:** Step 1

### Step 3: Rewire `write_export` to use the decide flow

**Files:** `src/aspis/export.py` (modify `write_export`)
**Gate:** `pytest tests/test_export_protection.py -x -q` — integration tests:
first export (ADD), second export unchanged (UNCHANGED), user-edit protect
(PROTECT), catalog-update (UPDATE), both-changed (CONFLICT), force bypass,
force_conflicts override, strict failure, scope filtering
**Depends on:** Step 2

### Step 4: Update `src/aspis/commands/models.py` — fix the bug

**Files:** `src/aspis/commands/models.py` (line 230)
**Gate:** `pytest tests/test_commands_models.py -x -q` — verify `models --apply`
no longer force-overwrites user-edited agents; verify PROTECT behavior
**Depends on:** Step 3

### Step 5: Add CLI flags to `src/aspis/commands/init.py`

**Files:** `src/aspis/commands/init.py` (register + _run)
**Gate:** `pytest tests/test_commands_init.py -x -q` — flag parsing,
invalid combinations rejected, dry-run output format, apply writes correctly
**Depends on:** Step 3

### Step 6: Update brain `.gitignore` scaffold

**Files:** `src/aspis/data/catalog/scaffold/brain.gitignore` (add 2 lines)
**Gate:** `pytest tests/test_brain_gitignore.py -x -q` — verify generated
`.aspis/.gitignore` contains the export entries
**Depends on:** nothing (independent)

### Step 7: End-to-end acceptance test

**Files:** `tests/test_f015_e2e.py` (new)
**Gate:** `pytest tests/test_f015_e2e.py -x -q` — full cycle: init, user edit,
re-init protects, catalog change updates, both-change conflicts, force bypass,
models --apply protects user edits, scope filtering, corrupted snapshot reset
**Depends on:** Steps 1–6

---

## 5. Risks and Rollback

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Snapshot lost/corrupted mid-write | Low | Users lose protection; re-export treats all as UNKNOWN | Atomic `os.replace` — old snapshot is intact until new one is fully written |
| `--force` users surprised by protection | Medium | Existing scripts that expect force behavior break | `--force` is **unchanged** — when passed, the entire decide loop is skipped; zero behavior change |
| `models --apply` regression | Low | User expects force behavior, gets protected | The bug being fixed IS the regression — force=True was destroying user edits. The fix restores correct behavior. Users who relied on the bug get a CONFLICT and are told to use `--force-conflicts` |
| CRLF hash mismatch on Windows | Medium | False PROTECT decisions | `sha256_text` normalizes CRLF→LF before hashing — eliminates the platform difference |
| Concurrent export runs | Low | Corrupted snapshot | Atomic `os.replace` for snapshot; log is append-only and best-effort |
| Large catalog performance | Low | Hash computation slow | SHA-256 of small text files (<100KB each) is negligible; catalog has ~50 assets |

**Rollback:** Revert commits in reverse order (Step 7 → Step 1). The snapshot and
log files are generated artifacts — deleting them restores the pre-F-015 state. No
database migration, no schema change.

---

## 6. Cost of Change

| Category | Files | Count |
|---|---|---|
| **Existing files changed** | `src/aspis/export.py`, `src/aspis/commands/init.py`, `src/aspis/commands/models.py`, `src/aspis/operations/init.py` | **4** |
| **New product code files** | `src/aspis/protect.py` | **1** |
| **New test files** | `tests/test_protect.py`, `tests/test_export_snapshot.py`, `tests/test_export_protection.py`, `tests/test_commands_models.py` (extended), `tests/test_commands_init.py` (extended), `tests/test_f015_e2e.py` | **6** |
| **Generated brain files** | `.aspis/current/export-snapshot.json`, `.aspis/current/export-log.json` | **2** (generated) |
| **Brain data update** | `src/aspis/data/catalog/scaffold/brain.gitignore` | **1** (2 lines) |

**Cost-of-Change verdict: 4 existing product files changed → WARNING** (within 5–10 range).

---

## 7. Constitution Compliance Checklist

| # | Rule | How satisfied |
|---|---|---|
| 1 | **Local Change** | 4 existing files changed, 1 new module. Within warning range (4 ≤ 5). |
| 2 | **Plugin First** | `protect.py` is runtime-agnostic — no `if runtime == "claude"`. Decision function compares hashes only. |
| 3 | **Single Source of Truth** | Catalog = source of what to write. Snapshot = record of what was last written. `decide()` reads both to determine action. No third source. |
| 4 | **No Special Cases** | No `if kind == "agents"` or `if scope == "x"` in the decision engine. Scope filtering is a prefix match on the source path — generic mechanism. |
| 5 | **Generated Artifacts** | Snapshot and audit log are written by `write_export()`, never hand-edited. |
| 6 | **Automation before Intelligence** | `sha256_text` + `decide` are pure deterministic functions. No agent, no LLM, no heuristic. |
| 7 | **Core is Stable** | `plan_export()` and `_apply()` are **untouched**. `write_export()` gains snapshot-awareness but the existing signature (`force`, `write`) is preserved. Existing callers with `force=True` are byte-identical in behavior. |
| 8 | **Configuration over Code** | Scope filter, strict mode, force_conflicts, reset_snapshot are passed as parameters — no if-chain on kind or runtime. |
| 9 | **Dependency Direction** | `protect.py` has zero imports from the ASPIS codebase (only stdlib). `export.py` imports `protect` (plugin → core pattern, not core → plugin). |
| 10 | **Consistency over Cleverness** | The 6-way decision table is the exact same truth table proven in the old repo. No novel algorithm. |
| 11 | **Architecture before Features** | The protection mechanism is general — any export operation (init, bootstrap, models --apply) uses the same decide flow. No per-operation special case. |
| 12 | **Portable by Default** | CRLF→LF normalization in `sha256_text` eliminates the Windows/Linux line-ending difference. All paths use posix separators in snapshot. Atomic write uses `os.replace` (cross-platform). |

---

## 8. Anti-Patterns Deliberately Rejected

| Anti-pattern | Why rejected |
|---|---|
| **Staging directory** | Old repo wrote to a staging dir before final placement. Rejected: atomic `os.replace` on the snapshot is sufficient; staging files adds complexity with no protection gain. |
| **Clobber classification** | Old repo classified files as "clobber-able" vs "safe". Rejected: the 6-way decide function handles all cases uniformly through hash comparison. No file-type heuristic needed. |
| **Accept / rebaseline commands** | Old repo had `accept()` (promote live→snapshot) and `rebaseline()`. Rejected: the user edits files directly; the next export run detects the change via hash comparison. No separate command needed. |
| **Per-runtime lock files** | Old repo had separate lock/snapshot files per runtime. Rejected: one snapshot covers all runtimes — simpler, and cross-runtime consistency is automatic. |
| **Orphan detection** | Old repo tracked files in live but not in catalog. Rejected: the UNKNOWN decision only triggers for files in the catalog scope. Orphan detection is a separate concern (future feature). |
| **Trace events** | Old repo emitted structured trace events. Rejected: the JSON audit log is sufficient for debugging and diagnostics. Trace events add complexity without a current consumer. |
| **Self-validation** | Old repo validated its own decisions post-hoc. Rejected: the test suite validates the decision table; runtime self-validation is redundant and untestable. |
| **YAML semantic diff** | Old repo had a YAML-level semantic diff for mode changes. Rejected: SHA-256 of normalized text is sufficient. If YAML-semantic comparison is needed later, it's a separate concern. |
| **Accept handler in decide()** | Old repo's decide function had side effects. Rejected: `decide()` is pure — all I/O is in `write_export()`. Testable in isolation. |
| **promote.py / regenerate.py** | Old repo split logic across promote (188 lines) and regenerate (568 lines). Rejected: a single `protect.py` (141 lines) + snapshot-aware `write_export` is simpler and has fewer integration surfaces. |

---

## 9. Function Signatures (complete)

### `src/aspis/protect.py`

```python
import enum
import hashlib
from dataclasses import dataclass

class DecisionKind(enum.Enum):
    ADD = "ADD"
    UNCHANGED = "UNCHANGED"
    UNKNOWN = "UNKNOWN"
    UPDATE = "UPDATE"
    PROTECT = "PROTECT"
    CONFLICT = "CONFLICT"

@dataclass(frozen=True)
class Decision:
    kind: DecisionKind
    live_hash: str | None = None
    snapshot_hash: str | None = None
    regen_hash: str | None = None

def sha256_text(text: str) -> str: ...
def decide(
    live_hash: str | None,
    snapshot_hash: str | None,
    regen_hash: str | None,
) -> Decision: ...
def plan_runtime(
    snapshot: dict[str, str],
    live_hashes: dict[str, str | None],
    regen_hashes: dict[str, str],
) -> dict[str, Decision]: ...
def summary(decisions: dict[str, Decision]) -> dict[DecisionKind, int]: ...
```

### `src/aspis/export.py` (additions)

```python
class ProtectionError(RuntimeError): ...  # NEW — raised on strict CONFLICT

def write_export(
    plan: ExportPlan, target_root: Path, *,
    force: bool = False, write: bool = False,
    apply: bool = False, strict: bool = False,
    scope: str | None = None,
    force_conflicts: bool = False,
    reset_snapshot: bool = False,
) -> list[str]: ...  # EXTENDED signature

def _load_snapshot(target_root: Path, *, reset: bool = False) -> dict: ...  # NEW
def _save_snapshot(target_root: Path, snapshot: dict) -> None: ...           # NEW
def _append_log(target_root: Path, entries: list[dict]) -> None: ...         # NEW
def _hash_file(path: Path) -> str | None: ...                                # NEW
def _regen_hash(source: Path, op: str) -> str: ...                           # NEW
```

---

## 10. Test Coverage Target

| Test file | Minimum tests | Coverage target |
|---|---|---|
| `tests/test_protect.py` | 16 | 100% branch coverage of `decide()` and `sha256_text()` |
| `tests/test_export_snapshot.py` | 8 | Snapshot load/save/corruption/reset paths |
| `tests/test_export_protection.py` | 12 | Full export cycle: ADD, UNCHANGED, UNKNOWN, UPDATE, PROTECT, CONFLICT, force bypass, force_conflicts, strict, scope |
| `tests/test_models_command.py` | 3 | models --apply with changed catalog, user-edited agent, both-changed |
| `tests/test_init_cli.py` | 6 | Flag parsing, invalid combinations, dry-run output, apply with protection |
| `tests/test_f015_e2e.py` | 6 | End-to-end: init→edit→re-init protects, catalog-change→re-init updates, both-change conflicts, force bypass, models-apply, snapshot corruption recovery |

**Total: ~51 tests across 6 test files.**

---

*Plan produced: 2026-06-24. Ready for independent review, then task decomposition.*
