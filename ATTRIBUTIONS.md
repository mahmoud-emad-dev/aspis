# Attributions

ASPIS is original work. It stands on a small set of well-established open-source
libraries, and a couple of its ideas were informed by prior art. Both are recorded
here, with thanks.

## Software ASPIS builds on

The CLI is pure Python and intentionally lean. Its runtime dependencies:

- **[Pydantic](https://docs.pydantic.dev/)** and **pydantic-settings** — typed config and
  data models (MIT).
- **[PyYAML](https://pyyaml.org/)** — parsing the catalog, profiles, and config (MIT).

The toolchain used to build and verify ASPIS:

- **[uv](https://docs.astral.sh/uv/)** — environments and packaging (Apache-2.0 / MIT).
- **[Ruff](https://docs.astral.sh/ruff/)** — formatting and linting (MIT).
- **[pytest](https://pytest.org/)** — the test suite (MIT).

ASPIS also exports configuration for two agent runtimes it neither vendors nor modifies —
**Claude Code** and **OpenCode** — each governed by its own license.

## Prior art

The design is ASPIS's own. One influence is worth naming: the **spec → plan → tasks**
ordering echoes the shape popularised by
[GitHub Spec Kit](https://github.com/github/spec-kit) (MIT). ASPIS took only that broad
principle — specify before you build — and implemented everything around it independently:
its own templates, prerequisite gating, agent roster, and the `plan-critic` consistency
check. No Spec Kit code is vendored; the mention is a nod to a shared idea, not a fork.

## Conventions

- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/).
- The changelog follows [Keep a Changelog](https://keepachangelog.com/).
- The Code of Conduct adapts the [Contributor Covenant](https://www.contributor-covenant.org/).
