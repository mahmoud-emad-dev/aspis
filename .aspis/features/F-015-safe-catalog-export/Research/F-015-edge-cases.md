# F-015 Edge-Case Analysis — Safe Catalog Export

**Author:** Test Lead
**Date:** 2026-06-24
**Feature:** F-015 — hash-based snapshot protection for `write_export`
**Branch:** feature/F-015-exporter-hardening (planned, not yet on disk)
**Status:** Analysis only — no code, no test execution. Input to the planner/build lead for T-NN sizing.

## Context the analysis rests on

- The exporter (`src/aspis/export.py`) currently does a binary `force=True/False` overwrite, with no awareness of "what the last export wrote."
- The init op (`src/aspis/operations/init.py`) calls `write_export(plan, root, force=force, write=write)`.
- The models command's `--apply` (`src/aspis/commands/models.py:230`) calls `write_export(..., force=True, write=True)` — a hard-coded overwrite that is the proximate cause of the "mode corruption" bug.
- Bootstrap's lead promotion (`src/aspis/operations/bootstrap.py` + `src/aspis/promotion.py`) edits the live `.opencode/agents/<lead>.md` files in place (frontmatter-only) to flip `mode: subagent → primary`. This is the *first* customization the exporter will see, and the failure mode the snapshot must protect.
- The catalog has 9 agents shipped with `mode: subagent` (the 4 promoted leads + 5 support/workers). `promotion.promote_leads` flips the 4 leads at bootstrap. Today, the next `init --write` (or any `models --apply`) re-renders them from catalog and reverts the promotion.

## How the snapshot decision tree works (recap)

For each `target = assetkinds.target(kind, runtime, rel)` in the plan, compute three SHA-256 hashes over the rendered bytes (or copied bytes for `op=copy`):

- `L` = hash of the live file on disk (None if file does not exist)
- `S` = hash stored in `.aspis/current/export-snapshot.json` (None if first run)
- `N` = hash of the file the exporter would write right now (catalog render or copy)

The five states:

| State | L | S | N | Decision |
|---|---|---|---|---|
| `NEW` | None | None | any | write; record `N` in snapshot |
| `IDENTICAL` | ==S | any | ==S | skip; no write |
| `CATALOG-CHANGED` | ==S | any | !=S | write; record `N` |
| `LIVE-CUSTOMIZED` | !=S | !=N | !=L | skip; report customization; do not touch snapshot |
| `CONFLICT` | !=S | !=L | !=N | both changed; refuse to write; require `--force-conflicts` |

A path that exists in the plan but not in the snapshot is `S = None`; treated as NEW only when `L = None`. A path that exists in the plan AND in the snapshot but `L = None` is a "live deleted" case (handle below).

---

## CRITICAL — must handle for v1

### C-1. Mode corruption on re-export (the bug the feature exists to fix)

**Scenario:** `src/aspis/data/catalog/agents/{system,planning,build,reviewer}-lead.md` all ship `mode: subagent`. After `aspis bootstrap`, `promotion.promote_leads` edits the live `.opencode/agents/<lead>.md` to `mode: primary`. The user then runs `aspis init --write` (or `aspis models --apply`).

- Snapshot hash `S` = rendered subagent form (from the previous export).
- Live hash `L` = primary form (from promotion).
- New render hash `N` = subagent form (catalog is unchanged).
- `L != S` AND `N == S` AND `L != N` → **LIVE-CUSTOMIZED**, skip the file. Mode preserved. ✓

**Expected behavior:** The exporter reports the four promoted leads as `LIVE-CUSTOMIZED` in dry-run output. With `--write`, it skips the write and does not touch the snapshot entry. The next `bootstrap` (idempotent) sees `mode: primary` and `result.already` contains the four leads.

**Test seams:** `tests/test_export.py` (add `test_snapshot_preserves_live_promotion`), `tests/test_promotion.py` (add `test_promotion_survives_re_export`).

### C-2. `aspis models --apply` re-renders with the current `force=True` — must change

**Scenario:** `commands/models.py:230` hard-codes `force=True` when re-rendering agents after a model change in `agent-models.yaml`. With the snapshot, force-overwrite reverts the promotion (C-1) on every model sync.

**Expected behavior:** Drop `force=True` from `models --apply`. Use the snapshot's 3-way check. A model change is a `CATALOG-CHANGED` (render output differs from snapshot), so it is applied automatically. A manual mode change in the live file is `LIVE-CUSTOMIZED` and is preserved.

**Risk:** If the user runs `models --apply` while the catalog also changed (e.g., a permission tweak landed), the agent file is `CONFLICT` — refuse and require `--force-conflicts`.

### C-3. First export (no snapshot)

**Scenario:** A freshly initialized project runs `aspis init --write` for the first time. No `.aspis/current/export-snapshot.json` exists. The brain scaffold was created in a prior step.

**Expected behavior:** `S = None` for every plan target. If `L = None`, write as `NEW`. If `L` exists (a previously-shipped or hand-written file), do **not** assume it is customized: it could be a leftover from a pre-F-015 ASPIS or a hand-init. **Preserve the live file** and report it as `live-existed-no-snapshot`; the snapshot is only created for `NEW` writes. Subsequent exports use the snapshot normally. This is the "first run" mode: a partial init that does not destructively overwrite an already-customized project.

**Test seam:** `tests/test_export.py::test_first_export_preserves_existing_live` — pre-place a live file with `mode: primary`, run export with no snapshot, assert live file is untouched and snapshot is not created (or only has the `NEW` entries).

### C-4. Snapshot file corrupted or invalid JSON

**Scenario:** A user or hook edits the snapshot (or it gets truncated by a crash). Next export reads invalid JSON.

**Expected behavior:** Refuse to apply. Emit a finding: "snapshot at `.aspis/current/export-snapshot.json` is corrupted; cannot determine which files were last exported." Exit non-zero in `--strict` mode; in default mode, allow the user to pass `--reset-snapshot` to start fresh (this is a destructive action: confirm with a second flag, e.g., `--reset-snapshot` requires `--force`, or prompt).

**Why critical:** A "treat as missing" fallback would silently lose every live customization — exactly the failure mode the feature is supposed to prevent.

### C-5. Snapshot duplicate keys

**Scenario:** Hand-edited or merge-conflict snapshot has the same target path twice.

**Expected behavior:** Refuse to apply. Emit a finding listing the duplicates. Do not silently last-wins — the snapshot is a contract, and corruption must be loud.

### C-6. Live file deleted between export and re-export

**Scenario:** A plan target exists in the snapshot (`S` is set). The live file on disk is gone (user deleted it, or a runtime cleanup removed it). The plan still includes the target.

**Expected behavior:** Treat as `L = None`, `S != None`, `N = render()`. The decision is: write it (the catalog still wants it). Classify as `recreate` (a sub-status of `CATALOG-CHANGED` or its own state). Record `N` in the snapshot.

**Edge within the edge:** What if the user *intended* the deletion (e.g., they removed the runtime and the file should not exist)? Then the plan should not contain the target — handled by the `runtimes` filter in `plan_export`. If the runtime is still in the profile, the user wanted the file. Write it.

### C-7. `force=True` (existing flag) must keep working for `init --write --force`

**Scenario:** User has a broken state, wants to "make it look like a fresh init." Runs `aspis init --write --force`.

**Expected behavior:** `--force` overwrites every state, including `LIVE-CUSTOMIZED` and `CONFLICT`. The snapshot is updated to the new render hashes. This preserves the existing CLI contract: `--force` means "I know what I'm doing." A future `init --write` (without `--force`) sees the new snapshot and is in `IDENTICAL`/`CATALOG-CHANGED` only.

### C-8. `--scope` semantics must be on the catalog source path, not the target

**Scenario:** `--scope agents/lead.md` is passed. The plan has two per-runtime actions for this source: `.opencode/agents/lead.md` and `.claude/agents/lead.md`.

**Expected behavior:** Scope filters by **catalog source** (the `(kind, rel)` pair). Both per-runtime targets are written/skipped together. The scope is the user's natural unit ("this agent/skill/command"), not the project-relative path. A scope of `.opencode/` is rejected with a hint: "scope targets catalog sources, not project paths; use --runtime opencode instead."

**Why critical:** This is the only sane way to scope per-runtime kinds. If scope were on the target, a rename or runtime change would break it.

### C-9. Scope path is a directory

**Scenario:** `--scope agents/` or `--scope skills/`.

**Expected behavior:** Treat as a prefix match on the catalog source. All `(kind, rel)` with `rel.startswith("agents/")` are in scope. For brain kinds this is one plan action; for per-runtime kinds this is `len(runtimes)` actions.

### C-10. New runtime added to project (OpenCode-only → OpenCode+Claude)

**Scenario:** Project was exported with `runtimes: [opencode]`; the user adds Claude. Plan now has Claude targets; snapshot has only OpenCode targets.

**Expected behavior:** Claude targets are `NEW` (no entry in snapshot). Write them; record hashes. OpenCode targets are checked against the snapshot normally. ✓

### C-11. Runtime removed from project

**Scenario:** Project had `runtimes: [opencode, claude]`, was exported, then Claude is removed from the profile.

**Expected behavior:** Claude targets are not in the plan. Do **not** delete the on-disk `.claude/...` files. The snapshot retains the Claude entries; if the user re-adds Claude, the next export will check the existing files against the snapshot and find them `IDENTICAL` (or `CATALOG-CHANGED` if the catalog changed). Add a `--prune` flag in a later iteration for explicit removal.

### C-12. Bootstrap integration — promotion + models --apply in sequence

**Scenario:** A fresh project runs `aspis init` then `aspis bootstrap`. Bootstrap calls `promotion.promote_leads(write=True)` and then `aspis models --apply` (via `_sync_models` → `subprocess "models --sync"`; the `_apply` path runs when `--apply` is the explicit verb). With F-015, `models --apply` no longer force-overwrites.

**Expected behavior:** After bootstrap's promotion, the live files have `mode: primary`. The next `init --write` (or `models --apply`) sees `LIVE-CUSTOMIZED` and preserves. Bootstrap itself does not call `write_export`; it is a post-init effect. But a `models --apply` immediately after bootstrap is now safe (was destructive before C-2). ✓

### C-13. Empty file in catalog

**Scenario:** A catalog source is empty bytes (0 bytes). The render produces only frontmatter (because the body is empty) — non-empty output.

**Expected behavior:** The snapshot records the *rendered* hash, not the source hash. The render path is already byte-stabilized (UTF-8, `newline="\n"`). Verify the renderer never produces 0 bytes for a non-empty frontmatter (or document it if it does — and decide what 0-byte live files mean).

### C-14. Hashes must be over raw bytes, not text

**Scenario:** User has CRLF in a file (Windows editor); render produces LF.

**Expected behavior:** `L` is computed from the raw bytes on disk (open in `rb`). `N` is the rendered bytes (already LF by the writer's `newline="\n"` contract). `S` is whatever was recorded. The state machine is correct regardless of line endings — CRLF triggers `LIVE-CUSTOMIZED` automatically.

**Test seam:** `tests/test_export.py::test_crlf_live_file_is_customized`.

### C-15. UTF-8 BOM handling

**Scenario:** User opens a generated file in Notepad (Windows default), Notepad saves with a BOM, live file has BOM, rendered file does not.

**Expected behavior:** Decision is yours; I lean toward **strip the leading BOM on read for the `L` hash only** (the BOM is a Windows editor artifact, not meaningful user content). This way a user who edits and saves in Notepad does not falsely trigger `LIVE-CUSTOMIZED`. Document this in the snapshot module's docstring. If you choose to keep the BOM as meaningful (it IS a content difference), state so explicitly — but the user-facing experience is "I touched nothing in Notepad, why is my file customized?"

### C-16. Snapshot write must be atomic

**Scenario:** Two `aspis init` runs in two terminals, or a crash mid-export.

**Expected behavior:** The snapshot is written **after all file writes** in a single `tempfile + os.replace` to the final path. The intermediate state (some files written, snapshot not yet updated) is observable by a concurrent reader, but the on-disk snapshot is never torn. Add a per-project lockfile (`.aspis/current/export.lock`) for the run duration to serialize concurrent invocations.

---

## IMPORTANT — should handle, can ship in v1 if scope allows

### I-1. File moved between kinds (agents/ → skills/)

**Scenario:** Catalog renames `catalog/agents/lead.md` to `catalog/skills/lead.md`.

**Expected behavior:** Source-path keying detects this. The old source path (`agents/lead.md`) is no longer in the plan; the new source path (`skills/lead.md`) is. The plan target for the new path is new (different kind → different target prefix). Old live file at `.opencode/agents/lead.md` is in the snapshot but not in the plan → handled as C-11 (left alone). If the user wants the live file gone, they delete it manually or use `--prune` (future).

**Edge:** If the source moves AND the live file was customized (different hash from snapshot), the user loses the customization. Report this as `removed-customized: <old-path> (customization lost if not preserved manually)`. Consider moving the content to the new path's snapshot entry if the customization is recoverable (text-level diff is too complex for v1; defer).

### I-2. File renamed in catalog (path changes, kind stays)

**Scenario:** `agents/lead.md → agents/lead-v2.md`.

**Expected behavior:** Same as I-1. Old live file (`.opencode/agents/lead.md`) is in the snapshot but not in the plan; left alone. New path is `NEW` or `CATALOG-CHANGED` depending on whether it is in the snapshot.

### I-3. Multiple `--scope` flags

**Scenario:** `aspis init --write --scope agents/lead.md --scope skills/`.

**Expected behavior:** Union of in-scope actions. The two flag values are OR'd. Implement as a list, dedupe.

### I-4. `--strict` semantics

**Scenario:** User wants to know about every change before applying.

**Expected behavior:** In `--strict`, refuse to write if any plan target is in `CATALOG-CHANGED` or `CONFLICT` state. The output is the full list of changes; the user must pass `--scope` (limit the set) or `--force-conflicts` (acknowledge conflicts) to proceed. Default behavior is "apply the safe ones, skip the conflicts" — that is, write `NEW` + `CATALOG-CHANGED`, skip `LIVE-CUSTOMIZED` + `CONFLICT`.

### I-5. `--force-conflicts`

**Scenario:** User knows the catalog and live diverge; they want the catalog version.

**Expected behavior:** `CONFLICT` items are overwritten; the snapshot is updated to the new render. `LIVE-CUSTOMIZED` items are still preserved (they are user-only changes; conflicts are two-way changes).

**Subtlety:** The distinction between `LIVE-CUSTOMIZED` and `CONFLICT` is that `CONFLICT` requires both sides to have changed. If the user wants to discard *any* customization, they use `--force`. `--force-conflicts` is the "I know the catalog changed; apply it even though I customized."

### I-6. Concurrent `aspis init --apply` from two terminals

**Scenario:** User runs init in two terminals, perhaps by accident.

**Expected behavior:** Lockfile (C-16) blocks the second run with a clear message: "another `aspis init` is in progress (lock at <path>, age <seconds>)." The lock is released on success, failure, or Ctrl-C. Stale lock detection: if the lock's PID is dead or the lock is older than a threshold (e.g., 10 min), allow takeover with `--force-lock`.

### I-7. `findings` integration

**Scenario:** A `LIVE-CUSTOMIZED` or `CONFLICT` item is found; the system should record it so the next session knows.

**Expected behavior:** Emit a `findings.json` entry with the file path, the snapshot hash, the live hash, the new render hash, and a recommendation (`preserve` / `force-conflicts` / `manual review`). The findings flow already exists (D-014 / `aspis findings`); the exporter should add a `finding_kind = "export-hash-mismatch"` for each non-IDENTICAL, non-NEW state.

### I-8. Large files (hash performance)

**Scenario:** A skill is 10 MB; rendering and hashing should not block the event loop.

**Expected behavior:** Stream the hash (`hashlib.sha256()` is already streaming via `.update()`); do not load the whole file into memory for the hash. For rendered Markdown, the whole string is in memory anyway (small); for `shutil.copytree`-copied skills, hash the *destination* after copy.

### I-9. Binary files (non-Markdown skills)

**Scenario:** A skill includes an image (PNG) or a PDF; the exporter copies it via `shutil.copy2`.

**Expected behavior:** Hashes are over the raw bytes (binary mode). The state machine works. Copying preserves the binary content. The snapshot key uses forward slashes (POSIX) to be portable across Windows and Linux.

### I-10. Snapshot path — `.aspis/current/export-snapshot.json` — and brain gitignore

**Scenario:** The snapshot lives under `.aspis/current/` (machine-generated state). It should be gitignored.

**Expected behavior:** Add `current/export-snapshot.json` to `.aspis/.gitignore` (the brain gitignore) and `current/*.lock` for the lockfile. Verify the existing `reap_stale_gitkeeps` does not delete the snapshot (it only reaps empty directories' `.gitkeep`).

**Why important:** If the snapshot is committed, two developers' exports would conflict at the git level. It is per-machine state, not durable.

### I-11. `init --write` should reset stale `--prune`-style behavior — but not delete unmanaged files

**Scenario:** User runs `init --write` after a profile change that removes some assets.

**Expected behavior:** Plan targets that are no longer present are not in the plan; the exporter does not touch their on-disk files. A future `--prune` flag (not v1) deletes them. The exporter's report lists `unmanaged: <path>` for each snapshot entry not in the plan.

### I-12. Snapshot version field

**Scenario:** The snapshot format evolves (e.g., we add per-file metadata).

**Expected behavior:** Include a `"version": 1` key in the snapshot JSON. On read, if the version is higher than the exporter knows, refuse and tell the user to upgrade. If lower, run a migration or refuse.

### I-13. Dry-run output

**Scenario:** User runs `aspis init` (default dry-run) on a project with a snapshot.

**Expected behavior:** The output shows the full state table: per target, the path, the state (NEW / IDENTICAL / CATALOG-CHANGED / LIVE-CUSTOMIZED / CONFLICT), and the hashes (or just the state and a count). This is the "what would happen" view. No writes, no snapshot update.

### I-14. `aspis models --sync` does not touch agents — verify

**Scenario:** `_sync` writes `agent-models.yaml`. It does not call `write_export`.

**Expected behavior:** Confirmed by reading `commands/models.py:111-193` — only writes `agent-models.yaml`. The snapshot is not involved. ✓

### I-15. Bootstrap does not call `write_export` — verify

**Scenario:** Bootstrap calls `promote_leads`, `_fill_slots`, `_enrich_gitignore`, `_write_project_config`, `_write_manifest`, `_detect_runtimes`, `_sync_models`, `_run_brain_fill`, `_self_clean`, `_record_done`, `_commit_bootstrap`, `_verify_subsystem`. None of these call `write_export`.

**Expected behavior:** Confirmed. Bootstrap's only effect on the runtime is `promote_leads` (regex edit) and `_strip_bootstrap_prose` (text edit). F-015 changes `models --apply` (used by users, not by bootstrap directly), so the bootstrap path is safe by construction.

---

## NICE-TO-HAVE — defer to a follow-up feature

### N-1. `--prune` flag to remove unmanaged files

**Scenario:** User removed a runtime or an asset kind from the profile; the on-disk files are leftover.

**Expected behavior:** `aspis init --write --prune` deletes any file under `.<runtime>/` (and `.aspis/<kind>/`) that is not in the current plan. Dry-run support: `--prune --dry-run` lists what would be deleted. Default behavior: do not delete.

### N-2. Smart editor-BOM detection

**Scenario:** Notepad saves a file with BOM; the user has not actually changed content.

**Expected behavior:** Optionally normalize the BOM away on read for the hash. Already covered in C-15; this is the "make it nicer" version with a config flag.

### N-3. Per-file write report in JSON

**Scenario:** CI / agent wants the change list as a structured artifact.

**Expected behavior:** `aspis init --write --report-json <path>` writes `{target: {state, snapshot_hash, live_hash, new_hash}}` to a file. Useful for downstream automation (e.g., an agent that prompts the user on conflicts).

### N-4. Snapshot compaction / archival

**Scenario:** Snapshot grows over time with entries for removed runtimes/files.

**Expected behavior:** On export, prune entries that have been "unmanaged" for N exports (default 1). Keep an archive at `.aspis/current/export-snapshot.archive.json` for debugging.

### N-5. Detect git smudge/clean filter impact

**Scenario:** The user's `.gitattributes` or `.git/config` has a smudge filter that changes file content on checkout. The post-checkout content differs from what was committed, so the live hash differs from the snapshot.

**Expected behavior:** Hard to detect generically. The current design treats the live hash as authoritative, which is the right call. Document this in the exporter docstring: "the live hash is computed from the bytes on disk, not from git." The user owns their git config.

### N-6. `mtime`-based fast-path for `IDENTICAL`

**Scenario:** Hashing 1000 files is slow; mtime could rule out `IDENTICAL` quickly.

**Expected behavior:** Optional optimization. Hash only when mtime differs from the snapshot's recorded mtime. Risk: any mtime change (e.g., `git checkout`) would force a full hash. Not worth the complexity for v1; defer.

### N-7. Migrations: convert pre-F-015 projects to the snapshot model

**Scenario:** A project has been bootstrapped with v0.1.0b3 (no snapshot). F-015 is installed.

**Expected behavior:** First export under F-015 has no snapshot. Already handled in C-3: preserve live files, snapshot only NEW writes. Subsequent exports work. No migration script needed; the natural first-run behavior is correct.

### N-8. `--scope <target-path>` (target-side scope)

**Scenario:** User wants to scope by project-relative target (e.g., `.opencode/agents/lead.md`), not by source.

**Expected behavior:** Reject as ambiguous (per C-8) or support as a separate `--target` flag. The source-side scope is the only one that makes sense for per-runtime kinds. Defer.

### N-9. Conflict resolution hints (per-file)

**Scenario:** User has a CONFLICT and wants to apply per-file.

**Expected behavior:** `--scope <source>` already narrows the set, and the per-file state is in the dry-run report. A `--resolve <source>=catalog|live` flag could be a future addition.

### N-10. Audit log of past exports

**Scenario:** "When was this file last re-rendered? Did the user customize it?"

**Expected behavior:** A `.aspis/current/export-history.jsonl` (gitignored) with one line per export: timestamp, target, state, hashes. Useful for debugging. Defer.

---

## Test seams — where the cases above plug in

| Test file | Add |
|---|---|
| `tests/test_export.py` | `test_snapshot_preserves_live_promotion` (C-1), `test_first_export_preserves_existing_live` (C-3), `test_crlf_live_file_is_customized` (C-14), `test_duplicate_snapshot_keys_refused` (C-5), `test_corrupt_snapshot_refused` (C-4) |
| `tests/test_promotion.py` | `test_promotion_survives_re_export` (C-1 integration) |
| `tests/test_models_command.py` | `test_models_apply_does_not_revert_promotion` (C-2) |
| `tests/test_init_cli.py` | `test_init_force_overwrites_every_state` (C-7), `test_init_scope_filters_by_source` (C-8, C-9) |
| New: `tests/test_snapshot.py` | All snapshot state-machine cases (5 states × edge cases), concurrent write (C-16) |

---

## Confidence read for the planner

The 5-state model handles every case I can construct, including the mode-corruption bug, the pre-F-015 first run, and the per-runtime reshape. The two real risks are:

1. **UX of the first run (C-3).** A user with a pre-F-015 project runs `init --write` and gets a wall of `live-existed-no-snapshot` reports. The output needs to be actionable: explain what happened and offer `--force` to overwrite.
2. **Concurrent runs (C-16).** A lockfile is a small piece of plumbing, but the OS specifics (PID file, stale lock detection, signal handling) deserve a real test, not a "feels fine" check. I rate this CRITICAL because the failure mode is silent corruption (one run's writes clobber another's snapshot).

Everything else is mechanical once the snapshot module is in place. The 3-hash check is the right algorithm.
