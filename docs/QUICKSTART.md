# Quickstart

From a clone to your first `plan → build → review → commit` loop, with a real
worked example at the end. ASPIS runs on **Windows and Linux**; the only
prerequisite is [`uv`](https://docs.astral.sh/uv/).

## 1. Get ASPIS

```bash
git clone <your-clone-url> aspis && cd aspis
uv sync
uv run aspis --version
```

Or install the CLI standalone:

```bash
uv tool install .
aspis --version
```

## 2. Initialize a project

In the directory you want to build software in:

```bash
aspis init .            # dry-run: shows exactly what it would create
aspis init . --write    # actually scaffold the project
```

`init` writes three things:

- **`.aspis/`** — the *brain*: durable, tool-neutral project memory (rules,
  context, decisions, the feature you're working on). The source of truth, in Git.
- **`.claude/` and `.opencode/`** — generated *runtime* configs (agents, skills,
  commands) for Claude Code and OpenCode. Disposable — regenerated from the brain.
- Root files (`AGENTS.md`, `.gitignore`, and `CLAUDE.md` when Claude is a target).

> Generated brain indexes (`CURRENT_STATE.md`, `RECENT_CHANGES.md`, `CODE_MAP.md`,
> `FILE_REGISTRY.yaml`) are **not** tracked — they're derived and regenerate on demand.

## 3. Make it live

```bash
aspis bootstrap         # a short wizard: project goal, stack, default build mode
aspis status            # confirm the project is detected and live
```

## 4. Run the loop in your runtime

Open the project in **Claude Code** or **OpenCode**. The exported agents, skills,
and commands are already there. The factory drives a deterministic loop:

1. **Plan** — turn a request into a SPEC / PLAN / TASKS (the planning lead).
2. **Build** — implement one task at a time, gates-first (the build lead + builders).
3. **Review** — an independent reviewer checks scope, gates, and acceptance.

Every change is proven by the gate (`ruff format --check`, `ruff check`, `pytest`)
before it counts as done — that's the point: the *cheapest sufficient* model
produces production-grade work because clarity, tests, and review are engineered
around it.

## 5. Commit

The **committer** is the single commit authority. It commits through `aspis commit`,
which stages exactly the paths you name (never `git add -A`), composes a conventional
message, and lets the hooks enforce it:

```bash
aspis commit src/feature.py tests/test_feature.py \
  --type feat --task T-02 --title "add the feature" \
  --bullet "what changed" --bullet "why"
```

The git hooks (installed by `init`) run automatically: `pre-commit` auto-fixes and
checks, `commit-msg` validates the convention, `post-commit` refreshes the brain.

---

## A real worked example — ASPIS builds itself

The clearest example of ASPIS is **ASPIS itself**: this repository is a live ASPIS
project that builds its own catalog and CLI through the same loop it ships to you.
Take **F-007, the git subsystem** — a real feature built and merged through the
loop. Its history reads as one clean, in-order line (`git log`):

```
feat(F-007/T-01): compose tool + the aspis commit verb
feat(F-007/T-02): committer uses aspis commit; ship commit skills
test(F-007/T-03): cover compose + aspis commit
docs(F-007/T-04): record the why — D-011, architecture, roadmap
Merge feature F-007: git subsystem
```

Each task was **proven by the deterministic gate** before it counted
(`uv run ruff format --check . && uv run ruff check . && uv run pytest -q`),
reviewed independently of whoever built it, then committed with the very tool the
feature introduced — `aspis commit`.

### What ASPIS adds over a bare runtime

| Without ASPIS | With ASPIS |
| --- | --- |
| "Looks done" — trust the model | **Gate-green or it isn't done** (ruff + pytest) |
| Scope drifts across files | **Scope is declared**; hooks flag out-of-scope edits |
| Ad-hoc commit messages, `git add -A` | **One commit authority**, a data-driven convention, explicit paths |
| Rules live in a prompt and rot | Rules are **files** — system rules + an architecture constitution agents enforce |
| State lives in a chat session | State lives in **`.aspis/` files**, in Git, readable by any runtime |
| Each model/runtime reinvents the setup | One **brain**, exported to Claude Code *and* OpenCode |

The bet, made concrete: *clarity × tests × review* let the cheapest sufficient
model produce production-grade work — repeatably.

## Where to go next

- `aspis doctor` — verify your environment and project health.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — how ASPIS is built.
- [`../ROADMAP.md`](../ROADMAP.md) — where it is and where it's going.
- `.aspis/rules/` — the system rules + architecture constitution every project inherits.
