# F-014 P5 / T-14 — System map: the loop, the roster, the subsystems

A one-page map of how a request flows through ASPIS, what each agent owns, and the deterministic
substrate underneath. Use it to see which agent/subsystem a change touches.

## Entry paths (both first-class)
- **user → project-lead** — the default. The Project Lead is the only primary; it classifies and routes.
- **user → system-lead (direct)** — for system/config changes the user can address the System Lead directly.
- A lead reaches the user/Project Lead back up when it is **stuck** (stop-and-escalate, never guess).

## The roster (3 layers)
- **L1 Project Lead** (primary) — project intelligence + router. Owns classify → route → answer/guide.
- **L2 Leads** (subagents): **planning-lead** (idea→plan), **build-lead** (plan→software),
  **fix-lead** (defect→repair), **reviewer** (independent verdict), **test-lead** (evidence),
  **research-lead** (external knowledge), **system-lead** (the ASPIS machine + config), **bootstrap** (one-time onboarding).
- **L3 Workers** (disposable): **general-builder** (implements a task packet), **project-explorer**
  (read-only context helper), **committer** (the only agent that commits).

## The build loop (the common path)
```
request → project-lead (classify + route)
        → planning-lead → SPEC/PLAN/TASKS  → reviewer (plan-critic)
        → build-lead: per task →
              prestart (aspis preflight) → general-builder (implement) →
              reviewer (verdict) / test-lead (evidence) → committer (aspis commit)
          [checkpoint per task — no multi-hour opaque turn]
        → build-lead verifies acceptance → done
defect at any point → fix-lead (reproduce → root cause → smallest fix → verify) → committer
```

## Each agent's one role → main subsystems it touches
| Agent | One role | Touches |
|---|---|---|
| project-lead | route + project intelligence | context (state/registry/map), routing |
| planning-lead | turn intent into an execution-ready plan | planning scripts, feature dir |
| build-lead | turn a plan into completed software | task packets, review/test/commit orchestration |
| general-builder | implement one task packet | source files in allowed scope |
| reviewer | independent verdict (plans + changes) | diff, tests, acceptance, artifact reports |
| test-lead | objective test evidence | test generation/execution |
| fix-lead | repair the root cause | diff, history, tests |
| research-lead | current external knowledge | web, reference assets |
| system-lead | the ASPIS machine + **config** | catalog assets, config (models/mode/policy via commands) |
| committer | the single commit authority | git (via `aspis commit`) |
| project-explorer | read-only context lookups | registry, code map |
| bootstrap | one-time onboarding, then self-deletes | bootstrap + brain fill |

## Deterministic substrate (under every agent — F-014)
- **Prestart:** `aspis preflight` (clean tree + branch) — every editing agent, step 0.
- **Context:** the `context-ladder` (L1 hot → L4 source) + `aspis context` (one-call fresh hot context).
- **Permissions:** per-agent allowlists, machine-checked (golden test scans bodies *and* skills).
- **Findings (fire-and-forget):** git pre-commit emits → `.aspis/current/findings.json` → next
  session/prestart surfaces (advisory in warn mode) → routed to a fix. No per-tool-call hook.
- **Git authority:** the committer + `aspis commit` (one commit grammar; hooks enforce on commit).
- **Config authority:** the system-lead via `config-management` (models/mode/policy/stack through `aspis` commands).

## Cross-cutting rules
- **Stop-and-escalate:** any agent that hits a blocker above its role stops and reports up — never guesses.
- **Cheapest mechanism first** (R-003): script → tool → hook → agent.
- **Workers never commit** (R-004); **leads don't write product code**; **reviewer is read-only**.
