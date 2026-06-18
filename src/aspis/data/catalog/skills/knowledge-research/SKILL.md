---
name: knowledge-research
description: Use to answer a technical unknown from authoritative, current sources — official docs, release notes, reputable references — verifying the version and separating verified fact from opinion. Produces validated findings, not guesses.
---

# Knowledge Research

## Purpose

Replace an unknown with verified, current knowledge. Models go stale; this skill
grounds the system in what's actually true now, from sources that can be trusted.

## When to use

When a real unknown blocks or shapes work and can't be settled from the project
itself — a framework's current API, a version's breaking changes, an external
service's behavior.

## Procedure

1. **Define the question.** State precisely what's unknown and what a complete
   answer must cover.
2. **Find authoritative sources.** Official documentation, release notes, the
   project's own repo/issues — prefer primary sources over blog hearsay.
3. **Verify currency.** Confirm the version that applies and whether the information
   is current; note breaking changes and compatibility constraints.
4. **Cross-check.** Confirm key claims against more than one source where it matters.
5. **Separate fact from opinion.** Mark what's verified vs. what's a recommendation,
   and flag remaining uncertainty.

## Outputs

- Validated findings with sources and version, and any caveats called out.

## Anti-patterns

- Answering from memory without checking current sources.
- Trusting a single unofficial source for a load-bearing claim.
- Presenting opinion or an outdated API as verified fact.
