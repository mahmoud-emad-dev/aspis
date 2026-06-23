# F-014 P1 / T-04 — Per-agent permission audit

Cross-reference of each agent's **bash allowlist** vs the **commands its instructions tell it
to run**. A gap = "told to do X, blocked from X" (the committer-class bug). 12 agents.

## Agents with `bash "*": allow` — no gap possible (broad)
`fix-lead`, `general-builder`, `test-lead`, `system-lead` — all allow any bash (only
`git commit*`/`git push*` denied). Their `aspis …`/script commands all run. ✓

## Agents with a restrictive allowlist (`"*": deny` + specific allows)
| Agent | Commands in its instructions | In allowlist? | Verdict |
|---|---|---|---|
| **committer** | `aspis commit` | yes (T-01 fixed) | ✓ |
| **project-lead** | `aspis bootstrap --check`, `aspis status`, `python .aspis/scripts/context/*` | yes (+both python/python3) | ✓ |
| **project-explorer** | `python .aspis/scripts/context/build_code_map.py` | yes (+both python/python3) | ✓ |
| **bootstrap** | `aspis bootstrap`, `aspis commit`, `aspis doctor`, `python .aspis/scripts/context/*` | yes (`aspis *` + both python) | ✓ |
| **build-lead** | **`aspis artifact build/feature`**, `python3 .aspis/scripts/{context,planning}/*` | **NO `aspis artifact*`** | ❌ **gap** |
| **reviewer** | **`aspis artifact review/test`**, `python3 .aspis/scripts/{context,planning}/*` | **NO `aspis artifact*`** | ❌ **gap** |
| **planning-lead** | `python3 .aspis/scripts/{context,planning}/*` (feature_scaffold, task_compile, prereq_validate) | scripts yes | ⚠ python-only |

## Findings

**F-A — `aspis artifact*` denied (hard bug).** `build-lead` and `reviewer` are told to run
`aspis artifact …` to stamp their reports, but it is **not** in their allowlist → denied by the
`"*": deny` default. Same failure mode as the committer: the agent will fall back to a hand-invented
report format (which the instruction explicitly forbids) or fail. **Fix:** add `"aspis artifact*": allow`.

**F-B — `python3`-only is Windows-fragile (portability).** `build-lead`, `reviewer`, and
`planning-lead` allow only `python3 .aspis/scripts/…`, not `python …`. On Windows `python3` is often
absent (the exact T-02 bug), and `python` is then *denied* — so these agents can't run their own
context/planning scripts. `project-lead`/`project-explorer`/`bootstrap` already allow **both**.
**Fix:** allow both `python` and `python3` for the same script dirs (consistency + portability).

## Proposed T-05 edits (permission-only; blanket-approved for F-014)
- `build-lead`: + `"aspis artifact*": allow`; + `"python .aspis/scripts/context/*"`, `"python .aspis/scripts/planning/*"`.
- `reviewer`: + `"aspis artifact*": allow`; + `"python .aspis/scripts/context/*"`, `"python .aspis/scripts/planning/*"`.
- `planning-lead`: + `"python .aspis/scripts/context/*"`, `"python .aspis/scripts/planning/*"`.
- No change to the four `"*": allow` agents or the three already-correct restrictive agents.

## T-06 — golden test (prevents recurrence)
A test that parses each agent: every `aspis <sub>` / `python[3] .aspis/scripts/…` token in the body
must match an allow pattern in that agent's bash allowlist. This would have caught the committer bug,
F-A, and F-B mechanically — turning the whole class from prose-asserted to machine-checked.
