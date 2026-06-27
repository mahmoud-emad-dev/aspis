---
name: runtime-author
description: Author one runtime-neutral catalog asset that is adapter-translated per runtime (OpenCode/Claude) — single source, no duplicate per-runtime files.
---

# runtime-author

## Purpose

Every runtime asset (agent body, skill, workflow, command, template, hook) is
authored once in the catalog as runtime-neutral markdown. The OpenCode adapter
and the Claude Code adapter each translate it for their runtime at export
time. This skill ensures the source is written so both adapters produce valid
output — preserving single source (R-006) and the byte-parity moat.

## When to use

When creating or modifying any catalog asset that will be rendered to a live
runtime: agents, skills, templates, commands, workflows, hooks.

## Procedure

1. **Determine the asset kind** (agent, skill, template, command, workflow,
   hook) and load its authoring standard from the catalog.
2. **Author runtime-neutral.** Write one source: frontmatter with every
   required field, body sections per the kind's standard. No runtime-specific
   syntax — the adapters translate the superset and drop what a runtime
   can't use.
3. **Structural validity.** Run `aspis validate-runtime` (agents) and resolve
   every broken reference before continuing.
4. **Adapter render check.** Run `aspis export --dry-run`; confirm no render
   errors for OpenCode or Claude Code. Fix the catalog — never patch the
   live file.
5. **Byte-parity proof.** Run `aspis export --check`; the catalog must
   regenerate the live runtime byte-for-byte. DRIFT means a hand-edit or a
   non-deterministic render — refuse the change until CLEAN.
6. **Cross-runtime spot check.** For the Claude Code adapter, verify the
   `permission:` block survives translation (known past asymmetry — a single
   stripped field is the worst kind of small change).

## Outputs

- One runtime-neutral catalog asset, frontmatter + body, wired into its owner.
- A `validate-runtime` pass and an `--dry-run` render with no errors.
- A byte-parity verdict of CLEAN — both runtimes regenerate from one source.

## Anti-patterns

- Authoring a separate file per runtime — defeats single source and R-006.
- Runtime-specific syntax in the catalog (e.g. `tools:` vs `permission:`) —
  breaks the other adapter's render.
- Skipping `--dry-run` or `--check`; trusting one adapter without testing both.
- Editing the live runtime file (`.opencode/`, `.claude/`) directly instead
  of the catalog source — guarantees the next parity check fails.
- Treating MISSING as DRIFT: a first export of a new asset is not drift and
  must not block the pipeline.
