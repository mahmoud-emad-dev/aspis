# Planning Scripts Deployment — Specification

> F-016 systemic spec. Defines the deployment path for 3 planning scripts from catalog to `.aspis/scripts/planning/`.

## Purpose
Specify how 3 planning scripts (used by planning-lead and build-lead) are deployed from their catalog source to the runtime destination, who calls them, when they run, and how to validate correct deployment. Catalog is the single source of truth; deployment is a copy, never a move.

## Catalog → runtime map

| Script | Catalog source | Runtime destination | Phase | Caller |
|---|---|---|---|---|
| `feature_scaffold.py` | `src/aspis/data/catalog/scripts/planning/feature_scaffold.py` | `.aspis/scripts/planning/feature_scaffold.py` | P1 Scaffold | planning-lead |
| `task_compile.py` | `src/aspis/data/catalog/scripts/planning/task_compile.py` | `.aspis/scripts/planning/task_compile.py` | P6 Tasks | planning-lead |
| `prereq_validate.py` | `src/aspis/data/catalog/scripts/planning/prereq_validate.py` | `.aspis/scripts/planning/prereq_validate.py` | P8 Gate | build-lead |

All three are stdlib-only and self-contained — they ship into the target project and run on its own Python without an ASPIS install.

## Script: feature_scaffold.py

### Trigger
Called by planning-lead during Phase P1 (Scaffold) of the planning lifecycle. Runs once when a new feature is started, immediately after intake (P0) classifies the request as a Feature or Project-plan track.

### Purpose
Allocates the next `F-NNN` id, derives a slug, creates `.aspis/features/F-NNN-slug/` with a `tasks/` packet folder, copies SPEC/PLAN/TASKS from `.aspis/templates/planning/`, writes `active_feature.json`, and creates+checks out the `feature/F-NNN-slug` git branch.

### CLI shape
```
python .aspis/scripts/planning/feature_scaffold.py [root] --name "<goal>" [--slug <s>] [--mode <m>] [--no-branch]
```

### Validation
- File exists at `.aspis/scripts/planning/feature_scaffold.py`
- `python .aspis/scripts/planning/feature_scaffold.py --help` returns usage info
- AST check passes: `python -c "import ast; ast.parse(open('.aspis/scripts/planning/feature_scaffold.py').read())"`
- Idempotent: refuses to overwrite an active feature, raises `FeatureActiveError`

## Script: task_compile.py

### Trigger
Called by planning-lead during Phase P6 (Tasks) of the planning lifecycle. Runs after TASKS.md is authored and before handoff to build-lead, to render one self-contained packet per task.

### Purpose
Reads the active feature's `TASKS.md`, parses each `- [ ] T-NN` line, and renders a packet from `.aspis/templates/planning/TASK_PACKET.md` into the feature's `tasks/` folder. Fills the deterministic fields (feature id, task id, title, allowed-files list); leaves rich fields (context, acceptance, review routing) for planning-lead to enrich.

### CLI shape
```
python .aspis/scripts/planning/task_compile.py [root] [--feature F-NNN] [--force] [--dry-run]
```

### Validation
- File exists at `.aspis/scripts/planning/task_compile.py`
- `python .aspis/scripts/planning/task_compile.py --help` returns usage info
- AST check passes on the deployed copy
- `--dry-run` against a known feature parses all task lines and reports the packet set without writing any files

## Script: prereq_validate.py

### Trigger
Called by build-lead at the P8 (Gate) phase boundary. Build-lead runs it before pulling task packets to start work, and as the final pre-build gate before handoff is accepted. Planning-lead also runs it with `--phase plan` / `--phase tasks` to self-check its own progress.

### Purpose
Enforces the loop's phase ordering — no plan without a spec, no tasks without a plan, no build without tasks — relaxed by mode (a vibe feature skips PLAN.md; production requires all three). Reads the rigour dial from `.aspis/config/modes.yaml`.

### CLI shape
```
python .aspis/scripts/planning/prereq_validate.py [root] --phase <plan|tasks|build> [--feature F-NNN] [--mode <m>]
```

### Validation
- File exists at `.aspis/scripts/planning/prereq_validate.py`
- `python .aspis/scripts/planning/prereq_validate.py --help` returns usage info
- Exit code 0 = prerequisites met, 1 = something missing (so it slots directly into a CI gate)
- `python .aspis/scripts/planning/prereq_validate.py --phase plan` returns 0 when SPEC.md is present
- `python .aspis/scripts/planning/prereq_validate.py --phase build` returns 0 when SPEC + PLAN + TASKS are all present

## Deployment mechanism
1. Scripts are deployed from catalog source to `.aspis/scripts/planning/` during project bootstrap (`aspis bootstrap`) or on first `feature_scaffold` run.
2. **system-lead owns deployment** (per system-lead reference spec §2 Protected Scope — `.aspis/scripts/` is system-lead's exclusive path).
3. Deployment is a **copy operation, never a move** — `src/aspis/data/catalog/scripts/planning/` remains the single source of truth; the deployed copies are byte-for-byte regenerable.
4. Deployed scripts are **read-only at runtime** — planning-lead and build-lead execute them, never edit them; any fix is made in the catalog and re-deployed.
5. Asset authoring uses the `asset-authoring` skill (system-lead's runtime-neutral, single-sourced style).

## Invariants
- **Catalog-as-source** — a fix to a script's logic is always made in `src/aspis/data/catalog/scripts/planning/`, never in `.aspis/scripts/planning/`.
- **Read-only deployed copy** — the runtime path is generated, not edited; the `asset-authoring` discipline applies.
- **Self-contained scripts** — stdlib-only, no third-party imports; the deployed copy runs on the target project's Python without an ASPIS install.
- **Phase alignment** — the three scripts cover the three deterministic anchors of the planning lifecycle (start, decompose, gate).

## Acceptance criteria
- [ ] All 3 scripts have: source path, destination path, trigger (which phase + which caller), purpose, CLI shape, validation method
- [ ] Deployment ownership specified (system-lead, per system-lead §2)
- [ ] Catalog-as-source invariant documented (deploy = copy, not move)
- [ ] Validation methods are runnable — the exact command is specified and exits 0 on a correct deployment
- [ ] CLI shapes match the actual scripts in `src/aspis/data/catalog/scripts/planning/`
- [ ] Consistent with planning-lead reference spec phases P1, P6, P8
- [ ] Consistent with system-lead reference spec §2 (Protected Scope) and §3 (`asset-authoring` skill)
- [ ] This spec closes planning-lead reference spec §17 Open Question #1 (deploy planning scripts)
