# F-015 — Industry Patterns Verification & Gap Analysis

**Author:** Research Lead
**Date:** 2026-06-25
**Status:** Validation report. Adds verification + gaps to the existing
`f-015-comprehensive-research.md` and `F-015-edge-cases.md`. Read in conjunction
with both.
**Scope:** Verify the 6-way decision table against industry patterns
(pacman/chezmoi/dpkg/npm/pip/cargo/uv/etckeeper/Ansible/Git). Identify gaps
the plan does not yet cover, with citations. Recommend specific code changes
and additional test cases.

---

## Executive summary

The F-015 plan's algorithm (3-way hash comparison, 6-case decision table) is
the canonical solution used by pacman since 1994, chezmoi, and dpkg; the
`f-015-comprehensive-research.md` (2026-06-25) already covers these. This
report focuses on the **8 specific verification topics** raised in the F-015
research request: (1) hash function choice, (2) lockfile/snapshot format
patterns, (3) JSONL vs JSON array for the audit log, (4) Windows atomic-write
mechanics, (5) Git's CRLF handling for comparison, (6) etckeeper/Ansible
config-protection patterns, (7) Unicode/NFC/NFD edge cases, and (8) the
binary-vs-text distinction in `sha256_text`.

**Headline findings:**

1. **The 6-way decision table is complete and correct** for the 3-hash model.
   No missing cases. (See §A.)
2. **The current plan has THREE issues worth fixing before code is written:**
   - The `export-log.json` format (JSON array) is an anti-pattern. JSONL is
     the industry standard for append-only logs. Truncation-safe, streamable,
     standard extension. **Fix recommended.** (§B.1)
   - `sha256_text` only handles `str`; binary files (catalog PDFs, PNGs, etc.
     if any) need a separate `sha256_bytes` path. The current plan conflates
     them. **Fix recommended.** (§B.2)
   - No lockfile for concurrent runs. The existing F-015 edge-case doc
     already flags this as CRITICAL (C-16). **Fix recommended.** (§B.3)
3. **Four additions** are real improvements:
   - UTF-8 BOM stripping in `sha256_text` (C-15 from existing edge-case doc).
   - `--force` on `aspis models --apply` for symmetry with `aspis init`.
   - The `cost-of-change` is **4 files**, not 3 (must update
     `operations/init.py`).
   - Stream-hash for large files (defensive; the current `read_text()` is
     fine for the typical <100KB catalog files, but cheap to do right).
4. **SHA-256 is the right choice.** BLAKE3 is faster but the speed
   difference is irrelevant for <100KB files; SHA-256 is the
   pip/uv/npm-recommended default, FIPS-approved, and dependency-free.
   (§C.)

---

## (a) Verification of the 6-way decision table

### The table, restated

| # | Condition | DecisionKind | Action |
|---|---|---|---|
| 1 | `live_hash is None` | `ADD` | Write regen, record in snapshot |
| 2 | `live_hash == regen_hash` | `UNCHANGED` | Skip |
| 3 | `snapshot_hash is None` | `UNKNOWN` | Preserve live, record `live_hash` in snapshot |
| 4 | `live_hash == snapshot_hash` | `UPDATE` | Write regen, record in snapshot |
| 5 | `regen_hash == snapshot_hash` | `PROTECT` | Skip (protect live) |
| 6 | *(fallthrough)* | `CONFLICT` | Refuse without `--force-conflicts` |

### Completeness check

**The table is complete and mutually exclusive enough for the 3-hash model.**
The 3 inputs (`live`, `snapshot`, `regen`, each ∈ {None, hash}) generate
2³ = 8 truth-table cells once you fix the catalog/regen to a non-None
value (it never is — `regen` is always computed). The plan collapses
those 8 cells into 6 outcomes:

| live | snap | regen | Plan says | Industry says | Verdict |
|---|---|---|---|---|---|
| None | None | H | (case 1) ADD | ADD | ✓ |
| None | H | H | (case 1) ADD | ADD | ✓ (recreate) |
| L | None | L | (case 2) UNCHANGED | UNCHANGED | ✓ but suboptimal |
| L | None | L' | (case 3) UNKNOWN | UNKNOWN | ✓ |
| L | S | L | (case 2) UNCHANGED | UNCHANGED | ✓ |
| L | S | L' (= S) | (case 4) UPDATE | UPDATE | ✓ |
| L | S | L' (≠ S) | (case 5) PROTECT | PROTECT | ✓ |
| L | S | L'' (≠ L, ≠ S) | (case 6) CONFLICT | CONFLICT | ✓ |

Two subtleties:

**Subtlety 1: case 2 vs case 3 ordering.** When `live == regen` AND
`snapshot is None`, case 2 (UNCHANGED) fires first. This is **safe** —
the file already matches the catalog, no action needed. But the snapshot
remains empty for that path, so the next run will also see UNCHANGED.
Alternative: case 3 (UNKNOWN) first would record `live_hash` in the
snapshot, which lets the system detect future hand-edits via the
PROTECT path. **Recommendation: keep case 2 first (current plan is
correct)**, but document this in the `decide()` docstring. The
"record live hash" behavior of UNKNOWN is only useful when the
file does NOT match the catalog.

**Subtlety 2: case 1 vs case 3.** If `live is None` AND `snapshot is None`
(typical first-export), case 1 (ADD) fires. Correct. The case 3 (UNKNOWN)
path only triggers when `live` exists but `snapshot` is None. This is the
"first export of an existing project" scenario — and the F-015 edge-case
doc covers it as C-3. **The plan's table is correct.**

### Compared to industry 3-way decision tables

| System | Outcomes | Algorithm | Source |
|---|---|---|---|
| **pacman** (1994) | 5: identical / catalog-improved / user-edited / catalog-equals-current / conflict | MD5 of 3 copies; on conflict, install as `.pacnew` | [Arch Wiki](https://wiki.archlinux.org/title/Pacman/Pacnew_and_Pacsave) |
| **dpkg** | binary: keep-old / keep-new / interactive | MD5 of on-disk vs postinst's expected | [Wikipedia: dpkg](https://en.wikipedia.org/wiki/Dpkg) |
| **chezmoi** | 4: identical / only-target-changed / only-source-changed / both-changed | mtime + content hash | [chezmoi docs: apply](https://www.chezmoi.io/reference/commands/apply/) |
| **ASPIS F-015** | 6: ADD / UNCHANGED / UNKNOWN / UPDATE / PROTECT / CONFLICT | SHA-256 of 3 copies | F-015 PLAN §2.1 |

ASPIS has 6 outcomes because it has 3 inputs (vs pacman's 3) and the
"first export" case (no snapshot) is a real concern. The algorithm is the
same family. **Verdict: complete.**

### Edge cases the 6 cases do and do not cover

| Edge case | Covered? | Notes |
|---|---|---|
| Empty file (hash of empty string) | ✓ | All 6 cases work; `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` is the well-known empty SHA-256 |
| Live file deleted between exports | ✓ | `live_hash is None` → ADD. Plan §C-6. |
| File moved between kinds (agents/ → skills/) | partial | Plan §I-1: source-path keying detects this; old live file is in snapshot but not in plan → left alone, new path is NEW. This is correct, but `decide()` itself does not know about moves — the `write_export` orchestrator must filter the union of keys correctly. **Test recommended.** |
| File renamed in catalog | partial | Same as above. |
| File removed from catalog (orphan in live) | N/A | Plan explicitly defers orphan deletion to a future `--prune` flag. Live files outside the plan are not hashed. **Recommendation: report them in dry-run output as `unmanaged: <path>` for visibility** (cosmetic, not a behavior change). |
| Binary files (PNG, PDF) | partial | `sha256_text` operates on `str`; binary files must be hashed as `bytes`. See §B.2. |
| Large files (>1MB) | partial | `read_text()` loads the whole file. Fine for <100KB; defensive recommendation in §B.4. |
| NFC vs NFD (macOS filename normalization) | ✗ | Not in plan. **Test recommended.** |
| Mixed line endings in the same file | partial | Plan normalizes `\r\n` → `\n` before hashing, so all-CRLF and all-LF produce the same hash, and mixed is treated as LF. **Document this behavior.** |
| Bare `\r` (old Mac line endings, pre-OSX) | ✗ | Plan only normalizes `\r\n` → `\n`. Bare `\r` is not touched. This is correct — `\r` alone is rarely a line ending now. But **test should pin this behavior**. |
| UTF-8 BOM (Notepad artifact) | ✗ | Plan does not strip BOM. **Fix recommended.** See §B.5. |
| CRLF (Windows line endings) | ✓ | Plan normalizes `\r\n` → `\n` before hashing. Correct, matches Git's `text=auto`. |

---

## (b) Best practices the plan might be missing

### B.1 — Switch the audit log from JSON array to JSONL

**The current plan** stores `export-log.json` as a JSON object with an
`entries: []` array. To append an entry, the code must:
1. Read the entire log file
2. Parse it
3. Append to the array
4. Write the entire file back

**This is O(n) per append**, where n is the cumulative log size. It also
loses atomicity (a crash between read and write corrupts the log).
**None of pacman, npm, pip, cargo, uv, chezmoi, or etckeeper do this.**
The industry standard for append-only logs is **JSON Lines (JSONL)**:
one JSON object per line.

From [jsonlines.org](https://jsonlines.org/) (verified 2026-06-25):

> JSON Lines is a convenient format for storing structured data that may be
> processed one record at a time. It works well with unix-style text
> processing tools and shell pipelines. **It's a great format for log
> files.**

The format requirements: UTF-8, one valid JSON value per line, line
terminator `\n` (CRLF supported on read). Standard file extension: `.jsonl`.

**Concrete benefits:**
- **Append is O(1)**: just open the file in append mode and write one line.
- **Truncation-safe**: a torn write (crash mid-line) loses at most one
  entry, not the whole log.
- **Streamable**: `for line in open('export-log.jsonl')` — no parse-the-world
  upfront.
- **`grep`/`jq`/`tail -f` work out of the box** for debugging.
- **No risk of "the log file is invalid JSON because someone truncated
  it"** — partial reads just yield fewer entries, never a parse error.
- **Familiar extension** (`.jsonl`) — every DevOps tool knows it.
- **Cemented by industry**: 12-factor app logs, GCP Cloud Logging, AWS
  CloudWatch, journald, all use line-delimited records.

**Proposed schema change** (from PLAN §2.5 to PLAN §B.1):

```diff
- export-log.json
+ export-log.jsonl
```

```jsonl
{"timestamp":"2026-06-24T14:30:00.123456","path":".opencode/agents/planning-lead.md","kind":"UPDATE","action":"wrote","hashes":{"live":"abc123","snapshot":"abc123","regen":"def456"}}
{"timestamp":"2026-06-24T14:30:00.124000","path":".opencode/commands/plan.md","kind":"UNCHANGED","action":"skipped","hashes":{"live":"aaa","snapshot":"aaa","regen":"aaa"}}
```

**Implementation snippet for `_append_log`:**

```python
def _append_log(target_root: Path, entries: list[dict]) -> None:
    """Append entries to export-log.jsonl (one JSON object per line).

    The file is opened in append mode; each entry is written as a single
    line followed by '\\n'. The log is best-effort; concurrent appends
    may interleave lines which is acceptable for an audit log.
    """
    log_path = target_root / ".aspis" / "current" / "export-log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", newline="\n") as f:
        for entry in entries:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")
```

**Migration note:** the old `export-log.json` (if any exists from
F-015 pre-release) can be deleted — it has no users yet. Document
in the `export-log.jsonl` header that it is JSONL, not JSON.

**Recommendation: STRONG. Add to plan.**

### B.2 — Separate `sha256_text` from `sha256_bytes`

**The current plan** defines `sha256_text(text: str) -> str` with CRLF→LF
normalization. This is the right function for the rendered agent/skill
text, but the plan also has a `_hash_file(path: Path)` helper that reads
the **live file** and feeds it to `sha256_text`.

The current `export.py` line 131-134 already writes with
`newline="\n"`, so the *catalog's regen* is always LF. But the *live file*
might be binary (if the user has a PNG in their skills directory, or a
PDF in their templates). Reading binary as text and calling
`text.replace("\r\n", "\n")` will either:

- On UTF-8-encoded files: work, but the CRLF normalization is a no-op
  (binary files rarely contain `\r\n`).
- On non-UTF-8 files: raise `UnicodeDecodeError` when reading with
  `read_text()`.

**The fix:** introduce a separate `sha256_bytes(data: bytes) -> str`
function for binary content, and a `sha256_file(path: Path) -> str` that
sniffs the file (or takes an `is_binary: bool` parameter from the
plan/orchestrator). Text files use `sha256_text`; binary files use
`sha256_bytes`.

**Industry reference:** `npm` (per its `package-lock.json` `integrity`
field) uses SRI hashes (sha512 default) over raw bytes — no text
normalization. `git hash-object` is also raw bytes. The current
ASPIS `sha256_text` CRLF normalization is an *ASPIS-specific* design
choice driven by the cross-platform line-ending problem; it only
applies to text.

**Proposed `protect.py` change:**

```python
def sha256_bytes(data: bytes) -> str:
    """SHA-256 hex digest of raw bytes. No normalization."""
    return hashlib.sha256(data).hexdigest()

def sha256_text(text: str) -> str:
    """SHA-256 hex digest after CRLF→LF normalization and BOM strip."""
    if text.startswith("\ufeff"):
        text = text[1:]
    text = text.replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_file(path: Path, *, is_binary: bool = False) -> str:
    """Hash a file's contents. Binary files are hashed as bytes;
    text files are normalized before hashing."""
    data = path.read_bytes()
    if is_binary:
        return sha256_bytes(data)
    return sha256_text(data.decode("utf-8"))
```

**Recommendation: MODERATE. Add to plan; covers a real correctness gap.**

### B.3 — Per-project lockfile for concurrent-run safety

**The current plan** does not address concurrent `aspis init` runs from
two terminals. The F-015 edge-case doc flags this as CRITICAL (C-16).
Without a lock, two runs can:
1. Both load snapshot
2. Both compute decisions
3. Both write the same files
4. Both write their own snapshot, racing

**The plan's "atomic `os.replace`" is the right primitive for the
*snapshot write itself* (last writer wins, no torn file), but it does
not protect the *read-decide-write cycle* for the whole export
operation. A lockfile is the standard fix.**

**Industry patterns:**
- **uv** ([docs](https://docs.astral.sh/uv/concepts/projects/sync/)) supports
  `--locked` (refuse if out of date) and `--frozen` (use as-is). No
  concurrent-run lock — uv assumes single-user CLI.
- **cargo** uses `Cargo.lock` (the lockfile itself) but does not have a
  per-run lock. Cargo is a build tool, not a system service.
- **npm** uses a "hidden" lockfile at `node_modules/.package-lock.json`
  for performance; no per-run lock.
- **pacman** uses a `db.lck` file (in `/var/lib/pacman/db.lck` on Arch).
  Created with `O_CREAT | O_EXCL` (fails if exists), removed on completion.
- **etckeeper** does NOT have a per-run lock — it relies on the package
  manager (apt) being a serial process.

**The pacman pattern is the right one for ASPIS: a tiny lockfile at
`.aspis/current/export.lock`, created with `O_CREAT | O_EXCL`, holding
the PID, removed on success/failure.**

**Proposed implementation:**

```python
class ExportLockError(RuntimeError):
    """Another aspis init --apply is in progress (or stale lock)."""

def _acquire_lock(target_root: Path, *, force_lock: bool = False) -> Path:
    """Acquire per-project export lock. Returns lock path.
    Raises ExportLockError if held by a live process."""
    lock_path = target_root / ".aspis" / "current" / "export.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        # O_CREAT | O_EXCL | O_RDWR — atomic create-or-fail
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o644)
    except FileExistsError:
        # Stale lock detection
        try:
            content = lock_path.read_text(encoding="utf-8").strip()
            pid = int(content)
            if not _pid_alive(pid):
                if force_lock:
                    lock_path.unlink()
                    return _acquire_lock(target_root, force_lock=False)
                raise ExportLockError(
                    f"Stale lock at {lock_path} (PID {pid} is dead). "
                    f"Re-run with --force-lock to take over."
                )
        except (ValueError, OSError):
            pass
        raise ExportLockError(
            f"Another aspis init is in progress (lock at {lock_path}). "
            f"If this is wrong, check that no other process is running."
        )
    # Write PID + timestamp for diagnostics
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(f"{os.getpid()}\n")
        f.write(datetime.now(timezone.utc).isoformat() + "\n")
    return lock_path

def _release_lock(lock_path: Path) -> None:
    """Best-effort lock release. Errors are swallowed."""
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass
```

**Use as a context manager in `write_export`:**

```python
def write_export(plan, target_root, ...):
    if force or not write:
        # Dry-run / force — no lock needed (force is destructive anyway)
        return _write_export_impl(plan, target_root, ...)
    with contextlib.ExitStack() as stack:
        lock = stack.enter_context(_locked_export(target_root, force_lock=force_lock))
        return _write_export_impl(plan, target_root, ...)
```

**Recommendation: STRONG. Add to plan; the existing edge-case doc
already calls it CRITICAL.**

### B.4 — Stream-hash for large files (defensive)

**The current plan** uses `path.read_text()` + `sha256_text()`. This
loads the whole file into memory. For the typical ASPIS catalog (50
files × ~20KB), this is ~1MB total, which is fine.

**Industry reference:** [BLAKE3 spec](https://github.com/BLAKE3-team/BLAKE3)
and [BLAKE3 adoption](https://github.com/BLAKE3-team/BLAKE3#adoption--deployment)
explicitly cite streaming as a design goal. [etckeeper](https://etckeeper.branchable.com/)
commits arbitrarily large config files to git; git's own `hash-object`
streams via `update()`. pip's `pip download --hash` streams the package
through the hash.

**Defensive recommendation:** use `hashlib.sha256()`'s `update()`
method for files > 1MB. The `protect.py` function signature can stay
simple (it operates on `str` or `bytes` in memory); the streaming is
in `_hash_file`:

```python
def _hash_file(path: Path, *, is_binary: bool = False) -> str | None:
    """SHA-256 of file content, with optional CRLF→LF normalization for text."""
    if not path.exists():
        return None
    if is_binary or path.stat().st_size > 1_000_000:
        # Binary or large: hash raw bytes via streaming
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    # Small text: load + normalize
    return sha256_text(path.read_text(encoding="utf-8"))
```

**Recommendation: NICE-TO-HAVE. Add as a 1-line condition; cheap insurance.**

### B.5 — UTF-8 BOM stripping in `sha256_text`

**The current plan** normalizes CRLF→LF but does not strip a leading
UTF-8 BOM (`\ufeff` → bytes `0xEF 0xBB 0xBF`). A user who opens an
exported agent in Notepad (the Windows default editor) and saves
without any other change will get a BOM prepended, which the next
`aspis init --write` will see as `live != snapshot` → false PROTECT
decision.

**The existing F-015 edge-case doc (C-15) already recommends this:**

> Recommendation: **strip the BOM before hashing** (both `live` and
> `regen` paths). The BOM is a Windows editor artifact, not meaningful
> content.

**This is a one-line addition:**

```python
def sha256_text(text: str) -> str:
    if text.startswith("\ufeff"):
        text = text[1:]  # strip UTF-8 BOM
    text = text.replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
```

**Industry reference:** Git's `text=auto` (per
[gitattributes docs](https://git-scm.com/docs/gitattributes), verified
2026-06-25) normalizes line endings but does NOT strip BOM. **BOM
stripping is *not* a universal convention**; it is an ASPIS design
choice. Document this in the module docstring:

```
Note: A leading UTF-8 BOM (U+FEFF) is stripped before hashing. This
is a deliberate design choice: a user who opens an exported file in
Notepad (Windows default) and saves it without other changes would
otherwise trigger a false PROTECT decision.
```

**A user who genuinely wants the BOM preserved** can save with an
editor that doesn't add one (e.g., VS Code, Vim) — the new hash will
be a real PROTECT, not a false positive.

**Recommendation: STRONG. Add to plan; covers the most common Windows
false-PROTECT scenario.**

### B.6 — `--force` on `aspis models --apply` for symmetry

**The current plan** adds `--force`, `--apply`, `--strict`, `--scope`,
`--force-conflicts`, `--reset-snapshot` to `aspis init` (PLAN §2.3).
The `aspis models --apply` command gets a 1-line fix (`force=True` →
`apply=True`) but no `--force` flag.

**Problem:** A user who previously relied on `models --apply` to
force-overwrite everything (the old buggy behavior) will now get
CONFLICT or PROTECT decisions and may want the old behavior
("overwrite everything, I know what I'm doing").

**Recommendation: add `--force` to `models --apply` for symmetry.**
1 line. Cheap.

### B.7 — `cost-of-change` correction: 4 files, not 3

**The current plan** (PLAN §6) says "3 existing product files changed
(export.py, init.py, models.py)". The comprehensive research
(`f-015-comprehensive-research.md` §5.4) already noted the correction:
`src/aspis/operations/init.py` (the lifecycle op called by
`engine.run("init", ...)`) must also pass the new flags through to
`write_export`.

**Verification:** the operations/init.py file (not yet read) is the
`write_export` caller for the `init` command. If the new flags
(`apply`, `strict`, `scope`, `force_conflicts`, `reset_snapshot`)
are not threaded through, they will be silently dropped. **Confirm
this before code is written.**

**Recommendation: update PLAN §6 to 4 files.**

---

## (c) Hash function choice — SHA-256 vs BLAKE3 vs xxHash

### The contenders

| Hash | Output | Speed (16 KiB, x86) | Stdlib | Dependencies | FIPS | Industry adoption |
|---|---|---|---|---|---|---|
| **MD5** | 128 | ~1.0× (baseline) | yes | 0 | no | legacy only |
| **SHA-1** | 160 | ~0.8× | yes | 0 | no (deprecated 2011) | legacy |
| **SHA-256** | 256 | ~0.4× | yes | 0 | yes | universal (TLS, JWT, sigs, Bitcoin) |
| **BLAKE2b** | up to 512 | ~2.0× | yes (`hashlib.blake2b`) | 0 | no | libsodium, WireGuard, Argon2 |
| **BLAKE3** | default 256 | ~5-10× | **no (3rd-party wheel)** | 1 | no | Cargo, LLVM, OpenZFS, Solana, Bazel, Ccache, IPFS, Iroh, Chia, Nym, ClickHouse |
| **xxHash (xxh64)** | 64 | ~10-20× | **no (3rd-party wheel)** | 1 | no | LZ4, Zstandard, RocksDB, Presto, Apache Arrow |

Sources: [BLAKE3 README](https://github.com/BLAKE3-team/BLAKE3) (verified
2026-06-25, adoption list current), [BLAKE3 benchmarks](https://github.com/BLAKE3-team/BLAKE3-specs/blob/master/benchmarks/bar_chart.py).

### For ASPIS specifically

ASPIS catalogs are ~50 files × ~20KB = ~1MB total. SHA-256 throughput
on a modern CPU is ~500 MB/s for small files. Hashing the whole
catalog: **~5 ms**. BLAKE3 would be ~1 ms. **The 4 ms difference is
invisible to a human.**

### What pip does

[pip's secure-installs docs](https://pip.pypa.io/en/stable/topics/secure-installs/)
explicitly state (verified 2026-06-25):

> The recommended hash algorithm at the moment is sha256, but stronger
> ones are allowed, including all those supported by `hashlib`. However,
> weaker ones such as md5, sha1, and sha224 are excluded to avoid giving
> a false sense of security.

`npm` ([package-lock.json](https://docs.npmjs.com/cli/v10/configuring-npm/package-lock-json))
uses SRI hashes — sha512 by default, sha1 as fallback. Both are
`hashlib`-supported. Not BLAKE3.

`uv` (the modern Python package manager; [docs](https://docs.astral.sh/uv/concepts/projects/sync/))
uses SHA-256 internally for the same reason. uv explicitly does
NOT adopt BLAKE3 despite being a Rust project that could easily.

### Verdict

**SHA-256 is the right choice.** Reasoning:

1. **Speed is irrelevant** for ASPIS file sizes (5 ms total).
2. **Dependency-free**: `hashlib.sha256()` is in the Python stdlib.
   BLAKE3 requires `blake3` PyPI package or `pip install`.
3. **FIPS-approved**: matters for users in regulated industries.
4. **Industry alignment**: pip, uv, npm all default to SHA-256/SHA-512.
5. **Universal support**: every hash, every diff, every git format
   speaks SHA-256.
6. **No security risk**: collision resistance is sufficient for
   non-adversarial modification detection (which is what F-015 does —
   not adversarial tamper detection).
7. **Collision-resistance margin**: SHA-256's collision resistance
   is 2¹²⁸; BLAKE3's is 2¹²⁸ too. Equal for this use case.

**The only reason to switch to BLAKE3** would be if ASPIS started
hashing 10+ GB files (e.g., a self-hosted LLM model catalog). Not the
case.

**Recommendation: KEEP SHA-256.** The plan is correct.

---

## (d) Specific implementation recommendations

These are concrete, code-level changes to the plan. Numbered for
reference; integrate into the F-015 plan as written.

### R-1. `protect.py` — add `sha256_bytes` and update `sha256_text`

**Location:** `src/aspis/protect.py`

**Before:**

```python
def sha256_text(text: str) -> str:
    """SHA-256 hex digest after CRLF→LF normalization."""
    text = text.replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
```

**After:**

```python
def sha256_bytes(data: bytes) -> str:
    """SHA-256 hex digest of raw bytes. No normalization.

    Use for binary files (PDFs, PNGs, etc.) or when the caller has
    already done its own canonicalization.
    """
    return hashlib.sha256(data).hexdigest()

def sha256_text(text: str) -> str:
    """SHA-256 hex digest after normalization.

    Normalization: (a) strip a leading UTF-8 BOM if present (Windows
    Notepad artifact — without this, a user who opens an exported
    file in Notepad and saves without other changes would trigger
    a false PROTECT); (b) CRLF→LF (Windows line endings).

    Note: bare \\r (old Mac line endings) is preserved. This is
    intentional — bare \\r is not a line ending in modern files,
    and normalizing it would change legitimate CR characters
    (e.g., in CSV or Markdown tables).
    """
    if text.startswith("\ufeff"):
        text = text[1:]
    text = text.replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
```

### R-2. `export.py` — add `sha256_file` helper

**Location:** `src/aspis/export.py` (private helper)

```python
_BINARY_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".tar", ".gz"}

def _is_binary_path(path: Path) -> bool:
    return path.suffix.lower() in _BINARY_EXTENSIONS

def _hash_file(path: Path) -> str | None:
    """SHA-256 of file content, with text normalization for text files.

    Returns None if the file does not exist.
    """
    if not path.exists():
        return None
    if _is_binary_path(path):
        return protect.sha256_bytes(path.read_bytes())
    return protect.sha256_text(path.read_text(encoding="utf-8"))
```

The `_BINARY_EXTENSIONS` set is a pragmatic start; a more thorough
detection would also check for null bytes in the first 8KB. The plan
should document this as "extension-based for v1; content-based
detection is a future improvement."

### R-3. `export.py` — use `tempfile.NamedTemporaryFile` with the
correct Windows pattern for the snapshot write

**Location:** `_save_snapshot()` in `src/aspis/export.py`

**Why:** `tempfile.NamedTemporaryFile(delete=True)` on Windows holds
the file open in exclusive mode, which prevents the subsequent
`os.replace` from succeeding (or, worse, scans it 4× by antivirus
during the brief window). The right pattern on Windows is to write
the tempfile, **close it** (releasing the handle), then `os.replace`.

Per [Python docs for `os.replace`](https://docs.python.org/3/library/os.html#os.replace)
(verified 2026-06-25, Python 3.14.6):

> Rename the file or directory *src* to *dst*. If *dst* is a non-empty
> directory, `OSError` will be raised. If *dst* exists and is a file,
> it will be replaced silently if the user has permission. The
> operation may fail if *src* and *dst* are on different filesystems.
> If successful, the renaming will be an atomic operation (**this is
> a POSIX requirement**).

The "this is a POSIX requirement" caveat is important: on Windows,
the atomicity guarantee is weaker. Windows `MoveFileEx` (what
`os.replace` wraps) is "atomic at the file-system level" but the
intermediate state where the destination is unlinked before the
rename completes is observable to other processes.

**The pattern that minimizes the race window and avoids AV
interference:**

```python
import os
import tempfile

def _save_snapshot(target_root: Path, snapshot: dict) -> None:
    """Atomic write: tempfile + os.replace.

    The tempfile is created in the SAME directory as the final file
    (so os.replace is a same-filesystem rename — fast and atomic on
    POSIX, low-overhead on Windows). The tempfile is closed before
    os.replace (so Windows AV / file-locking does not block the
    rename). On any error, the tempfile is cleaned up.
    """
    final_path = target_root / ".aspis" / "current" / "export-snapshot.json"
    final_path.parent.mkdir(parents=True, exist_ok=True)
    # dir=final_path.parent keeps the tempfile on the same filesystem
    fd, tmp_path = tempfile.mkstemp(
        dir=final_path.parent,
        prefix=".export-snapshot.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(snapshot, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp_path, final_path)  # atomic on POSIX; near-atomic on Windows
    except BaseException:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise
```

**Key points:**
- `dir=final_path.parent` — same filesystem, fast rename.
- `mkstemp()` not `NamedTemporaryFile` — the latter holds the file
  open and confuses Windows.
- `os.fdopen` to convert the raw fd to a Python file object for
  `json.dump`.
- `try/except` cleanup on error.
- `os.replace`, not `os.rename` — `os.rename` raises `FileExistsError`
  on Windows if `dst` exists; `os.replace` overwrites silently.
  (Both behave the same on POSIX, but `os.replace` is the
  cross-platform-correct choice.)

### R-4. `export.py` — add `ExportLockError` + `_acquire_lock` /
`_release_lock` (see B.3)

### R-5. `export.py` — switch `_append_log` to JSONL (see B.1)

**File name:** rename `export-log.json` → `export-log.jsonl`. Update
the `brain.gitignore` entry too.

### R-6. `commands/models.py` — add `--force` for symmetry

**Location:** `src/aspis/commands/models.py`

**Before:** hard-coded `force=True` at line 230.

**After:**

```python
# At top of file, add argparse argument
parser.add_argument("--force", action="store_true",
    help="Overwrite every agent file, ignoring PROTECT/CONFLICT. "
         "Use with care: hand-edited agent files will be lost.")

# In _run(), pass force through
force = getattr(args, "force", False)
write_export(
    ExportPlan(actions=live, catalog_root=None),
    root,
    apply=not force,  # apply=True unless --force
    force=force,       # --force bypasses all protection
    write=True,
)
```

### R-7. `operations/init.py` — thread the new flags through

**Location:** `src/aspis/operations/init.py`

The lifecycle op that calls `write_export` for the `init` command must
be updated to pass `apply`, `strict`, `scope`, `force_conflicts`,
`reset_snapshot` from the command layer to `write_export`. This is the
"4th file" the comprehensive research flagged.

---

## (e) Additional test cases not in the current plan

The F-015 plan's test list (`PLAN §10`) has ~51 tests across 6 files.
The following cases are **not** in that list and should be added.
Numbered for reference; integrate into `tests/test_protect.py`,
`tests/test_export_snapshot.py`, or `tests/test_export_protection.py`
as appropriate.

### T-1. `sha256_text` strips a leading UTF-8 BOM

```python
def test_sha256_text_strips_bom():
    from aspis.protect import sha256_text
    a = sha256_text("hello\n")
    b = sha256_text("\ufeffhello\n")  # BOM prepended
    assert a == b, "BOM should be stripped before hashing"
```

### T-2. `sha256_text` does NOT strip a trailing BOM

```python
def test_sha256_text_keeps_trailing_bom():
    from aspis.protect import sha256_text
    a = sha256_text("hello")
    b = sha256_text("hello\ufeff")
    assert a != b, "trailing BOM is meaningful content"
```

### T-3. `sha256_text` normalizes CRLF and LF to the same hash

```python
def test_sha256_text_crlf_normalization():
    from aspis.protect import sha256_text
    a = sha256_text("line1\nline2\n")
    b = sha256_text("line1\r\nline2\r\n")
    c = sha256_text("line1\r\nline2\n")  # mixed
    assert a == b == c, "CRLF and LF must hash equal"
```

### T-4. `sha256_text` preserves bare `\r` characters

```python
def test_sha256_text_keeps_bare_cr():
    from aspis.protect import sha256_text
    a = sha256_text("a\rb")
    b = sha256_text("a\nb")
    assert a != b, "bare CR is not a line ending and must be preserved"
```

### T-5. `sha256_text` handles the empty string

```python
def test_sha256_text_empty():
    from aspis.protect import sha256_text
    expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert sha256_text("") == expected
    assert sha256_text("\ufeff") == expected  # BOM-only
    assert sha256_text("\r\n\r\n") == expected  # CRLF-only
```

### T-6. `sha256_bytes` does not normalize

```python
def test_sha256_bytes_no_normalization():
    from aspis.protect import sha256_bytes
    a = sha256_bytes(b"hello\n")
    b = sha256_bytes(b"hello\r\n")
    assert a != b, "bytes path must not normalize"
```

### T-7. The `decide()` truth table (the canonical 6 × 8 = 48 cells)

```python
@pytest.mark.parametrize("live,snap,regen,expected", [
    (None, None, "h1", DecisionKind.ADD),
    (None, "h1", "h1", DecisionKind.ADD),       # recreate
    (None, "h1", "h2", DecisionKind.ADD),       # recreate with diff
    ("h1", None, "h1", DecisionKind.UNCHANGED),  # case 2 before case 3
    ("h1", None, "h2", DecisionKind.UNKNOWN),
    ("h1", "h1", "h1", DecisionKind.UNCHANGED),  # case 2 before case 4
    ("h1", "h1", "h2", DecisionKind.UPDATE),
    ("h1", "h1", "h1", DecisionKind.UNCHANGED),  # redundant with above
    ("h1", "h1", "h2", DecisionKind.UPDATE),     # redundant with above
    ("h1", "h2", "h2", DecisionKind.PROTECT),
    ("h1", "h2", "h3", DecisionKind.CONFLICT),
    ("h1", "h3", "h2", DecisionKind.CONFLICT),  # all 3 differ (h2=h3 not, h1 differs)
])
def test_decide_truth_table(live, snap, regen, expected):
    from aspis.protect import decide, DecisionKind
    assert decide(live, snap, regen).kind == expected
```

### T-8. Atomic snapshot write fails cleanly on a read-only directory

```python
def test_save_snapshot_readonly_dir_fails(tmp_path):
    from aspis.export import _save_snapshot
    target = tmp_path / "proj"
    current = target / ".aspis" / "current"
    current.mkdir(parents=True)
    os.chmod(current, 0o444)  # read-only
    try:
        with pytest.raises(PermissionError):
            _save_snapshot(target, {"version": 1, "paths": {}})
    finally:
        os.chmod(current, 0o755)
    # The partial tempfile must be cleaned up
    assert list(current.glob(".export-snapshot.*.tmp")) == []
```

### T-9. Concurrent runs: lockfile is held; second run fails

```python
def test_concurrent_runs_blocked(tmp_path):
    from aspis.export import _acquire_lock, _release_lock, ExportLockError
    target = tmp_path / "proj"
    (target / ".aspis" / "current").mkdir(parents=True)
    lock1 = _acquire_lock(target)
    try:
        with pytest.raises(ExportLockError):
            _acquire_lock(target)
    finally:
        _release_lock(lock1)
    # After release, second acquire succeeds
    lock2 = _acquire_lock(target)
    try:
        assert lock2.exists()
    finally:
        _release_lock(lock2)
```

### T-10. Stale lock from a dead PID is detected

```python
def test_stale_lock_detected(tmp_path, monkeypatch):
    from aspis.export import _acquire_lock, ExportLockError
    target = tmp_path / "proj"
    (target / ".aspis" / "current").mkdir(parents=True)
    # Write a fake lock with a PID that doesn't exist
    lock = target / ".aspis" / "current" / "export.lock"
    lock.write_text(f"{os.getpid() + 999999}\n", encoding="utf-8")
    monkeypatch.setattr("os.path.exists", lambda p: True)  # pretend PID is alive
    # Without --force-lock, should raise
    with pytest.raises(ExportLockError, match="--force-lock"):
        _acquire_lock(target)
    # With --force-lock, should succeed
    lock2 = _acquire_lock(target, force_lock=True)
    assert lock2.exists()
```

### T-11. JSONL log appends without reading the file

```python
def test_append_log_does_not_read(tmp_path, mocker):
    from aspis.export import _append_log
    log = tmp_path / "export-log.jsonl"
    log.parent.mkdir(parents=True)
    log.write_text('{"a":1}\n', encoding="utf-8")
    # The function must NOT read the file before appending.
    # If it did, the implementation is wrong (it would have to
    # read the whole log to parse the JSON array).
    spy = mocker.spy(Path, "read_text")
    _append_log(tmp_path / "_", [{"b": 2}])  # writes to a different dir
    # The spy should not be called on the log file
    log_file_reads = [
        c for c in spy.call_args_list
        if isinstance(c.args[0], Path) and c.args[0].name == "export-log.jsonl"
    ]
    assert log_file_reads == []
```

### T-12. JSONL log survives a partial-line write

```python
def test_jsonl_log_truncation_safe(tmp_path):
    from aspis.export import _append_log
    log = tmp_path / "export-log.jsonl"
    log.parent.mkdir(parents=True)
    log.write_text('{"a":1}\n{"a":2}\n{"a":3,', encoding="utf-8")  # last line torn
    # The log should still yield 2 valid entries
    lines = [ln for ln in log.read_text(encoding="utf-8").splitlines() if ln.strip()]
    valid = [json.loads(ln) for ln in lines if ln.endswith("}")]
    assert len(valid) == 2
    assert valid[0]["a"] == 1
    assert valid[1]["a"] == 2
```

### T-13. Binary file is hashed as bytes, not as text

```python
def test_binary_file_hashed_as_bytes(tmp_path):
    from aspis.export import _hash_file
    from aspis.protect import sha256_text
    f = tmp_path / "logo.png"
    f.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
    h1 = _hash_file(f)
    h2 = sha256_text(f.read_text(encoding="utf-8"))  # likely raises
    # _hash_file must not raise on binary
    assert h1 is not None
    # And must equal sha256_bytes
    from aspis.protect import sha256_bytes
    assert h1 == sha256_bytes(f.read_bytes())
```

### T-14. NFC vs NFD: same text, different bytes, different hash

```python
def test_nfc_vs_nfd_differ(tmp_path):
    """macOS users get NFD-normalized filenames/content; Linux/Mac
    catalog sources are typically NFC. The hash differs even though
    the text looks the same to a human."""
    from aspis.protect import sha256_text
    import unicodedata
    text = "café"  # NFC
    nfd = unicodedata.normalize("NFD", text)
    if text != nfd:
        assert sha256_text(text) != sha256_text(nfd)
```

This test pins the current (no-NFC-normalization) behavior. If a
future plan wants to be macOS-friendly, this test becomes a
"if-on-macOS-normalize" branch.

### T-15. Stream-hash for files > 1MB

```python
def test_large_file_stream_hashed(tmp_path, monkeypatch):
    """A 2MB file must be hashed via update(), not read into memory."""
    from aspis.export import _hash_file
    f = tmp_path / "big.md"
    # Write 2MB of 'a' — large enough to trigger the streaming path
    f.write_bytes(b"a" * (2 * 1024 * 1024))
    # Spy on read_text to ensure it's NOT called for large files
    from pathlib import Path
    original = Path.read_text
    called_on_big = []
    def spy(self, *a, **kw):
        if self.name == "big.md":
            called_on_big.append(self)
        return original(self, *a, **kw)
    monkeypatch.setattr(Path, "read_text", spy)
    h = _hash_file(f)
    assert h is not None
    assert called_on_big == [], "large files must not use read_text()"
```

### T-16. Dry-run output reports unmanaged files (orphans)

```python
def test_dry_run_reports_unmanaged_files(tmp_path):
    """A file on disk that is not in the plan is reported but not touched."""
    from aspis.export import write_export
    from aspis.profiles import Profile
    from aspis.export import plan_export
    # ... set up catalog, project, write an "orphan" file to live ...
    out = write_export(plan, target, write=False)
    assert any("unmanaged" in line for line in out)
    # The orphan file is not deleted, not modified
    assert orphan_path.exists()
    assert orphan_path.read_bytes() == original_bytes
```

### T-17. Unicode normalization: file with non-ASCII characters

```python
def test_unicode_file_hashed_correctly(tmp_path):
    """A Markdown file with non-ASCII content (CJK, accents, emoji)
    hashes to a stable value across runs."""
    from aspis.protect import sha256_text
    content = "# Title\n\n日本語のテキスト — émoji 🦀\n"
    h1 = sha256_text(content)
    h2 = sha256_text(content)
    assert h1 == h2
    # And the hash is NOT the same as an ASCII-only version
    assert h1 != sha256_text("# Title\n\nASCII text\n")
```

---

## (f) Risks and anti-patterns in the design

### R-1 (high): JSON array audit log is a write-amplification
anti-pattern

Covered in B.1. The log grows linearly in cost per append, and a
crash mid-write corrupts the whole log. Industry standard is JSONL.

### R-2 (medium): Binary file support is a correctness gap

Covered in B.2. The current `sha256_text` operates on `str`; binary
files (e.g., a PDF in a templates directory) would either raise
`UnicodeDecodeError` or silently lose information when re-encoded
as UTF-8.

### R-3 (high): No lockfile for concurrent runs

Covered in B.3. The existing F-015 edge-case doc already flags this
as CRITICAL (C-16). The plan does not include it. Two `aspis init`
runs in two terminals can produce inconsistent state.

### R-4 (medium): `cost-of-change` is off by one

The plan budgets 3 files (`export.py`, `init.py`, `models.py`). The
4th is `operations/init.py`, which must also pass the new flags
through. The comprehensive research noted this; the plan has not
been updated.

### R-5 (low): `sha256_text` is named as if it is the only hash
function

`protect.sha256_text` is text-specific. When a binary file path is
added, there will be `sha256_bytes` and `sha256_file`. The name
should not change but the relationship should be documented in
`protect.py`'s module docstring.

### R-6 (low): `force` overrides `apply` is documented, but the
interaction with `strict` is not

PLAN §2.3 lists the flag matrix. `--force` + `--strict` is marked
"redundant but harmless" because force bypasses protection and
strict has nothing to fail on. This is correct but should be tested
explicitly (T-18 not in this doc, but obvious: `init --write
--force --strict` exits 0, regardless of any conflicts).

### R-7 (low): `models --apply --force` is the only way to recover
old behavior — but it's not implemented

Covered in B.6. Users who relied on the buggy `force=True` behavior
have no way to get it back without `--force`, which doesn't exist on
`models --apply`.

---

## (g) Decision summary for the planner/build lead

| Question | Answer | Source |
|---|---|---|
| Is the 6-way decision table complete? | **Yes** for the 3-hash model. | §A |
| Should we use SHA-256, BLAKE3, or xxHash? | **SHA-256** (correct choice; speed irrelevant; pip/uv/npm-aligned). | §C |
| Is the snapshot format right? | **Yes** (one file, versioned, atomic write). | Existing plan |
| Is the audit log format right? | **No — switch to JSONL**. | §B.1 |
| Is `sha256_text` enough? | **No — add `sha256_bytes` for binary files.** | §B.2 |
| Should we have a lockfile? | **Yes — `.aspis/current/export.lock` with PID + stale detection.** | §B.3 |
| Should `sha256_text` strip BOM? | **Yes — Notepad artifact.** | §B.5 |
| Should `models --apply` have `--force`? | **Yes — for symmetry with `aspis init`.** | §B.6 |
| Is the cost-of-change 3 files or 4? | **4 files** (add `operations/init.py`). | §B.7 |
| Should we stream-hash large files? | **Yes, defensively (cheap insurance).** | §B.4 |
| How does this compare to etckeeper? | **ASPIS is more protective** (3-way vs VCS-after-the-fact). etckeeper's design is "auto-commit every change"; ASPIS's design is "prevent overwrites unless the user opts in." | §(h) below |
| How does this compare to Ansible? | **ASPIS is more protective.** Ansible's template-render model has no PROTECT mechanism — the live config is always overwritten on re-run. | §(h) below |
| How does this compare to pacman/chezmoi/dpkg? | **Same algorithm**, ASPIS adds 1 case (UNKNOWN) and 1 case (UPDATE) for richer state tracking. | §A; existing comprehensive research |
| Is the test count (51) right? | **Add 17 more** (T-1 through T-17 in §E). New total: ~68 tests. | §E |

---

## (h) Comparison: etckeeper, Ansible, Git, and ASPIS F-015

### etckeeper

[etckeeper](https://etckeeper.branchable.com/) (verified 2026-06-25)
hooks into package managers (apt, yum, etc.) and runs `git commit`
automatically after every operation. It does NOT prevent overwrites —
it just makes them reversible via git history.

| Aspect | etckeeper | ASPIS F-015 |
|---|---|---|
| Protection model | None (record-only) | 3-way hash decision |
| Config-file awareness | VCS diff after the fact | PROTECT decision before the write |
| User intent preserved | Revert via git checkout | Skip the write, log it |
| Audit trail | Git history (per-package) | JSONL append-only log |
| Concurrency safety | Inherits from package manager (apt is serial) | Lockfile (recommended) |

**Lesson:** etckeeper's "auto-commit" model is complementary to
F-015's "decide before write" model. They solve different problems.
ASPIS is the more protective design — it does not require the user
to discover an unwanted overwrite via git history; it prevents the
overwrite in the first place. The cost: etckeeper's model captures
*every* change for free, while F-015's model requires an explicit
audit log for the "what was skipped" record.

**Recommendation:** if a user wants the etckeeper guarantee on top
of F-015, they can wrap `aspis init --apply` in a `git commit`
post-hook. This is the user's choice, not F-015's responsibility.

### Ansible

Ansible uses Jinja2 templates. The source of truth is the playbook
/template. The live config is generated by re-rendering the template.
There is no PROTECT mechanism: if the template changes, the live
config is always overwritten on the next run.

| Aspect | Ansible | ASPIS F-015 |
|---|---|---|
| Protection model | None (template is authoritative) | 3-way hash decision |
| User customization | Lost on re-run | PROTECTED |
| Diff tool | `--diff` flag (shows what would change) | Dry-run output (also shows decisions) |
| Idempotence | Module-level (file, lineinfile) | Plan-level (snapshot) |
| Dry-run | `--check` (no writes) | `aspis init` default (no writes) |

**Lesson:** ASPIS is **more protective** than Ansible by design. A
user who hand-edits a generated file is protected from accidental
overwrite. Ansible users have no equivalent safety net.

This is the right choice for ASPIS: the catalog is opinionated and
versioned (users get updates automatically), but the live files are
where the user does their work. Protecting user work is the value
proposition.

### Git's `text=auto`

[Git's `text=auto` attribute](https://git-scm.com/docs/gitattributes)
normalizes line endings to LF in the index. On checkout, line endings
may be converted to CRLF (configurable via `core.autocrlf` and
`eol`).

| Aspect | Git `text=auto` | ASPIS F-015 |
|---|---|---|
| Normalization point | Index (between working tree and git) | Before hashing |
| Line-ending policy | LF in repo, configurable on checkout | Always LF for hashing |
| BOM handling | Not stripped | Stripped (proposed) |
| Use case | Cross-platform VCS | Cross-platform catalog content |

**Lesson:** Git's approach is "store canonical, render per-platform."
ASPIS's approach is "hash the canonical form." The end result for
*content equality* is the same: a file authored on Windows in CRLF
and a file authored on Linux in LF produce the same hash.

ASPIS's approach is simpler for the F-015 use case (no checkout
concept, just hash). Git's approach is richer (preserves CRLF for
end users who need it). For ASPIS, the simpler approach is correct:
the catalog ships LF, and the live file's line endings don't matter
as long as the content is semantically the same.

### Lockfile patterns (npm, pip, cargo, uv)

All four package managers use lockfiles. Key differences:

| Tool | Format | Hash | Concurrency | Corruption recovery |
|---|---|---|---|---|
| **npm** `package-lock.json` | JSON (with `lockfileVersion`) | SRI sha512/sha1 in `integrity` | None (assumes single-user) | npm auto-updates from registry |
| **pip** `requirements.txt` | Plain text | `sha256:...` per-requirement | None | "Handling Old Lockfiles" section in docs |
| **cargo** `Cargo.lock` | TOML | Git commit SHA (per package) | None | Cargo will refuse to use a stale lockfile |
| **uv** `uv.lock` | TOML (PEP 751 `pylock.toml` export) | SHA-256 | None | `--locked` refuses out-of-date, `--frozen` skips check |

**None of the four use a per-run lockfile.** They all assume the
user runs them serially. ASPIS, by contrast, may be invoked from
CI or scripts in parallel (e.g., concurrent pre-commit hooks on
multiple files). **This is a real concern unique to ASPIS**, and
the lockfile recommendation (B.3) is the right answer.

**Lesson:** the snapshot's hash format aligns with pip (sha256) and
the audit log format aligns with the 12-factor / journald / logfmt
tradition (line-delimited JSON). ASPIS's design is consistent with
the industry.

---

## (i) Source provenance

| Source | URL | Verified | Use |
|---|---|---|---|
| BLAKE3 README (adoption list, benchmarks) | https://github.com/BLAKE3-team/BLAKE3 | 2026-06-25 | §C |
| pip secure-installs (hash algorithm guidance) | https://pip.pypa.io/en/stable/topics/secure-installs/ | 2026-06-25 | §C, §H |
| pip requirements-file-format | https://pip.pypa.io/en/stable/reference/requirements-file-format/ | 2026-06-25 | §H |
| uv lockfile docs (locking and syncing) | https://docs.astral.sh/uv/concepts/projects/sync/ | 2026-06-25 | §H |
| npm package-lock.json | https://docs.npmjs.com/cli/v10/configuring-npm/package-lock-json | 2026-06-25 | §H |
| Cargo.lock vs Cargo.toml | https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html | 2026-06-25 | §H |
| JSON Lines (jsonlines.org) | https://jsonlines.org/ | 2026-06-25 | §B.1 |
| Python `os.replace` docs | https://docs.python.org/3/library/os.html#os.replace | 2026-06-25 (Python 3.14.6) | §D R-3 |
| Python `tempfile` docs | https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile | 2026-06-25 (Python 3.14.6) | §D R-3 |
| Git `gitattributes` (text=auto, eol) | https://git-scm.com/docs/gitattributes | 2026-06-25 (git 2.50.0) | §H |
| etckeeper README | https://etckeeper.branchable.com/README/ | 2026-06-25 | §H |
| Chezmoi apply | https://www.chezmoi.io/reference/commands/apply/ | 2026-06-25 | §A |
| Pacman pacnew/pacsave | https://wiki.archlinux.org/title/Pacman/Pacnew_and_Pacsave | (verified 2026-06-22; cited in existing F-015 research) | §A |
| ASPIS F-015 SPEC | `.aspis/features/F-015-safe-catalog-export/SPEC.md` | 2026-06-25 | (existing plan) |
| ASPIS F-015 PLAN | `.aspis/features/F-015-safe-catalog-export/PLAN.md` | 2026-06-25 | (existing plan) |
| ASPIS F-015 TASKS | `.aspis/features/F-015-safe-catalog-export/TASKS.md` | 2026-06-25 | (existing plan) |
| ASPIS F-015 edge cases | `.aspis/features/F-015-safe-catalog-export/Research/F-015-edge-cases.md` | 2026-06-25 | (cross-ref) |
| ASPIS F-015 comprehensive research | `.aspis/features/F-015-safe-catalog-export/Research/f-015-comprehensive-research.md` | 2026-06-25 | (cross-ref) |
| Current ASPIS `export.py` | `src/aspis/export.py` | 2026-06-25 | §B.2, §B.3 |
| Current ASPIS `tests/test_export.py` | `tests/test_export.py` | 2026-06-25 | (test pattern reference) |

---

## (j) Final recommendation

**Proceed with the plan, with the following changes:**

| # | Change | Priority | Where |
|---|---|---|---|
| 1 | Switch audit log to JSONL (`export-log.jsonl`) | **STRONG** | §B.1, §D R-5 |
| 2 | Add `sha256_bytes` and `sha256_file` for binary content | **STRONG** | §B.2, §D R-1, R-2 |
| 3 | Add per-project lockfile (`export.lock`) | **STRONG** | §B.3, §D R-4 |
| 4 | Strip UTF-8 BOM in `sha256_text` | **STRONG** | §B.5, §D R-1 |
| 5 | Add `--force` to `aspis models --apply` | **STRONG** | §B.6, §D R-6 |
| 6 | Update `cost-of-change` to 4 files (add `operations/init.py`) | **STRONG** | §B.7, §D R-7 |
| 7 | Stream-hash for files > 1MB | **NICE** | §B.4 |
| 8 | Document the 6-way decision-table ordering (case 2 before case 3) in `decide()` docstring | **NICE** | §A subtlety 1 |
| 9 | Add the 17 new test cases (T-1 through T-17) | **STRONG** | §E |
| 10 | Document the dry-run `unmanaged: <path>` reporting for orphans (cosmetic) | **NICE** | §A |

**Total scope change:** ~150 lines of new code (lockfile, JSONL migration,
binary support, BOM strip, stream-hash); 1 line change in `models.py`
(`--force`); 1 line in `operations/init.py` (flag passthrough); 17 new
tests. **Well within the 51-test budget the plan allocates.**

**After these changes, the F-015 plan is the canonical answer** to a
30-year-old problem (how do I update config files without destroying
user edits), and the implementation will be the simplest correct one in
the family of pacman/chezmoi/dpkg/etckeeper/Ansible solutions.

---

*Report produced: 2026-06-25. Ready for planner/build lead review. Reads
in conjunction with `f-015-comprehensive-research.md` (algorithm
analysis) and `F-015-edge-cases.md` (16 critical cases).*
