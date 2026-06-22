# `.aspis/config/` — what to edit, what to leave

This folder is **tiered** so you can tell at a glance what is yours to change and
what is the machine's. Most days you touch only the three files at the top.

```
config/
  README.md            ← this guide
  project.yaml         ← YOU EDIT: project mode + overrides
  models.yaml          ← YOU EDIT: which model each tier uses
  agent-models.yaml    ← YOU EDIT: which model each agent uses (generated, then edited)
  purposes.json        ← mostly agents: one-line purpose per file (the file registry)
  policy/              ← rarely edited: how the system behaves
  reference/           ← do not edit: machine data the system reads
```

---

## Tier 1 — the files you actually edit (flat, here)

### `project.yaml` — your project's settings
The main knob. Sets the default **build mode** and any **overrides**:
```yaml
mode: production            # vibe | mvp | production — the default when a request omits one
models:                     # (optional) override a tier for THIS project, per runtime
  opencode:
    deep: opencode-go/deepseek-v4-pro
agents:                     # (optional) pin ONE agent to a tier or a concrete model id
  reviewer: deep
```

### `models.yaml` — tier → model defaults
Every agent declares a **tier** (`cheap` / `standard` / `deep`); this maps the tier to a
model, per runtime. Change a line to move *all* agents on that tier:
```yaml
opencode:
  cheap:    opencode/deepseek-v4-flash-free   # free OpenCode Zen default
  standard: opencode/deepseek-v4-flash-free
  deep:     opencode/nemotron-3-ultra-free
claude:
  standard: claude-sonnet-4-6
  deep:     claude-opus-4-8
```
A value may be a full `provider/model` (used as-is) or a bare catalog id (the runtime
resolves it to a connected provider).

### `agent-models.yaml` — model per agent (generated, then yours to edit)
The per-agent assignments. **Generated** by `aspis models --sync` from the models your
connected runtimes actually expose, with each agent pre-set to the best available model
for its job. Open it and change any agent (or whole capability) to any listed model.

> **After editing `agent-models.yaml`, `project.yaml`, or `models.yaml`, run
> `aspis models --apply`** — the chosen model is baked into each runtime agent file, so
> your edit is inert until you apply it.

---

## The commands you need

| Goal | Command |
|------|---------|
| See each tier's model + per-agent pins (validated) | `aspis models` |
| Also list every model your connected providers expose | `aspis models --available` |
| (Re)generate `agent-models.yaml` from connected runtimes | `aspis models --sync` |
| **Make your model edits active on the agents** | `aspis models --apply` |
| Refresh *and* apply in one step | `aspis models --sync --apply` |
| Health check (runtimes, config, drift) | `aspis doctor` |

Model ids come from **real detection** — `aspis models --available` shows exactly what
your plan/subscription provides (under the hood: `opencode auth list` + `opencode models`,
and `~/.claude`). You never have to guess an id.

---

## Tier 2 — `policy/` (rarely edited: how the system behaves)

Change these only to retune behaviour; defaults are sensible.

| File | What it controls |
|------|------------------|
| `modes.yaml` | The build modes (`vibe`/`mvp`/`production`) and each one's knobs. |
| `capabilities.yaml` | The capability taxonomy (review, planning, …) and each one's preferred tier. |
| `agent-capabilities.yaml` | Which capability each agent maps to (drives model assignment). |
| `commit-convention.yaml` | The commit-message convention the git hooks enforce. |
| `hooks.yaml` | Git-hook rules: secrets, junk files, protected paths, enforcement mode. |
| `constitution-checks.yaml` | The architecture-constitution checks. |

---

## Tier 3 — `reference/` (do not edit: machine data)

The system reads these; you don't write them.

| File | What it is |
|------|-----------|
| `model_catalog.yaml` | What each model *is* — scores, pricing, context window. The source the resolver ranks from. |
| `providers.yaml` | The provider registry (detection + naming) used to translate model ids. |

Generated state (the detected runtime inventory and last-sync snapshot) is written as
hidden `.runtime-inventory.json` / `.last-sync.json` and is git-ignored — never edit it.

---

## How resolution works (so an edit is predictable)

Most-specific wins:

1. a per-agent pin in `project.yaml` (`agents:`) or `agent-models.yaml`,
2. then a project tier override in `project.yaml` (`models:`),
3. then the global `models.yaml` tier map,
4. then the runtime adapter's default.

A concrete `provider/model` passes straight through; a bare tier (`deep`) is mapped per
runtime. After any change, `aspis models --apply` re-renders the agents so what you see
here is what runs.
