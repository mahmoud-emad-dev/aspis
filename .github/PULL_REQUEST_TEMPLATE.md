<!-- Keep PRs scoped to one feature/fix. ASPIS commits follow a convention — see CONTRIBUTING.md. -->

## What & why

<!-- What does this change, and why? Link the issue/feature it closes. -->

Closes #

## How it was proven

<!-- ASPIS's rule: gate-green or it isn't done. -->

- [ ] `uv run ruff format --check . && uv run ruff check .` passes
- [ ] `uv run pytest -q` passes
- [ ] Tests added/updated for the change (red → green)
- [ ] Docs updated (README / docs / ROADMAP / CHANGELOG) where relevant
- [ ] Commit messages follow the convention; **no AI/tool attribution**

## Scope

<!-- Which areas does this touch? Confirm nothing leaked outside the intended scope. -->

- [ ] Changes stay within the declared scope (no unrelated files)
