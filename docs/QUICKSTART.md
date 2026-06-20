# Quickstart

From a clone to your first `plan → build → review` loop. ASPIS runs on **Windows and
Linux**; the only prerequisite is [`uv`](https://docs.astral.sh/uv/).

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

- **`.aspis/`** — the *brain*: durable, tool-neutral project memory (rules, context,
  decisions, the feature you're working on). This is the source of truth, in Git.
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

Open the project in **Claude Code** or **OpenCode**. The exported agents, skills, and
commands are already there. The factory drives a deterministic loop:

1. **Plan** — turn a request into a SPEC / PLAN / TASKS (the planning lead).
2. **Build** — implement one task at a time, gates-first (the build lead + builders).
3. **Review** — an independent reviewer checks scope, gates, and acceptance.

Every change is proven by the gate (`ruff format --check`, `ruff check`, `pytest`)
before it counts as done — that's the point: the *cheapest sufficient* model produces
production-grade work because clarity, tests, and review are engineered around it.

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

## Where to go next

- `aspis doctor` — verify your environment and project health.
- `.aspis/context/ARCHITECTURE.md` and `DECISIONS.md` — how ASPIS is built and why.
- `.aspis/rules/` — the system rules and the architecture constitution every project inherits.
