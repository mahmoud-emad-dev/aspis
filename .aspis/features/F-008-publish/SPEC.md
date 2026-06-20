# F-008 — v0 publish-readiness · Specification

Mode: **mvp** — focused rigor, built directly (no task packets), committed per unit.

## Goal

Make ASPIS honestly publishable as v0: the gate runs in CI on **both** OSes, the docs
match reality and onboard a newcomer, the two F-007 dogfood findings are fixed, and a
worked example proves the loop on a real (small) project. After this, creating the
GitHub remote and making it public is the user's action.

## Scope

### Allowed
- `.github/workflows/**` — CI.
- `README.md`, `docs/**` — docs + quickstart + worked example.
- `src/aspis/data/catalog/config/commit-convention.yaml`,
  `src/aspis/data/catalog/scripts/hooks/commitmsg.py` — attribution-blocklist fix.
- `.gitignore`, the generated brain index files — stop tracking generated brain.
- `examples/**` (or `docs/examples/**`) — the worked example.
- `tests/**` for any new behaviour; `.aspis/context/**` docs; dogfood regenerate.

### Forbidden
- Model-routing / OpenCode provider detection (separate future feature, gated on research).
- Tracing spine, dashboard, self-improvement (post-v0).
- Pushing / creating the remote (the user's action).

## User stories
- **US-1 — Trusted gate.** As a contributor, every push runs ruff + pytest on Windows and
  Linux, so the cross-platform rule (C-PORTABLE) is enforced, not just claimed.
- **US-2 — Onboarded in minutes.** As a newcomer, the README and a quickstart take me from
  clone to a first `init → bootstrap → loop` without guessing.
- **US-3 — Clean dogfood.** As a committer, a commit may mention the `.claude` directory,
  and the working tree stays clean after each commit (no generated-file churn).
- **US-4 — Proof it's real.** As an evaluator, a worked example shows ASPIS running its
  loop on a small project, and what it adds over a bare runtime.

## Functional requirements
- **FR-001 (finding 1)**: The commit-message attribution check flags real attribution
  (`Co-Authored-By`, "generated with", model-by/with phrases, 🤖) but **not** a bare
  mention of the `.claude` / `.opencode` runtime directories. Rules stay data-driven.
- **FR-002 (finding 2)**: Generated brain index files (CURRENT_STATE, RECENT_CHANGES,
  CODE_MAP, FILE_REGISTRY) are **no longer tracked** (constitution rule 8, Generated
  Artifacts); they regenerate locally on demand / post-commit, so the tree stays clean.
  `.gitignore` ignores them; existing copies are `git rm --cached`-ed.
- **FR-003 (CI)**: A GitHub Actions workflow runs `uv sync` + `ruff format --check` +
  `ruff check` + `pytest` on a **Windows + Linux** matrix, on push and PR.
- **FR-004 (docs)**: README fixes `.asps`→`.aspis`, lists the real CLI, and links a
  quickstart. A quickstart doc walks `clone → uv sync → init → bootstrap → the loop`.
- **FR-005 (example)**: A small worked example + "your first ASPIS build" doc shows the
  loop end-to-end and what ASPIS adds over a bare runtime.

## Success criteria
- **SC-1**: `commitmsg.validate` rejects `Co-Authored-By: …` and "generated with claude"
  but accepts "ship to the `.claude` runtime dir"; covered by a test.
- **SC-2**: After a commit, `git status` is clean (no generated brain files dirty).
- **SC-3**: The CI workflow exists and its steps mirror the local gate on both OSes.
- **SC-4**: README has no `.asps` reference and lists `init/bootstrap/.../commit/doctor`.
- **SC-5**: The example runs and is documented; the full gate stays green.

## Out of scope (deferred)
Model routing, OpenCode provider/subscription detection, the research/stack subagent,
real-env A/B comparison harness, tracing — captured in the post-F-007 backlog.
