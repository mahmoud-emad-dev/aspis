---
name: harvest-protocol
description: The 7-step R-008-gated path for bringing an external skill, source, or reference into the ASPIS catalog as a permanent asset.
---

# harvest-protocol

## Purpose
When the research-lead discovers external knowledge worth keeping — a skill
pattern, a reference architecture, a library's official usage pattern — the
harvest protocol governs how that external content becomes a permanent catalog
asset. It is R-008-gated: bringing external intellectual property into the
system requires human approval for license compliance and source authority.

## When to use
- When research discovers a reusable pattern, skill, or reference that should
  live in the catalog rather than a one-off RESEARCH_NOTE.
- When a delegating lead explicitly requests harvesting ("add this to the catalog").
- When the same external source is referenced by multiple features — it's time to
  promote it from per-feature reference to global catalog asset.

## Procedure — the 7 steps

### 1. Candidate
Identify the external content: a URL, a document, a skill pattern, a reference
architecture. Record:
- Source URL and retrieval date
- What problem it solves
- Why it deserves catalog status (reusability, authority, frequency of use)

### 2. Record
Write a `HARVEST_CANDIDATE.md` in `.aspis/research/harvest/<slug>/` with the
candidate information. This is a working document, not yet a catalog asset.

### 3. License check (R-008 gate)
**This is the R-008 human gate.** Before adapting external content:
- Identify the source's license (MIT, Apache, CC-BY, proprietary, etc.)
- Determine whether the license permits incorporation into the ASPIS catalog
- If the license is ambiguous, restrictive, or absent → **STOP. Request R-008
  approval.** The human owner must confirm the license is compatible.
- Record the license determination in the candidate document.

### 4. Adapt
Transform the external content into catalog shape:
- **Skill**: `catalog/skills/<name>/SKILL.md` with Purpose / When to use /
  Procedure / Outputs / Anti-patterns
- **Template**: `catalog/templates/<category>/<name>.md`
- **Reference**: `catalog/data/<name>.yaml` or `.md`
- Attribute the source: include "Adapted from <URL>" and the license in a
  comment or metadata field.
- Do NOT copy verbatim unless the license explicitly permits it — adaptation
  means understanding the pattern and re-expressing it in ASPIS form.

### 5. Prove
Demonstrate the adapted asset works:
- For a skill: can a lead agent execute the procedure from the SKILL.md alone?
- For a template: does it produce a valid artifact when filled?
- For a reference: is every claim traceable to the original source?
- Run the catalog validator to confirm structural integrity.

### 6. Review
Route the adapted asset through the reviewer:
- Is the adaptation faithful to the original pattern?
- Is the attribution correct and the license honored?
- Does the asset meet the catalog quality standard (frontmatter, sections,
  anti-patterns)?
- The reviewer's verdict is the gate — approved, changes-required, or rejected.

### 7. Promote
On reviewer approval:
- Move the asset from `.aspis/research/harvest/<slug>/` to its permanent catalog
  location.
- Wire the asset into the owning agent's frontmatter (system-lead does this,
  not research-lead).
- Update `FILE_REGISTRY.yaml` to include the new asset.
- Archive the harvest candidate as `HARVEST_COMPLETE.md` with the promotion date
  and the reviewer's verdict.

## Outputs
- A promoted catalog asset (skill, template, or reference).
- Archived harvest candidate with the full 7-step trail.
- Updated catalog with the new asset wired and validated.

## Anti-patterns
- Skipping the license check — incorporating unlicensed or restrictively-licensed
  content is a legal risk. The R-008 gate exists for this reason.
- Copying verbatim instead of adapting — unless the license explicitly permits
  verbatim copy, adaptation is required. "Adapted from" means re-expressed, not
  copy-pasted.
- Harvesting content the system doesn't need yet — a RESEARCH_NOTE is sufficient
  for one-off references. Promote to catalog only when the content is reused
  across features or by multiple agents.
- Harvesting without attribution — every harvested asset must cite its source
  URL, retrieval date, and license.
