# F-014 P3 / T-12 — Runtime hook-event surface (research)

What OpenCode and Claude Code expose, and which few events P3 should use. P3 **extends** the two
hook files we already ship (`runtime-hooks/opencode/scope-guard.ts`, `runtime-hooks/claude/settings.json`).

## OpenCode (plugin, 25+ lifecycle events)
A plugin is a TS module returning a hooks object; ctx gives `$` (Bun shell), `directory`, `project.worktree`.
- `tool.execute.before` — **runs before a tool; throwing vetoes it.** (we use this for scope-guard)
- `tool.execute.after` — after a tool completes.
- `session.created` — a new session started.
- `session.idle` — the agent finished responding.
- `message.updated` — a message was added/changed.

## Claude Code (~12 core events; settings.json)
Cadences: once/session (`SessionStart`, `SessionEnd`), once/turn (`UserPromptSubmit`, `Stop`,
`StopFailure`), every tool call (`PreToolUse`, `PostToolUse`).
- `SessionStart` — fires per session, **and again on resume** (good for surfacing state).
- `PreToolUse` — before a tool; **can block.** (we use this for scope-guard, matcher `Edit|Write`)
- `PostToolUse` — after a tool (cleanup/format/refresh).
- `UserPromptSubmit` — can inject context / validate the prompt.
- `Stop` / `SessionEnd` — final checks.

## The shared, F-014-aligned trio
| Purpose | OpenCode | Claude | Status |
|---|---|---|---|
| Block out-of-scope edit | `tool.execute.before` | `PreToolUse` (Edit\|Write) | **already shipped** (scope-guard) |
| Surface open findings at start | `session.created` | `SessionStart` | **P3 adds** — run the findings check, print open findings |
| Keep context fresh after edits | `tool.execute.after` | `PostToolUse` | **P3 — optional/data-gated** (perf: don't refresh on every edit) |

## Design constraints (constitution)
- **Capability-checked, not `if runtime==`** — a runtime that lacks an event simply ships no handler for it.
- **Data-driven** — which events are active is config (`hooks.yaml`), degrade to **no-op** when absent.
- **Portable** — interpreter already baked (T-02); keep handlers cheap and cross-platform.

## Recommendation
P3 adds **session-start → surface open findings** on both runtimes (the continuous-validation signal),
keeps the pre-tool scope-guard, and leaves **post-tool context refresh** as a data-gated option
(default off) to avoid per-edit cost. The findings store + emitter (T-11) is the dependency.
