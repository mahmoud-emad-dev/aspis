# Planning Lead — Dynamic Handling of Modes, Tiers, and Cost

> **Author:** Research Lead
> **Date:** 2026-06-26
> **Status:** v1, validated against `cheap-models-quality.md`,
> `core-loops-2026.md` §1.5, `models.yaml`, `planning-lead.md` (live
> frontmatter), and `local/AGENT-SYSTEM-ARCHITECTURE.md`. Cite by section
> (`PDH-2.1`, `PDH-3.4`, etc.) when a plan or review references it.
>
> **Stale-check:** 90 days. Re-run if the tier map (`models.yaml`) or
> `modes.yaml` knob vocabulary changes.
>
> **Rule of the doc:** mode is the *user-facing dial* (vibe/MVP/production).
> Model tier is the *internal lever* (cheap/standard/deep). They are not the
> same axis and they must be decoupled in the planning-lead's head. This
> document is the reconciliation.

---

## 0. Bottom line up front

The planning-lead orchestrates **three independent dials** that compose:

| Dial | Knob vocabulary | Where it lives | Who sets it |
|---|---|---|---|
| **Mode** (the *user-facing* rigor dial) | `vibe` / `mvp` / `production` | `modes.yaml` | user, project, or auto-detect |
| **Model tier** (the *internal* cost dial) | `cheap` / `standard` / `deep` | `models.yaml` | planning-lead per-phase |
| **Cost profile** (the *user's wallet*) | `save-money` / `balanced` / `max-quality` | `.aspis/config/project.yaml` + user rules | user, falling back to `balanced` |

**Mode tunes the *shape* of the planning artifacts** (which steps run, how
deep each one goes). **Tier tunes the *model* that runs each step.**
**Cost profile tunes the *default tier per step*.** All three are data; no
code change is needed to alter any of them.

**Five rules the rest of this document proves and applies:**

1. **Decide mode first, tier second, cost profile third.** Resolution
   order: explicit user > active feature > project default > system default
   (`modes.yaml` `default: production`). Re-decide at any phase boundary.
2. **Different phases can run at different modes and tiers.** A
   *production-mode* feature can have a *vibe* intake if the request is
   unambiguous; a *vibe-mode* feature still demands a *standard* plan-critic
   pass if the work is high-risk. The phase, not the feature, sets the rigor.
3. **Cheap-by-default with deterministic gates; escalate only on measurable
   signal.** Three cheap attempts → one standard → one deep, capped. Never
   escalate on the model's self-report of difficulty.
4. **Surface cost *before* planning writes anything durable.** The user sees
   a per-phase tier forecast and a worst-case cost, then approves.
5. **A research gap is not a tier gap.** When research-lead cannot verify,
   mark the claim `[UNVERIFIED]` and continue. Don't burn tier budget
   trying to make a fact become true.

---

## 1. Mode selection — how planning-lead picks the right mode

### 1.1 Decision tree (resolution order)

The mode is resolved in **strictly this order**, with the first hit winning.
This is the same precedence `planning-intake` already uses for the mode
*name*; this document extends it to the *whole* mode+phase+tier tuple.

```
1. EXPLICIT USER OVERRIDE
   - "/plan --mode vibe", "build this MVP-style", "production-grade please"
   - CLI flag, request text, or current-message instruction
   - WINS UNLESS the user contradicts themselves in the same message
     (then ask; do not guess — R-001 scope, "if stuck, stop")

2. ACTIVE FEATURE MODE
   - .aspis/current/active_feature.json → .mode (set by previous planning cycle)
   - WINS if the user is asking to *continue* the existing feature
     ("add another story", "now do the API too")
   - ASK if the user is asking to *change* the active feature's mode

3. PROJECT DEFAULT
   - .aspis/config/project.yaml → planning.default_mode
   - WINS for a brand-new project or a request with no mode signals

4. MODES.YAML DEFAULT
   - .aspis/config/modes.yaml → default: production
   - LAST RESORT
```

After the mode is chosen, read its knobs from `modes.yaml`. The knobs are
**the same word the skill expects** (`spec`, `architecture`, `task_size`,
`plan_review`, `build_review`, `test_depth`, `docs`, `promotable`). No
re-derivation; no hard-coding.

### 1.2 Auto-detection — signals that *suggest* a mode (used when nothing is explicit)

When no user/feature/project signal exists, the planning-lead infers the mode
from the request itself. **Inference is always confirmable** — the lead
states the inferred mode in the plan-of-plan (one or two lines) before
proceeding. The user can override at that point cheaply.

| Signal in the request | Inferred mode | Why |
|---|---|---|
| "throwaway", "spike", "explore", "what if", "draft" | `vibe` | the user signals they don't want ceremony |
| Single file or one-line change | `vibe` | the diff fits in one sentence (Anthropic, `core-loops-2026.md` §1.5) |
| "MVP", "first cut", "demo", "iterable" | `mvp` | ship-and-iterate intent |
| Multi-file, dependency-ordered, no risk markers | `mvp` | shape demands a spec, not full architecture |
| "production", "ship to customer", "compliance", "audit" | `production` | explicit quality bar |
| Touches `auth/`, `security/`, `payments/`, `rules/`, `permissions/`, `*.yaml` policy | `production` (minimum) | the blast radius is the existing system; risk is real (R-001) |
| Touches >5 files OR cross-cuts >1 module | `mvp` minimum | spec/architecture signal |
| New public API surface, new external dependency | `production` | surface is now part of the contract |
| Breaking change to a stable interface | `production` | the cost of being wrong is high |
| Single-coherent test fix in one file | `vibe` | even with `test_depth: gate` from `modes.yaml` |

**Decision rule when signals disagree** (e.g., "throwaway auth experiment"):
the *riskier* signal wins. A throwaway request that touches `auth/` is
**not** vibe — it is production minimum, because the cost of an oversight
is paid by the project, not the user. (R-001 scope + R-008 human gate on
security/risk changes.)

### 1.3 Auto-escalation — when to UPGRADE the mode (vibe → mvp → production)

The mode is upgraded in three cases, all of them *re-derivable from
artifacts*, not vibes:

**E1. The request grows in scope mid-planning.**

```
Trigger: clarification reveals a hidden slice; the SPEC's user stories
         expand beyond what the intake predicted.
Action:  re-derive the mode from the new SPEC's size; if higher, re-run
         intake. Record the escalation in the plan-of-plan ("escalated
         from mvp → production at P3 because risk assessment revealed
         <X>"). Do NOT silently re-do work; carry the artifacts forward
         and deepen them.
```

**E2. Risk markers appear after intake.**

```
Trigger: during architecture-planning or task-decomposition, a step is
         identified that touches:
           - permissions / secrets / R-008-gated paths
           - data model (schema migration, deletion, irreversibility)
           - public API or contract surface
           - rules/**, .aspis/rules/**, profiles/defaults.yaml
           - any file a prior feature flagged "load-bearing"
Action:  escalate the mode of *that step's task packet* to production
         (small task, full review, full tests). Leave the rest of the
         feature at the original mode. This is the per-phase mode
         discipline (see §1.5).
```

**E3. A previous feature on the same area is in the lesson log with a
"regret" entry.**

```
Trigger: .aspis/runs/lessons/ or .aspis/context/RECENT_CHANGES.md
         contains a "would have planned differently" note for the same
         module / pattern.
Action:  escalate the mode by one step. Cheap insurance against a known
         failure mode. Document the trigger in the plan's Risks section.
```

**The escalation is always recorded.** The plan-of-plan tracks "started
as X, escalated to Y at step Z, because W." This is the auditable trail
that satisfies R-009 (trace and learn).

### 1.4 Auto-downgrade — when to *suggest* DOWNGRADING the mode

Downgrade is **suggest, never auto-apply**. Three reasons:

1. The user picked a mode for a reason; demoting it is a quality decision
   they should ratify.
2. A downgrade in mid-feature wastes the work already done at higher
   rigor (the spec, the architecture, the deeper task packets). The savings
   is real but small; the loss of audit is large.
3. A future reader of the feature folder needs to know what was promised.
   A retroactive downgrade is a footgun.

**Downgrade triggers the planning-lead surfaces to the user:**

**D1. The intake inferred a higher mode than the work warrants.**

```
Example: user said "build a production-grade CLI flag parser" and the
         feature is a one-file, 20-line change.
Surface: "The intake set production mode. The work is 20 lines in
         one file; vibe would meet the bar. Continue with production,
         or downgrade to vibe and save ~3x cost? (reversible until P3)"
```

**D2. The user said "production" but the work is throwaway.**

```
Surface: "You asked for production mode. This is a one-shot script in
         a scratch directory; recommend vibe. Switch now, or keep
         production for the audit trail?"
```

**D3. The mode was set by the project default but the request is clearly
out of pattern.**

```
Surface: "Project default is production. This request is a typo fix
         in a non-load-bearing file. Recommend vibe. Override?"
```

**How to surface.** The plan-of-plan (the one-or-two-line preamble) names
the mode *and* the recommendation, e.g.:

> Plan-of-plan: track=small, mode=production (intake) →
> recommend vibe (20 lines, one file, non-load-bearing). User's call.

The user replies or proceeds. If they proceed without answering, the
intake-set mode stands — silence is consent to the original choice.

### 1.5 Per-phase mode — different phases, different modes

**Mode is per-phase, not per-feature.** A feature can run a `vibe`
intake and a `production` architecture step on the same track. This is the
"mode is a ceiling, not a floor" rule from `core-loops-2026.md` §1.5 and
`planning-intake` §"Mode is a ceiling, not a floor."

**Why.** Different phases have different blast radii. Intake's blast
radius is the planning artifacts (cheap to redo). Architecture's blast
radius is the implementation (expensive to redo). The mode should track
the blast radius, not the feature's overall posture.

**The matrix — how to apply per-phase mode (production feature):**

| Phase | Default mode for that phase | Why this mode | When to *raise* |
|---|---|---|---|
| **P0 Intake** | mode of the feature | sets everything downstream | — (intake *is* the setter) |
| **P1 Clarify** | mode of the feature | clarification is the same regardless | when the user can't answer; switch to higher to be conservative with assumptions |
| **P2 SPEC.md** | mode of the feature | the spec IS the mode's output depth | when a slice is identified as load-bearing for the system |
| **P3 PLAN.md** | mode of the feature | the plan IS the mode's output depth | when the plan touches R-008-gated paths; raise THAT STEP only |
| **P4 TASKS.md** | one tier *below* the feature mode | tasks are mechanical; a higher task depth wastes tokens | — |
| **P5 plan-critic** | mode of the feature | the critic's rigor must match the spec it reviews | — (modes.yaml knob `plan_review: independent` already enforces) |
| **P5 plan-critic** (per step, not per feature) | **production** when the reviewed step is gated | a load-bearing step deserves a deep critic regardless of feature mode | always when a step touches R-008 paths |

**The mechanics.** The `modes.yaml` knobs (`spec`, `architecture`,
`task_size`, `plan_review`, `build_review`, `test_depth`, `docs`,
`promotable`) ARE the per-phase depth setting. The planning-lead reads
them, then shades them per task as the per-phase escalation rules
require. The output is the **per-task mode** in the TASKS.md, not the
**per-feature mode** as a single value.

**Example.**

```
Feature mode: mvp
P2 SPEC.md → mvp (stories)
P3 PLAN.md → mvp (note)
P4 TASKS.md → mvp (medium)
  T-001 scaffold cli.py → vibe (large, gate only)
  T-002 add --dry-run flag → vibe (large, gate only)
  T-003 add audit log → production (small, full review, full tests)
    ^ per-phase escalation: touches audit log, irreversibility, audit
P5 plan-critic → mvp (self), then independent on T-003 only
```

This is the per-phase discipline. The feature folder's `feature.yaml`
records the *original* feature mode; the per-task mode lives in TASKS.md.

### 1.6 User override — how preference interacts with auto-detection

The user can override at **four distinct points**, each with different
blast radius and reversibility:

| Point | Override form | Reversibility | Cost to override |
|---|---|---|---|
| **Pre-intake** | "use vibe mode" in the request | full — planning hasn't started | zero |
| **In plan-of-plan** | reply to the lead's recommendation | full — planning is one or two lines in | zero |
| **Mid-P2 (SPEC)** | "actually, make this production" | partial — SPEC needs re-write; downstream hasn't started | small (the SPEC redraft) |
| **Mid-P4 (TASKS)** | "switch everything to MVP" | partial — task packets may need re-slicing | medium (packet re-compile) |
| **Post-P5 (plan-critic)** | "let's do this in vibe after all" | expensive — the work is fully planned and reviewed | large (re-plan + re-review) |

**The override is the user's, not the lead's.** The planning-lead never
silently downgrades or upgrades; it always surfaces the new mode in the
plan-of-plan and asks for confirmation when the cost of getting it wrong
is high. The exception is the per-phase escalation in §1.3 E1–E3, which
is itself a deterministic trigger and does not need user confirmation.

**The override is logged.** Every mode change is a single line in
`feature.yaml`'s `mode_history` (or in the planning artifact's preamble
until `feature.yaml` is generated). Auditability over silence.

---

## 2. Model tier selection — per planning phase

The model tier is the *internal* lever; the user does not see it directly.
The tier is bound to a phase by the table below; the **cost profile** (§3)
*shades* the defaults of this table.

### 2.1 Per-phase tier matrix (default = `balanced` cost profile)

The **planning phase** is the planning-lead's own work; the *builder's*
phase is a separate decision (the `task-decomposition` skill shades task
size, and the Build Lead decides tier per packet). The matrix below is
*for planning-lead's own work only*.

| Phase | Default tier (balanced) | When to raise to standard | When to raise to deep | When cheap is wrong |
|---|---|---|---|---|
| **P0 Intake / classify** | **cheap** | request is ambiguous and the classifier must *reason* | never (intake never justifies deep) | always (intake is routing) |
| **P1 Clarify** (max-5 questions) | **cheap** | the user already pushed back twice; the model needs to weigh "ask" vs "assume" | never (clarification is pattern-matching on a known skill) | always — if cheap returns nonsense, the question is wrong, not the tier |
| **P2 SPEC.md** | **standard** for MVP mode, **deep** for production mode | never raise above mode | **always deep for production** (per `planning-quality-and-rules-reference.md` §4.1) | vibe mode stays cheap — a vibe SPEC is bullets, not full prose |
| **P3 PLAN.md** (architecture) | **standard** for MVP mode, **deep** for production mode | novel integration with an existing module | **always deep for production** and for any step touching R-008-gated paths (Constitutional impact) | vibe mode = `architecture: skip`; no tier is needed (no plan) |
| **P4 TASKS.md** (task decomposition) | **standard** | novel task shape (first time this project uses subplanners / workers) | never — decomposition is mechanical given a good plan | MVP-decomposition stays cheap *only* if the plan is itself deep (cheap decomposes a deep plan poorly) |
| **P4 TASK_PACKET enrichment** | **cheap** | the packet references files the cheap model hasn't seen | never | cheap is the default; an enriched packet is a 1-2k-token fill, not a design decision |
| **P5 plan-critic** | **standard** for self-check (MVP), **deep** for independent pass (production) | the plan is in a high-stakes module (auth, data, security) | **always deep for production** (`plan_review: independent` from `modes.yaml`) | vibe = `plan_review: skip`; no tier |
| **P5 acceptance criteria** (SC-###) | **cheap** | novel test patterns the cheap model has never seen | never | always — SC-### is a mechanical derivation from FR-### |
| **Hand-off doc to Build Lead** | **cheap** | — | — | always — the artifacts already exist |

**Source for the deep-on-architecture default:** `cheap-models-quality.md`
§2.2 ("Architecture decisions / root-cause debugging: ❌ Use frontier"),
and `planning-quality-and-rules-reference.md` §4.2 ("SPEC authoring →
deep; Architecture design → deep; sets the bar for everything
downstream"). Deep is non-negotiable for production SPEC + architecture
because the cost of a bad SPEC compounds — every task packet, every
builder call, every review verdict is downstream of it. The
"frontier for judgment, cheap for context" rule from
`AGENT-SYSTEM-ARCHITECTURE.md` ("How Cheap Models Are Used").

### 2.2 When to cascade — the failure pattern

The cascade is the escape valve when a tier fails to produce an acceptable
artifact. The default cascade is from
`planning-quality-and-rules-reference.md` §4.3 and
`AGENT-SYSTEM-ARCHITECTURE.md` ("Cascade on failure"):

```
cheap (1st)  → cheap (2nd, with feedback) → cheap (3rd, with explicit rubric) → standard → deep
```

**This is a budget, not a rule.** `mode: production` may tighten the cap
on critical phases (e.g., SPEC: 1 cheap → 1 standard → 1 deep; no
redundant cheap retries). `mode: vibe` may loosen (cheap → standard;
never deep).

**The trigger is a *deterministic* failure signal**, not the model's
self-report. Valid triggers:

| Signal | Verifier | What it means |
|---|---|---|
| **Spec violates a `modes.yaml` knob** | the lead re-reads `modes.yaml` and confirms the SPEC's `spec:` depth matches | the cheap model produced a "full" SPEC in vibe mode, or a "bullets" SPEC in production mode |
| **SPEC's FR-### / SC-### ratio is wrong** | the lead counts FR with no SC and SC with no FR (the plan-critic's check) | the cheap model skipped acceptance criteria or invented requirements |
| **PLAN references a non-existent file or a forbidden path** | the lead greps the file registry | the cheap model hallucinated a file |
| **TASKS.md has a cycle or `[NEEDS CLARIFICATION]` surviving into build** | `prereq_validate.py` | the cheap model carried ambiguity forward |
| **plan-critic returns "rejected"** | the critic's own verdict (not a self-report) | a real defect was caught |
| **The cheap model refused** ("I can't do this", "I need more context") | the refusal itself | the cheap model is out of its depth; do not retry, escalate |

**What is NOT a trigger:**

- The cheap model says "this is hard." → not a trigger; it can be wrong.
- The cheap model is verbose. → not a trigger; verbose is a rubric, not
  a defect.
- The user says "this looks thin." → not a trigger; ask the user what
  specifically is missing, then verify.
- Latency / cost pressure. → NEVER a trigger. Tier is a quality dial,
  not a deadline dial (R-002 gates first, R-009 trace and learn).

The cascade cap (PDH-5.4) applies across the whole feature, not per
phase; see §5.

---

## 3. Cost profiles — user preferences

### 3.1 The three profiles

The cost profile is the **user's wallet**; the mode is the user's **quality
bar**; the tier is the planning-lead's **internal lever**. Three profiles
ship by default. The profile is *per user/project*, not per feature; the
planning-lead reads it once at intake and shades the per-phase tier matrix
from §2.1.

| Profile | Tier mix (planning phase) | SPEC tier | PLAN tier | Critic tier | When to use |
|---|---|---|---|---|---|
| **`save-money`** | ~85/14/1 | cheap | cheap (vibe) or cheap (mvp/prod) | cheap or skip | hobby, learning, throwaway, capacity pressure |
| **`balanced`** (default) | ~70/20/10 | standard for mvp, deep for prod | standard for mvp, deep for prod | standard for mvp, deep for prod | most projects; the ASPIS default |
| **`max-quality`** | ~40/30/30 | deep always | deep always | deep always | shipping a customer-facing surface, audit, compliance |

**Numeric grounding.** Per `cheap-models-quality.md` §2.4: a typical
ASPIS-style feature at a 70/20/10 mix is ~$0.30–$0.80 in model cost; a
Sonnet-everywhere baseline is ~$1.50–$3.00. So `save-money` is ~50% of
`balanced`; `max-quality` is ~3-5× of `balanced`. The user sees these
numbers *before* planning, not after.

**Source for the `balanced` default.** `AGENT-SYSTEM-ARCHITECTURE.md`:
"The model tier strategy is **70% cheap / 20% standard / 10% deep**
(target)."

### 3.2 How the user expresses preference

The preference is resolved in this order, first hit wins:

```
1. EXPLICIT IN REQUEST
   - "/plan --profile save-money", "use cheap models for this"
   - "I want max quality for the auth rewrite"
   - WINS for the current request

2. USER RULE (validated)
   - The user's global rules file contains a validated cost preference
   - WINS for the user's typical work
   - Validation: system-lead has already confirmed the rule is applicable
     to the current project (per system-rules.md §"The three rule layers")

3. PROJECT DEFAULT
   - .aspis/config/project.yaml → planning.cost_profile
   - WINS if the user is mid-project and wants the project's default

4. SYSTEM DEFAULT
   - .aspis/config/modes.yaml (or .aspis/config/defaults.yaml in future)
     → cost_profile: balanced
   - LAST RESORT
```

**The user can also express the profile indirectly**, via the mode:
`vibe` tends to imply `save-money`; `production` tends to imply
`max-quality`. The planning-lead surfaces this implication in the
plan-of-plan, e.g.:

> Plan-of-plan: track=feature, mode=mvp, profile=save-money
> (mvp + save-money = 80% cheap, 18% standard, 2% deep)
> Recommend balanced for SPEC+PLAN; save-money keeps task
> decomposition at cheap. Continue? [y/n]

### 3.3 Cost estimation surface — before planning writes anything durable

**The user must see a cost estimate before the SPEC is committed.**
This is the *cost gate*, and it sits at the end of intake, before
clarification begins.

**The estimate is per-phase, with a worst-case bound:**

| Phase | Tier | Estimated tokens (planning artifact size) | $ at cheap | $ at standard | $ at deep |
|---|---|---|---|---|---|
| P1 Clarify | cheap | ~2k | $0.001 | — | — |
| P2 SPEC | (per profile) | ~5k (vibe) / ~12k (mvp) / ~25k (prod) | $0.005 / $0.012 / $0.025 | $0.012 / $0.030 / $0.063 | $0.020 / $0.050 / $0.105 |
| P3 PLAN | (per profile) | ~3k (vibe=skip) / ~8k (mvp) / ~20k (prod) | — / $0.008 / $0.020 | — / $0.020 / $0.050 | — / $0.033 / $0.083 |
| P4 TASKS | standard | ~4k (vibe=large) / ~10k (mvp) / ~20k (prod) | $0.004 / $0.010 / $0.020 | $0.010 / $0.025 / $0.050 | $0.017 / $0.042 / $0.083 |
| P4 Packets | cheap | ~1k each × N tasks | $0.001 × N | — | — |
| P5 Critic | (per mode) | ~6k (self) / ~15k (independent) | $0.006 / $0.015 | $0.015 / $0.038 | $0.025 / $0.063 |
| **Total** | | | **<$0.10 (vibe) / <$0.20 (mvp) / <$0.50 (prod)** | **<$0.20 / <$0.40 / <$0.80** | **<$0.40 / <$0.80 / <$1.50** |

**Notes:**

- The dollar figures use the *current* tier map in `models.yaml`. The
  reference doc tracks the *tier names*; the `aspis models` script can
  refresh the dollars.
- These are *planning* costs only. The *build* cost (per
  `cheap-models-quality.md` §2.4) is ~$0.30–$0.80 per feature at
  balanced mix and is shown separately in the hand-off to Build Lead.
- The "worst case" line is the tier-deep end of the range; the
  planning-lead caps its own retry cost at this number, regardless of
  cascade depth (see §5.4).

**The cost gate output is part of the plan-of-plan.** The user sees:

> Plan-of-plan:
>   track:  feature
>   mode:   production
>   profile: balanced
>   cost:   ~$0.30–$0.80 worst case (planning only)
>   build:  ~$0.50–$2.00 estimated (5 task packets, standard mix)
>   proceed? [y/n]

If the user declines, the planning-lead asks for a profile change
(`save-money`) or a scope cut, not a silent downgrade.

---

## 4. Dynamic adaptation — during planning

The plan is a *living artifact*, not a contract. Five mid-planning events
trigger re-evaluation; the planning-lead handles each by name.

### 4.1 Mid-planning mode switch — "actually, make this production"

**Trigger:** at any phase boundary, the user says "switch to production"
(or "drop to vibe").

**Procedure:**

1. **Acknowledge** the change. Record it in the plan-of-plan
   (`mode_history` line: "P3 → production at <timestamp> on user request").
2. **Re-read `modes.yaml`** for the new mode's knobs. The knobs drive
   the depth of subsequent phases.
3. **Do NOT redo work silently.** The completed phases stay at their
   original depth. The mode change applies *forward* — a SPEC at
   `mvp/stories` does not get rewritten to `production/full` unless
   the user asks. The plan-of-plan says so explicitly.
4. **Re-shade the per-task mode for remaining tasks.** TASKS.md gets a
   `mode: production` annotation on the remaining tasks; completed
   task packets keep their original.
5. **Re-run the cost gate** (PDH-3.3) for the *remaining* work. Show
   the user the new estimate.
6. **Update `feature.yaml`'s `mode` field** to the new mode. The
   `mode_history` field captures the change for the audit trail.

**Reversal cost (per §1.6):** low at the start, growing with each
phase. The planning-lead says the cost in the plan-of-plan; the user
ratifies.

**Mode downgrade mid-feature (production → vibe):**

- Same procedure, but the lead *also* asks: "do you want to discard
  the production-mode artifacts (SPEC, PLAN, plan-critic) or keep
  them as reference?" The user picks; the lead records.
- A downgrade typically does NOT save tokens already spent; it saves
  the *build* cost downstream. Surface that fact.

### 4.2 Research need detected — if a plan needs research-lead

**Trigger:** during clarification or SPEC writing, the planning-lead
discovers a real unknown that requires external evidence: an API
contract, a benchmark, a regulatory text, a current best-practice.
The planning-lead **does not research**; it delegates to research-lead.

**Procedure:**

1. **Identify the research need precisely.** "What is the exact rate
   limit of the X API in 2026?" is research. "What's a good default
   rate limit?" is planning. The first is delegated; the second is
   decided in the SPEC's Assumptions.
2. **Delegate to research-lead** with the question, the source hint
   (if any), and the urgency (the planning-lead's current phase).
3. **Mark the SPEC's claim that depends on the research** as
   `[PENDING: <research question>]` — not `[UNVERIFIED]`. A
   pending research question is a known open item; an unverified
   claim is a research-lead failure to verify (PDH-5.2).
4. **Do NOT escalate the tier** of the SPEC to deep *because* of the
   research need. The SPEC's tier is about its quality, not its
   dependency on research. If the research is genuinely critical to
   the SPEC (e.g., the spec is a regulatory compliance spec), the
   SPEC was already at deep.
5. **Wait for research-lead's `RESEARCH_NOTE` artifact.** Consume it
   in place of the `[PENDING]` marker. If the note contains
   `[UNVERIFIED]`, see PDH-5.2.

**Cost impact.** A research call is *separate* from the planning tier
mix. The cost gate (PDH-3.3) does not include research; the lead
adds a separate line to the plan-of-plan:

> research: 1 question → research-lead (~$0.05–$0.20, research-tier)

**Research that does not exist.** If research-lead reports
`[UNVERIFIED]` and the SPEC is blocked, the lead does NOT escalate its
own tier. It surfaces the gap to the user: "I could not verify X. I
can (a) defer the spec and ask you, (b) make X an explicit assumption
in the SPEC's Assumptions section, (c) drop the slice that depends
on X. Pick."

### 4.3 Complexity discovered — if a "simple" feature turns out to have hidden complexity

**Trigger:** during architecture or task decomposition, the planning-lead
discovers the feature is materially more complex than the intake
predicted. Typical signals:

- The SPEC's P1 story is one task packet, but the implementation needs
  >3 (the "1 story = 1 task" assumption breaks).
- The architecture step identifies a hidden dependency on an
  out-of-scope module.
- The plan-critic (or its self-check) reports >3 unresolvable
  consistency gaps.
- The blast radius crosses a system-rule boundary (R-008 paths).
- A new external dependency or contract surfaces that the intake
  did not see.

**Procedure:**

1. **Stop and surface the complexity finding** in the plan-of-plan
   before continuing. Do not silently expand scope.
2. **Re-derive the mode** from the new size (per §1.2 / §1.3 E1).
   The new mode is the user-facing signal; the lead also re-derives
   the cost (PDH-3.3).
3. **Ask the user to ratify the new mode and cost**, or to cut
   scope. Three options to present:

   - **Expand:** keep the full scope, raise the mode, accept the
     higher cost.
   - **Cut:** drop the slice(s) that drove the complexity, keep the
     original mode.
   - **Defer:** record the complexity in a follow-up feature, ship
     the rest at the original mode.

4. **If the user picks "expand":** the lead re-runs intake with the
   new mode, re-runs the cost gate, and continues. Artifacts written
   so far are deepened (not re-written) — the SPEC's "stories" stay
   as stories unless the new mode requires "full," in which case
   the lead deepens the SPEC.
5. **If the user picks "cut":** the lead edits the SPEC's Scope
   section to reflect the cut, drops the orphan stories (the
   plan-critic's traceability check enforces this), and continues
   at the original mode.
6. **If the user picks "defer":** the lead writes a follow-up
   feature folder stub (`.aspis/features/F-NNN-deferred-slug/`)
   with a one-paragraph "why deferred" note, and continues at the
   original mode.

### 4.4 Ambiguity wall — if 5 questions aren't enough

`requirement-clarification` caps at 5 questions (the planning lead's hard
limit per `plan.md` step 3). The wall is hit when:

- After 5 questions, the lead has 3+ unresolved critical items.
- The user's answers contradict earlier answers.
- The user is unable to answer a question (defer-to-human is the
  default response).

**Procedure at the wall:**

1. **Stop asking.** The 5-question cap is a hard limit to protect the
   user's time; the wall means the cap is exhausted, not that the
   lead should keep going.
2. **State the residual ambiguities** as `[NEEDS CLARIFICATION: ...]`
   markers in the SPEC's Open Questions section. Each marker is
   a *specific* question, not "please clarify the requirements."
3. **Do not write a SPEC with surviving critical ambiguities** in
   `production` mode. The plan-critic's §"Resolved unknowns" check
   (from `plan-critic` SKILL.md) will reject it.
4. **Two recovery paths:**
   - **Carry forward in the SPEC as open questions** (acceptable in
     vibe or mvp modes; the build proceeds with the open question
     recorded as a risk). The reviewer checks that the question
     was, in fact, asked and recorded.
   - **Escalate to project-lead** (or the user directly) for
     arbitration. Project-lead can change the mode, the scope, or
     the user.
5. **Do NOT escalate the tier to "make the model resolve the
   ambiguity."** A bigger model does not invent the answer to a
   genuine human decision. The cap is on questions, not on tier.

**Anti-pattern to avoid.** The lead does not split one question into
five ("do you want A?" × 5 sub-questions). One question, one decision;
five decisions is the budget.

---

## 5. Tier cascade on failure

The cascade is the planning-lead's safety net when a tier produces an
unacceptable artifact. The cascade is **measurable** (PDH-2.2) and
**bounded** (PDH-5.4).

### 5.1 Cheap SPEC failure → escalate tier and retry

**Trigger:** the cheap tier produces a SPEC that fails one of the
measurable signals in PDH-2.2 (knob violation, FR/SC mismatch, file
hallucination, or surviving `[NEEDS CLARIFICATION]` in `production`).

**Procedure:**

1. **Identify the specific failure** in the cheap artifact. The cheap
   output is not discarded wholesale; the lead extracts the parts that
   pass.
2. **Retry at the same tier ONCE** with a *focused feedback prompt*:
   "Your previous SPEC failed the following check: <check>. Produce
   only the failing section; do not regenerate the rest." This is
   cheaper than a full re-generation and tests whether the cheap
   model can correct with feedback.
3. **If the focused retry also fails, escalate to standard.** The
   standard tier re-generates the failing section (or the whole SPEC
   if the failure is structural).
4. **If standard also fails, escalate to deep.** Deep is the final
   planning tier; failure here is escalated to the project-lead.
5. **Record the cascade** in the plan-of-plan: "P2 SPEC: cheap → cheap
   (focused) → standard → accepted. Total cost: $X. Time: Y min."

**Why this shape.** Per `cheap-models-quality.md` §2.6 Pattern 1
(Cascaded retry with budget), and `planning-quality-and-rules-reference.md`
§4.3: cheap first, escalate on a *measurable* failure, cap the cascade.
The focused retry step is the one improvement over the generic pattern;
it tests the cheap model on its *correction* ability, which is often
stronger than its *first-pass* ability on a large artifact.

### 5.2 Research unverifiable → mark `[UNVERIFIED]`, do not escalate tier

**Trigger:** research-lead returns a `RESEARCH_NOTE` with the claim
`[UNVERIFIED]` (could not find an authoritative source; could not
confirm the version; the source contradicts itself).

**Procedure:**

1. **Mark the dependent SPEC claim** with `[UNVERIFIED: <reason>]`. The
   marker is a *flag*, not a blocker — the SPEC proceeds.
2. **Do NOT escalate the planning tier.** A bigger model does not
   verify a fact; the research function does, and it has already
   reported failure. Escalating tier is wasted budget.
3. **Surface the `[UNVERIFIED]` to the user** in the plan-of-plan
   with three options:
   - **Accept the assumption** (mark the SPEC's Assumptions with
     the unverified claim and the reason).
   - **Defer the slice** that depends on the claim (drop from the
     current feature; revisit in a future feature).
   - **Arbitrate** the user supplies the missing fact.
4. **Track `[UNVERIFIED]` in `feature.yaml`** as a risk. The reviewer
   in production mode flags any unverified claim in the SPEC's
   Acceptance section.

**Why this shape.** Per `cheap-models-quality.md` §2.6 Pattern 5
(confidence-based escalation): escalating on uncertainty is the wrong
lever when the uncertainty is *about the world*, not about the
model's capability. The model can't fix a fact it doesn't have.

### 5.3 Plan-critic rejection → revise with same tier, escalate only on 3rd rejection

**Trigger:** the plan-critic returns `rejected` or `changes-required`
on the SPEC + PLAN + TASKS bundle.

**Procedure:**

1. **Read the critic's findings** in order. Each finding is a specific
   defect; the lead fixes it.
2. **Revise at the same tier** as the original (cheap for vibe-tier
   work, standard for mvp, deep for production). The critic is a
   gate, not a tier upgrade signal.
3. **Re-submit.** A revision is not a re-plan; it's a targeted fix
   to the failing artifact.
4. **Cap:** **two revisions at the same tier; on the 3rd rejection,
   escalate the tier by one** (cheap → standard, or standard → deep)
   and re-plan. The escalation is recorded.
5. **Cap of caps:** on the 3rd escalation (i.e., the 9th total
   rejection), the planning-lead stops and surfaces to project-lead
   with the full finding history. The lead does not loop.

**Why this shape.** Per `AGENT-SYSTEM-ARCHITECTURE.md` ("3 attempts
max for fixes, then escalate to human") and `fix-lead`'s hard cap.
The same 3-strikes rule applies to the planning loop: 2 cheap retries
+ 1 escalation is a small enough loop to debug; beyond that, the
problem is upstream (a bad intake, an unsolvable ambiguity, a
broken `modes.yaml`).

**Vibe mode and `plan_review: skip`.** There is no critic in vibe
mode (PDH-2.1, `modes.yaml`). The lead's own re-read is the gate.
A self-rejection still counts toward the cap.

### 5.4 The cascade budget — total planning cost ceiling

The cascade is bounded by a **total cost ceiling**, not just by a
retry count. The ceiling is set by the cost gate (PDH-3.3):

```
planning_ceiling = sum of (per-phase worst-case tier-deep cost)
                 ≈ $0.40 (vibe) / $0.80 (mvp) / $1.50 (production)
```

If the cumulative planning cost exceeds the ceiling, the lead stops
and surfaces:

- "I have spent $X on planning, above the $Y ceiling. Three options:
  (a) raise the ceiling and accept the cost, (b) drop a phase's depth
  and re-plan, (c) hand the partial plan to project-lead for
  arbitration."

The ceiling applies to the *feature*'s planning cost, not per phase.
A phase that has finished cheaply is banked; subsequent phases can
spend more without violating the ceiling.

**Why this shape.** Per `cheap-models-quality.md` §2.6 Pattern 1
("Cap the cascade (3 cheap retries → 1 mid → 1 frontier) so a
pathological task doesn't drain the budget"). A cost ceiling is a
stronger guard than a retry count because the user feels cost more
than retries.

---

## 6. Reconciliation gap — the planning-lead frontmatter problem

The current `planning-lead.md` frontmatter pins `model:
opencode-go/deepseek-v4-pro` (deep tier per `models.yaml`). The
catalog intent (per `planning-quality-and-rules-reference.md` §4.5
and `local/agents/planning-lead.md`) is **standard for MVP, deep for
production**.

**The resolution this spec proposes:**

- The frontmatter `model:` is the **agent's *default* tier** — what
  the agent runs at when no mode is set. With the system default
  being `production`, the deep pin is *correct as the default* but
  *overpays for MVP work*.
- The mode and profile **shade the default**:
  - `vibe` mode + any profile → override the frontmatter to **cheap**.
  - `mvp` mode + `save-money` or `balanced` → override to **standard**.
  - `mvp` mode + `max-quality` → keep **deep**.
  - `production` mode + any profile → keep **deep**.
- The override happens in the planning-lead's *intake step*, not in
  the frontmatter; the frontmatter is a static pin, the intake is
  the dynamic read.
- The override is logged in the plan-of-plan so the cost audit is
  accurate.

**Until this is wired into the runtime adapter**, the planning-lead
uses the deep pin and accepts the cost — the cost of a deep SPEC is
less than the cost of a bad SPEC. The runtime adapter is the
system-lead's concern; this spec is the policy the adapter will
implement.

---

## 7. Anti-patterns to refuse

These are the planning-lead mistakes the spec is designed to prevent.
Each is a deterministic trap; the plan-critic and the user can spot them.

| Anti-pattern | Why it fails | Refuse with |
|---|---|---|
| **Picking mode without stating it in the plan-of-plan** | the user can't override cheaply; the audit trail is missing | one-line mode statement at the start of every plan |
| **Silently escalating the tier to "fix" a bad output** | the model's self-report is unreliable; the cost grows without a measurable signal | apply the cascade only on a PDH-2.2 signal, not a feeling |
| **Asking >5 clarification questions** | the user disengages; the questions that matter get lost | the wall procedure in PDH-4.4 |
| **Re-doing work after a mode change** | the artifacts are already at the new mode's depth at the cost of the old | deepen, do not re-write; the plan-of-plan records the change |
| **Pinning the planning tier in the frontmatter and never changing it** | cost overruns on vibe/mvp work; quality gaps on high-risk phases | the intake-driven shade (PDH-6) |
| **Escalating to deep to "be safe"** | the cost of deep is 8× cheap; the benefit is in the SPEC, not in TASKS | reserve deep for SPEC + Architecture + plan-critic |
| **Treating a research gap as a tier gap** | the model can't verify a fact; bigger model is the same uncertainty | `[UNVERIFIED]` + user arbitration (PDH-5.2) |
| **Accepting "looks done" from the cheap model** | the cheap model often produces confident wrongness | run the prereq-validate gate; the gate is the only accept signal |
| **Producing a SPEC with surviving `[NEEDS CLARIFICATION]` in `production` mode** | the plan-critic will reject; the user expected production quality | either ask the user, lower the mode, or split the feature |
| **Mid-planning mode downgrade to save the user's "money" without asking** | the user picked production for a reason; a silent downgrade is a quality decision the lead should not make | suggest (PDH-1.4), don't auto-apply |
| **Cascade loop** (3 retries → escalate → 3 retries → escalate → ...) | the problem is upstream, not in the tier | the 3-strike cap (PDH-5.3); escalate to project-lead after |

---

## 8. The five-question summary (for the plan-of-plan)

The planning-lead answers these five questions in the plan-of-plan
*before* writing the SPEC. The user can see all of them and override
any one cheaply.

```
1. What track?      (question | trivial | small | feature | project)
2. What mode?       (vibe | mvp | production) + the resolution path
3. What profile?    (save-money | balanced | max-quality) + the resolution path
4. What does it cost? (per-phase tier forecast + worst-case ceiling)
5. What's the per-phase mode? (any per-phase overrides from §1.5)
```

A plan-of-plan that does not answer all five is incomplete; the
planning-lead returns to intake.

---

## 9. Sources and provenance

| Source | What it grounded in this spec |
|---|---|
| `cheap-models-quality.md` §2.2 (task-by-task cheap capability) | §2.1 per-phase tier matrix (cheap for intake/clarify/decomposition, deep for SPEC/architecture) |
| `cheap-models-quality.md` §2.4 (cost numbers) | §3.1 cost profile dollar estimates; §3.3 cost gate |
| `cheap-models-quality.md` §2.6 Pattern 1 (cascade) | §2.2 cascade triggers; §5.1 cheap-→-deep cascade procedure; §5.4 cost ceiling |
| `cheap-models-quality.md` §2.6 Pattern 5 (confidence-based escalation) | §5.2 unverifiable research → don't escalate tier |
| `core-loops-2026.md` §1.5 (rigor dial) | §1.1 mode resolution; §1.5 per-phase mode; §1.6 override at four points |
| `core-loops-2026.md` §4 "What has been abandoned" (esp. "the agent knows when it's done") | §2.2 invalid triggers (no self-report) |
| `models.yaml` (cheap/standard/deep → canonical ids) | §6 reconciliation gap; tier-name stability |
| `modes.yaml` (knob vocabulary: `spec`, `architecture`, `plan_review`, etc.) | §1.1 mode knobs read at intake; §1.5 per-phase mode uses the same knobs |
| `planning-lead.md` (live frontmatter: `model: deepseek-v4-pro` deep pin) | §6 reconciliation gap |
| `local/AGENT-SYSTEM-ARCHITECTURE.md` ("70/20/10 cheap/standard/deep") | §3.1 `balanced` profile mix |
| `local/AGENT-SYSTEM-ARCHITECTURE.md` ("Cascade on failure: 3 cheap → 1 mid → 1 deep") | §2.2 cascade default; §5 cascade procedures |
| `local/AGENT-SYSTEM-ARCHITECTURE.md` ("3 attempts max for fixes, then escalate to human") | §5.3 plan-critic 3-strike cap |
| `local/AGENT-SYSTEM-ARCHITECTURE.md` ("frontier for judgment, cheap for context") | §2.1 deep reserved for SPEC + architecture |
| `planning-intake` SKILL.md (mode resolution order; "ceiling, not a floor") | §1.1 decision tree; §1.5 per-phase mode |
| `requirement-clarification` SKILL.md (max-5-questions cap) | §4.4 ambiguity wall |
| `plan-critic` SKILL.md (cross-artifact consistency, "no [NEEDS CLARIFICATION] in production build") | §5.3 plan-critic rejection loop; §2.2 invalid triggers |
| `system-rules.md` R-001 / R-002 / R-007 / R-008 / R-009 | §1.2 risk markers (R-001, R-008); §2.2 gate signal (R-002); §6 tier pin (R-007); §4.1 audit trail (R-009) |
| `local/AGENT-SYSTEM-ARCHITECTURE.md` "Quality = model capability × task clarity × test strength × review discipline" | §0 rule of the doc |

---

## 10. Risk and uncertainty

**Well-established (cite as fact):**

- Mode resolution order (explicit → active → project → system) is the
  `planning-intake` default; this spec codifies it.
- Mode-per-phase (the "ceiling, not a floor" rule) is the
  `core-loops-2026.md` §1.5 finding, attested in Anthropic, Cursor, and
  GitHub Copilot.
- The 70/20/10 mix target and the cascade pattern are attested in
  `cheap-models-quality.md` with primary sources (Wayfair, Bugbot, SWE-bench).

**Caveat — dollar estimates.** The §3 cost numbers use the
**June 2026** pricing from `cheap-models-quality.md` §2.4 and the
current `models.yaml`. **Re-run the cost gate annually**; model
pricing moves faster than the spec.

**Caveat — runtime adapter gap.** §6 is a *policy* that the runtime
adapter must implement. Until then, planning-lead runs at the deep
frontmatter pin and accepts the overpayment. The cost is bounded by
the §5.4 ceiling; the lead does not exceed it.

**Caveat — research.[UNVERIFIED] is a planning-lead surface, not a
research-lead guarantee.** Research-lead may later verify the claim;
the SPEC's marker is updated in place. The plan-critic at P5 checks
for surviving markers in production mode.

**Caveat — user-rule validation.** §3.2 step 2 ("user rule validated
by system-lead") assumes the system-lead has run the validation per
`system-rules.md` §"The three rule layers." If the user rule has not
been validated, the planning-lead falls through to the project default.
The plan-of-plan notes the fallback.

**Caveat — feature-folder mode_history.** §4.1 records the mode change
in `feature.yaml`'s `mode_history`. If the field is not yet in the
schema, the lead records in the SPEC's preamble (`## Mode history`)
until the schema catches up. The system-lead owns the schema change;
this spec is data-shape-agnostic.

---

## 11. Stale-check and refresh

This spec is correct as of **2026-06-26** against the cited sources.
**Refresh when:**

- The tier map in `models.yaml` changes (tier *names* should stay
  stable; canonical ids will change).
- The `modes.yaml` knob vocabulary changes (a new knob invalidates
  the per-phase matrix in §2.1).
- The runtime adapter implements §6 and the frontmatter pin can
  be retired.
- The 70/20/10 mix target is empirically revised by the
  `.aspis/runs/` telemetry (planned for Phase 4/5 per
  `model_catalog.yaml`'s "scores — refined by tracing").
- A new production model lands at a materially different price point
  (e.g., a frontier model at 0.5× the cost of the current deep tier
  would shift the §3 dollar estimates).

**Refresh procedure:**

1. Re-read the five sources at the top of this doc.
2. Re-run the cost numbers in §3.1 and §3.3 from current
   `models.yaml` pricing.
3. Re-validate the cascade cap in §5.4 against any new evidence in
   `cheap-models-quality.md` successors.
4. Bump the date and version in the frontmatter of this file.
5. Cite the change in `.aspis/runs/lessons/` if the spec materially
   changes a decision the planning-lead made.

---

**End of spec.** Cite by section ID (`PDH-2.1`, `PDH-3.4`,
`PDH-5.1`, etc.) when a plan, plan-critic, or review references it.
