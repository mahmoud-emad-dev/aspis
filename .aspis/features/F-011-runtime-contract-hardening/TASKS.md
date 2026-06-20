# F-011 — TASKS

Sequenced, dependency-ordered. Each task ends with tests + a green Windows gate +
one atomic `aspis commit`. Line numbers in the audit have shifted — re-verify each
`file:symbol` before editing (done during planning; references below are current).

## Cluster A — adapter-contract consolidation (one-place runtime change)

- **T-01 — Extend the `RuntimeAdapter` contract.** In `runtimes/base.py` add three
  members: `runtime_dir` (property, default `f".{self.name}"`), `root_guide`
  (`str | None`, default `None` — the runtime's own root guide filename) and
  `supports_mode` (`bool`, default `False` — whether the runtime expresses an agent
  `mode` field). Set `root_guide = "CLAUDE.md"` on `ClaudeAdapter`; set
  `supports_mode = True` on `OpenCodeAdapter`. Add a `runtime_dirs()` helper to
  `runtimes/__init__.py`. Unit-test each member. Update `.aspis/context/ARCHITECTURE.md`
  (adapter section) + a `DECISIONS.md` entry (why `supports_mode`, not `promotable`).

- **T-02 — Route the `.<runtime>` dir through `runtime_dir`.** Replace the three
  hand-built dirs: `detect.py` `_IGNORED` (use `runtime_dirs()`), `assetkinds.py:target`
  (`prefix = f".{runtime}/{name}"`), `promotion.py:promote_leads`
  (`target_root / f".{runtime}" / "agents"`). All via the adapter. Tests stay green.

- **T-03 — Route the root-guide rule through `root_guide`.** In
  `operations/init.py:_write_root_files` replace `if "claude" in profile.runtimes:`
  with: for each runtime in the profile, if its adapter declares a `root_guide`, emit
  it. Test: a profile without claude emits no CLAUDE.md; one with it does.

- **T-04 — Route mode-promotion through `supports_mode`.** In `promotion.py` drop
  `_MODE_RUNTIME = "opencode"`; default the runtime to the one whose adapter
  `supports_mode`. Existing promotion tests pass; add one asserting the default resolves.

- **T-05 — Remove the dead runtime source.** Drop `RUNTIMES` from `constants.py` and
  `runtimes` from `settings.py` (no engine reader). Update `test_settings.py` to assert
  against `available_runtimes()` (the real source). One source of truth.

## Cluster B — correctness & portability

- **T-06 — Fix dangling template paths.** `skills/feature-planning/SKILL.md` and
  `skills/architecture-planning/SKILL.md` point at `.aspis/templates/{SPEC,PLAN}.md`;
  fix to `.aspis/templates/planning/{SPEC,PLAN}.md` (match `task-decomposition`). Then
  dogfood-regenerate `.claude`/`.opencode` (separate chore commit).

- **T-07 — Cross-platform subprocess fixes (rule 12).** Add `encoding="utf-8",
  errors="replace"` to the output-reading `subprocess.run` in `operations/bootstrap.py`
  (`_git`) and `hooks.py` (`HookRunner._run_one`). Match the `commit.py` pattern.

## Cluster C — close the untested-gate hole (R-005)

- **T-08 — Test `scripts/hooks/secret_scan.py`** (matches secrets in added lines,
  ignores `+++` headers; `main()` exits non-zero on a hit).
- **T-09 — Test `scripts/hooks/precommit.py`** (R-009 protected-paths gate blocks an
  unapproved edit, passes when approved).
- **T-10 — Test `scripts/hooks/runtime_guard.py`** (parses PreToolUse JSON from stdin,
  applies the block/warn veto).
- **T-11 — Test the rest** (`install.py` wrapper creation + idempotency; `postcommit.py`
  always exits 0; doctor/health FAIL branch exits 1). Per-unit commits if large.

## Cluster D — doc/config drift (last, cosmetic)

- **T-12 — Drift cleanup.** (a) `constitution-checks.yaml` — wire a check or reframe the
  header as advisory. (b) `commit-convention.yaml` — refresh the stale header; annotate
  unconsumed keys. (c) `base.yaml` — remove vestigial empty `hooks:`/`scripts:`. (d) the
  `model:` → `tier:` rename is **R-008 — confirm with the user**; leave a flagged note only.

## Definition of done
All tasks committed per unit, gate green on Windows. Set the feature phase to `review`,
then `merged` after the user confirms. F-010 (models) is next.
