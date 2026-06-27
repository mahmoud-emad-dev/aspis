# Agent Body Standard

The contract every ASPIS agent body must satisfy. This is the **single source of
truth** for body shape — individual agents do not restate it; they conform to it.
Used by the planning-lead (design), build-lead (construction), reviewer (gate),
and system-lead (validation).

## Principles

- **R-006 Thin agents, single source**: content lives in skills/workflows; the body
  *references* by name/path, never inlines procedure or data.
- **Cite, don't restate**: system rules cited by ID only (e.g. "R-001, R-004").
  The body never restates what the rule says.
- **Every section is short**: Identity is 2–4 lines; Core rules is a bullet list of
  IDs plus brief own-rules; Responsibilities is a table; Delegation is a list.
- **No dead references**: every delegate, skill, workflow, and template the body
  names must exist.

## Required frontmatter

Every agent body opens with YAML frontmatter between `---` fences:

| Field | Required | Description |
|---|---|---|
| `name` | yes | Unique agent name (kebab-case) |
| `description` | yes | One sentence — what it does |
| `mode` | yes | `vibe` / `mvp` / `production` |
| `model` | yes | Model tier: `cheap` / `standard` / `deep` |
| `temperature` | yes | Float, typically `0.0`–`0.3` for deterministic agents |
| `tools` | yes | List of tool grants (least-privilege) |
| `permissions` | yes | Permission allow/deny block (least-privilege + deny floor) |
| `delegates` | yes | List of agent names this agent may delegate to |
| `skills` | yes | List of skill names this agent uses (catalog-relative) |
| `runtimes` | yes | `[opencode, claude]` or subset |
| `export_scope` | yes | What paths this agent is allowed to touch |

## Required body sections

After the frontmatter, the body contains these sections in order:

### 1. Title line
```
# <Agent Name>
> Derived from Research/ref/<agent>.md
```

### 2. Identity
2–4 lines establishing **what the agent IS** and **what it IS NOT**, plus its
**prime directive** — the one non-negotiable rule that overrides all others.

### 3. How you work
1–2 lines of natural-language procedure plus a **pointer to the workflow**
(e.g. "See `.aspis/workflows/build.md`"). Never restate the workflow steps here.

### 4. Core rules
- A bullet list of **system rules cited by ID** (R-001, R-004, etc.) this agent
  must honour — never restate what the rule says.
- The agent's **own rules** if any — brief, agent-specific, not covered by system
  rules.
- Maximum 8–12 rules total per body.

### 5. Responsibilities → skills
A table mapping each responsibility to the skill(s) that handle it:

```
| Responsibility | Skill |
|---|---|
| <what the agent is responsible for> | `<skill-name>` |
```

### 6. Delegation
A list of **who** this agent delegates to, **when**, and **for what kind of work**.
Every name in this section must match a catalog agent. No orphan delegates.

### 7. Dynamic-readiness
One short block (3–6 lines) applying the three dynamic-readiness dials to this
agent's work. References `.aspis/context/DYNAMIC_READINESS.md`. See that document
for the convention.

## Forbidden patterns

- **No duplicated content**: skill procedures, rule text, workflow steps, or
  template content must never appear inline in a body. Reference by name/path.
- **No missing references**: every `skill:`, `delegate:`, or workflow pointer
  must resolve to an existing asset.
- **No orphan delegates**: a delegate listed in Delegation must exist as a
  catalog agent at `src/aspis/data/catalog/agents/<name>.md`.
- **No `bash: '*': allow`**: every agent's permission surface must be
  least-privilege with the universal deny floor honoured.
- **No restated rules**: never write "R-001 means scope control — don't touch
  forbidden files." Write only "R-001" and let the system rules speak for
  themselves.

## Checklist

Use this to verify any agent body before accepting it:

- [ ] Frontmatter has all 11 required fields
- [ ] Identity section is 2–4 lines with IS / IS NOT / prime directive
- [ ] How you work section is 1–2 lines + a workflow pointer
- [ ] Core rules cite system rules by ID only; own rules (if any) are brief
- [ ] Responsibilities→skills table maps every responsibility to at least one skill
- [ ] Delegation section lists only existing catalog agents
- [ ] Dynamic-readiness block is present and references the convention document
- [ ] Zero duplicated content from skills or workflows
- [ ] Every `skill:` in frontmatter resolves to a `SKILL.md` file
- [ ] Every delegate exists as a catalog agent
- [ ] Permission surface is least-privilege; no `bash: '*': allow`; deny floor
  honoured (`git commit*` committer-only, `git push*` none, `webfetch`
  system-lead + research-lead only, `websearch` research-lead-only)
- [ ] Cost-of-change for this agent's asset set ≤ 3 files (the body, any
  skill it uniquely owns, and at most one referencing agent's frontmatter)
