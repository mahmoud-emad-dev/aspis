---
name: profile-manager
description: Create, inherit, and merge ASPIS profiles (base.yaml + per-project overrides) — define which agents, runtimes, and settings are active for a project. Owned by system-lead.
---

# profile-manager

## Purpose

ASPIS profiles are the **declarative specification of a project's runtime surface**: which
agents are active, which runtimes (OpenCode / Claude) are generated, and which settings apply.
One profile fully describes the project's ASPIS surface with no hidden defaults — the profile
is the single source for asset selection (R-006). This skill guides creating new profiles,
inheriting from `base.yaml`, and merging per-project overrides.

## When to use

- Setting up a new project with a custom agent set.
- Authoring a specialized profile (e.g. `python-data-science` that excludes some agents).
- Layering per-project overrides on top of an inherited profile.
- Auditing what a project's runtime actually contains.

## Procedure

1. **Pick a base** — almost always `src/aspis/data/profiles/base.yaml` (the full shared roster).
2. **Author the new profile YAML** declaring only overrides: target runtimes, agent
   include/exclude lists, model-tier assignments, hook enforcement, gate plan.
3. **Inherit by merge** — undeclared fields fall through to the base; only declared fields
   override. Validate against the profile schema (`asps.profiles.parse_profile` /
   `load_profile`).
4. **Verify the export plan** — run `aspis export --dry-run` with the new profile; every
   referenced agent, skill, and runtime must resolve. Any UNKNOWN / missing reference
   fails the plan.
5. **For per-project overrides only** — create `project.yaml` (Tier 1) in the project root
   that layers over the active profile; re-run `aspis export --dry-run` to confirm the merge.
6. **Document the diff** — in the profile's header comment, state the purpose and what it
   changes from the base. A profile without a documented why is a maintenance hazard.

## Outputs

- A new profile YAML under `src/aspis/data/profiles/` (or a merged `project.yaml` override).
- A passing `aspis export --dry-run` plan — every reference resolves, no UNKNOWN.
- A short header comment explaining the profile's purpose and its diff from the base.

## Anti-patterns

- **Forking the base** — copying `base.yaml` whole instead of inheriting. The fork silently
  drifts from base and never picks up roster or rule updates.
- **Overriding without documenting why** — overrides are surprises for the next maintainer;
  every override needs a one-line reason.
- **Excluding agents but leaving delegate references live** — delegates that point at an
  excluded agent break the runtime; update delegate targets or keep the agent.
- **Skipping `--dry-run`** — a profile that "looks right" but has a broken reference ships
  as a runtime gap, not a build error.
- **A new profile for every minor difference** — each profile is a maintenance burden;
  prefer per-project `project.yaml` overrides when the change is local.
