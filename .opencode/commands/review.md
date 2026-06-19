---
description: Review a change, branch, or completed feature and return a verdict.
agent: reviewer
---

Review the change described below, following `.aspis/workflows/review.md`.

$ARGUMENTS

Set the depth from risk and mode (`review-strategy`), evaluate the in-scope quality
dimensions against the SPEC's acceptance criteria (`quality-review`), and return a
verdict (`acceptance-decision`): approve / approve-with-notes / changes-required /
rejected. Stay read-only and cite file:line. Route rejections to the Fix Lead.
