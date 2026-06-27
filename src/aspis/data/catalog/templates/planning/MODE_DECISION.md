---
type: template
category: planning
version: 1.0
---

# Mode Decision — <feature-id>

> The rationale for the build mode selected for this feature. Mode is the
> single highest-leverage planning decision — it controls depth, gates, review
> strategy, and artifact requirements. Document why this mode was chosen and
> what alternatives were considered.

---

## Feature

- **ID**: <F-NNN>
- **Title**: <Feature Title>
- **Decision date**: <YYYY-MM-DD>
- **Decided by**: <planning-lead or project-lead>

---

## Proposed mode

<vibe / mvp / production>

### Mode knobs at this level

| Knob | Setting | What it means |
|------|---------|---------------|
| Planning depth | <depth> | <e.g. "Full 8-phase lifecycle" or "Spec only, no PLAN"> |
| Task granularity | <size> | <e.g. "≤3 files per task" or "bare TASKS outline"> |
| Review strategy | <strategy> | <e.g. "Per-task review by reviewer" or "Self-review only"> |
| Gate requirements | <gates> | <e.g. "pytest + ruff + validate-runtime" or "None"> |
| Artifact depth | <depth> | <e.g. "SPEC + PLAN + TASKS + packets" or "SPEC only"> |
| Evidence requirements | <level> | <e.g. "Gate reports + test output" or "Verbal confirmation"> |

---

## Risk assessment

| Risk | Likelihood (L/M/H) | Impact (L/M/H) | Mode mitigates? |
|------|--------------------|----------------|-----------------|
| <e.g. "Scope creep without detailed plan"> | M | H | Yes — production mode gates every layer. |
| <e.g. "Over-engineering a trivial fix"> | H | M | Yes — vibe mode skips heavy artifacts. |
| ... | | | |

---

## Justification

<Why this mode is correct for this feature. Reference the feature's scope,
risk profile, team context, and urgency. One or two paragraphs.>

Example:
> This feature adds a new runtime adapter (Claude Code) — it touches the export
> pipeline, permission surfaces, and every agent body. A defect here could break
> all agent rendering. Production mode's per-task review and full gate sweep are
> warranted. The cost of under-planning is a broken export; the cost of
> over-planning is one extra planning session — an easy trade.

---

## Alternatives considered

| Alternative mode | Why rejected |
|------------------|--------------|
| vibe | <e.g. "Too risky — no gate sweep means a broken export could ship."> |
| mvp | <e.g. "MVP would skip per-task review, and the export pipeline is too sensitive for self-review only."> |
| production | <Selected> |

---

## D-### references

<If a durable decision (D-###) covers mode selection policy, reference it here.
Otherwise, this decision stands on its own rationale.>
