# Future Feature — Structured Rules System

> Captured from the owner's direction while reorganising the rules files.
> The rules **reorg** (4 layers + precedence + `project-rules.md` template) is
> done now. This note records the **larger system** to build later — NOT in F-016.

## Vision

Turn project/user rules from prose into a **validated, structured store** that the
system grows and a dashboard controls.

### 1. Rules as structured data (with metadata)
Each rule carries: `id`, `applies-to` (project kinds: software / data / web /
automation / research / all), `roles` (which agents load it), `severity`
(block / warn / advisory — the violation policy), `status` (active / draft),
and `source` (profile / user / system / captured). The markdown format in
`project-rules.md` is the seed; this feature makes it machine-structured.

### 2. Validation engine
For any rule, answer deterministically: **is it valid? does it apply to this
project? can it be applied / enforced here?** A rule that can't apply is carried
as `draft`, not enforced — never forced onto the wrong project.

### 3. Growth / capture
As the system is used, **capture new rules** from what worked, normalise them into
the structured format, and add them to the right layer.

### 4. Global user rules → seed new projects
A **global user rules file on the user's machine**. On a brand-new project with no
code and no rules yet, the system seeds `project-rules.md` from the validated
subset of the user's global rules. The user **adds rules one by one**; ASPIS turns
them into the structured, valid file.

### 5. Per-agent rule loading (partly seeded now)
Agents read only their relevant rules via the `roles:` tag/section — already
expressed in the `project-rules.md` template. This feature wires the actual
load path (context step pulls the tagged subset; system rules cited by ID in the
agent body).

### 6. Dashboard
Later, surface the rules store in the dashboard to **view, configure, customise,
and control** rules per project / profile / user.

## Relationship to what's done now

- **Done (rules reorg):** 4 layers, precedence, generalised Constitution,
  `project-rules.md` template with the metadata format + role tags, R-010.
- **This feature builds:** the validated structured store, the validation engine,
  global user rules + seeding, the load path, and the dashboard surface.

## Scope note

Feature-sized and partly depends on the dashboard (roadmap Phase 5) and the
user-rules layer. Plan it as its own feature; do not fold into F-016 or F-017.
