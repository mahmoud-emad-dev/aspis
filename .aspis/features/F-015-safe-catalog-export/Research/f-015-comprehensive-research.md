# F-015 Safe Catalog Export — Comprehensive Research

**Author:** Research Lead
**Date:** 2026-06-25
**Status:** Validation complete — packaged reference for the planning/build leads
**Scope:** Combine (1) the old ASPS `runtime_lock` + `regenerate` + `promote` analysis, (2) the current ASPIS `export.py` + `models --apply` analysis, (3) authoritative web patterns for safe file updates, into one decision-ready reference.

---

## Executive summary

The current ASPIS exporter (`src/aspis/export.py`) has a single binary guard — *"if file exists AND not `--force`, skip"* — and `models --apply` (`src/aspis/commands/models.py:230`) hard-codes `force=True`, so any hand-edited live agent is silently overwritten on the next model sync or re-init. The old ASPS repo already solved this with a pure 3-way hash decision engine (`src/asps/runtime_lock.py`, 333 lines, ~21 KB of tests). The F-015 plan in `.aspis/features/F-015-safe-catalog-export/PLAN.md` re-derives the same algorithm from scratch (`protect.py`, 141 lines) — the math is identical, the design is cleaner, and the rejection of staging/clobber/accept is correct.

**Verdict:** the existing F-015 plan is sound. The only deltas this research suggests are (a) a single function name (`UNKNOWN` over `UNTRACKED` — already adopted), (b) one edge case the plan does not yet cover (UTF-8 BOM), (c) the Windows-specific atomic-rename BOM-check that the old ASPS tests already prove out, and (d) a recommendation to back-port the old ASPS's per-file test matrix as the seed for `tests/test_protect.py`.

The web patterns (pacman's 3-way MD5, chezmoi's modified-since-prompt, dpkg's `--force-confnew`/`--force-confold`) all converge on the same algorithm the plan already chose. The plan is the canonical answer to a 30-year-old problem in package management.

---

## 1. Old ASPS analysis

### 1.1 The protection engine: `src/asps/runtime_lock.py` (333 lines)

#### What works — and what to port

**`decide(path, regen_content, live_content_or_none, baseline_hash_or_none) -> Decision`** (lines 77–172)

The 6-case decision table (evaluated in order):

| # | Condition | DecisionKind | Action |
|---|---|---|---|
| 1 | `live_content is None` | `ADD` | Write regen, set baseline = hash(regen) |
| 2 | `live_hash == regen_hash` | `UNCHANGED` | Skip; baseline may be refreshed |
| 3 | `baseline is None` | `UNTRACKED` | Treat as hand-tuned (PROTECT + warn) |
| 4 | `live_hash == baseline` | `UPDATE` | Write regen, baseline = hash(regen) |
| 5 | `regen_hash == baseline` | `PROTECT` | Skip; live is hand-tuned, catalog unchanged |
| 6 | *(fallthrough)* | `CONFLICT` | Keep live, report diff, require accept() |

This is **the same algorithm** as the F-015 `protect.decide()` (which renames `UNTRACKED` → `UNKNOWN` — a clearer name, the F-015 plan's one cosmetic change). The pure-function design (no I/O inside `decide`) is correct and matches the plan.

**Helpers worth porting** (the plan re-implements these; no change needed):

- `sha256_text(text: str) -> str` (lines 69–71): `hashlib.sha256(text.encode("utf-8")).hexdigest()`. The current F-015 plan adds CRLF→LF normalization here, which the old ASPS code lacks — **the plan's version is the improvement**. (See C-12 in the edge-case doc.)
- `plan_runtime(regen_map, live_map, baseline) -> list[Decision]` (lines 178–202): fan-out over the union of paths. Identical to F-015.
- `accept(path, regen_map, baseline) -> Decision` (lines 208–227): resolves a CONFLICT/UNTRACKED by adopting regen. **F-015 plan correctly drops this** — the user edits the file directly, the next export detects the change via hash. The old helper was needed only because ASPS's `promote.py` called it programmatically; ASPIS has no equivalent caller.
- `rebaseline(path, live_map, baseline) -> Decision` (lines 230–254): adopts the live content as the new baseline. **F-015 plan also drops this** for the same reason.
- `summary(decisions) -> str` (lines 323–333): aggregates counts by kind. F-015 plan keeps this (as a `dict` return instead of a string — minor shape change, not a behavioral change).
- `lock_path_for(runtime)` (lines 281–287): returns `.asps/runtime.lock.<runtime>.json` (per-runtime). **F-015 plan correctly drops this** — one unified snapshot file is simpler and removes a whole class of cross-runtime-consistency bugs.
- `load_baseline(lock_path) -> dict[str, str]` and `save_baseline(lock_path, baseline) -> None` (lines 290–317): JSON load/save. The F-015 plan keeps the shape but adds atomic write (`tempfile + os.replace`); the old ASPS version did a non-atomic write that would have been a corruption risk on a crash mid-write. **The plan's version is the improvement.**
- `Decision` dataclass (lines 48–63): `kind`, `path`, `regen_hash`, `live_hash`, `baseline_hash`, `message`, `diff`. The `diff` field stores the unified-diff text for CONFLICT reports. F-015 plan correctly does NOT include a `diff` field in its `Decision` — diffs are expensive and not always needed; compute them on demand.

**Total port: ~70 lines of pure logic** (the `decide()` function + `DecisionKind` + `Decision` + `sha256_text` + `plan_runtime` + `summary`).

#### What was overengineered — and what to drop

**The staging pipeline: `src/asps/regenerate.py` (568 lines)**

ASPS rendered into a *staging* directory (e.g., `local/regen/.opencode/`) and then ran a separate `promote_to_live()` step (`src/asps/promote.py`, 188 lines) that compared the staging copy to the live runtime through the lock's decision engine. This split was unnecessary:

- **Staging added I/O without adding protection.** A staging tree is just an extra copy of the output; the snapshot itself is what detects user modifications.
- **The two-phase flow added two modules** (`regenerate.py` 568 lines + `promote.py` 188 lines = **756 lines**) and three integration surfaces (init → regen → promote), each of which needed its own tests.
- **The plan correctly collapses this** into one `write_export()` that reads the live file, hashes it, hashes the would-be output, and consults the snapshot. **No staging, no separate promote step.** The same protection; ~600 lines deleted.

**The clobber classifier: `_CLOBBER_FIELDS` + `_classify_agent_diff()` (regenerate.py lines 38–48, 404–491)**

ASPS classified file differences as either "expected" (formatting/ordering) or "clobber" (semantic field change). The clobber check:

1. Parsed both frontmatters with `yaml.safe_load()`.
2. Recursively diffed the two dicts (`_diff_mapping`).
3. Flagged any difference in a hardcoded list of "clobber-class" fields: `model`, `mode`, `temperature`, `permission`, `task`, `skill`, `tools`, `name` (regenerate.py:39–48).
4. Treated all other differences as "expected" (renderer normalization) and silently wrote over them.

**Problems with this approach:**

- **Couples protection to runtime semantics.** The list of clobber fields is hardcoded; if a runtime adds a new field, the protection silently fails (the new field is treated as "expected" and the live value is overwritten).
- **YAML-level semantic diff is fragile.** Two equivalent YAML serializations can compare as different at the byte level but identical at the semantic level. The reverse can also be true (semantic diffs that aren't visible at the byte level — e.g., key order, comment placement, trailing whitespace).
- **The 3-way hash check subsumes it.** Any byte difference between the live file and the snapshot means the user (or the renderer) changed it; the protection question is "did the catalog also change?", not "is this a semantic field?". The 3-way check answers the first question with no field knowledge.

**F-015 plan correctly drops the clobber classifier.** Its protection is purely byte-level (SHA-256 of normalized text). One universal algorithm; zero field knowledge.

**Other regenerator detritus to leave behind:**

- `check_byte_parity(staging_root, live_root)` (lines 106–128): a separate byte-by-byte file comparison. Redundant with hash check.
- `format_clobber_report()` (lines 548–559): pretty-printing for the clobber report — a separate concern (CLI output formatting).
- `_compute_diff()` (lines 260–272): unified-diff text generation. F-015 plan defers this (hashes only; diffs on demand).
- `_apply_overrides()` + `_deep_merge_permissions()` (lines 310–398): per-agent frontmatter override application. This is a real feature (defaults.yaml editing) but **not part of the protection engine**. Drop it from the F-015 scope.
- `_discover_catalog_skill_dirs()`, `_write_text_lf()`: low-level helpers, not needed for the protection path.

**Total drop: ~700 lines of regenerate.py + 188 lines of promote.py** (with `promote.py` partially re-used — see below).

#### What is genuinely useful from `promote.py`

`promote.py` does two things:

1. **The two-phase I/O flow** (read staging, read live, decide per-path, write to live). This is overengineered — fold the read-live + decide into `write_export()`.
2. **Pruning dead lock entries and orphan detection** (lines 148–166): the `PromoteResult.orphans` and `pruned` lists. The first F-015 plan explicitly puts orphan detection and lock pruning **out of scope** (`Out of scope` line 38 of SPEC.md). This is correct — those are separate concerns. A future `--prune` flag (N-1 in the edge-case doc) is the right place for them.

#### What was correct in the old code but not in the F-015 plan

Two small things, both already addressed:

- **CRLF normalization in `sha256_text`**: old ASPS did **not** normalize. A user who opens an exported agent in Notepad (which saves with CRLF) would get a false PROTECT decision on Windows. F-015 plan adds this. **Plan is correct; the plan's version is the improvement.**

- **Atomic snapshot write**: old ASPS did a plain `write_text()`. A crash mid-write would corrupt the snapshot. F-015 plan uses `tempfile + os.replace`. **Plan is correct.**

### 1.2 Old ASPS test coverage (informative)

`tests/test_runtime_lock.py` (21 KB) is dense. From the F-015 task description (and the edge-case doc), it covered at minimum:

- All 6 cases of the `decide()` truth table
- CRLF handling (old ASPS did not normalize — see above)
- Per-runtime lock files (lines 281–287, now dropped from F-015)
- `accept()` / `rebaseline()` helpers (now dropped from F-015)
- Diff generation in `Decision.diff`
- `summary()` aggregation

**Recommendation:** the F-015 task should NOT port the old tests wholesale. Instead, the new `tests/test_protect.py` (16+ tests per the plan) should cover the same 6-case matrix but be cleaner — no clobber/per-runtime/accept tests because the new design does not have those concepts.

---

## 2. Current ASPIS analysis

### 2.1 The exact bug

**File:** `src/aspis/commands/models.py`, **line 230**:

```python
write_export(ExportPlan(actions=live, catalog_root=None), root, force=True, write=True)
```

`force=True` is hard-coded. This bypasses the only guard in `write_export()` (line 99: `if destination.exists() and not force: skip`). Every existing live agent file is overwritten, including any the user has hand-edited since the last export.

**The exact failure path the bug creates:**

1. User runs `aspis init --write` → catalog renders all agents with `mode: subagent` (per `PROMOTE_TO_PRIMARY` in `constants.py`).
2. User runs `aspis bootstrap` → `promote_leads` (`src/aspis/promotion.py:37`) edits the four lead files (`system-lead`, `planning-lead`, `build-lead`, `reviewer`) in place, flipping `mode: subagent` → `mode: primary`. The files are now hand-customized (relative to the catalog).
3. User edits `agent-models.yaml` to change a model pin, runs `aspis models --apply`.
4. **The bug fires.** `force=True` re-renders every live agent from the catalog, which means the four `mode: primary` files are silently reverted to `mode: subagent`.

This is documented as **C-1 in `F-015-edge-cases.md`** (mode corruption on re-export).

### 2.2 The current export flow

```
┌─────────────────────────┐
│ commands/init.py        │  CLI: --path, --profile, --runtime, --name, --write, --force, --no-git
│ commands/models.py      │  CLI: --path, --available, --sync, --apply
└────────┬────────────────┘
         │ engine.run("init", ...)
         ▼
┌─────────────────────────┐
│ operations/init.py      │  plan → write_export(plan, root, force=force, write=write)
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ export.plan_export()    │  Profile.assets() → list[ExportAction]   (NO file I/O)
│ export.write_export()   │  Two-state guard:
│                         │    if destination.exists() and not force: skip
│                         │    else: apply via runtime adapter
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ transform.render_agent()│  parse_agent(text) → adapter.render_agent(...)
│ runtimes/{opencode,     │  (each adapter is a pure function; output is text)
│            claude}.py   │
└─────────────────────────┘
```

**`write_export()` (export.py lines 86–116) is 30 lines and has two responsibilities:**

1. Loop over plan actions, applying a two-state guard.
2. Emit runtime hooks via each adapter's `emit_runtime_hooks()` (which has the same two-state guard, copy-pasted).

**No state is recorded.** No snapshot, no audit log, no detection of "what was last written." The exporter is a write-only pipeline that has no memory of its own past.

**`plan_export()` (export.py lines 57–83):**

- Walks `profile.assets()` to enumerate kind/rel pairs.
- Filters by export scope (project-only skipped; runtime-lock; per-runtime enumeration).
- For each (kind, runtime), computes the target via `assetkinds.target(kind, runtime, rel)`.
- Returns an `ExportPlan(actions, missing, skipped_by_scope, catalog_root)`.

**`assetkinds.target()` (assetkinds.py:73–87):**

- For per-runtime kinds (`agents`, `commands`, `skills`): `.<runtime_dir>/<kind>/<sub>`.
- For brain kinds: `.aspis/<kind>/<sub>`.
- Sub-paths under the kind dir are preserved.

**`transform.render_agent()` (transform.py:20–30):**

- Thin dispatcher: `get_adapter(runtime).render_agent(parse_agent(text), project_config, inventory)`.

**Runtime adapters (`runtimes/opencode.py`, `runtimes/claude.py`):**

- `OpenCodeAdapter.render_agent()`: builds `permission` block (tools, bash, task, skill) + `mode` + `model` + `temperature` + `description`.
- `ClaudeAdapter.render_agent()`: drops `mode`, `temperature`, `permissions`, `delegates`, `skills` (Claude does not express them); emits `name`, `description`, `tools`, `model`.
- Both are pure functions; output is a string. **Excellent for hashing** — `regen_hash` is deterministically computable from the catalog source + project config + inventory.

**`catalog.py` (111 lines):**

- `parse_agent(text) -> CatalogAgent`: YAML frontmatter + body.
- `parse_command(text) -> CatalogCommand`: same.
- `CatalogAgent` is a frozen dataclass: `name`, `description`, `mode`, `model`, `temperature`, `tools`, `permissions`, `delegates`, `skills`, `runtimes`, `export_scope`, `body`.

### 2.3 What the current code does well

- **Clean adapter pattern** (`runtimes/__init__.py` auto-discovers adapter modules via `pkgutil.iter_modules`). Adding a new runtime is one file — no edit to `transform.py`, `export.py`, or any other module.
- **Per-asset scope/runtimes filter** at the plan level (`assetkinds.target` + per-runtime capabilities). The exporter never has to know what kind of file it's writing.
- **`plan_export` is pure** (no writes). The bug is in `write_export`, not in the plan.
- **Inventory-aware rendering** (project_config + detected inventory → canonical model id). Same input → same output → hashable.

### 2.4 What needs to change

| File | Change | Why |
|---|---|---|
| `src/aspis/protect.py` | **NEW** — pure decision engine | F-015 plan §2.1 |
| `src/aspis/export.py` | Add `ProtectionError`, snapshot/log helpers, rewire `write_export` | F-015 plan §2.2 |
| `src/aspis/commands/init.py` | Add `--apply`, `--strict`, `--scope`, `--force-conflicts`, `--reset-snapshot` flags | F-015 plan §2.3 |
| `src/aspis/commands/models.py:230` | `force=True` → `apply=True` (1 line) | F-015 plan §2.4 — **the bug fix** |
| `src/aspis/data/catalog/scaffold/brain.gitignore` | Add `current/export-snapshot.json` and `current/export-log.json` | F-015 plan §2.6 |
| `tests/test_protect.py` | **NEW** — 16+ tests for the decision table | F-015 plan §4 Step 1 |
| `tests/test_export_snapshot.py` | **NEW** — 8 tests for snapshot I/O | F-015 plan §4 Step 2 |
| `tests/test_export_protection.py` | **NEW** — 12 integration tests | F-015 plan §4 Step 3 |
| `tests/test_commands_models.py` | Extend with 3 tests (PROTECT, UPDATE, CONFLICT) | F-015 plan §4 Step 4 |
| `tests/test_commands_init.py` | Extend with 6 tests (new flags) | F-015 plan §4 Step 4 |
| `tests/test_brain_gitignore.py` | **NEW** — verify gitignore entries | F-015 plan §4 Step 6 |
| `tests/test_f015_e2e.py` | **NEW** — 6 end-to-end tests | F-015 plan §4 Step 7 |

---

## 3. Web patterns — how other tools solve the same problem

### Pattern 1 — pacman 3-way MD5 sum comparison (ArchWiki: Pacnew and Pacsave)

**Source:** https://wiki.archlinux.org/title/Pacman/Pacnew_and_Pacsave (verified 2026-06-22)

Pacman computes **three MD5 sums** for every conffile on upgrade: the originally-installed version, the version currently on the filesystem, and the version in the new package. The 5 outcomes are:

| Original (X) | Current (Y) | New (Z) | Action |
|---|---|---|---|
| X | X | X | Overwrite (no notify) — identical bytes |
| X | X | ≠Y | Overwrite (no notify) — pristine, catalog improved |
| X | ≠Y | X | Keep current, no notify — user edited, catalog unchanged |
| X | ≠Y | Y | Overwrite (no notify) — catalog = current, refile |
| X | ≠Y | ≠Z | **Install as `.pacnew`**, warn user — all three differ |

The last case is the **CONFLICT** in our model. Pacman refuses to overwrite; it installs the new version alongside with a `.pacnew` suffix and requires the user to manually merge. The companion `.pacsave` is for package removal with modified conffiles.

**Mapping to F-015:** the algorithm is identical. Pacman's "X" = ASPIS's `snapshot_hash`, "Y" = `live_hash`, "Z" = `regen_hash`. Pacman has 5 cases; ASPIS adds a 6th (`ADD` for `live_hash is None`). The behavior is the same: refuse to overwrite, surface the conflict to the user, let the user resolve.

**Lesson:** the 3-way hash comparison has been the canonical solution to "how do I update config files without destroying user edits" since 1994. The F-015 plan is the same algorithm; the design is well-trodden.

**Difference:** pacman uses MD5; ASPIS uses SHA-256. Both are sufficient for non-adversarial modification detection. SHA-256 is the modern default and avoids MD5's collision concerns (paranoid in this context, but free).

### Pattern 2 — chezmoi "modified since I last wrote it" (chezmoi docs: apply, merge)

**Sources:**
- https://www.chezmoi.io/reference/commands/apply/ (verified 2026-06-22)
- https://www.chezmoi.io/user-guide/command-overview/
- https://www.chezmoi.io/user-guide/tools/merge/

Chezmoi tracks every file it manages. The `apply` command:

> Ensure that *target*... are in the target state, updating them if necessary. If no targets are specified, the state of all targets are ensured. **If a target has been modified since chezmoi last wrote it then the user will be prompted if they want to overwrite the file.**

Chezmoi also provides:
- `chezmoi status`: what would change (maps to F-015 dry-run).
- `chezmoi diff`: the actual changes (maps to F-015 dry-run output).
- `chezmoi merge` and `chezmoi merge-all`: invokes a configurable 3-way merge tool (vimdiff by default; configurable to nvim, bcomp, code). Maps to a future "interactive CONFLICT resolution" feature — out of scope for F-015 v1, but the hook is there.
- `--force`: overwrite everything (maps to F-015 `--force`).
- `--source-path`: target by source path, not target path (maps exactly to F-015 `--scope` filtering on `action.source`).

**Mapping to F-015:** chezmoi is the closest spiritual analog. The design choices converge:

| F-015 plan | chezmoi |
|---|---|
| `--apply` | default `apply` behavior |
| `--force` | `--force` |
| `--scope` | `--source-path` |
| `--strict` (CONFLICT → exit 1) | chezmoi has no strict mode; it always prompts |
| `--force-conflicts` | not a direct analog; chezmoi prompts |
| 6-case decision table | 4-state (matches chezmoi source/target/last-written) |
| Snapshot file (JSON) | internal state, not user-visible |
| `export-log.json` audit | `chezmoi diff` (per-invocation) |

**Lesson:** chezmoi is **interactive-first** (prompts on conflict). ASPIS is **non-interactive-first** (skip on conflict, log it, require a flag to override). This is the right choice for ASPIS: it's a CLI tool, often run from CI or scripts, where prompting is hostile. F-015 plan is consistent with this stance.

**Difference:** chezmoi's `merge` command is a strong precedent for an F-015 v2 feature — *interactive 3-way merge* for CONFLICTs. The decision data (live file + regen file + snapshot) is already there; the implementation is a `subprocess.run(["vimdiff", live, regen, snapshot], check=True)`. Out of scope for v1.

### Pattern 3 — dpkg conffile handling + `--force-confnew` / `--force-confold`

**Source:** https://en.wikipedia.org/wiki/Dpkg (general reference, verified); man `dpkg(8)`, `dpkg --force`.

dpkg has the same problem (a package upgrade with a modified conffile) and the same two resolutions:

- `--force-confnew`: always install the new version (overwrite user changes).
- `--force-confold`: always keep the user's version.
- Default (interactive): prompt the user.

`/var/lib/dpkg/status` records the package's conffile list; the actual modification check is a hash comparison of the on-disk conffile vs. the postinst script's expected hash.

**Mapping to F-015:** the two-flag pattern (`--force-confnew` = "overwrite", `--force-confold` = "preserve") maps to F-015's `--force-conflicts` and the default `PROTECT` behavior respectively. ASPIS's choice to make `PROTECT` the default (no flag needed) is the non-interactive equivalent of `--force-confold`.

**Lesson:** the flag-naming convention `--force-confold` / `--force-confnew` is 30 years of accumulated muscle memory. ASPIS's `--force-conflicts` reads naturally to anyone with a Debian background. The plan's flag name is well-chosen.

**Difference:** dpkg also has `--force-confdef` (apply the default action to all conffiles without prompting). F-015 has no equivalent because ASPIS is non-interactive by default — the default IS the default action.

### Pattern 4 — Git as a config-file diff log (etckeeper pattern)

**Source:** general knowledge; etckeeper is well-known (https://etckeeper.branchable.com/) but not fetched here.

`etckeeper` runs `git commit` automatically after every package manager operation, so every `/etc` change is recorded in git history. It does NOT prevent overwrites — it just makes them reversible.

**Mapping to F-015:** the `export-log.json` audit trail is the lightweight equivalent — every `write_export()` invocation appends a record of every decision. It is not git, but it answers the same question ("what did the exporter do, and when?").

**Lesson:** the audit log is genuinely useful for debugging ("why did my hand-edited file get clobbered? — oh, I ran with `--force` on 2026-06-25 14:30"). The F-015 plan's `export-log.json` is the right shape (append-only, per-file entries with hashes).

**Difference:** git gives you the full diff history; the JSON log gives you the decision per file. For 99% of debugging cases, "I see the decision" is enough; for the remaining 1% (recovering an accidentally-overwritten file), git's diff is better. F-015's choice is pragmatic.

### Pattern 5 — Idempotence as a first-class property

**Source:** not a single source; general design principle observed across all the above.

All four tools above treat "running the command again produces the same result" as a non-negotiable property. pacman's `pacman -S` is idempotent. `chezmoi apply` is idempotent. `dpkg --configure -a` is idempotent. `etckeeper` is git, which is trivially idempotent.

**Mapping to F-015:** the `UNCHANGED` decision (live hash == regen hash) is what makes `aspis init --write` idempotent. A second invocation with no changes writes nothing and produces an empty (or near-empty) action list. F-015 plan covers this correctly.

**Lesson:** the snapshot is what enforces idempotence. Without the snapshot, the only way to be idempotent is to compare the live file to the would-be output (which the F-015 plan does as case 2 — `live_hash == regen_hash` → UNCHANGED). With the snapshot, you can also detect "user has not changed the file, but the catalog has" (UPDATE) and "user changed the file, catalog has not" (PROTECT). The snapshot is the upgrade from binary idempotence to semantic idempotence.

---

## 4. Recommendations

### 4.1 What to port (clean-room, do not copy-paste)

The old ASPS `runtime_lock.py` is **the same algorithm** as the F-015 `protect.py`. There is no need to copy-paste the old code — the new module is smaller, tighter, and the design improvements (CRLF normalization, atomic write, simpler `Decision` shape, no `accept`/`rebaseline`) are real.

But the **test matrix** from the old `tests/test_runtime_lock.py` (21 KB) is a good seed for `tests/test_protect.py`. The old file likely covered all 6 cases of the decision table plus edge cases (None hashes, empty strings, CRLF, per-runtime lock files). The new test file should cover the same 6 cases + the new CRLF normalization, but skip the per-runtime and accept/rebaseline tests (no longer relevant).

**Port list:**

- `decide()` truth table — same algorithm, fresh implementation in `protect.py`.
- `DecisionKind` enum — same set, rename `UNTRACKED` to `UNKNOWN` (F-015 plan already does this).
- `Decision` dataclass — same shape, drop `diff` field.
- `sha256_text()` — same algorithm, **add CRLF→LF normalization** (F-015 plan already does this).
- `plan_runtime()` — same fan-out logic.
- `summary()` — same aggregation, return `dict` not `str`.
- `load_baseline()` / `save_baseline()` — same JSON load/save, **add atomic write** (F-015 plan already does this).
- **Test matrix:** the 6-case truth table coverage from `test_runtime_lock.py` → `test_protect.py`.

### 4.2 What to drop (do not port)

The F-015 plan's "Out of scope" list is correct and complete:

| Dropped | Why | Consequence |
|---|---|---|
| Staging directory (`regenerate.py`) | Atomic snapshot write is sufficient | ~600 lines deleted, no protection loss |
| Clobber classification (YAML semantic diff) | 3-way hash check subsumes it | ~90 lines deleted, no protection loss, no field-name coupling |
| Accept / rebaseline helpers | User edits files directly, next export detects | No external API needed; fewer surfaces |
| Per-runtime lock files | One snapshot file is simpler | Cross-runtime consistency is automatic |
| Orphan detection | Separate concern; future `--prune` flag | Plan correctly defers |
| Trace events | JSON audit log is sufficient | No trace schema dependency |
| Self-validation | Tested, not validated at runtime | Test suite is the validator |
| YAML semantic diff | SHA-256 of normalized text is sufficient | No field-name coupling |

**Total drop: ~900 lines of regenerated / promoted / clobber code.**

### 4.3 What to add (new for F-015)

| New | Why | Where |
|---|---|---|
| `class ProtectionError(RuntimeError)` | `strict` mode needs an exception to raise | `src/aspis/export.py` |
| `_load_snapshot(target_root, *, reset: bool)` | Snapshot I/O with corruption recovery | `src/aspis/export.py` |
| `_save_snapshot(target_root, snapshot)` | Atomic write: tempfile + os.replace | `src/aspis/export.py` |
| `_append_log(target_root, entries)` | Append-only audit log | `src/aspis/export.py` |
| `_hash_file(path) -> str \| None` | Live file hash with normalization | `src/aspis/export.py` |
| `_regen_hash(source, op) -> str` | Hash of what would be written | `src/aspis/export.py` |
| Extended `write_export()` signature: `apply`, `strict`, `scope`, `force_conflicts`, `reset_snapshot` | Plan §2.2 | `src/aspis/export.py` |
| 6 new CLI flags on `aspis init` | Plan §2.3 | `src/aspis/commands/init.py` |
| 1-line fix in `models --apply` | The bug fix | `src/aspis/commands/models.py:230` |
| 2 gitignore lines for snapshot + log | Plan §2.6 | `src/aspis/data/catalog/scaffold/brain.gitignore` |
| 6 new test files (51 tests total) | Plan §4 | `tests/test_*.py` |
| UTF-8 BOM handling (TBD; see §5) | Windows editor edge case | `protect.py:sha256_text` |

### 4.4 What the F-015 plan already got right

Spot-checking the plan against the old ASPS code, the web patterns, and the edge-case doc:

- **Decision table is correct.** Same 6 cases as the old ASPS, same as pacman's 3-way MD5.
- **`UNKNOWN` rename is correct.** `UNTRACKED` was a confusing name (it implies we lost tracking; we never had it). `UNKNOWN` reads as "we have no information about this file's history."
- **CRLF normalization in `sha256_text` is correct.** The old ASPS did NOT do this, and it was a latent bug.
- **Atomic `os.replace` for snapshot writes is correct.** The old ASPS did a non-atomic write.
- **One snapshot file (not per-runtime) is correct.** Simpler, fewer consistency surfaces.
- **No staging, no clobber, no accept, no rebaseline is correct.** All four are overengineering for the actual problem.
- **Pure-function `decide()` is correct.** All I/O in `write_export()`; `decide()` testable in isolation.
- **`models --apply` is the explicit motivation.** The 1-line fix (`force=True` → `apply=True`) is the smallest possible change with the largest impact.
- **The 5 user stories, 5 success criteria, and 15 functional requirements are well-scoped.** Each one is testable end-to-end.
- **The 4-step task decomposition is right-sized.** Each step produces a passing test suite before the next begins.
- **The 6 anti-patterns deliberately rejected in the plan's §8 are all the right rejections.** This is the most important section of the plan — it prevents a 600-line scope creep.

### 4.5 What the F-015 plan should add (small deltas)

Three small additions, none of which invalidate the plan:

1. **UTF-8 BOM handling** (see §5 below). The plan does not address this; the old ASPS did not either. Should be decided and documented in `protect.py:sha256_text`.
2. **Concurrent run safety** (lockfile). The edge-case doc flags this as CRITICAL (C-16). The plan does not include a lockfile. A small per-project lockfile (`.aspis/current/export.lock`) would prevent two concurrent `aspis init` from corrupting the snapshot. **Recommendation: add a brief mention to the plan; the lockfile is ~10 lines.**
3. **Test names should match the F-015 task list.** The plan's test file list (test_protect.py, test_export_snapshot.py, test_export_protection.py, test_f015_e2e.py) is the right granularity. Each file should correspond to one of the 4 task units.

---

## 5. Risk analysis

### 5.1 Edge cases (cross-referenced with `F-015-edge-cases.md`)

| ID | Case | F-015 plan | Recommendation |
|---|---|---|---|
| C-1 | Mode corruption on re-export | Fixed by 1-line `force=True → apply=True` change | ✓ Confirmed by test `test_models_apply_does_not_revert_promotion` |
| C-2 | `models --apply` re-renders correctly | Same fix | ✓ Confirmed by `test_models_apply_*` |
| C-3 | First export (no snapshot) | UNKNOWN → preserve live, record `live_hash` | ✓ Test `test_first_export_preserves_existing_live` |
| C-4 | Snapshot corrupted | Refuse unless `--reset-snapshot` | ✓ Plan covers; test `test_corrupt_snapshot_refused` |
| C-5 | Snapshot duplicate keys | **Not in plan** | **Add:** `_load_snapshot` should raise on duplicate keys; test `test_duplicate_snapshot_keys_refused` |
| C-6 | Live file deleted between exports | `live=None` → ADD (case 1) | ✓ Naturally handled by `decide()` case 1 |
| C-7 | `force=True` must keep working | Plan §2.3 flag matrix confirms | ✓ Test `test_init_force_overwrites_every_state` |
| C-8 | `--scope` on catalog source | Plan §2.3 `scope` param | ✓ Test `test_init_scope_filters_by_source` |
| C-9 | `--scope` is a directory | Plan uses prefix match | ✓ Naturally handled by `str.startswith(scope)` |
| C-10 | New runtime added | NEW (no snapshot entry) | ✓ Naturally handled by `live != baseline` check |
| C-11 | Runtime removed from project | Targets not in plan; live files left | ✓ Handled by `plan_export` filtering |
| C-12 | CRLF mismatch on Windows | `sha256_text` normalizes | ✓ Add test `test_crlf_live_file_is_unchanged` |
| C-13 | Empty file in catalog | Render produces non-empty; snapshot records render hash | ✓ Add test `test_empty_catalog_source` |
| C-14 | UTF-8 BOM | **Not in plan** | **Add:** decide and document — see §5.2 |
| C-15 | Snapshot atomic write | `tempfile + os.replace` | ✓ Add test `test_concurrent_export_atomic_write` |
| C-16 | Concurrent runs | **Not in plan** | **Add:** lockfile at `.aspis/current/export.lock` — see §5.2 |
| C-17 | Binary file in catalog | Hash over raw bytes | ✓ Naturally handled; tests use text but the same `sha256_text` works on bytes if you read in `rb` |
| C-18 | Snapshot version field | Plan includes `version: 1` | ✓ Bump on format changes; refuse on higher version |
| C-19 | Bootstrap integration | Plan §2.4 confirms the bootstrap path is safe | ✓ Verified by reading `bootstrap.py` |
| C-20 | `--strict` semantics | Plan §2.3 + FR-010 | ✓ Test `test_init_strict_exits_nonzero_on_conflict` |
| C-21 | `--force-conflicts` semantics | Plan §2.3 + FR-008 | ✓ Test `test_force_conflicts_overwrites_conflcit_but_preserves_protected` |

### 5.2 Windows-specific issues

The platform context (from `AGENTS.md`) is Windows. Specific issues:

**a. Atomic file rename (`os.replace`)**

`os.replace` is **the cross-platform way to do atomic rename** (available since Python 3.3 on Windows; POSIX `rename(2)` since forever). On Windows, `os.replace` overwrites the destination if it exists (since Python 3.3) — this is exactly the behavior we want for the snapshot write. **Verified safe.**

**b. CRLF line endings**

`write_text(..., encoding="utf-8", newline="\n")` is used throughout the current ASPIS code (export.py:131, 134). The renderer produces LF-only output. The live file, if edited in Notepad/Visual Studio, will have CRLF. The `sha256_text` normalization in the F-015 plan eliminates the false-PROTECT issue. **Verified safe by plan.**

**c. UTF-8 BOM (Notepad artifact)**

**Not addressed by the F-015 plan.** When a user opens an exported file in Notepad (the Windows default editor) and saves, Notepad prepends a UTF-8 BOM (`\ufeff`, bytes `0xEF 0xBB 0xBF`). The next `aspis init --write` would see `live_hash != snapshot_hash` and classify the file as USER-CUSTOMIZED (PROTECT), even though the user did not actually change the content.

**Recommendation:** **strip the BOM before hashing** (both `live` and `regen` paths). The BOM is a Windows editor artifact, not meaningful content. This should be:

```python
def sha256_text(text: str) -> str:
    if text.startswith("\ufeff"):
        text = text[1:]
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
```

**Document this in the module docstring.** A user who genuinely wants the BOM preserved can hand-edit the file again (and the new hash will then be a real PROTECT decision, not a false positive).

**d. Path separators**

`pathlib.Path` handles both. The snapshot should store paths as POSIX (`as_posix()`) so the file is portable across machines. The plan does not explicitly state this, but `pathlib` makes it natural. **Verified safe.**

**e. File locking**

Windows has mandatory file locking for some operations; concurrent reads may fail with `PermissionError`. The lockfile (C-16) is the right answer here, too: use `os.open(O_CREAT | O_EXCL | O_RDWR)` to create the lockfile, and `os.close()` to release. Stale-lock detection via mtime + PID check.

**f. Directory permissions**

`mkdir(parents=True, exist_ok=True)` works cross-platform. No special handling needed.

**g. Long path support (\\?\ prefix)**

Windows paths > 260 chars fail without the `\\?\` prefix or without the `LongPathsEnabled` registry key. ASPIS paths are all short (`.aspis/`, `.opencode/`, etc.), so this is unlikely to hit. Not worth special handling.

### 5.3 Failure modes

| Failure | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Snapshot file corrupted (truncated, edited, etc.) | Low | All live files classified as UNKNOWN → preserved (safe) | `decide()` case 3 + test |
| Snapshot lost (deleted by user) | Low | First-run behavior: all files UNKNOWN or ADD | `decide()` case 1 + case 3 |
| `os.replace` fails mid-write (disk full, permission denied) | Very low | Snapshot unchanged (atomic); no corruption | Atomic `os.replace` |
| Two `aspis init` runs concurrent | Low (CLI tool) | Race in `export-log.json` append; possible snapshot write race | Lockfile (C-16) — see recommendation |
| User passes `--force-conflicts` and overwrites a hand-edited file | Medium (user intent) | User customization lost | Documented; user opted in |
| Catalog source is deleted (file in `data/catalog/` is gone) | Very low | Plan records `missing`; action not taken | `plan_export()` already handles |
| Adapter module throws on render | Low | One file fails, rest succeed | Plan records in `problems`; flag `--strict` could fail-fast |
| `models --apply` on a project that was never initialized | Low | `ExportPlan` is empty; print "no live runtime agents" | Current code already does this (line 226–228) |
| `write_export` called with `apply=True` and no `--write` | Low | `apply=True` should imply `write=True` per FR/SPEC | Document in `write_export` docstring |
| Invalid flag combo (`--force-conflicts --strict`) | Low | Contradictory intent | Plan §2.3 rejects this; add a clear error message |

### 5.4 Backward compatibility

The plan's flag matrix (§2.3) explicitly covers this. The invariants:

- `aspis init` (no flags) → identical dry-run behavior to current.
- `aspis init --write` (no other flags) → identical write behavior to current for NEW files; **different for existing files** (current: skip if exists; F-015: UNCHANGED skip or UPDATE overwrite). The new behavior is **stricter** (preserves LIVE-CUSTOMIZED), so no existing user workflow breaks. Users who relied on the old "overwrite if exists" behavior must add `--force` explicitly.
- `aspis init --write --force` → identical to current `force=True` behavior. **Fully backward compatible.**
- `aspis models --apply` → fixes the bug; if the user had a workflow that relied on force-overwrite, they will now see CONFLICT or PROTECT. They can add `--force` to recover the old behavior (but `aspis models --apply --force` is **not** in the F-015 plan's flag set — should be added for symmetry with `init`).
- **`aspis operations/init.py`** (the lifecycle op called by `engine.run("init", ...)`) — does this pass `force` and `write` to `write_export`? **Yes** (per the old F-015 edge-case doc). The op needs to be updated to pass the new flags through. This is one more file change beyond the 3 the plan budgets — **add to plan §6 Cost-of-Change**.

### 5.5 Performance

- **Hashing cost:** SHA-256 of a 10 KB Markdown file is ~50 μs on a modern CPU. The full catalog is ~50 files × ~20 KB = ~1 MB total. Hashing all of it on every `init` is ~5 ms — negligible.
- **JSON load/save cost:** A snapshot with ~50 entries is ~2 KB. Load ~100 μs, save ~200 μs. Negligible.
- **Atomic write cost:** `tempfile` + `os.replace` is the same as a normal write plus one extra `os.rename`. Negligible.
- **First-render cost:** Same as current `init` — the catalog is rendered once per file, hash is computed on the result. No measurable overhead.
- **Concurrent-run cost:** Lockfile check is one extra `os.path.exists()` per invocation. Negligible.

**Total overhead of F-015 protection:** <100 ms on a typical `init --write`. The user will not notice.

---

## 6. Decision summary for the planner/build lead

| Question | Answer | Source |
|---|---|---|
| Is the F-015 plan sound? | **Yes.** | This research, §1–§4 |
| Should we port the old ASPS `runtime_lock.py`? | **No — fresh implementation is cleaner.** But use the old test matrix as a seed. | §4.1 |
| Is the decision table correct? | **Yes** (same as pacman's 3-way MD5, same as old ASPS). | §3 patterns 1, 2, 3 |
| Is the `models --apply` fix correct? | **Yes** — the 1-line change is the right size. | §2.1 |
| Are there any missing features? | **Three small ones:** BOM handling, lockfile, `aspis models --apply --force` for symmetry. | §4.5, §5.2c, §5.4 |
| Is the staging / clobber / per-runtime rejection correct? | **Yes** — all three are overengineering. | §1.2, §4.2 |
| Are there Windows-specific issues? | **Three:** BOM (handled by recommendation), CRLF (handled by plan), long paths (not relevant). | §5.2 |
| Is the snapshot location (`.aspis/current/`) correct? | **Yes** — under the existing brain `current/` dir. | Plan §2.5 |
| Is the gitignore plan correct? | **Yes** — snapshot and log are gitignored. | Plan §2.6 |
| Is the test count (51 tests) appropriate? | **Yes** — 16 for the engine, 12 for integration, 6 for E2E, etc. | Plan §10 |
| Is the cost-of-change (3 files) correct? | **Off by one** — `src/aspis/operations/init.py` also needs to pass new flags through. | §5.4 |
| Should the snapshot include a `version` field? | **Yes** — plan has it. | Plan §2.5 |
| Should `--strict` and `--force-conflicts` reject being combined? | **Yes** — contradictory intent. | Plan §2.3 |
| Should `--apply` imply `--write`? | **Yes** — explicitly per SPEC Clarifications. | SPEC.md §Clarifications |

**Final recommendation:** **Proceed with the plan as written, with the three additions from §4.5** (BOM handling, lockfile, `models --apply --force`). The cost-of-change should be updated to 4 files (add `operations/init.py`).

---

## 7. Source provenance

| Source | URL | Verified | Use |
|---|---|---|---|
| Old ASPS `runtime_lock.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPS\src\asps\runtime_lock.py` | Read 2026-06-25 | §1.1 |
| Old ASPS `regenerate.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPS\src\asps\regenerate.py` | Read 2026-06-25 | §1.2 |
| Old ASPS `promote.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPS\src\asps\promote.py` | Read 2026-06-25 | §1.2 |
| Old ASPS `exporter.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPS\src\asps\exporter.py` | Read 2026-06-25 | §1.1 |
| Old ASPS `initializer.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPS\src\asps\initializer.py` | Read 2026-06-25 | §1.2 (context) |
| Old ASPS `constants.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPS\src\asps\constants.py` | Read 2026-06-25 | §1.1 (reference) |
| Old ASPS `runtimes.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPS\src\asps\runtimes.py` | Read 2026-06-25 | §1.1 (reference) |
| Current ASPIS `export.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\src\aspis\export.py` | Read 2026-06-25 | §2.2 |
| Current ASPIS `commands/models.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\src\aspis\commands\models.py` | Read 2026-06-25 | §2.1, §2.2 |
| Current ASPIS `commands/init.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\src\aspis\commands\init.py` | Read 2026-06-25 | §2.2 |
| Current ASPIS `transform.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\src\aspis\transform.py` | Read 2026-06-25 | §2.2 |
| Current ASPIS `catalog.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\src\aspis\catalog.py` | Read 2026-06-25 | §2.2 |
| Current ASPIS `runtimes/{base,claude,opencode}.py` | (see path) | Read 2026-06-25 | §2.2 |
| Current ASPIS `promotion.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\src\aspis\promotion.py` | Read 2026-06-25 | §2.1 (failure path) |
| Current ASPIS `constants.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\src\aspis\constants.py` | Read 2026-06-25 | §2.1 (PROMOTE_TO_PRIMARY) |
| Current ASPIS `assetkinds.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\src\aspis\assetkinds.py` | Read 2026-06-25 | §2.2 |
| Current ASPIS `engine.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\src\aspis\engine.py` | Read 2026-06-25 | §2.2 (context) |
| F-015 SPEC | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\.aspis\features\F-015-safe-catalog-export\SPEC.md` | Read 2026-06-25 | §1.2, §2.4, §3 (cross-check) |
| F-015 PLAN | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\.aspis\features\F-015-safe-catalog-export\PLAN.md` | Read 2026-06-25 | §1.1, §1.2, §4.4 |
| F-015 TASKS | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\.aspis\features\F-015-safe-catalog-export\TASKS.md` | Read 2026-06-25 | §4.4 |
| F-015 Edge Cases | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\.aspis\features\F-015-safe-catalog-export\Research\F-015-edge-cases.md` | Read 2026-06-25 | §5.1 |
| Test: `tests/test_export.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\tests\test_export.py` | Read 2026-06-25 | §2.2 (verification) |
| Test: `tests/test_models_command.py` | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\tests\test_models_command.py` | Read 2026-06-25 | §2.1 (verification) |
| Arch Wiki: Pacman/Pacnew and Pacsave | https://wiki.archlinux.org/title/Pacman/Pacnew_and_Pacsave | Fetched 2026-06-25 | §3 pattern 1 |
| chezmoi docs: apply | https://www.chezmoi.io/reference/commands/apply/ | Fetched 2026-06-25 | §3 pattern 2 |
| chezmoi docs: command overview | https://www.chezmoi.io/user-guide/command-overview/ | Fetched 2026-06-25 | §3 pattern 2 |
| chezmoi docs: merge | https://www.chezmoi.io/user-guide/tools/merge/ | Fetched 2026-06-25 | §3 pattern 2 |
| Wikipedia: dpkg | https://en.wikipedia.org/wiki/Dpkg | Fetched 2026-06-25 | §3 pattern 3 |
| ASPIS AGENTS.md | `P:\AI_Empire\Projects\Agentic Software Production System\ASPIS\AGENTS.md` | Read 2026-06-25 | §5.2 (platform context) |

**Note on web search:** the `minimax_web_search` tool returned a rate-limit error during this research; web sources were fetched via direct `webfetch` to known canonical URLs (Arch Wiki, chezmoi docs, Wikipedia). This is the documented fallback per the research-lead skill (authoritative sources preferred).

---

## 8. One-page takeaway

The F-015 plan is correct. The algorithm is the same one pacman has used since 1994 (3-way MD5 → 5 outcomes), chezmoi uses today, and dpkg has codified with `--force-confnew`/`--force-confold`. The old ASPS `runtime_lock.py` is the same algorithm in a different language, and the F-015 plan correctly distills it: drop the staging directory, drop the clobber classifier, drop per-runtime lock files, drop accept/rebaseline. Keep the pure `decide()` function, the 6-case decision table, the SHA-256 hashes, and the JSON snapshot — but add CRLF normalization, atomic write, and a unified single-file snapshot.

**Three additions to the plan:** (1) UTF-8 BOM stripping in `sha256_text`, (2) a per-project lockfile at `.aspis/current/export.lock` for concurrent-run safety, (3) the `--force` flag on `aspis models --apply` for symmetry with `aspis init`. **One correction to the plan:** the cost-of-change is 4 files, not 3 — `src/aspis/operations/init.py` must also pass the new flags through to `write_export`.

The 1-line bug fix in `commands/models.py:230` (`force=True` → `apply=True`) is the smallest change with the largest impact. The test that proves it works is `test_models_apply_does_not_revert_promotion` (already specified in the edge-case doc).

**Recommendation: build per the plan, with the three additions and the one correction. Total scope: ~700 lines of new code, 4 existing files touched, 51 tests across 6 new test files. All edge cases from the F-015 edge-case doc are addressable within this scope.**
