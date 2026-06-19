# F-007 — Git subsystem · Specification

Mode: **mvp** — focused rigor, built directly (no task packets), committed per unit.

## Goal

Make commits a **single, conventional, deterministic act**. F-006 already built the
automatic enforcement wall (the git hooks); F-007 adds the *authoring side*: one
commit authority (the committer) that composes a convention-valid message with a
deterministic tool and commits, letting the hooks fire automatically. No second
copy of the message rules, no `git add -A`, no AI attribution in history.

The split, in one line: **the agent composes, the tool builds the message, the
hooks enforce.** Each rule lives once — message style in `commit-convention.yaml`
(F-005), enforcement in `.aspis/scripts/hooks/` (F-006), composition in
`.aspis/scripts/git/` (this feature).

## Scope

### Allowed
- `src/aspis/data/catalog/scripts/git/**` — the deterministic compose helper.
- `src/aspis/commands/commit.py`, `src/aspis/commands/__init__.py` — the `aspis commit` verb.
- `src/aspis/data/catalog/agents/committer.md` — enrich the existing committer.
- `src/aspis/data/catalog/skills/{commit-message,commit-splitting,clean-tree-precondition}/**`.
- `src/aspis/data/profiles/base.yaml` — ship the three skills.
- `tests/test_commit.py`.
- `.aspis/context/{DECISIONS,ARCHITECTURE,ROADMAP}.md`, `.aspis/current/active_feature.json`.
- The dogfood regenerate (`.aspis/**` runtime, `.claude/**`, `.opencode/**`).

### Forbidden
- Touching the F-006 hook scripts or `commit-convention.yaml` rules (reuse, don't fork).
- Any `rules/**` or permission change (R-009).
- Pushing to a remote, or any worktree/conflict machinery (deferred).

## User stories
- **US-1 — One commit authority.** As a lead, I hand reviewed, gate-green work to the
  committer; it stages exactly the intended paths, composes a conventional message,
  and commits — consistently, every time.
- **US-2 — Compose, don't hand-format.** As the committer, I build the message from a
  tool (`aspis commit` / the compose script), so it always matches the convention and
  carries the right `F-NNN/T-NN..T-MM` scope and `Tasks:` trailer.
- **US-3 — The wall is automatic.** As anyone committing, the F-006 hooks validate the
  message and auto-fix the tree without me invoking them — the tool just commits.
- **US-4 — Human-authored history.** As the project owner, every commit reads as if a
  careful human wrote it — no model/tool attribution ever reaches the log.

## Functional requirements
- **FR-001**: A deterministic `scripts/git/compose.py` composes a message
  `type(F-NNN[/T-NN | /T-NN..T-MM]): title` + a bullet body + an optional
  `Tasks: …` trailer, reading the active-feature id from `active_feature.json`.
  Inputs (type, task/span, title, bullets, tasks) come from argv; output is the
  message on stdout. It **self-validates** by reusing F-006's
  `commitmsg.validate()` against `commit-convention.yaml` — no second rule copy.
- **FR-002**: `aspis commit` is the commit tool the committer triggers. It stages
  the explicitly-named paths (**never `-A`**), composes the message via
  `compose.py`, and runs `git commit -F <message>` so the F-006 hooks fire
  (pre-commit auto-fix/checks, commit-msg validation, post-commit refresh). It
  **never pushes** and never amends.
- **FR-003**: With no paths given, `aspis commit` refuses (nothing staged blindly);
  with a non-conventional input it reports the validation errors and does not commit.
- **FR-004**: The committer agent is enriched to use `aspis commit` as its only commit
  path: confirm scope → stage explicit paths → `aspis commit` → never push.
- **FR-005**: Three skills ship in the base profile and encode the scenarios:
  `commit-message` (how to compose), `commit-splitting` (one logical change per
  commit), `clean-tree-precondition` (start from a clean tree). They reference
  `aspis commit` and plain git — no resurrected `validate_commit`/`git_state` scripts.
- **FR-006**: `DECISIONS.md` records **D-011**; `ARCHITECTURE.md` gains a Git section;
  `ROADMAP.md` marks Phase 3.6 (F-007) done on merge.

## Out of scope (deferred)
- Pushing / remote management, PRs, worktrees, conflict resolution.
- Re-running the test suite inside any hook (F-006 decided: fast checks only).
- A separate commit-splitting *script* — guidance only for MVP (plain `git add <paths>`).

## Success criteria
- **SC-1**: `compose()` returns a message that `commitmsg.validate()` accepts, for a
  single task, a task span, and a scopeless lifecycle commit; it includes the
  `Tasks:` trailer when a span is given.
- **SC-2**: `aspis commit` with explicit paths creates exactly one commit of exactly
  those paths in a temp repo; called with no paths it exits non-zero without committing.
- **SC-3**: A composed message never contains a forbidden-attribution token; a message
  carrying one is rejected by the self-validate before git is invoked.
- **SC-4**: The committer agent and three skills ship via the base profile after export.
- **SC-5**: The full existing suite stays green; new tests cover SC-1..SC-3.

## Design notes / decisions
- **Reuse over rebuild (DRY).** Message rules = `commit-convention.yaml` (F-005);
  validation = `commitmsg.validate()` (F-006); git state = `scripts/hooks/_git.py`
  (F-006). F-007 adds only composition + the `aspis commit` orchestration.
- **Tool, then agent (R-003 / Automation-before-Intelligence).** A script composes the
  structured message; the agent supplies only the human content. Determinism first.
- **The committer is the single writer (R-004).** One commit authority; explicit paths;
  hooks are the automatic wall; the agent never pushes.
