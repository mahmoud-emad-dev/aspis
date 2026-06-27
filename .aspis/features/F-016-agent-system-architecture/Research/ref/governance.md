# Governance Subagent — Agent Specification

> **F-016 reference file.** Target design — the abstract system role. Synthesized
> from system-lead spec §5 (self-modification is governed, not free), §7 (config
> tier model — Tier 2 is governance-only), §8 (hook system — R-008 protected
> paths), §10 (P0 future subagent: `governance`), §12 (OLD ASPS comparison —
> reject LLM governance agent), §13 (Q1: deterministic script is the decided
> answer; Q3: R-008 enforcement needs code, not prose), `system-rules.md` R-008
> (human gate definition), and the `protect.py` / `governance-check` stub work
> in `.aspis/scripts/hooks/`.

---

## 1 · Identity

**The governance subagent is the single writer for protected paths — the
deterministic chokepoint that turns R-008 (human gate) from prose into
mechanism.** Every change to architecture, rules, permissions, security posture,
or model routing must pass through it. It is **not an LLM agent** — it is a
**deterministic script** invoked by pre-commit hooks and runtime tools
(system-lead §13 Q1: "constitution checks are tests, not judgments"). It
records every human approval in an append-only ledger and blocks in-flight
writes that lack a matching, unexpired approval.

### What it IS

- **The only agent permitted to edit `rules/**` and protected paths** —
  system-lead, committer, builder, fixer, reviewer, planner, and every other
  role is **denied** write access to the protected set; only `governance` holds
  the key (system-lead §5, §10)
- **A deterministic enforcement script** — pure code, no model, no reasoning,
  no judgment; same input → same output, every time
- **An R-008 enforcer** — translates the human-gate rule from prompt prose into
  hard code that hooks, runtime guards, and the export pipeline all check
- **An approval ledger writer** — appends every human approval with timestamp,
  approver identity, exact scope (file paths), reason, and optional expiry
- **An intervention handler** — intercepts writes to protected paths at three
  boundaries and blocks any write without a matching active approval
- **An audit trail producer** — every protected-path change is traceable, end
  to end, to a recorded human decision
- **A reader and reporter** — exposes the full approval history via
  `aspis governance audit` for review, compliance, and post-incident analysis

### What it is NOT

- **An LLM agent** — no model, no reasoning, no judgment calls; it does not
  decide *what* to write, only *whether the write is allowed* (system-lead §12
  rejects "LLM governance agent" explicitly; §13 Q1 confirms the decision)
- **A planner / reviewer / builder / committer / fixer** — orthogonal role;
  called by hooks, not by agents
- **A delegator** — leaf responsibility, no `task:` block, no subagents
- **A rule author without approval** — even *governance* cannot write a
  protected path without a matching approval in the ledger; the gate is
  symmetric — the gatekeeper is gated
- **A history rewriter** — the approval ledger is **append-only**; revocations
  set `status: revoked` but never delete entries
- **A bypass** — no `--force`, no environment variable, no override short of a
  new, explicitly scoped approval

### The R-008 invariant

> **Architecture, rules, permissions, security posture, and model-routing
> changes require human approval — never an automated rewrite.**
> *(system-rules.md R-008)*

Governance is the mechanism that makes this invariant hold in code, not just
in prompt text. If a write to a protected path reaches disk, there **must** be
an active approval in the ledger that names that exact path with a matching
scope. There are no exceptions.

### Why deterministic, not LLM

| Concern | LLM agent | Deterministic script |
|---|---|---|
| Predictability | Same input ≠ same output (temperature, drift) | Same input → same output, always |
| Audit | "The model decided" is not auditable | Every decision is reproducible from ledger + diff |
| Failure mode | Silent degradation, hallucinations | Loud: `BLOCK` with the exact reason and the exact command to unblock |
| Cost | Per-call model cost on every protected write | One Python invocation, sub-millisecond |
| Trust | "Trust the model" is the worst possible gate | "Trust the code" — code is reviewable, testable, deterministic |
| Scope | Tempted to "helpfully" broaden scope | Strict equality check on paths; no scope creep |

The decision is locked (system-lead §13 Q1). The LLM form is rejected
explicitly (system-lead §12). Governance is a script.

---

## 2 · Protected Paths

The protected set is the union of: (a) the system rules and policy files that
define how agents operate, (b) the agent and runtime files that define what
agents exist and what they can do, and (c) the state files that record which
agent is currently active. **No agent other than `governance` may write to any
path in this set.**

### The protected set (canonical)

```
# Rules — how the system operates
rules/**
.aspis/rules/**

# Policy / Tier-2 config — system-lead §7 Tier 2 is governance-only
.aspis/config/hooks.yaml
.aspis/config/modes.yaml
.aspis/config/constitution-checks.yaml
.aspis/config/capabilities.yaml
.aspis/config/agent-capabilities.yaml
.aspis/config/commit-convention.yaml

# Defaults — the policy anchor
profiles/defaults.yaml

# Runtime agents and permissions — the agents themselves are governance
.opencode/agents/**
.claude/agents/**
.claude/settings.json

# Permission files anywhere in the tree
**/permissions*.yaml

# Active-feature state — who is in charge right now
.aspis/current/active_feature.json
```

### The matching rule

A path is protected if it matches **any** glob in the protected set, evaluated
with `pathlib.PurePath.match()` semantics. Symlinks are resolved to their
target before matching. Case-sensitive on Linux/macOS, case-insensitive on
Windows is **not** normalised away — `Rules/**` and `rules/**` are distinct
patterns and both are protected if both are listed.

### What the set does NOT include

- Product source code (`src/**`, product tests, docs for the product)
- `.aspis/features/**` — feature planning and research; belongs to
  project-lead / planning-lead
- `.aspis/context/**` and `.aspis/index/**` — generated brain state;
  system-lead regenerates, not governance
- The approval ledger itself — owned by governance; not in the protected set
  (the gatekeeper is gated by its own write protocol, not by the path matcher)

### Reading the actual set

The protected set is the source of truth. It is loaded at governance startup
from `.aspis/config/hooks.yaml` if present (the `protected_paths:` key); the
canonical set above is the fallback used when the file is missing or the key
is absent. The set is itself **Tier 2 policy-locked** — adding or removing a
protected path is itself an R-008-governed change.

---

## 3 · R-008 Human Approval Workflow

The end-to-end flow from "I want to change a rule" to "the change is on disk
and auditable" is seven steps. Every step is deterministic except step 3
(human decision) and step 4 (human signs the scope).

```
1. REQUEST    — agent or human declares intent to write a protected path
2. INTERCEPT  — hook or runtime guard catches the write
3. APPROVE    — human approves with exact scope (file paths + reason)
4. RECORD     — approval appended to the ledger
5. CHECK      — intervention handler verifies ledger entry against the write
6. WRITE      — file change is allowed through
7. AUDIT      — every approval is queryable, every write traceable
```

### Step-by-step

**1. REQUEST.** A human (most often system-lead on behalf of a feature) or, in
rare cases, a builder that has been *explicitly* delegated the request step
(not the write — the request) calls:

```bash
aspis governance request \
  --path .aspis/rules/system-rules.md \
  --reason "F-016: add governance subagent reference spec"
```

The request is **passive** — it does not approve anything, does not write
anything, does not change state. It is a structured intent declaration that
the human will reference when approving.

**2. INTERCEPT.** When the actual write attempt reaches a protected path, the
intervention handler fires (see §5). The handler asks: "is there an active
approval in the ledger that names this exact path with a matching scope?" If
yes → allow and log. If no → block.

**3. APPROVE.** The human runs:

```bash
aspis governance approve \
  --paths .aspis/rules/system-rules.md \
  --reason "F-016: add governance subagent reference spec" \
  --approver human-identifier
```

The human signs the approval with their identity and the exact paths. Scope
is a **set of file paths**, not a glob — paths are recorded literally, and
matching is exact. A request for `rules/**` does not implicitly approve
`rules/agent-rules.md`; the human must name each path or explicitly pass the
glob they want to allow (and glob approvals are a distinct, more dangerous
class that requires the `--glob-approval` flag).

**4. RECORD.** The approval is appended to the ledger (see §4) with a unique
id, the current UTC timestamp, the approver identity, the scope (paths +
reason), the optional expiry, and `status: active`. The ledger is
**append-only** — entries are never edited; revocations append a new entry
that flips the status.

**5. CHECK.** On every intercepted write, the handler loads the ledger,
filters to entries with `status: active` and (if set) `expiry > now`, and
checks for an exact-match path. The check is:

```
exists(approval in ledger
       where approval.status == 'active'
         and (approval.expiry is null or approval.expiry > now)
         and approval.scope.paths ⊇ {path_being_written})
```

**6. WRITE.** The write proceeds only if step 5 returns true. The handler
emits a structured log entry (`AUDIT: APPROVED write to <path> by <approver>,
approval-id <id>`) to the run log, the ledger's `applied:` list, and the
trace spine (when it exists; the field is reserved today).

**7. AUDIT.** Every approval and every approved write is queryable:

```bash
aspis governance audit                      # all entries
aspis governance audit --since 2026-06-01   # date filter
aspis governance audit --path .aspis/rules/  # path filter
aspis governance audit --approver alice     # approver filter
```

### What the workflow forbids

- **No silent approvals** — every approval requires an interactive human
  command; there is no auto-approve path
- **No pre-baked blanket approvals** — the closest equivalent is a *narrow*
  approval that names a specific file with an optional expiry; "approve
  everything forever" is not a valid scope
- **No retroactive approvals** — an approval is checked **at write time**;
  approving after a write is not "approval", it is documentation of an
  unsanctioned change, and the audit trail will reflect that ordering
- **No model-mediated approvals** — the human signs; the LLM cannot

---

## 4 · Approval Ledger Format

The ledger is a single YAML file in append-only mode. It is the durable
record of every R-008 decision.

### Location

```
.aspis/state/approval-ledger.yaml
```

Alternate location under consideration: `.aspis/config/approval-ledger.yaml`.
The `state/` location is preferred because the ledger is **operational data**
generated by the system, not configuration authored by humans; humans
**query** the ledger, they do not edit it directly. The location is fixed
today and may move only via an R-008-governed change.

### Schema

```yaml
# .aspis/state/approval-ledger.yaml
# Append-only ledger of R-008 human approvals. Generated by `aspis governance
# approve`; queried by `aspis governance audit` and the intervention handler.
# NEVER hand-edit. NEVER delete entries. Revoke via `aspis governance revoke`.
---
- id: APRV-001
  timestamp: 2026-06-27T12:00:00Z         # ISO 8601 UTC, set at approval time
  approver: human-identifier              # who signed; e.g. "alice" or "team:platform"
  scope:
    paths:                                 # exact paths (or explicit globs with --glob-approval)
      - .aspis/rules/system-rules.md
    reason: "F-016 governance spec update"  # human-supplied; required, non-empty
  expiry: null                             # null = permanent until revoked; or ISO 8601 UTC
  status: active                           # active | revoked | expired
  applied:                                 # writes that used this approval
    - timestamp: 2026-06-27T12:05:14Z
      path: .aspis/rules/system-rules.md
      actor: system-lead                   # who/what triggered the write
      run-id: RUN-2026-06-27-001           # optional; ties to trace spine
  revocation:
    revoked-at: null                       # set if status=revoked
    revoked-by: null
    reason: null
```

### Field reference

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Unique approval id, format `APRV-NNN` (zero-padded, monotonic) |
| `timestamp` | ISO 8601 UTC | yes | When the approval was recorded |
| `approver` | string | yes | Identity of the human who signed; not a free-text label, must be a known handle |
| `scope.paths` | list of strings | yes | Exact file paths (or explicit globs, see below) being approved |
| `scope.reason` | string | yes | Human-supplied justification; non-empty, max 500 chars |
| `expiry` | ISO 8601 UTC or null | yes | `null` = permanent until revoked; else auto-expires at this timestamp |
| `status` | enum | yes | `active` (default) \| `revoked` \| `expired` |
| `applied` | list | yes | Audit of every write that consumed this approval (see below) |
| `revocation` | object | yes | Set when `status` flips to `revoked`; null while active |

### Glob approvals (the dangerous extension)

A path entry in `scope.paths` may be a **glob** (`rules/**`,
`.aspis/config/hooks.yaml`) only when the approval was created with the
`--glob-approval` flag. The ledger records `glob-approved: true` on the entry
when this flag is used. Glob approvals are a deliberate footgun: they widen
the blast radius of a single decision and are intended for **bulk governance
operations** (e.g. "approve the entire F-016 rule set update"), not for
routine single-file changes. The CLI warns and asks for confirmation when
`--glob-approval` is used.

### Append-only invariant

The ledger file is **never edited in place**. Every state change is a new
entry: a revocation is a new entry that flips an existing entry's `status` to
`revoked`; an expiry is detected at check time, not by mutating the file.
This means a full audit history is always available, and a crash mid-write
cannot corrupt prior decisions.

### Concurrency

The ledger is protected by a process-level file lock
(`fcntl.flock` / `msvcrt.locking`) at write time. Two simultaneous approvals
serialise; the second waits for the first to release. A crashed lock is
detected by the `stale-lock` check on next write (a lock older than 60
seconds with no live process is treated as stale and broken).

### Retention

The ledger has **no retention policy** — entries are kept for the life of
the project. Archival is the responsibility of the project's normal backup
process, not of governance.

---

## 5 · Intervention Handler

The intervention handler is the runtime side of governance: the part that
actually blocks an in-flight write to a protected path. It runs at **three
boundaries**, in this order of authority:

### Boundary 1 — Runtime tool boundary (Edit / Write)

The agent runtime (Claude Code `PreToolUse`, OpenCode plugin layer) inspects
every `Edit` and `Write` call against the protected set. If the target path
matches, the tool is **denied at the runtime layer** unless a matching
approval exists in the ledger.

```
Agent calls Edit(path=".aspis/rules/system-rules.md", ...)
  → Runtime guard: "is .aspis/rules/system-rules.md protected? yes"
  → Runtime guard: "is there an active approval for this exact path? no"
  → Runtime guard: DENY with reason
  → Agent receives: "Protected path .aspis/rules/system-rules.md requires
                     R-008 human approval. Use:
                     aspis governance request --path <path> --reason <reason>"
  → Agent reports blocker to the lead; lead either gets approval or reroutes
```

This is the **earliest** and most effective boundary — the write never even
attempts to hit the filesystem.

### Boundary 2 — Pre-commit hook boundary

Git's `pre-commit` hook runs `protect.py` (or equivalent) over the staged
diff. Any staged change to a protected path is checked against the ledger. If
unapproved, the commit is **blocked** with a non-zero exit and the same
message as boundary 1.

This is the **safety net** for boundary 1 — a misconfigured runtime, a
manual `git commit` outside the agent loop, or a boundary-1 bypass all land
here. The pre-commit hook runs in `enforcement: block` mode (system-lead §8
target state; current default is `warn` and will flip to `block` once the
runtime boundary is proven).

### Boundary 3 — OS sandbox boundary (future)

A future OS-level sandbox (e.g. macOS App Sandbox, Linux landlock) that
physically denies non-governance processes write access to the protected set.
This is the **last line of defence** and the only one that cannot be bypassed
by a misconfigured runtime or a skipped hook. **Not built today**; tracked in
the roadmap (system-lead §11 M3 trace spine is adjacent infrastructure).

### On interception — the exact behaviour

For every intercepted write, the handler:

1. Resolves the target path (symlinks → real path)
2. Tests the path against the protected set
3. If not protected → return `ALLOW` immediately, no further work
4. If protected → load the ledger, filter to `status: active` and not expired
5. Test for an exact-match path (or a matching glob, if glob-approval)
6. If a match exists → return `ALLOW` and **append to the matching entry's
   `applied:` list** (the audit record of this specific write)
7. If no match → return `BLOCK` with the canonical message:

```
Protected path <path> requires R-008 human approval.
  Step 1: aspis governance request --path <path> --reason "<reason>"
  Step 2: aspis governance approve   --paths <path> --reason "<reason>" --approver <you>
  Step 3: re-run your command.
No override is available. Contact your system-lead if you believe this is wrong.
```

### What the handler does NOT do

- It does not **ask** for approval interactively — the human must run the
  `aspis governance` command; the handler is a gate, not a prompt
- It does not **modify** the protected path — it only allows or denies the
  caller's write
- It does not **read the contents** of the write — the gate is on the path,
  not the content (a separate content-conformance check, if any, is a
  different concern; see system-lead §12 "ADD" list)
- It does not **cache decisions** across processes — every write checks the
  ledger fresh; a revoked approval is effective on the next check, not
  delayed

---

## 6 · CLI Interface

The governance subagent exposes a single CLI namespace: `aspis governance`.
Every verb is deterministic, every output is machine-readable (default) and
human-readable (with `--pretty`). The CLI is the only sanctioned way to
interact with the ledger outside the handler.

### `aspis governance request`

Declare intent to write a protected path. **Passive** — does not approve, does
not write.

```
aspis governance request --path <path> [--reason <reason>]

  --path <path>     (required, repeatable)  the protected path(s) you intend to write
  --reason <text>   (optional)              human-readable reason; prompted if absent
  --pretty          (flag)                  human-readable output (default: machine YAML)

Exit 0 on success. Prints a request id and the exact approve command to run.
Does not modify the ledger.
```

### `aspis governance approve`

Record a human approval. **This is the gate** — running this command is the
human signing off on the named scope.

```
aspis governance approve --paths <paths> --reason <reason> --approver <id>
                          [--expiry <iso8601>] [--glob-approval]

  --paths <paths>   (required, repeatable)  the exact paths being approved
  --reason <text>   (required)              human-readable justification (max 500 chars)
  --approver <id>   (required)              the human's identity handle
  --expiry <iso>    (optional)              ISO 8601 UTC expiry; default = permanent
  --glob-approval   (flag)                  allow glob patterns in --paths (warns + confirms)
  --pretty          (flag)                  human-readable output (default: machine YAML)

Exit 0 on success. Appends an entry to the ledger; prints the new APRV-NNN id.
Exit 2 on validation error (empty paths, missing approver, bad ISO 8601, etc.).
```

### `aspis governance audit`

Query the ledger.

```
aspis governance audit [--since <iso>] [--until <iso>] [--path <glob>]
                       [--approver <id>] [--status <active|revoked|expired>]
                       [--pretty]

  --since <iso>     (optional)  filter to approvals created at/after this timestamp
  --until <iso>     (optional)  filter to approvals created at/before this timestamp
  --path <glob>     (optional, repeatable)  filter to approvals whose scope touches this path
  --approver <id>   (optional)  filter to approvals signed by this approver
  --status <s>      (optional)  filter by status (default: all)
  --pretty          (flag)      human-readable table output (default: machine YAML)

Exit 0 always. Prints matching ledger entries.
```

### `aspis governance revoke`

Revoke a previously recorded approval. **Append-only** — the original entry
remains; a new entry flips its status to `revoked`.

```
aspis governance revoke --id <APRV-NNN> --reason <reason> [--approver <id>]

  --id <APRV-NNN>   (required)  the approval id to revoke
  --reason <text>   (required)  why the approval is being revoked
  --approver <id>   (optional)  who is revoking; defaults to the original approver
  --pretty          (flag)      human-readable output

Exit 0 on success. Appends a revocation record and flips the entry's status.
Exit 3 if the approval is already revoked or does not exist.
```

### `aspis governance check` (diagnostic)

Diagnostic — simulate a write to a protected path and report whether it would
be allowed. **Does not write, does not modify the ledger.** Useful for
debugging "why is my write blocked?" without an interactive trial-and-error
loop.

```
aspis governance check --path <path> [--pretty]

Exit 0 = the write would be allowed (a matching active approval exists).
Exit 4 = the write would be blocked (no matching active approval).
Exit 5 = the path is not in the protected set (no check needed).
```

### `aspis governance ledger` (operational)

Operational — show ledger health, size, last-write timestamp, lock state.
Used by `aspis doctor` and `aspis governance-check` (system-lead §9).

```
aspis governance ledger [--pretty]

Exit 0 always. Prints ledger path, entry count, oldest/newest timestamps,
and current lock state.
```

### Error model

All `aspis governance` commands share a consistent exit-code model:

| Exit | Meaning |
|---|---|
| 0 | Success |
| 2 | Validation error (bad input, missing required flag) |
| 3 | State error (approval not found, already revoked, ledger corrupt) |
| 4 | Permission denied (path protected and no matching approval, or non-governance caller tried to mutate the ledger) |
| 5 | Not applicable (path not in protected set, for `check`) |
| 6 | Internal error (ledger I/O failure, lock timeout, schema violation) |

Non-zero exits always print a one-line machine-readable error and (with
`--pretty`) a human-readable explanation.

### Authorship of the CLI

The CLI is the governance subagent. It is the **only** code permitted to
write the ledger, and it is the **only** code that should be calling the
ledger's read API from outside the intervention handler. Other tools
(`aspis doctor`, `aspis governance-check`, hooks) **read** the ledger via
`aspis governance audit` / `aspis governance ledger` — they do not touch
the file directly. This keeps the ledger's append-only invariant enforceable
in one place.

---

## 7 · Acceptance Criteria

- [ ] **Protected paths are complete and match `hooks.yaml`** — the canonical
      set in §2 is the fallback; when `.aspis/config/hooks.yaml` exists, the
      set is loaded from it; the two agree
- [ ] **R-008 workflow is specified** — the seven-step request → intercept →
      approve → record → check → write → audit flow is documented end to end
      (§3)
- [ ] **Approval ledger format is fully defined** — every field in §4 is
      typed, required/optional is marked, and the append-only invariant is
      stated
- [ ] **Intervention handler covers all three boundaries** — runtime tool
      (Edit/Write), pre-commit hook, and the future OS-sandbox boundary are
      all specified (§5); the exact block message and behaviour are nailed
      down
- [ ] **CLI verbs are specified with full signatures** — `request`, `approve`,
      `audit`, `revoke`, `check`, and `ledger` all have argument lists, exit
      codes, and behaviour (§6)
- [ ] **Governance is a deterministic script, not an LLM agent** — stated in
      §1, justified in the "Why deterministic" table, and consistent with
      system-lead §12 (reject) and §13 Q1 (decision)
- [ ] **No overlap with committer** — governance governs **rules** (R-008
      territory); committer commits **code** (R-004 territory). The two
      agents touch disjoint surfaces: governance owns the protected-path
      write, committer owns the `git commit` invocation that lands it
- [ ] **Audit trail is complete and traceable** — every protected-path
      change has a recorded approval (id, timestamp, approver, scope, reason)
      and every approved write appends to the `applied:` list (§4); nothing
      reaches disk without a paper trail
- [ ] **No LLM is in the loop on R-008 decisions** — the human signs
      `aspis governance approve`; no model mediates, suggests, or auto-fills
      the approver or the scope
- [ ] **Glob approvals are explicitly dangerous** — the `--glob-approval`
      flag exists, warns, and confirms; the ledger records `glob-approved:
      true`; the surface is opt-in, not default
- [ ] **Append-only ledger** — no code path edits or deletes ledger entries;
      revocations are new entries; expiry is detected at check time, not by
      mutation
- [ ] **The gatekeeper is gated** — even governance's own writes to the
      protected set are subject to an active approval; the symmetry holds
- [ ] **No `--force`, no env-var override, no back door** — the only way to
      write a protected path is a matching active approval; documented
      explicitly in §1 and §3
- [ ] **The 6 governance subagent requirements are present** — P0 subagent in
      system-lead §10 is one; the four build blocks (governance subagent,
      approval ledger, intervention handler, CLI) are all in this spec
- [ ] **The `aspis governance-check` validation gate is named** — system-lead
      §9 lists it as "not built"; this spec is the design it must satisfy
- [ ] **Consistent with R-008 verbatim** — the human-gate definition in §1 is
      quoted from `system-rules.md` lines 101–103; no reinterpretation
- [ ] **F-016 / system-lead citations** — every design choice cites its
      source (system-lead §5, §7, §8, §10, §12, §13; system-rules.md R-008)

---

*Built from: system-lead spec §1 (the prime directive — governance enforcement
is one of four system-health factors), §5 (self-modification is governed, not
free — the `governance` subagent is named as the only path to `rules/**` and
`profiles/defaults.yaml`), §7 (Tier 2 config tier model — `hooks.yaml`,
`modes.yaml`, `constitution-checks.yaml`, `capabilities.yaml`,
`agent-capabilities.yaml`, `commit-convention.yaml` are all governance-only),
§8 (hook system — pre-commit "protected paths (R-008)", runtime guard
"per-tool scope + protected paths", target `enforcement: block`), §10 (P0
future subagent: `governance`), §12 OLD ASPS comparison (reject "LLM
governance agent — use deterministic script instead"; ADD "governance
subagent (R-008 enforcement in code)", "approval ledger", "intervention
handler"), §13 open design questions (Q1 decided: deterministic script,
"constitution checks are tests, not judgments"; Q3 P0: "R-008 enforcement:
prompt rule only — needs code"), `system-rules.md` R-008 (human gate
definition, lines 101–103), F-015 protection engine (the byte-hash
"PROTECT" decision class is the runtime analogue of the governance block),
and the `protect.py` / `governance-check` stubs under `.aspis/scripts/hooks/`.*
