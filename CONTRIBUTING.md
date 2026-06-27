# Contributing to ASPIS

Thanks for your interest in ASPIS — *the shield for agentic software production*.

ASPIS is a **file-first, deterministic** agentic software factory: all durable project
state lives as plain files under `.aspis/`, so any AI runtime reads and writes the same
source of truth. Contributions that keep that discipline are very welcome.

## Ground rules

- **File-first & deterministic.** Prefer the cheapest mechanism that solves a need —
  deterministic code before an agent. Durable state belongs in `.aspis/`, not hard-coded.
- **Cross-platform is non-negotiable.** Everything must run on **Windows and Linux/WSL**.
  Use `pathlib`, pass `encoding="utf-8"` to any `subprocess` call that reads output, and
  never rely on the platform default codec. **Do not create or commit a `.venv`** — a WSL
  virtualenv breaks `uv` on Windows.

## Development setup

ASPIS uses [uv](https://docs.astral.sh/uv/):

```bash
uv sync                 # create the environment from the lockfile
uv run aspis --help     # run the CLI
```

## The quality gate

Keep the gate green before every commit:

```bash
uv run ruff format --check . && uv run ruff check . && uv run pytest -q
```

Add tests for every behavior change. The toolchain is deliberately lean (ruff + pytest);
heavier tooling is added only when a part truly needs it.

## Commits

- Use [Conventional Commits](https://www.conventionalcommits.org/), scoped to the feature
  and task: `type(F-xxx/T-yy): subject` (`feat`, `fix`, `docs`, `chore`, `refactor`,
  `test`, `style`). Commit **per unit** of work — one logical change per commit.
- Write commit messages and pull-request descriptions as natural, human-authored prose.
  A commit-message hook enforces this style.
- Branch from `main` as `feat/F-xxx-slug`.

## Pull requests

1. Keep the gate green and include tests for any behavior change.
2. Keep each change scoped to a single concern.
3. Explain the *why*, not just the *what* — the PR template prompts for this.

Open a [bug report or feature request](https://github.com/mahmoud-emad-dev/aspis/issues/new/choose)
before a large change so we can align on the approach.

## Reporting & conduct

- **Security vulnerabilities:** see [SECURITY.md](SECURITY.md) — please do **not** open a
  public issue.
- By participating, you agree to our [Code of Conduct](CODE_OF_CONDUCT.md): be respectful
  and constructive in all project interactions.

---

**Next:** [Architecture](docs/ARCHITECTURE.md) · [Roadmap](ROADMAP.md) · [Quickstart](docs/QUICKSTART.md)
