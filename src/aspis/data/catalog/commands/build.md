---
name: build
description: Build the active (or named) feature from its task packets.
agent: build-lead
---

Build the feature, following `.aspis/workflows/build.md`.

$ARGUMENTS

Confirm prerequisites with `prereq_validate.py --phase build`, then drive the task
packets in `.aspis/features/<id>/tasks/` in dependency order. Hold the whole-feature
context yourself; delegate each larger task to a context-isolated `general-builder`
with only its packet. Review per each packet's routing, and hand approved changes to
the `committer` — never commit yourself.
