# Architecture Constitution

The **global default standard** every ASPIS project is held to — including ASPIS
itself — until a project sets its own [project rules](project-rules.md), which
take precedence. Where [system rules](system-rules.md) (R-001…) govern how the
*agents* operate, this constitution governs how a project's *work product* is
designed, so it stays easy to understand, change, test, and extend as it grows.

It applies to **any kind of project, not only software** — data analysis, data
science, automation, web, research, content — wherever a user runs ASPIS. The
rules below are written in software terms because that is the most common case;
read each as the **general principle first**, with the software phrasing as one
domain's expression of it. A project's own rules and profile specialise them.

It is a **shipped, reusable asset**, not prompt text: the planning lead designs
against it, the build lead builds to it, and the reviewer checks against it. The
machine-readable checklist (`config/constitution-checks.yaml`) says which rule
each role owns. An agent loads only the rules its role enforces.

> The means (SOLID, clean code, a tidy pipeline, a clear dataset) are never the
> goal. The goal is **low cost of change**. These rules are how we keep it low —
> in any domain.

---

## The north star

**Things that change together live together; things that change independently
stay apart.** Every rule below serves that one idea.

**The Cost-of-Change test** — the one measurable rule. *To add one feature, how
many existing files must change?*

| Files changed | Verdict |
| --- | --- |
| 1–3 | healthy |
| 5–10 | warning |
| 10+ | architecture problem |
| 20+ | critical |

**Automation before Intelligence** — this is [R-003](system-rules.md#r-003-deterministic-first)
restated for design: `Script → Tool → Workflow → Agent`, always in that order.
If a deterministic mechanism can do it, it must **not** be an agent. Formatting,
secret-scanning, gitignore upkeep, cleanup, indexing → scripts/hooks. Planning,
review, commit grouping → agents.

---

## Extension rules (how the system grows)

1. **Local Change** — add a feature by *creating files*, not editing many.
   Review question: *can this be added with mostly new files?*
2. **Plugin First** — anything that will grow (profiles, agents, skills,
   runtimes, asset kinds, templates) is a plugin; the core never names a concrete one.
3. **Single Source of Truth** — every fact has exactly one owner; everything else
   is generated from it.
4. **Configuration over Code** — describe behaviour with data, not `if` chains.
5. **Core is Stable** — most work happens in plugins/assets; if every feature
   touches the core, the design is wrong.
6. **Dependency Direction** — dependencies flow inward: plugins → core, never the reverse.
7. **Discovery over Registration** — load by convention; no hand-maintained
   `REGISTRY = [...]`.
8. **Generated Artifacts** — humans edit source; machines generate catalogs,
   indexes, docs. Never hand-maintain generated output.
9. **No Special Cases** — never `if runtime == "claude"` / `if profile == "x"`.
   Use abstractions and **capability checks** (`runtime.supports(kind)`).
10. **Consistency over Cleverness** — boring, predictable, repeatable wins.
11. **Architecture before Features** — if more features of this shape are coming,
    build the extension mechanism first, then the feature.
12. **Portable by Default** — every script and tool runs on **Windows and Linux**.
    Prefer the cross-platform mechanism over an OS-specific one: force **UTF-8**
    on stdio and on every `subprocess` read (`encoding="utf-8"`), use `pathlib`
    over string paths, and never assume a console codec, path separator, or shell.
    An OS difference (encoding, paths, line endings, process spawning) is a bug to
    fix at the source, not to work around per machine.

If only three are enforced: **Plugin First · Single Source of Truth · Local Change.**

---

## File rules (how every file is written — agents read these first)

Optimise for agent readability → navigation → modification → review, then humans.

**The one rule:** *every artifact is understandable without reading its
implementation* — from its purpose, interface, dependencies, and skeleton.

- **Every file explains itself** — a top docstring with Purpose / Responsibilities
  / Does Not / Used By.
- **One concept per file** — small knowledge units; split a growing module.
- **No hidden dependencies** — pass roots/settings explicitly; no module-level
  global reached from everywhere.
- **Known dependency direction** — "who imports / depends on this?" is answerable
  from the context index, not a repo-wide grep.
- **Deterministic discovery** — registry → code map → exact file/symbol; never
  search-and-guess.

---

## How this is enforced in the loop

- **Planning lead** — designs against the extension rules; rejects a plan whose
  Cost-of-Change is high or that adds a special case instead of a mechanism.
- **Build lead / builder** — builds to the file rules and Automation-before-
  Intelligence; new capability is new files, not edits to the core.
- **Reviewer** — runs the Cost-of-Change test and checks the rules each change
  touches; a violation is a finding, not a style nit.
