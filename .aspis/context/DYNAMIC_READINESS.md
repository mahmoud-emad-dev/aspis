# Dynamic Readiness Convention

How every loop agent right-sizes its own process — steps, files, delegations,
intermediate artifacts — from what exists today, while holding output quality
fixed. The convention is written so a future model-router engine can drive these
dials without rewriting any body.

## The key distinction

**Optimize the path, never the bar.** A stronger model reduces
*scaffolding/overhead* (fewer files, fewer micro-steps, fewer intermediate
artifacts) to reach the **same** quality. It does **not** reduce the
*rigor/validation* the mode + task demand. The gates (R-002) still run. The
output is the same quality — it just takes fewer turns and files to get there.

## The three dials

Every loop agent reads these three dials from existing infrastructure to decide
its process depth:

### 1. Mode — the rigor ceiling

| Source | How to read |
|---|---|
| `.aspis/config/modes.yaml` | The project's mode knob per task kind |
| The active feature's `mode` field | Override set by planning-lead |
| User config / preference | Final override (if supported) |

**How it affects process:**

| Mode | Process depth |
|---|---|
| `production` | Full depth — all steps, full review, full verification |
| `mvp` | Standard depth — core steps, standard review |
| `vibe` | Compressed — minimal steps, light review |

Mode sets the **maximum** rigor. A lower mode can compress; a higher mode can
never be compressed below its floor. The user pays for the mode they choose —
honour it.

### 2. Task kind / scope — the inherent need

| Source | How to read |
|---|---|
| The task's packet | `Type` and `Criticality` fields |
| The task's `V0–V4` version | From packet validation (V0=Vibe, V4=Production) |
| The number of allowed files | Proxy for blast radius |

**How it affects process:**

| Task scope | Process |
|---|---|
| Question / Trivial (1 line, 0–1 files) | No plan, no spec, no architecture. Answer/fix directly. |
| Small-task (1 file, low risk) | One packet, light review, one commit. |
| Bug (defect, 1–3 files) | Reproduce → root-cause → fix → regression test. |
| Feature (3+ files, new capability) | Full lifecycle: SPEC → PLAN → TASKS → build → review. |

The "skip the plan" logic, generalized: if the task doesn't warrant a full
lifecycle, don't run one. But when it does (production mode on a critical
feature), honour the **full** depth — even hundreds of nested steps.

### 3. Model capability — the scaffolding need

| Source | How to read |
|---|---|
| Agent frontmatter `model` tier | `cheap` / `standard` / `deep` |
| Runtime model inventory | Actual available models per tier |
| `config/models.yaml` | Tier-to-model mapping |

**How it affects process:**

| Model tier | Scaffolding |
|---|---|
| `cheap` | Full scaffolding — detailed packets, explicit steps, intermediate
  artifacts, frequent checkpoints. The model needs hand-holding. |
| `standard` | Moderate scaffolding — enriched packets, clear steps. |
| `deep` | Lean scaffolding — concise packets, fewer intermediate artifacts.
  The model needs less hand-holding to reach the same quality. |

A frontier model staying consistent without loading every file or emitting
every intermediate packet **collapses the hand-holding steps that exist to make
cheap models succeed** — don't drag a strong model through cheap-model ceremony.

**The tier doesn't change the bar.** A deep model still runs the same gates,
meets the same acceptance criteria, and produces the same quality output. It
just takes a shorter path.

## How agents encode this

Each loop agent's Dynamic-readiness block (the last section of its body)
encodes its *application* of the three dials. It does NOT restate this
convention — it references it:

```
## Dynamic-readiness
Right-sizes process per `.aspis/context/DYNAMIC_READINESS.md`:
- Mode (`production`/`mvp`/`vibe`) from the active feature → sets my rigor ceiling.
- Task kind/scope from the packet → determines whether I run the full loop or a
  compressed path.
- Model tier (`cheap`/`standard`/`deep`) from my frontmatter → sets how much
  scaffolding I need. Stronger model = fewer files, fewer intermediate packets,
  same quality bar.
Default: the leanest correct path for the scope — no extra phases, reviews, or
delegations the work doesn't warrant.
```

## The leanest-correct-path default

The agent's **default** behaviour must be the most efficient route that still
meets the quality bar:

1. **Right delegation chain**: delegate only where it adds value. Don't spin up
   a subagent for a one-line edit.
2. **Right context**: load only what the task needs, the most direct way
   (`context-ladder`). A delegate sees only its packet, not the whole feature.
3. **Right steps**: skip phases/workflows the work doesn't warrant. A typo fix
   doesn't need architecture review.
4. **Right model**: use the cheapest model that can do the work at the required
   quality. Escalate tier only when the work demands it.

The agent is always free to choose a *shorter* path than the mode ceiling; it
chooses a *longer* path only when the task kind or model capability requires it.

## Future router integration

When the model-router engine is built (future feature), it drives all three
dials from a single decision point. Bodies written to this convention will work
with the router without changes — the router reads the same sources (`modes.yaml`,
frontmatter tier, packet fields) and the bodies already encode their response to
each dial value.
