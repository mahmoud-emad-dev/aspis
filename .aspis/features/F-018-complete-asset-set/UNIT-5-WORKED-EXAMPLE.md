# Unit #5 — Worked Example: how Claude detects, what it found (OpenCode fixes this)

> This is a **teaching example** for OpenCode. Claude did the *detection* only
> (no fixes). Below is exactly how the checks were run, what was found, and —
> most importantly — **how each finding was triaged** (DEFECT / LEAN-FIX / KEEP /
> DEFER) and *why*. OpenCode: apply the LEAN-FIX items, leave the KEEP/DEFER items
> alone, then use this same method on the next units.
>
> **The judgment is the lesson, not the list.** Notice that most things were
> KEPT. The skill is knowing what *not* to touch.

**Unit #5 — Project setup.** Files: `operations/init.py` (209), `operations/bootstrap.py`
(489), `commands/init.py` (118), `commands/bootstrap.py` (77), `promotion.py` (66).

---

## Step 1 — Deterministic checks (scripts, no model judgment)

```
ruff check  → 2 issues, both in commands/init.py:
    init.py:3   I001  import block unsorted
    init.py:43  E501  line too long (101 > 100)
#9 special-cases grep → 1 hit: operations/init.py:27  `if name == "base"`
hardcoded model strings → none
pytest coverage → test_bootstrap.py, test_bootstrap_cli.py, test_init_cli.py,
                  test_init_op.py, test_promotion.py  (5 files — well covered)
```

## Step 2 — Read every file, judge against the criteria

Overall: **this unit is well-built.** `bootstrap.py` is 489 lines but every step
is a small single-job function with a clear docstring, staged as pre/core/post on
the lifecycle engine — the length is *earned*, not bloat. `promotion.py` promotes
via the `supports_mode` capability, never a runtime name (constitution #9 ✅).

## Step 3 — Findings, triaged

| # | Finding | Where | Label | Why this label |
|---|---|---|---|---|
| F1 | import block unsorted | `commands/init.py:3` | **LEAN-FIX** | mechanical, `ruff --fix` handles it |
| F2 | line too long (101) | `commands/init.py:43` | **LEAN-FIX** | wrap the help string |
| F3 | profile load+merge reimplemented in **4 places** | `export_cmd.py:76`, `byte_parity.py:90`, `models.py:225`, `operations/init.py:26` | **LEAN-FIX** | real single-source/#3 issue: a profile-loading change today touches 4 files. Extract one helper. |
| F4 | commit message `"chore: initialize ASPIS project"` duplicated | `operations/init.py:84` + `operations/bootstrap.py:269` | **LEAN-FIX** | two literals that must stay identical → one constant |
| F5 | `if name == "base"` | `operations/init.py:27` | **KEEP** | NOT a behavioural special-case — it's a root-identity guard (don't merge the base profile onto itself). Fixing it (rely on merge idempotency) adds fragility for zero gain. |
| F6 | `bootstrap.py` is 489 lines | whole file | **KEEP** | length is justified — many genuine steps, each small + documented. Splitting it would scatter one cohesive operation across files (worse, not better). |
| F7 | broad `except Exception` | `bootstrap.py:319` (`_validate_exports`) | **KEEP** | intentional — this is a validation gate collecting *any* parse failure as a problem; a narrow catch would miss real breakage. |
| F8 | `subprocess.run(...)` without `text/encoding` | `init.py` ×2, `bootstrap.py` ×3 | **KEEP** | every one uses `capture_output=True` but **discards** the output — nothing is decoded, so there is no portability bug. Adding `encoding=` would be cargo-cult. |
| F9 | bootstrap default mode = `production`; no `--mode` flag | `bootstrap.py:84` | **DEFER** | this is the "smooth for normal users" design lever, not a code defect — owner decides (mvp default + FAST PATH). Don't touch in a hardening pass. |
| F10 | top docstring is Purpose-only (not 4-part) | `operations/bootstrap.py:1` | **DEFER/optional** | the per-function docstrings already make it fully readable; raising the top one to 4-part is nice-to-have, not needed. |

**Net: 0 DEFECTS. 4 LEAN-FIX. 4 KEEP. 2 DEFER.** A clean unit — the value is the 4 small fixes, not a rewrite.

---

## Step 4 — Hand-off: what OpenCode should fix (the 4 LEAN-FIX only)

**F1+F2 — `commands/init.py` lint.**
- Run `ruff check --fix src/aspis/commands/init.py` for the import sort.
- Wrap line 43 (the `--apply` help string) under 100 chars.

**F3 — single-source the profile loader (the important one).**
- Add to `src/aspis/profiles.py`:
  ```python
  def load_merged(name: str, profiles_dir: Path) -> Profile:
      """Load *name* merged under the shared base profile (base alone when name=='base')."""
      base = load_profile(profiles_dir / "base.yaml")
      if name == "base":
          return base
      return merge(base, load_profile(profiles_dir / f"{name}.yaml"))
  ```
- Replace the 4 call sites to use it:
  `operations/init.py:_load_profile`, `commands/export_cmd.py:_resolve_profile`,
  `commands/models.py:225`, `commands/byte_parity.py:90` (the last two load base
  only — pass `"base"`). Keep each site's extra behaviour (export_cmd's runtime
  narrowing stays where it is).
- Note: `commands/models.py` is in the deferred Unit #4, but this is a pure
  mechanical call-site swap — safe to include.

**F4 — single-source the init commit message.**
- Add a constant (e.g. in `constants.py`): `INIT_COMMIT_MESSAGE = "chore: initialize ASPIS project"`.
- Use it in `operations/init.py:_commit_scaffold` and `operations/bootstrap.py:_autocommit_init`.

**After fixing — re-gate (mandatory):**
```
ruff check src/aspis/profiles.py src/aspis/operations/ src/aspis/commands/{init,export_cmd,models,byte_parity}.py   → clean
uv run pytest tests/test_init_op.py tests/test_init_cli.py tests/test_bootstrap_cli.py tests/test_promotion.py tests/test_export.py tests/test_profiles.py   → green
```
Then `committer` commits: `refactor(F-018): single-source profile loader + init commit msg (Unit #5)`.

Do **not** touch F5–F10. If you think one of them needs changing, STOP and flag it
for Claude — that is the flag-don't-fix rule.

---

## The lesson for the next units

1. Run the deterministic checks first — they find half the findings for free.
2. Read for *purpose and shape*, not just lint.
3. **Triage honestly: most findings are KEEP.** A "violation" that makes the code
   simpler to leave is not a defect.
4. Duplication across files (like F3) is the highest-value find — it's the
   cost-of-change test failing. Look for it.
5. Fix only DEFECT + LEAN-FIX. Keep gates green after every change.
