---
name: commit-message
description: How to compose a commit message in the ASPIS convention — used by the committer before every commit.
---

# Commit message

One convention everywhere. The rule lives in data
(`.aspis/config/commit-convention.yaml`) and is applied by `aspis commit` (which
composes the message) and enforced by the F-006 `commit-msg` hook. This skill is the
human-facing "how" — you supply the parts, the tool builds and validates the message.

## Format

```
type(F-NNN[/T-NN | /T-NN..T-MM | /SYS]): short imperative title

- what changed, as a person would say it — one short line per point
- 2–5 points (3–5 typical), sized to the change; the why when it isn't obvious
- only go past 5 when the change truly needs it

Tasks: T-NN, …        # only on a multi-task commit (auto-added from a span)
```

- **type** — one of: feat, fix, refactor, docs, chore, test, style, perf.
- **scope** — almost always the **active feature** id, optionally a task or span: `F-007`,
  `F-007/T-02`, `F-007/T-01..T-05`. Use `F-NNN/SYS` for an aspis system/config change routed
  through the system-lead. Omit scope only for true repo-lifecycle commits (init/bootstrap/release) —
  not for ordinary feature work.
- **title** — imperative, lower-case, ≤ 72 chars, no trailing period.
- **body** — required; **2–5 concise single-line points** (3–5 typical), no filler; a point wraps
  to a second line only for a genuinely large change. Real change/notes, not diff narration.

## Compose with the tool, don't hand-format

```
aspis commit <path> [<path> ...] \
  --type feat --task T-02 --title "add the committer agent" \
  --bullet "single git writer, composes per the convention" \
  --bullet "reuses the F-006 validator as the one rule source"
```

- `--task T-01..T-05` for a multi-task commit (the `Tasks:` trailer is auto-added).
- omit `--task` for a feature-wide commit; `--no-scope` for a lifecycle commit.
- The tool self-validates before committing and the `commit-msg` hook validates again,
  so a malformed or non-conventional message never lands.

## Hard rule — no attribution

A commit message must never contain any AI / model / tool / co-author attribution
(`Co-Authored-By`, model names, "generated with", 🤖, …). History reads as fully
human-authored; both the composer and the hook reject any such token.

## Sizing

Keep each commit atomic — one logical change. When a change set mixes concerns
(code + docs + config), split it; see the `commit-splitting` skill.
