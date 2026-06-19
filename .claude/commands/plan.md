---
description: Plan a feature — run the planning lifecycle (spec → architecture → tasks → packets).
---

Plan the work described below, following `.aspis/workflows/plan.md`.

$ARGUMENTS

Start with the `planning-intake` skill: read `.aspis/config/modes.yaml`, classify the
request, and pick the mode. Then proceed through the workflow's steps, using the
planning scripts for the mechanical parts — `feature_scaffold.py` to scaffold,
`task_compile.py` to emit packets, `prereq_validate.py` to gate before handoff.
