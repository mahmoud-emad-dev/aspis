# F-017 L2-P0 — CLI Verb Quality Review

> **Reviewer**: Reviewer (independent quality authority)
> **Date**: 2026-06-27
> **Scope**: F-017 T-33, T-34, T-35, T-36 — 4 new CLI verbs (`validate-runtime`, `byte-parity`, `export`, `governance`)
> **Perspective**: CLI verb quality — interface design, contract conformance, spec-divergence, capability-driven design, R-006 discipline
> **Verdict**: **CHANGES REQUIRED** — 1 CRITICAL, 3 HIGH, 4 MEDIUM, 4 LOW findings

---

## Executive summary

The 4 L2-P0 verbs are **architecturally honest** in their wrapper design: every verb sits on top of the existing public APIs of `aspis.export` / `aspis.protect` / `aspis.catalog` / `aspis.transform` — **no re-implementation of the rendering or protection engine**. The `validate-runtime` and `byte-parity` verbs are clean stdlib-only additions; `export` is a true thin wrapper over the same `plan_export`/`write_export` pipeline `aspis init` uses; `governance` is a single 582-line file that implements the R-008 deterministic-script end-to-end (path glob matching with `**`-depth support, atomic ledger writes, process-level lock with stale detection, exit-code model per spec §6).

**However, three load-bearing contract items are wrong or missing, blocking L2-P0 acceptance:**

1. **CRITICAL — T-35 Claude adapter `permission:` block fix is NOT done.** T-35's spec text says "preserves `permission:` block in Claude Code adapter output (fix the stripping bug in `src/aspis/runtimes/claude.py`)", and FR-010 makes this a hard requirement. The F-017 L2-P0 commit (`42d589a`) modified 5 files, all in `src/aspis/commands/` — **`src/aspis/runtimes/claude.py` was not touched.** The adapter's `render_agent` (lines 43–58) still emits only `name`, `description`, `tools`, `model` — no `permissions`. A `aspis export` to a Claude project today will land agents with no permission surface, breaking R-008 / boundary-1 enforcement and FR-010. This is the **same CRITICAL that the L1 plan-feasibility review flagged** (H-3) and the architecture-constitution review flagged (M-2) — the build did not address it.

2. **HIGH — governance verb signatures diverge from `Research/ref/governance.md` §6 in load-bearing ways.** The spec says `revoke` has `--approver` as **optional** (defaults to original approver) — the implementation makes it **required**. The spec says `request` has `--reason` as **optional** (prompted if absent) — the implementation makes it **required**. Two flags on `audit` from the spec are **missing** (`--until`, `--status`). The spec uses kebab-case field names (`revoked-by`, `glob-approved`); the implementation uses snake_case. The spec shows a top-level YAML list; the implementation wraps in `{"entries": [...]}`. The divergences are operationally small but the spec explicitly says "MUST match governance.md §6 verbatim" (T-36 line 108).

3. **HIGH — verbs reject the flags the spec's acceptance criteria invoke.** `aspis validate-runtime --runtime all` (SC-003, SPEC.md:124) fails with `unrecognized arguments: --runtime`. `aspis byte-parity --dry-run` (SC-004, SPEC.md:125) fails with `unrecognized arguments: --dry-run`. The verbs do the right thing internally; they just don't accept the flags the SC-### acceptance text names.

**Positive signals**:
- All 4 verbs are in `src/aspis/commands/` (not `src/aspis/cli/`) — the plan-feasibility CRITICAL-1 was resolved.
- All 4 use the `register(subparsers)` pattern and are listed in `COMMAND_MODULES` — no missing entries.
- `validate-runtime` and `byte-parity` are stdlib-only (no PyYAML, no third-party).
- The export verb is a genuine thin wrapper — same imports as `init`, same `plan_export`/`write_export` calls, identical protection-engine semantics.
- The governance verb's ledger code is **production-grade**: atomic write via `os.replace`, process-level lock via `O_CREAT|O_EXCL`, stale-lock recovery after 60s, expiry detected at check time, deterministic 0/2/3/4/5 exit codes per spec §6 error model.

**Cross-cutting verdict**: **CHANGES REQUIRED** before T-40 (L2-P0 integration check) can pass. The CRITICAL is a one-file fix in `claude.py`; the HIGHs are a 2-line edit per subcommand in `governance.py` + adding `--runtime` / `--dry-run` no-op flags. The MEDIUMs and LOWs are clean-up items for the polish pass (T-55) or a follow-up review.

---

## 1 · Per-verb evaluation

### 1.1 · `validate-runtime` — T-33

**File**: `src/aspis/commands/validate_runtime.py` (179 lines)
**Verb registration**: `validate-runtime` (hyphenated), line 50 — `add_parser("validate-runtime", ...)`

| Check | Status | Evidence |
|---|---|---|
| Reads all 12 agent catalog files | ✓ | line 157 `agent_files = sorted(agents_dir.glob("*.md"))` — globbed 12 .md files in `src/aspis/data/catalog/agents/` |
| Checks 11 frontmatter fields | ✓ | lines 24-36 `_REQUIRED_FIELDS` tuple is exactly 11: `name, description, mode, model, temperature, tools, permissions, delegates, skills, runtimes, export_scope` — **match for AGENT_BODY_STANDARD.md §"Required frontmatter"** |
| Every skill ref resolves | ✓ | lines 106-119 check each `skills:` entry against `skills_dir / skill / SKILL.md` — for non-string entries, the line is reported |
| Every delegate exists | ✓ | lines 123-136 check each `delegates:` entry against `agents_dir / f"{delegate}.md"` — orphan delegates are reported with file:line evidence |
| Stdlib-only | ✓ | only `argparse`, `pathlib` (stdlib) + `aspis.catalog.split_frontmatter`, `aspis.resources.catalog_dir` (project) |
| File:line evidence on failure | ✓ | `f"{agent_path.name}:{_FRONTMATTER_OPEN_LINE} missing field: '{field}'"` (line 101) and `f"{agent_path.name}:{skills_line or _FRONTMATTER_OPEN_LINE} missing skill ref: '{skill}' (expected {skill_path})"` (line 117) |
| Exit 0 on pass / non-zero on failure | ✓ | line 173 `return 0 if total_failures == 0 else 1` |
| Registered in `COMMAND_MODULES` | ✓ | `src/aspis/commands/__init__.py:53` — `validate_runtime,` |
| `register(subparsers)` pattern | ✓ | lines 48-57 |
| `__main__` block (for ad-hoc `python -m`) | ✓ | lines 176-179 (the only L2-P0 verb with one) |
| Module path matches actual file | ✓ | `src/aspis/commands/validate_runtime.py` (underscored) — verb is `validate-runtime` (hyphen); dispatch via `aspis validate-runtime` works |

**Issues**:

- **H-1** (HIGH): `--runtime` flag is not accepted. SC-003 (SPEC.md:124) says `aspis validate-runtime --runtime all` must exit 0. The verb's parser (lines 48-57) accepts only `--help` and the `func` default. `--runtime` raises `unrecognized arguments: --runtime all`. **The verb always checks every agent**, so functionally `--runtime all` would be a no-op, but the SC-### text the spec ships says the flag is there.
- **MEDIUM** (low risk): the spec's invocation `python -m src.aspis.commands.validate_runtime` (the integration-gates review's C-1) doesn't work for any verb except `validate_runtime` (the only one with a `__main__` block) — the other 3 are reachable only via the `aspis` entry point. Not a defect of this verb, but worth noting that the verb IS the most debug-friendly of the four.

**Verdict**: APPROVED WITH NOTES (H-1 is the only blocker; fix is a 2-line edit).

---

### 1.2 · `byte-parity` — T-34

**File**: `src/aspis/commands/byte_parity.py` (212 lines)
**Verb registration**: `byte-parity` (hyphenated), line 57

| Check | Status | Evidence |
|---|---|---|
| THIN WRAPPER over `src/aspis/export.py` (plan_export) | ✓ | line 32 `from aspis.export import ExportAction, plan_export`; line 102 `plan = plan_export(catalog, profile)` — **the SAME `plan_export` init uses** |
| THIN WRAPPER over `src/aspis/protect.py` | ✓ | line 36 `from aspis.protect import DecisionKind, decide, sha256_text`; line 198 `regen_hash = sha256_text(rendered)`; line 209 `decision = decide(live_hash=None, snapshot_hash=None, regen_hash=regen_hash)` — **the SAME `decide` and `sha256_text` export uses** |
| Reimplementation? | ✗ **No** | Uses `render_agent` (line 192, from `aspis.transform`) — the same dispatcher export uses. The implementation does NOT re-implement the rendering pipeline. |
| Read-only | ✓ | docstring (line 22) "this verb never writes the live file, the export snapshot, or the audit log"; verified by source: no `write_export` call, no `os.replace`, no `shutil.copy` |
| Dry-run only | ✓ | No `--apply` or `--force` flag exists. The verb is read-only by design. |
| Does NOT write live files | ✓ | `decide(live_hash=None, snapshot_hash=None, ...)` (line 209) — both live and snapshot hashes passed as `None`, so the live tree is never consulted |
| Catalog self-consistency check — correct | ✓ | Frontmatter shape (lines 173-176) → skill/delegate ref resolution (lines 179-184) → render in-memory (line 192) → hash via public API (line 198) → classify CLEAN/CONFLICT (line 210-211). All steps use existing public functions. |
| PROTECT status | ✓ | The implementation documents (lines 11-15) that PROTECT only fires when a live file is present; the catalog-only check collapses to CLEAN (ADD) or CONFLICT. PROTECT is reserved for forward-compat with the live-tree check. |
| Required fields for render | ✓ | lines 47-52 `_REQUIRED_FIELDS: (name, description, mode, model)` — the 4 fields the renderer needs |
| Stdlib-only | ✓ | only `argparse`, `pathlib`, `typing` (stdlib) + project modules — no PyYAML, no third-party |
| Registered in `COMMAND_MODULES` | ✓ | `src/aspis/commands/__init__.py:37` — `byte_parity,` |
| `register(subparsers)` pattern | ✓ | lines 55-74 |
| Module path matches actual file | ✓ | `src/aspis/commands/byte_parity.py` |

**Issues**:

- **H-2** (HIGH): `--dry-run` flag is not accepted. SC-004 (SPEC.md:125) says `aspis byte-parity --dry-run` must exit 0. The verb's parser (lines 56-74) accepts only `path` (positional, default `.`) and `--help`. `--dry-run` raises `unrecognized arguments: --dry-run`. The verb IS dry-by-design (it never writes), so the flag would be a no-op — but the SC-### text the spec ships says the flag is there.
- **LOW** (cosmetic): the verb accepts only a positional `path` (default `.`), no `--catalog`, `--runtime`, or `--profile` override. For most use cases this is fine, but it means the verb always reads the bundled `base.yaml` profile (line 84). A user with a custom profile can't point byte-parity at it. Not a defect; just a scope observation.

**Verdict**: APPROVED WITH NOTES (H-2 is the only blocker; fix is a 2-line edit).

---

### 1.3 · `export` — T-35

**File**: `src/aspis/commands/export_cmd.py` (143 lines)
**Verb registration**: `export`, line 32

| Check | Status | Evidence |
|---|---|---|
| THIN WRAPPER over `plan_export`/`write_export` | ✓ | line 25 `from aspis.export import ProtectionError, plan_export, write_export`; line 112 `plan = plan_export(...)`; line 115 `performed = write_export(plan, root, ...)` |
| Same pipeline as `aspis init` | ✓ | `src/aspis/commands/init.py:10` imports the same `ProtectionError` from `aspis.export`; `init.py:84-99` calls `engine.run("init", ...)` which uses `aspis.operations.init.init_core` which calls the same `plan_export`/`write_export`. **Three call sites, one pipeline.** |
| No duplication of rendering | ✓ | No local copy of `_regen_hash`, `_apply`, or `_write_decide`; all delegated to `write_export` |
| Claude adapter fix — capability-driven approach | ✗ **NOT DONE** | see C-1 below |
| No `if runtime == "claude"` check | ✓ | `grep "if runtime == 'claude'"` finds 0 matches in `src/aspis/`; the architecture-constitution rule C-9 "No Special Cases" is honored. **However, the adapter fix is missing entirely** (see C-1). |
| Dry-run default | ✓ | lines 45-49 `--dry-run` with `default=True`; the writer's `write=apply` is set to `False` by default |
| `--apply --force` for real | ✓ | line 99 `apply = bool(args.apply or args.force)`; line 119 `write=apply` — `--apply` or `--force` flips write to True |
| `--strict`, `--force-conflicts` | ✓ | lines 62-70; passed to `write_export` (lines 121-122) |
| Stdlib-only | ✓ | only `argparse`, `pathlib` (stdlib) + project modules |
| Registered in `COMMAND_MODULES` | ✓ | `src/aspis/commands/__init__.py:38` — `export_cmd,` |
| `register(subparsers)` pattern | ✓ | lines 30-71 |
| Module path matches actual file | ✓ | `src/aspis/commands/export_cmd.py` (note: verb is `export`, file is `export_cmd.py` because `export.py` would shadow `aspis.export`) |

**Issues**:

- **C-1** (CRITICAL): **The Claude adapter's `permission:` block fix is NOT implemented.** T-35 explicitly says "preserves `permission:` block in Claude Code adapter output (fix the stripping bug in `src/aspis/runtimes/claude.py`)" (TASKS.md:102). FR-010 (SPEC.md:86) makes this a hard requirement. **The F-017 L2-P0 commit `42d589a` modified 5 files, all in `src/aspis/commands/` — `src/aspis/runtimes/claude.py` was not touched.** Verified by `git log --oneline -5 -- src/aspis/runtimes/claude.py` — the most recent commit on the Claude adapter is `4c12b5d fix(F-013)` from 2026-06-15, **before F-017 began**. The adapter's `render_agent` (lines 43-58) still emits only `name, description, tools, model` — no `permissions`. **A `aspis export` to a Claude project today lands agents with no permission surface**, breaking:
  - **R-008 / Boundary 1** (governance.md §5): the runtime guard that blocks writes to protected paths is enforced through the `permissions:` block — Claude has no block to enforce.
  - **FR-010**: explicit "Claude Code adapter MUST preserve the `permission:` block" — violated.
  - **Deny floor** (R-004/R-008): Claude-side `git push*` denial is enforced via `permissions.bash` patterns; without the block, no enforcement.
  - **The "M-2 — Claude Code adapter fix wording is capability-flavored but the location is not pinned to the adapter" finding from the architecture-constitution review** (`.aspis/features/F-017-complete-agent-system/Review/architecture-constitution.md:323`) was not addressed.

  **Fix (one file, one method, ~10 lines)**:
  ```python
  # src/aspis/runtimes/claude.py — render_agent, after line 56
  data = {
      "name": agent.name,
      "description": agent.description,
      "tools": self.tools_for(agent.tools),
      "model": self._resolve_model(agent, project_config, inventory),
  }
  if agent.permissions:
      data["permissions"] = dict(agent.permissions)
  frontmatter = to_frontmatter(data)
  ```
  The current docstring (lines 5-8) states the adapter "deliberately drops ... `permissions`" — **that line is the bug.** The fix changes the docstring to describe the preserved block.

- **MEDIUM** (UX): `--dry-run` is `default=True` (line 47) but its value is never read in `_run` (line 86). The actual logic uses `args.apply or args.force`. So passing `--dry-run` explicitly does nothing different from omitting it. The flag is a UX hint, not a switch. This was flagged by the integration-gates review (M-1); unchanged in the build.
- **LOW** (doc): the docstring (line 7) says "the only init steps `export` deliberately does NOT do are brain scaffolding, root-file seeding, git init, and the first commit." The reconciliation is honest and accurate; **good R-006 hygiene** (no restated content, single source = `init.py` + `aspis.operations.init`).

**Verdict**: **CHANGES REQUIRED** (C-1 blocks T-40).

---

### 1.4 · `governance` — T-36

**File**: `src/aspis/commands/governance.py` (582 lines)
**Verb registration**: `governance`, line 522; 6 subcommands (lines 526, 529, 538, 556, 566, 576, 580)

| Subcommand | Spec §6 signature | Implementation | Status |
|---|---|---|---|
| `request` | `request --path <path> [--reason <reason>]` (line 442) | `req.add_argument("--path", ...)` required; `req.add_argument("--reason", required=True, ...)` | **✗ M-1** — spec says `--reason` is **optional**, impl requires it |
| `approve` | `approve --paths <paths> --reason <reason> --approver <id> [--expiry] [--glob-approval]` (line 458) | `app.add_argument("--paths", required=True, nargs="+", ...)`; `--reason` required; `--approver` required; `--expiry` optional; `--glob-approval` flag | **✓ — matches** (the `nargs="+"` form is one valid "repeatable" shape) |
| `audit` | `audit [--since] [--until] [--path] [--approver] [--status] [--pretty]` (line 477) | `--since`, `--approver`, `--path` (action="append") only; **missing `--until`, `--status`, `--pretty`** | **✗ M-2** — 2-3 spec flags dropped |
| `revoke` | `revoke --id <APRV-NNN> --reason <reason> [--approver]` (line 497) | `--id` required; `--reason` required; `--approver` **required** | **✗ H-3** — spec says `--approver` is **optional** (defaults to original approver), impl requires it |
| `check` | `check --path <path> [--pretty]` (line 516) | `--path` required; **no `--pretty`**; exit 0/4/5 (line 491) | **⚠ partial** — `--pretty` is cosmetic, but missing |
| `ledger` | `ledger [--pretty]` (line 530) | no args | **⚠ partial** — `--pretty` is cosmetic |

**Cross-cutting checks**:

| Check | Status | Evidence |
|---|---|---|
| `--approver` REQUIRED on `approve` (R-008) | ✓ | line 545 `app.add_argument("--approver", required=True, ...)`; handler also rejects empty (line 320) |
| `--approver` REQUIRED on `revoke` | ✓ (impl), **✗** (spec) | line 570 `rev.add_argument("--approver", required=True, ...)`; spec line 500 says `[--approver]` (optional, defaults to original) |
| Ledger at `.aspis/state/approval-ledger.yaml` | ✓ | line 42 `LEDGER_REL = Path(".aspis/state/approval-ledger.yaml")` |
| Ledger append-only | ✓ (operationally) / **⚠** (technically) | writes the entire entries list via `os.replace` (line 215) — **atomic**, never partial; **but `revoke` mutates the existing entry in place** (lines 452-457) rather than appending a new entry. Spec §4 line 323 says "Revocations are new entries" — the impl is consistent with §1 "Revocations set `status: revoked` but never delete entries" but slightly at odds with §4's append-only framing. **Operationally equivalent — the original entry is never deleted, only mutated.** See L-3. |
| Keeps `approver` | ✓ | line 351 `entry["approver"] = args.approver.strip()` |
| Keeps `expiry` | ✓ | line 356 `entry["expiry"] = args.expiry` (None when not set) |
| Keeps `glob_approval` | ✓ (with L-1 naming) | line 358 `entry["glob_approval"] = bool(args.glob_approval)`; spec line 314 says `glob-approved: true` (kebab-case) — see L-1 |
| Protected paths set | ✓ | lines 52-67 `PROTECTED_PATHS` matches spec §2 lines 99-122 verbatim |
| Process-level file lock | ✓ | lines 227-257 `_acquire_lock` uses `O_CREAT|O_EXCL` atomic create; stale lock (>60s) is broken on next acquire (lines 242-249) |
| Atomic write | ✓ | lines 213-215 `tmp = ledger.with_suffix(ledger.suffix + ".tmp"); tmp.write_text(payload); os.replace(tmp, ledger)` |
| Stale lock detection >60s | ✓ | line 48 `LOCK_STALE_SECONDS = 60`; line 242 `if age > LOCK_STALE_SECONDS: lock.unlink(); continue` |
| Exit codes 0/2/3/4/5 | ✓ | line 491 — `0` allowed, `2` validation, `3` not found, `4` blocked, `5` not protected. **Matches spec §6 "Error model" lines 537-546.** |
| Stdlib-only | ✗ | line 35 `import yaml` — PyYAML is a third-party dep (in `uv.lock`); spec says "stdlib-only" (PLAN.md:164) |
| Registered in `COMMAND_MODULES` | ✓ | `src/aspis/commands/__init__.py:51` — `governance,` |
| `register(subparsers)` pattern | ✓ | lines 520-581 |
| Module path matches actual file | ✓ | `src/aspis/commands/governance.py` |

**Subcommand semantic checks**:

- `request` — line 300-312: prints the exact `approve` command the human should run; **passive** (no ledger write, no path check). Matches spec §3 step 1.
- `approve` — line 315-375: validates `--approver` non-empty, `--reason` non-empty, `--expiry` ISO 8601; acquires lock; appends entry; releases lock. **Production-grade.**
- `audit` — line 378-421: filters by `--since` (date) and `--approver` (exact match); `--path` does bidirectional glob match (line 403). Missing `--until`, `--status`, `--pretty`.
- `revoke` — line 424-464: validates `--approver` non-empty (over-restrictive per spec); rejects double-revoke with exit 3 (line 451); flips status + writes revocation block; **mutates in place** (line 452-457).
- `check` — line 488-513: validates path protected; finds active approval; exit 0 (allowed) / 4 (blocked) / 5 (not protected). **Diagnostic — does NOT write to ledger, does NOT update `applied:` list.** Spec §5 step 6 says the intervention handler appends to `applied:`; the CLI's `check` is the diagnostic, not the handler, so it correctly does not write. **The intervention handler (Boundary 1, the runtime guard) is a separate piece not built in T-36** — it lives in `.claude/settings.json` and the OpenCode plugin. The CLI's `check` is the **read-only diagnostic** the spec describes.
- `ledger` — line 467-485: prints `path, exists, count, oldest, newest, active, revoked`. **Spec says it should print "lock state" (line 531) — not implemented** (no `lock_state` field in output). See L-2.

**Verdict**: **CHANGES REQUIRED** (H-3 is the highest-priority divergence; M-1, M-2, L-1, L-2, L-3 are clean-up).

---

## 2 · Cross-cutting checks

### 2.1 · Location: `src/aspis/commands/`, NOT `src/aspis/cli/`

**All 4 verbs in the correct location.** The plan-feasibility review's CRITICAL-1 (paths) was correctly resolved during build.

| Verb | Module file | OK? |
|---|---|---|
| `validate-runtime` | `src/aspis/commands/validate_runtime.py` | ✓ |
| `byte-parity` | `src/aspis/commands/byte_parity.py` | ✓ |
| `export` | `src/aspis/commands/export_cmd.py` | ✓ (file is `export_cmd.py` to avoid shadowing `aspis.export`) |
| `governance` | `src/aspis/commands/governance.py` | ✓ |

### 2.2 · `register(subparsers)` pattern

**All 4 verbs expose `register(subparsers: argparse._SubParsersAction)`.** Verified by reading the 4 module files. The pattern is honored:

| Verb | `register` location | Signature |
|---|---|---|
| `validate-runtime` | line 48 | `def register(subparsers: argparse._SubParsersAction) -> None:` |
| `byte-parity` | line 55 | `def register(subparsers: argparse._SubParsersAction) -> None:` |
| `export` | line 30 | `def register(subparsers: argparse._SubParsersAction) -> None:` |
| `governance` | line 520 | `def register(subparsers: argparse._SubParsersAction) -> None:` |

### 2.3 · `COMMAND_MODULES` registration

`src/aspis/commands/__init__.py` lines 11-31 (imports) and lines 34-53 (COMMAND_MODULES tuple):

| Verb | Import | In tuple | Position in tuple |
|---|---|---|---|
| `byte_parity` | line 14 | line 37 | 3rd |
| `export_cmd` | line 18 | line 38 | 4th |
| `governance` | line 22 | line 51 | 17th |
| `validate_runtime` | line 30 | line 53 | 19th |

**No missing entries.** The tuple is the source of truth for the CLI dispatch loop in `src/aspis/cli.py:53-54`:
```python
for module in COMMAND_MODULES:
    module.register(subcommands)
```
All 4 new verbs are reachable via `aspis <verb> --help`.

### 2.4 · Stdlib-only

| Verb | Third-party imports? | Stdlib-only? |
|---|---|---|
| `validate-runtime` | none (only `argparse`, `pathlib` + project) | ✓ |
| `byte-parity` | none (only `argparse`, `pathlib`, `typing` + project) | ✓ |
| `export` | none (only `argparse`, `pathlib` + project) | ✓ |
| `governance` | `yaml` (line 35) | ✗ (PyYAML is third-party; already a project dep, but violates the "stdlib-only" spec rule) |

**3 of 4 verbs are stdlib-only.** The `governance` verb imports `yaml`, which is PyYAML. PyYAML is already a project dep (in `uv.lock` line 244, listed in `ATTRIBUTIONS.md:13`), so the verb works correctly. The spec's "stdlib-only" rule (PLAN.md:164) is violated. **LOW severity** — the verb works, and the cost of using `yaml` is a 50KB dep that's already loaded for other parts of the codebase. **Fix**: either (a) replace `yaml.safe_load` / `yaml.dump` with stdlib `json` (requires a JSON ledger, which has different ergonomics), or (b) update the spec to allow `yaml` for verbs that need human-readable ledger I/O. The pragmatic choice is (b) — the spec's "stdlib-only" rule was written for the planning scripts, where YAML is also used. The governance verb is the only verb that needs human-readable, append-only structured I/O, and YAML is the project's standard.

### 2.5 · `--help` works on each

**Cannot live-test** (bash permission layer in this env denies all `aspis *` invocations; the env allowlist is `git status*`, `git diff*`, `git log*`, `aspis context*`, `aspis artifact*`, and the planning/context scripts). **Source-verified** — all 4 verbs use `argparse.add_parser(..., help=...)` (lines 50-56, 57-63, 32-36, 522-525) and do not pass a custom `formatter_class` or override `_print_help`. **Argparse auto-generates `--help`** for any subparser. The `help=` strings are accurate and on-contract (Gate 5 of the integration-gates review verified this).

### 2.6 · Exit codes

| Verb | Exit codes | Status |
|---|---|---|
| `validate-runtime` | 0 = all pass; 1 = any failure (line 173) | ✓ — matches the spec's "0 on success, non-zero on failure" |
| `byte-parity` | 0 = all CLEAN; 1 = any issues (line 133) | ✓ |
| `export` | 0 = plan executed; 1 = not a project / protection error; 2 = contradictory flags (line 97) | ✓ — rich exit-code model |
| `governance` | 0/2/3/4/5 per spec §6 (line 491) | ✓ — matches the spec's error model verbatim |

**All 4 verbs have sensible, documented exit codes.** No CRITICAL/HIGH exit-code issues.

### 2.7 · `src/aspis/commands/__init__.py` correctness

The `__init__.py` is correct:
- Imports at lines 11-31 cover all 20 modules (16 existing + 4 new)
- `COMMAND_MODULES` at lines 34-53 has 20 entries
- No duplicate entries
- No missing entries
- Order is mostly historical (init, bootstrap first; new verbs at lines 37, 38, 51, 53)

**Note**: the new verbs are NOT in display order (init, bootstrap, byte-parity, export, status, ...). `byte-parity` and `export` are placed at positions 3-4 (right after init/bootstrap), which is the "logical discovery order" — a user running `aspis init` next wants to see `aspis export`. `governance` is at position 17 (between `doctor` and `uninstall`); `validate-runtime` is at the end. This is a **minor UX choice** — the spec says "in the order their verbs appear in `aspis --help`" but doesn't specify the order. The current order is defensible.

---

## 3 · Per-verb score

| Verb | Score | Tier | Notes |
|---|---|---|---|
| `validate-runtime` | **92 / 100** | APPROVED WITH NOTES | Clean; H-1 (missing `--runtime` flag) is a 2-line fix |
| `byte-parity` | **94 / 100** | APPROVED WITH NOTES | Truly thin wrapper; H-2 (missing `--dry-run` flag) is a 2-line fix |
| `export` | **60 / 100** | **CHANGES REQUIRED** | Wrapper is honest, but C-1 (Claude adapter fix not done) is a FR-010 violation |
| `governance` | **78 / 100** | **CHANGES REQUIRED** | Production-grade ledger code; H-3 (`revoke --approver` over-restrictive) + M-1 + M-2 + L-1 + L-2 + L-3 are spec divergences |

**Aggregate score: 81 / 100.** Above the L1 leaves' 88-96 range on most metrics, but pulled down by the CRITICAL Claude-adapter fix that was supposed to land with T-35.

---

## 4 · Findings (severity-ordered, with file:line evidence)

### CRITICAL (1)

#### C-1 · T-35 Claude adapter `permission:` block fix NOT done (FR-010 violation)

**File**: `src/aspis/runtimes/claude.py` (not modified in this build)
**Standard violation**: FR-010 (SPEC.md:86) — "The Claude Code adapter MUST preserve the `permission:` block (not strip it), maintaining capability-equivalence with the OpenCode runtime." T-35 (TASKS.md:102) explicitly says: "preserves `permission:` block in Claude Code adapter output (fix the stripping bug in `src/aspis/runtimes/claude.py`)".

**Evidence**:

1. `git log --oneline -5 -- src/aspis/runtimes/claude.py` — the most recent commit on the Claude adapter is `4c12b5d fix(F-013)` from 2026-06-15, **before F-017 began**. The F-017 L2-P0 commit `42d589a feat(F-017/T-33..T-36): add L2-P0 verbs` modified 5 files, all in `src/aspis/commands/`:
   ```
   src/aspis/commands/__init__.py
   src/aspis/commands/byte_parity.py
   src/aspis/commands/export_cmd.py
   src/aspis/commands/governance.py
   src/aspis/commands/validate_runtime.py
   ```
   `src/aspis/runtimes/claude.py` is **not** in the list. **The fix was not done.**

2. `src/aspis/runtimes/claude.py:43-58` — `ClaudeAdapter.render_agent` emits only:
   ```python
   frontmatter = to_frontmatter({
       "name": agent.name,
       "description": agent.description,
       "tools": self.tools_for(agent.tools),
       "model": self._resolve_model(agent, project_config, inventory),
   })
   ```
   **No `permissions` key.** The adapter's docstring (lines 5-8) explicitly states it "deliberately drops ... `permissions`" — **that line is the bug.** Compare with `OpenCodeAdapter.render_agent` at `src/aspis/runtimes/opencode.py:38-53`:
   ```python
   data["permission"] = self._permission(agent)
   ```
   The OpenCode adapter DOES emit a `permission` block, built from the agent's frontmatter `permissions:` field via `_permission` (lines 55-74).

3. `agent.permissions` is a dict parsed by `src/aspis/catalog.py:93`:
   ```python
   permissions=dict(data.get("permissions", {})),
   ```
   The data is available to the adapter; the adapter just doesn't use it.

**Why it matters** (3 breakages):

- **R-008 / Boundary 1** (governance.md §5 lines 351-367): the runtime guard that blocks writes to protected paths is enforced through `permissions.bash` deny patterns on each agent's rendered file. A Claude project with no `permissions` block has **no runtime enforcement** of the R-008 protected-path set. The `governance` verb's `check` will return 4 (blocked), but **the runtime will not block anything** — the user gets a green light on the CLI and an unwritten runtime. This is the **asymmetry** the spec was designed to prevent.
- **FR-010** — explicit "MUST preserve". The check is a one-liner: grep the Claude-rendered output for `permissions:` → currently 0 matches.
- **Deny floor** (system-rules.md R-004, R-008): Claude-side `git push*` denial is enforced via `permissions.bash` patterns on the rendered agent. Without the block, the runtime has no mechanism to deny `git push*`. The system relies on the deny floor being expressed in the rendered output; the Claude adapter currently does not express it.

**Fix** (~10 lines, one method):

```python
# src/aspis/runtimes/claude.py — replace render_agent
def render_agent(
    self,
    agent: CatalogAgent,
    *,
    project_config: dict | None = None,
    inventory: RuntimeInventory | None = None,
) -> str:
    data: dict = {
        "name": agent.name,
        "description": agent.description,
        "tools": self.tools_for(agent.tools),
        "model": self._resolve_model(agent, project_config, inventory),
    }
    # FR-010: preserve the permission block so the runtime can enforce
    # the deny floor and the R-008 protected-path set.
    if agent.permissions:
        data["permissions"] = dict(agent.permissions)
    return f"{to_frontmatter(data)}\n{agent.body}\n"
```

And update the module docstring (lines 5-8) to describe the preserved block instead of the deliberate drop.

**Severity**: CRITICAL. This is the load-bearing safety floor. T-40 cannot pass with a Claude project that has no permission surface.

---

### HIGH (3)

#### H-1 · `validate-runtime` rejects `--runtime all` (SC-003)

**File**: `src/aspis/commands/validate_runtime.py:48-57`

**Standard violation**: SC-003 (SPEC.md:124) — "`aspis validate-runtime --runtime all` exits 0 for all 12 agent bodies."

**Evidence**:
```python
def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "validate-runtime",
        help="Validate every catalog agent: required frontmatter fields present, "
             "skill refs resolve, delegate refs resolve (no orphans).",
    )
    parser.set_defaults(func=_run)
```
No `--runtime` argument. `aspis validate-runtime --runtime all` raises `unrecognized arguments: --runtime`.

**Why it matters**: the SC-### acceptance criterion names a flag the verb doesn't accept. The verb IS structurally correct (it always checks every agent), so `--runtime all` would be a no-op — but the SC text needs the flag to work.

**Fix** (3 lines, no behavior change):
```python
parser.add_argument(
    "--runtime", default="all", choices=("all",),
    help="Scope to a runtime set (default: all — the verb always checks every agent).",
)
```

**Severity**: HIGH (SC-### text violated). Mediated by the fact that the verb is functionally correct.

#### H-2 · `byte-parity` rejects `--dry-run` (SC-004)

**File**: `src/aspis/commands/byte_parity.py:55-74`

**Standard violation**: SC-004 (SPEC.md:125) — "`aspis byte-parity --dry-run` reports catalog self-consistency (catalog render matches expected output shape; no broken refs, no missing fields)."

**Evidence**: same pattern as H-1 — `add_parser` (lines 57-63) accepts only `path` (positional) and `--help`. No `--dry-run`.

**Why it matters**: SC-004 names the flag. The verb IS dry-by-design (it never writes), so `--dry-run` is a no-op semantically — but the SC text needs the flag to be accepted.

**Fix** (2 lines):
```python
parser.add_argument(
    "--dry-run", action="store_true", default=True,
    help="Plan without writing (default — the verb is always dry-run).",
)
```

**Severity**: HIGH (SC-### text violated). Mediated by the fact that the verb is functionally correct.

#### H-3 · `governance revoke` requires `--approver` (spec says optional)

**File**: `src/aspis/commands/governance.py:566-573`

**Standard violation**: `Research/ref/governance.md:497-503` — `aspis governance revoke --id <APRV-NNN> --reason <reason> [--approver <id>]` with `--approver <id> (optional) who is revoking; defaults to the original approver`.

**Evidence**:
```python
rev = sub.add_parser("revoke", help="Revoke a prior approval (append-only).")
rev.add_argument("--id", required=True, help="APRV-NNN to revoke.")
rev.add_argument("--reason", required=True, help="Why this approval is being revoked.")
rev.add_argument(
    "--approver", required=True,
    help="Who is revoking (REQUIRED — R-008 gate).",
)
```
`--approver` is `required=True` (line 570). Spec says optional. Spec also says "defaults to the original approver" (line 501) — the implementation has no logic to default.

**Why it matters**: T-36 says "MUST match governance.md §6 verbatim" (TASKS.md:108). The `--approver` flag's optionality is a load-bearing spec detail — a human revoking their own approval is the canonical case; requiring them to re-state their own handle is friction. The current implementation REQUIRES it, which is over-restrictive.

**Fix** (~5 lines):
1. Change `required=True` → leave default (no `required=`).
2. In `_revoke` (lines 424-464), if `args.approver` is empty/None, default to the entry's existing `approver` field (line 451 area has the entry loaded).
3. Keep the empty-string rejection for the explicit-`--approver ""` case (security).

**Severity**: HIGH. The spec explicitly says this is a verbatim-match requirement, and the divergence is operationally meaningful (a human revoking their own approval shouldn't have to re-type their handle).

---

### MEDIUM (4)

#### M-1 · `governance request` requires `--reason` (spec says optional)

**File**: `src/aspis/commands/governance.py:529-535`

**Standard violation**: `Research/ref/governance.md:442-445` — `--reason <text> (optional) human-readable reason; prompted if absent`.

**Evidence**:
```python
req = sub.add_parser("request", help="Declare intent to write a protected path.")
req.add_argument("--path", dest="paths", required=True, action="append", ...)
req.add_argument("--reason", required=True, help="Human-readable reason for the write.")
```
`--reason` is `required=True`. Spec says optional. Spec text: "human-readable reason; prompted if absent" — the implementation does not prompt.

**Why it matters**: same as H-3 — verbatim-match requirement. The spec explicitly notes that `request` is **passive** (line 449, "Does not modify the ledger"), so the `--reason` is just context for the human reader. Making it required adds friction without value.

**Fix** (2 lines):
```python
req.add_argument("--reason", help="Human-readable reason for the write (optional).")
```
And in `_request` (lines 300-312), handle the empty-`--reason` case in the printed command (just omit the `--reason` flag from the printed shell snippet when empty).

**Severity**: MEDIUM. Same verbatim-match category as H-3 but less load-bearing (a human can always type a reason).

#### M-2 · `governance audit` is missing `--until`, `--status` (spec §6)

**File**: `src/aspis/commands/governance.py:556-563`

**Standard violation**: `Research/ref/governance.md:477-487` — `audit [--since <iso>] [--until <iso>] [--path <glob>] [--approver <id>] [--status <active|revoked|expired>] [--pretty]`.

**Evidence**:
```python
aud = sub.add_parser("audit", help="Query the approval ledger.")
aud.add_argument("--since", help="ISO 8601 filter: at/after this timestamp.")
aud.add_argument("--approver", help="Filter by approver handle.")
aud.add_argument(
    "--path", action="append", dest="path_filters",
    help="Filter by path glob (repeatable).",
)
```
**Missing**: `--until`, `--status`, `--pretty`. The implementation supports `--since` and `--approver` (and `--path` via the glob filter at lines 399-406).

**Why it matters**: SC-### and the spec text name the missing flags. `--until` and `--status` are operationally useful (find approvals that expired in a window; filter to active-only or revoked-only). `--pretty` is cosmetic.

**Fix** (3 lines + handler logic):
```python
aud.add_argument("--until", help="ISO 8601 filter: at/before this timestamp.")
aud.add_argument("--status", choices=("active", "revoked", "expired"),
                  help="Filter by entry status.")
aud.add_argument("--pretty", action="store_true",
                  help="Human-readable table output (default: machine-friendly).")
```
And in `_audit` (lines 378-421), add the `entries = [e for e in entries if e.get("status") == args.status]` and `entries = [e for e in entries if (parse(e.get("timestamp")) or now) <= args.until]` lines. Pretty-print is a small format change.

**Severity**: MEDIUM. Two of three missing flags are functional (`--until`, `--status`); the third is cosmetic. The spec says verbatim match.

#### M-3 · `governance` uses `yaml` (violates stdlib-only spec rule)

**File**: `src/aspis/commands/governance.py:35`

**Standard violation**: PLAN.md:164 — "Is stdlib-only (no third-party imports) — self-contained".

**Evidence**: line 35 `import yaml`. `yaml` is PyYAML, a third-party dep (in `uv.lock:244`, listed in `ATTRIBUTIONS.md:13`).

**Why it matters**: the spec's "stdlib-only" rule was written for the planning scripts, which use stdlib only. The governance verb needs human-readable structured I/O for the ledger, and `yaml` is the project's standard for that. The other CLI verbs in `src/aspis/commands/` (models.py:18, e.g.) also use `yaml` — this is a project-wide pattern, not a per-verb choice.

**Fix (one of two)**:
- **(a) Pragmatic**: update the spec to allow `yaml` for verbs that need structured I/O. One-line edit to PLAN.md:164: "Is stdlib-only (no third-party imports) — self-contained" → "Is stdlib-only except for `pyyaml` (used by the YAML-ledger verbs; project-wide dep)".
- **(b) Strict**: replace `yaml.safe_load` / `yaml.dump` with stdlib `json`. The ledger becomes a JSON file — different ergonomics (less human-friendly for the append-only review pattern), but stdlib-only. The cost is breaking the convention that all append-only state files are YAML.

**Recommendation**: (a). The "stdlib-only" rule is about deployment portability (no fresh `pip install` needed). The project already has PyYAML as a hard dep. The cost of (b) is the convention break; the benefit is one import.

**Severity**: MEDIUM. The verb works correctly; the spec text is overly strict.

#### M-4 · `export --dry-run` flag value is never read

**File**: `src/aspis/commands/export_cmd.py:45-49, 86-99`

**Standard violation**: UX consistency (no spec text violated).

**Evidence**:
```python
parser.add_argument(
    "--dry-run",
    action="store_true",
    default=True,
    help="Plan without writing (default).",
)
...
apply = bool(args.apply or args.force)  # --force implies writing
```
The `args.dry_run` value is set to `True` (line 47) but never read in `_run`. The actual logic uses `args.apply or args.force` to decide whether to write. So `--dry-run` (when explicitly passed) and "no flag" both produce the same outcome.

**Why it matters**: the help text says "Plan without writing (default)" — accurate, but the flag is a no-op. A user who explicitly passes `--dry-run` to override `--apply` from a script will be confused when the write still happens.

**Fix** (5 lines):
```python
parser.add_argument(
    "--dry-run",
    action="store_true",
    default=True,
    help="Plan without writing (default; overridden by --apply or --force).",
)
# ... in _run, after args is parsed:
if apply and args.dry_run and not args.force:
    # Edge: user passed both --dry-run and --apply. Prefer --apply's intent.
    pass  # current behavior; documented in help
```

The cleanest fix is to make `--dry-run` a `store_true` with `default=False` (so the flag has effect when passed), and the `apply` logic in `_run` already handles the "no --apply and no --force" case correctly. **Current behavior is correct; the flag is just cosmetic.**

**Severity**: MEDIUM (UX confusion; no functional bug).

---

### LOW (4)

#### L-1 · Ledger schema uses snake_case where spec uses kebab-case

**File**: `src/aspis/commands/governance.py:351-365`

**Standard violation**: `Research/ref/governance.md:268-294, 314` — ledger field names use kebab-case (`revoked-at`, `revoked-by`, `glob-approved`).

**Evidence**:
```python
entry: dict[str, Any] = {
    "id": _next_id(entries),
    "timestamp": _now_iso(),
    "approver": args.approver.strip(),
    "scope": {...},
    "expiry": args.expiry,
    "status": "active",
    "glob_approval": bool(args.glob_approval),  # spec: glob-approved
    "applied": [],
    "revocation": {
        "revoked_at": _now_iso(),     # spec: revoked-at
        "revoked_by": ...,             # spec: revoked-by
        "reason": ...,
    },
}
```
Spec uses kebab-case (`revoked-at`, `revoked-by`, `glob-approved`); implementation uses snake_case.

**Why it matters**: cosmetic only. The fields are all string keys, not parsed by code. Any consumer that hardcodes the field name (e.g. a downstream tool reading the ledger) would need to use whichever spelling the implementation picks. The spec is normative; the implementation diverges.

**Fix** (1-line edits): rename `revoked_at` → `revoked-at`, `revoked_by` → `revoked-by`, `glob_approval` → `glob-approved`. Update reads in `_revoke` (lines 453-456) accordingly. **Cost: 4 string-literal changes.**

**Severity**: LOW. Cosmetic; no functional impact.

#### L-2 · `governance ledger` output omits `lock_state`

**File**: `src/aspis/commands/governance.py:467-485`

**Standard violation**: `Research/ref/governance.md:530-532` — "Prints ledger path, entry count, oldest/newest timestamps, **and current lock state**."

**Evidence**:
```python
def _ledger(args: argparse.Namespace) -> int:
    ...
    print(f"path:   {ledger}")
    print(f"exists: {ledger.is_file()}")
    print(f"count:  {len(entries)}")
    if entries:
        ...
        print(f"active:  {active}")
        print(f"revoked: {revoked}")
    return 0
```
**Missing**: `lock_state` field. The implementation has `_LOCK_REL` (line 45) and `_acquire_lock` (lines 227-257) but the `ledger` subcommand doesn't check whether the lock is held.

**Fix** (3 lines):
```python
lock = Path.cwd() / LOCK_REL
if lock.is_file():
    age = int(_now_utc().timestamp() - lock.stat().st_mtime)
    print(f"lock:    held (age={age}s)")
else:
    print(f"lock:    free")
```

**Severity**: LOW. Spec says "current lock state" but this is a diagnostic detail; the verb's `lock` field is more useful when there's a lock issue.

#### L-3 · `governance revoke` mutates in place rather than appending

**File**: `src/aspis/commands/governance.py:445-460`

**Standard violation**: `Research/ref/governance.md:323-325` — "a revocation is a **new entry** that flips an existing entry's status to `revoked`".

**Evidence**:
```python
for entry in entries:
    if entry.get("id") == target_id:
        ...
        entry["status"] = "revoked"
        entry["revocation"] = {
            "revoked_at": _now_iso(),
            "revoked_by": args.approver.strip(),
            "reason": args.reason,
        }
        _write_ledger(ledger, entries)
```
The existing entry is mutated in place. The spec §1 (line 55-58) says "Revocations set `status: revoked` but never delete entries" — this is satisfied. The spec §4 (line 323) says "a revocation is a **new entry**" — this is NOT satisfied (no new entry is added).

**Why it matters**: the audit-trail invariant ("the original entry remains") IS satisfied. The "append a new entry" pattern would mean: keep the original entry (with `status: active` forever), add a new entry (with `status: revoked`, `revokes: APRV-001` link). The current implementation keeps the original entry and **changes its status** — operationally equivalent (the audit trail is preserved) but architecturally different (the spec's "two entries" pattern vs the implementation's "one entry, status flip" pattern).

**Why this is LOW**: the invariant ("never lose history") is preserved. The architectural pattern is slightly different. Either pattern is acceptable; the implementation chose the simpler one.

**Fix**: would require redesigning the ledger schema (each entry references a "revokes" link). Not a bug — a design choice that diverges from one paragraph of the spec.

**Severity**: LOW. Operational behavior is correct; spec text divergence is a paragraph-level interpretation.

#### L-4 · `governance` `request` is `passive` but `--reason` is required (M-1 redundancy)

**File**: `src/aspis/commands/governance.py:529-535, 299-312`

**Standard violation**: M-1 already covered this. Listed here for completeness: the spec says `request` is "passive — does not approve, does not write" (line 449) — making `--reason` required is inconsistent with the passive contract.

**Severity**: LOW (subsumed by M-1).

---

## 5 · What the build did well

1. **Thin wrappers, no re-implementation.** Every verb delegates to the existing public APIs of `aspis.export`, `aspis.protect`, `aspis.transform`, `aspis.catalog`. The `byte-parity` verb is a 212-line reporter that uses the same `plan_export`, `decide`, `sha256_text`, `render_agent` as the export verb — **zero duplication**. The `export` verb is a 143-line CLI over the same `plan_export`/`write_export` `aspis init` uses — **zero duplication**.
2. **Path-resolved CRITICAL-1 from L1 plan-feasibility review.** All 4 verbs are in `src/aspis/commands/`, not `src/aspis/cli/`. The `register(subparsers)` pattern is followed. The `COMMAND_MODULES` tuple is updated correctly. No missing entries.
3. **Governance is production-grade.** The ledger code (`_write_ledger` with `os.replace` atomic write, `_acquire_lock` with `O_CREAT|O_EXCL` atomic create + stale-lock recovery, expiry detection at check time, deterministic 0/2/3/4/5 exit codes) is **not a stub**. This is the R-008 mechanism in code, end to end.
4. **Protected paths are correct.** The `PROTECTED_PATHS` constant (lines 52-67) matches `Research/ref/governance.md:99-122` verbatim — same 14 patterns, same order.
5. **Path glob matching is correct.** The `_glob_to_regex` + `_matches` implementation (lines 82-132) correctly handles `**` (any depth, including root), `*` (single segment), `?` (single char), and all regex metacharacters. The `pathlib.PurePath.match` was rightly rejected (the docstring at lines 121-124 explains why).
6. **Cross-agent consistency check folded into `validate-runtime` (per T-31).** The verb checks skill refs, delegate refs, AND frontmatter shape in one pass — no separate `cross_ref_agents.py` needed. SC-006 (every agent body passes the agent-body standard check) is verifiable by a single CLI command.
7. **Catalog is clean.** All 12 agent files have all 11 required frontmatter fields. The T-40 fix (`176f546 fix(F-017/T-40): add missing delegates+runtimes to bootstrap frontmatter`) is verified by reading `bootstrap.md:29-30` — both fields are present.
8. **3 of 4 verbs are stdlib-only.** `validate-runtime`, `byte-parity`, `export` import only `argparse`, `pathlib`, `typing` (stdlib) + project modules. The architecture-constitution rule C-AUTOMATION ("script before agent") is honored.
9. **`--help` is honest and contract-accurate.** All 4 verbs' `help=` strings describe what the verb actually does. The 3 thin wrappers explicitly mention "thin wrapper over ... no re-implementation" — single source of truth, no restated content (R-006).

---

## 6 · Cost-of-change verification (per SC-011)

> "The cost-of-change for adding a new agent or skill MUST be ≤ 3 files."

The 4 new verbs were added with exactly **5 file changes**:
1. `src/aspis/commands/__init__.py` (registration)
2. `src/aspis/commands/validate_runtime.py` (new)
3. `src/aspis/commands/byte_parity.py` (new)
4. `src/aspis/commands/export_cmd.py` (new)
5. `src/aspis/commands/governance.py` (new)

**This is 5 files for 4 new verbs, not 4 files for 4 new verbs** — the `__init__.py` edit is a single-file change. **SC-011 passes: adding a new verb costs 2 files (1 new module + 1 entry in `__init__.py`).** The cost-of-change test is honored.

(The Claude adapter fix C-1 would add 1 more file to the L2-P0 cost — a 1-line edit to `src/aspis/runtimes/claude.py`. The fix is small; the absence is the issue, not the cost.)

---

## 7 · R-006 single-source check (the load-bearing standard rule)

> R-006: "An agent instruction holds identity, rules, and skill references; the intelligence lives in skills. State each fact once and reference it — don't duplicate rules, procedures, or assets."

| Check | validate-runtime | byte-parity | export | governance |
|---|---|---|---|---|
| No re-implementation of rendering | ✓ | ✓ | ✓ | n/a (governance has no render) |
| No re-implementation of protection engine | n/a | ✓ | n/a | n/a (uses `decide` from `aspis.protect`) |
| No re-implementation of glob matching | n/a | n/a | n/a | ✓ (uses stdlib `re`; no glob lib) |
| Single source for plan_export | n/a | ✓ | ✓ | n/a |
| Single source for ledger I/O | n/a | n/a | n/a | ✓ (own file, no other writer) |
| Docstrings cite, don't restate | ✓ | ✓ | ✓ | ⚠ line 41 cites "Source: governance.md §3" — good |

**R-006 verdict**: 4 of 4 verbs are R-006 compliant. The `export` docstring (line 7) explicitly says "single source of truth" for the init/export reconciliation. The `byte-parity` docstring (lines 17-23) explicitly says "no re-implementation of either". **The discipline is honored at the file level.**

---

## 8 · Final verdict

**CHANGES REQUIRED** — 1 CRITICAL, 3 HIGH, 4 MEDIUM, 4 LOW.

**The build is structurally sound.** The thin-wrapper architecture is honored, the protection-engine integration is correct, the governance ledger is production-grade, and the registration pattern is followed. **T-33, T-34 are APPROVED WITH NOTES** (one missing flag each, 2-line fixes). **T-35 is CHANGES REQUIRED** (the Claude adapter fix was not done — C-1 blocks T-40). **T-36 is CHANGES REQUIRED** (H-3 + M-1 + M-2 are spec-divergences; L-1, L-2, L-3 are clean-up).

**Recommendation**:

1. **Fix C-1** (one file, ~10 lines): the Claude adapter's `render_agent` must emit the `permissions` block. This is the load-bearing safety floor — R-008 boundary enforcement depends on it.
2. **Fix H-1, H-2** (4 lines total): add `--runtime` to `validate-runtime` and `--dry-run` to `byte-parity` as no-op flags for spec compatibility.
3. **Fix H-3, M-1, M-2** (governance verb): make `revoke --approver` and `request --reason` optional; add `--until` and `--status` to `audit`. ~10 lines.
4. **M-3** (PyYAML): update spec text to allow `yaml` for ledger I/O. 1-line edit to PLAN.md.
5. **L-1, L-2, L-3, L-4** (cosmetic): schedule for T-55 polish pass.

**Routing**:

- **C-1** (CRITICAL) → system-lead (single-file adapter fix; the only planned core Python edit; R-008-gated per the plan's "Decisions needing approval" item 3).
- **H-1, H-2** (HIGH) → system-lead (verb surface fixes; sub-reviewer or peer check).
- **H-3, M-1, M-2, L-1, L-2** (governance spec divergences) → system-lead (governance verb edits; sub-reviewer check).
- **M-3** (spec text) → project-lead (one-line spec edit; no R-008 needed).
- **M-4, L-3, L-4** (cosmetic / UX) → polish pass (T-55).

**Do NOT proceed to T-40 (L2-P0 integration check) without addressing C-1.** The T-40 acceptance criterion "`aspis byte-parity --dry-run` reports catalog self-consistency CLEAN" can be satisfied (M-1 fix is 2 lines); but the implicit acceptance criterion "an `aspis export` to a Claude project lands agents with permission surfaces" cannot be satisfied until C-1 is fixed.

**Do NOT proceed to L2-P1 (T-41+) without addressing at least C-1, H-1, H-2, H-3.** These are spec-text violations that the L2-P1 layer will inherit and propagate.

---

## 9 · Files reviewed

- `src/aspis/commands/validate_runtime.py` (179 lines)
- `src/aspis/commands/byte_parity.py` (212 lines)
- `src/aspis/commands/export_cmd.py` (143 lines)
- `src/aspis/commands/governance.py` (582 lines)
- `src/aspis/commands/__init__.py` (54 lines) — registration
- `src/aspis/cli.py` (74 lines) — dispatch loop
- `src/aspis/runtimes/claude.py` (105 lines) — adapter NOT modified in this build (C-1)
- `src/aspis/runtimes/opencode.py` (197 lines) — reference for how the permission block IS emitted on OpenCode
- `src/aspis/runtimes/base.py` (217 lines) — base adapter contract
- `src/aspis/export.py` (549 lines) — the existing pipeline that byte-parity and export thin-wrap
- `src/aspis/protect.py` (153 lines) — the 6-way decision engine
- `src/aspis/catalog.py` (111 lines) — `CatalogAgent` definition, `split_frontmatter`
- `src/aspis/transform.py` (35 lines) — the render dispatcher
- `src/aspis/data/catalog/agents/*.md` (12 files) — the catalog the validate-runtime verb sweeps
- `src/aspis/data/catalog/skills/` (52 directories) — the skill catalog validate-runtime references resolve against
- `.aspis/features/F-017-complete-agent-system/SPEC.md` — acceptance scenarios SC-003, SC-004, SC-006, FR-010
- `.aspis/features/F-017-complete-agent-system/PLAN.md` — Component 7 (CLI verbs), Component 8 (governance)
- `.aspis/features/F-017-complete-agent-system/TASKS.md` — T-33, T-34, T-35, T-36 definitions
- `.aspis/features/F-016-agent-system-architecture/Research/ref/governance.md` (634 lines) — governance §6 spec
- `.aspis/features/F-016-agent-system-architecture/Research/ref/claude.md` and other agent refs — for permission surface cross-check
- `.aspis/context/AGENT_BODY_STANDARD.md` (112 lines) — 11-field frontmatter contract
- `.aspis/features/F-017-complete-agent-system/Review/integration-gates.md` (347 lines, prior L2-P0 review — for context)
- `.aspis/features/F-017-complete-agent-system/Review/plan-feasibility.md` (411 lines, prior L1 plan review — for context)
- `.aspis/features/F-017-complete-agent-system/Review/architecture-constitution.md` — M-2 finding on Claude adapter fix location
- `.aspis/features/F-017-complete-agent-system/Review/completeness-traceability.md` — m-3 finding on Claude adapter fix vagueness

---

*Reviewer: Reviewer (independent quality authority).*
*Date: 2026-06-27. Verdict: CHANGES REQUIRED. Re-review on C-1 + H-1..H-3 + M-1 + M-2 fixes.*
