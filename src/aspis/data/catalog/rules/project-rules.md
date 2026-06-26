# Project Rules

The conventions and constraints for **this one project's work product** — its
stack, structure, naming, testing, and domain choices. This is the **highest
priority** rule layer for product work: where it conflicts with the global
[Constitution](architecture-constitution.md), **project rules win**. (System
rules in [system-rules.md](system-rules.md) sit on a separate axis and are never
overridden.)

## How these rules are set and changed

- **Set by** (in priority order): the active **profile** default → the **user**
  directly → **proposed by the system** (project-lead → System Lead) when the user
  has none yet.
- **Seeded** on a brand-new project that has no code or rules file: from the
  user's **global user rules** (future feature) — the System Lead validates each
  and writes the relevant subset here as a valid structured rule.
- **Changed while the project runs:** by the user directly, or via project-lead →
  System Lead. Every change is human-gated (R-008) and traced (R-009).

## How an agent reads only its rules

Each rule carries a `roles:` tag. An agent loads, through its context step, only
the rules tagged for its role (plus `all`) — never the whole file (R-006). Tags
match the roster: `all`, `planning`, `build`, `review`, `test`, `fix`,
`research`, `system`, `commit`.

## Rule format

```
### PR-NNN <short name>   `applies-to: <domains|all>` · `roles: <tags>` · `severity: block|warn|advisory` · `status: active|draft`
<the rule, one or two plain lines>
```

- **applies-to** — which project kinds it holds for (`software`, `data`,
  `web`, `automation`, `research`, … or `all`). Lets one file serve many domains.
- **severity** — what a violation means: `block` (must fix), `warn` (flag, may
  proceed), `advisory` (guidance). The practical default is `warn`.
- **status** — `active` (enforced) or `draft` (carried, not yet enforced).

> These fields are deliberately lightweight markdown today. A later feature turns
> this file into a **validated, structured rules store** the dashboard can show,
> configure, and control — and that the system can grow by capturing new rules as
> the project is used. Keep this format so that migration is mechanical.

## Rules

> Empty for now — this project has not defined product rules yet. Add them below
> using the format above, grouped by role. Example shape (remove when real ones
> are added):

<!--
### PR-001 Stack is Python + uv   `applies-to: software` · `roles: all` · `severity: warn` · `status: active`
Use Python with uv for env/deps; match the surrounding code's style and idioms.

### PR-002 Tests live beside the suite   `applies-to: software` · `roles: build,test` · `severity: warn` · `status: active`
New behaviour ships with a test under `tests/`; a fix ships with a regression test.
-->
