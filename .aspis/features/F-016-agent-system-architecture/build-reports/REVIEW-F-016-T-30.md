# Review — F-016 / T-30

> Filled by the reviewer (read-only — you evaluate and report, you never edit the
> work). The header is stamped by `aspis artifact`; you fill the verdict and
> findings from evidence (the diff, the tests, the acceptance criteria).

- **Feature**: F-016 — Agent System Architecture
- **Task**: T-30 — Catalog structural validation
- **Date**: 2026-06-27
- **Verdict**: changes-requested

## Scope reviewed

All 11 catalog agent files at `src/aspis/data/catalog/agents/`:

- `project-lead.md`, `planning-lead.md`, `build-lead.md`, `reviewer.md`,
  `system-lead.md`, `fix-lead.md`, `test-lead.md`, `research-lead.md`,
  `committer.md`, `general-builder.md`, `project-explorer.md`

Plus the SPEC/PLAN/TASKS contracts that define the gate:

- `.aspis/features/F-016-agent-system-architecture/SPEC.md` (FR-007, FR-011)
- `.aspis/features/F-016-agent-system-architecture/TASKS.md` (T-30 gate)
- `.aspis/features/F-016-agent-system-architecture/PLAN.md` (§Component 2)
- `src/aspis/catalog.py` (CatalogAgent dataclass; runtime-lock default)
- Diff of `04f79a8` (the committer.md fix)

`bootstrap.md` is excluded from F-016 per the audit (1.4 in
`Research/current-aspis-audit-1.md`): it self-deletes post-onboarding, so the
working agent count is 11.

## Findings

| Severity | Where | Finding | Suggested fix |
|----------|-------|---------|---------------|
| **high** | `src/aspis/data/catalog/agents/*.md` (all 11 files) | The `runtimes` field is **missing from all 11 catalog agent files**. The T-30 gate (`TASKS.md:214`) lists it as required: *"Every frontmatter has: name, description, mode, model, tools, permissions, delegates, skills, **runtimes**, export_scope."* FR-011 (`SPEC.md:75`) also requires it: *"Every catalog agent frontmatter MUST include: name, description, mode, model (tier), temperature, tools, permissions (bash + web), delegates, skills, **runtimes**, export_scope."* PLAN §Component 2 (`PLAN.md:30`) names runtimes as one of the fields the catalog updates align. The `CatalogAgent` dataclass (`src/aspis/catalog.py:59`) has `runtimes: tuple[str, ...] = ()` and the parser (`src/aspis/catalog.py:96`) reads `data.get("runtimes", [])`, so absence defaults to "all runtimes" — functionally correct (all 11 agents ARE intended for all runtimes) but the gate as defined is failing. The validation request's claimed "11/11 PASS" omits `runtimes` from its check list, so the failure was not flagged. | Add `runtimes: []` to the frontmatter of all 11 files (one-line edit per file). Alternatively, if the design intent is that absence == all runtimes, update FR-011 and the T-30 gate to mark `runtimes` as optional — but document the decision in a `D-###` and re-validate. |
| **high** | The validation request itself | The validation's field list ("name, description, mode, model, temperature, tools, permissions (bash + webfetch keys), delegates, skills, export_scope") is **incomplete against its own gate**. It omits `runtimes` (required by T-30 gate and FR-011) and lists `temperature` (which is in FR-011 but not in the T-30 gate as literally written). The claimed "**11/11 PASS**" is therefore a check against a *different* field list than the gate defines. This is the root cause of finding #1 being missed. | Re-run the structural check against the exact field list in `TASKS.md:214` (T-30 gate) and `SPEC.md:75` (FR-011), reconcile any difference, and reissue the PASS/FAIL verdict. |
| medium | `src/aspis/data/catalog/agents/planning-lead.md:42-48` | The `delegates:` list includes 7 future L3 subagents (`clarify`, `task-decomposer`, `idea-capture`, `prd-writer`, `constitution-checker`, `scope-estimator`, `research-request-writer`) that do not exist as agents. The T-30 gate says *"Every delegate exists"* — strictly failing. The build notes (`TASKS.md:19-21`) explicitly allow this: *"Subagent roster is OUT of scope → F-017. The 'future subagents' named in the specs are NOT built here — leave them as references."* So the violation is intentional, but neither the gate definition nor the validation report captures the exemption. | One of: (a) move the future subagents to a clearly-marked "future / F-017" block that the gate's "every delegate exists" check ignores, (b) update the T-30 gate to exclude F-017 future subagents, or (c) record the exemption in the gate's output. The current state lets the gate be passed silently, which is harder to audit later. |
| medium | `src/aspis/data/catalog/agents/system-lead.md:32` | `websearch: deny` is set, but FR-007 (`SPEC.md:69`) says: *"All universal denies MUST be present in every agent's permission surface: `webfetch`/`websearch` denied except system-lead and research-lead."* So FR-007 implies system-lead's `websearch` should be `allow`. T-23 task spec explicitly overrides: *"websearch: deny (align with catalog intent)."* The T-23 owner decision is the right behavior (the SPEC was wrong), but the SPEC was never updated, and FR-007 is still a published acceptance criterion. This is a SPEC/PLAN inconsistency, not a catalog bug. | File a follow-up to update FR-007 to match the T-23 locked work-order. Tracked as a SPEC clarification, not a T-30 blocker. |
| low | The validation report summary (informational) | The committer isolation check (only `committer.md` has `git commit*: allow`) and the read-only check (`reviewer.md` + `project-explorer.md` have no `edit`/`write`) are both **correct and verifiable** by direct read of the files. `grep "commit\*\": allow"` returns exactly 2 hits, both in `committer.md` (lines 24, 26: `aspis commit*: allow` and `git commit*: allow`). All 10 other catalog files have `git commit*: deny` on their bash allowlist. The `tools:` lists of `reviewer.md` and `project-explorer.md` are `[read, grep, glob, bash]` — no edit, no write — and their `edit:` / `write:` permission blocks are absent or `*: deny`. Both claims PASS. | None — the claims are sound. |
| low | Diff `04f79a8` (`committer.md`) | The committer.md fix is appropriate and complete: `temperature: 0.1` was added (consistent with the other 10 agents) and `delegates: []` was added (correct for a leaf agent with no delegation; the same form already appears in `general-builder.md:46` and `project-explorer.md:35`). The fix is a one-line `+` per field. | None — the fix is good. |

## Acceptance criteria walk-through

From the review request (FR-010, FR-011, FR-012) and the T-30 gate (TASKS.md:214):

- **FR-010** — "All 11 catalog agent files MUST be updated to reflect their reference specs." → **PASS** in spirit (frontmatter shape aligned, body instructions reflect the spec identity; the `> Derived from Research/ref/<name>.md` headers are present). But see finding #high re: `runtimes`.
- **FR-011** — "Every catalog agent frontmatter MUST include: name, description, mode, model (tier), temperature, tools, permissions (bash + web), delegates, skills, **runtimes**, export_scope." → **FAIL** — `runtimes` is absent from all 11 files. All other fields are present (10/11 fields pass; the 11th is missing).
- **FR-012** — "Every skill referenced by an agent's body or skill allowlist MUST exist in the catalog." → **DEFERRED to T-31** (per the review request's own note, and the task definition).
- **T-30 gate** ("name, description, mode, model, tools, permissions, delegates, skills, **runtimes**, export_scope") → **FAIL** on `runtimes` (all 11 files); PASS on the other 9. Delegate resolution fails for the 7 planning-lead future subagents (medium finding).

## Decision & hand-off

**Verdict: changes-requested.**

The validation summary is **incomplete and overstates the result**. The
fix to `committer.md` is correct, and the committer-isolation / read-only /
delegate-resolution claims are all true as stated. But the
"Frontmatter completeness 11/11 PASS" line is wrong: the `runtimes` field
required by both FR-011 and the T-30 gate is missing from all 11 files. The
validation's own field list omits `runtimes`, which is why the gap was not
caught. The catalog parser tolerates the absence (defaults to all runtimes,
which is the correct intent for all 11 agents), so this is a
**gate-against-data inconsistency** rather than a runtime break — but the
T-30 gate as defined is failing.

**Required changes before T-30 can be marked done:**

1. **Add `runtimes: []` to all 11 catalog files** (11 one-line edits). This
   is the trivial fix; absence is already functionally equivalent, but the
   gate requires the field.
2. **Re-run the structural check against the T-30 gate's exact field list**
   (`TASKS.md:214`) and FR-011's exact field list (`SPEC.md:75`), and
   reissue the verdict with the corrected scope.
3. **Resolve the planning-lead future-subagents issue** (medium): either
   move them to a separate "F-017 future" block the gate ignores, update
   the gate to exempt F-017, or document the exemption in the gate's
   output.
4. **File a SPEC follow-up to reconcile FR-007** with the T-23 locked
   work-order (system-lead `websearch: deny`). Tracked, not blocking T-30.

**Route to:** a builder (a new mini-task T-30a) for the `runtimes: []` edits
and the field-list re-validation, then back to the reviewer for a clean
re-check. The committer.md fix is already in place (`04f79a8`) and does not
need to be re-done.

The committer fix, the committer-isolation claim, and the read-only claim
all stand as PASS; the verdict is `changes-requested` purely on the
`runtimes` gap and the planning-lead future-delegates structure.
