# L4 Hook Configuration — BLOCKED

**Status:** BLOCKED  
**Blocker:** Awaiting R-008 owner approval (REQ-F-018-001)  
**Date:** 2026-06-28  
**Feature:** F-018 L4 — Hardening

---

## What's blocked

- **T-046:** Apply PreToolUse hook to `.claude/settings.json` — cannot proceed without owner approval per R-008 governance gate.

## What's ready

The 3 PreToolUse hook modules are authored and exist in the catalog:

| Module | Path | Purpose |
|--------|------|---------|
| `deny_floor.py` | `.aspis/scripts/hooks/deny_floor.py` | Universal deny rules enforcement (git commit/push blocks) |
| `pretool_secret_scan.py` | `.aspis/scripts/hooks/pretool_secret_scan.py` | Secret/key leak detection before tool use |
| `protected_path.py` | `.aspis/scripts/hooks/protected_path.py` | R-008 protected-path write prevention |

The governance request **REQ-F-018-001** has been filed at `.aspis/state/approval-ledger.yaml` with `status: pending`.

## What the owner must do (post-approval)

### Step 1: Approve the governance request

```bash
python -m src.aspis.commands.governance approve REQ-F-018-001 --approver owner
```

Or manually update `.aspis/state/approval-ledger.yaml`:
```yaml
- id: REQ-F-018-001
  status: active   # was: pending
```

### Step 2: Add PreToolUse hook to `.claude/settings.json`

Edit `.claude/settings.json` to include:

```json
{
  "preToolUseHooks": [
    {
      "path": ".aspis/scripts/hooks/deny_floor.py",
      "enforcement": "warn"
    },
    {
      "path": ".aspis/scripts/hooks/pretool_secret_scan.py",
      "enforcement": "block"
    },
    {
      "path": ".aspis/scripts/hooks/protected_path.py",
      "enforcement": "block"
    }
  ]
}
```

**Configuration rationale:**
- `deny_floor.py` — `warn` (non-blocking; the allow-list in agent bodies already enforces this)
- `pretool_secret_scan.py` — `block` (immediate stop on secret leak)
- `protected_path.py` — `block` (R-008 enforcement; no write without governance approval)

### Step 3: Verify

```bash
python .aspis/scripts/hooks/deny_floor.py --agent build-lead --tool "read: file"
# Expected: ALLOW
```

### Step 4: Mark T-046 complete

After applying the hook configuration and verifying, update this report status from BLOCKED to COMPLETE.

---

## Cross-references

- Governance request: `.aspis/state/approval-ledger.yaml` → `REQ-F-018-001`
- R-008 rule: `.aspis/rules/system-rules.md` §R-008
- Feature spec: `.aspis/features/F-018-complete-asset-set/SPEC.md` §L4
- Task spec: `.aspis/features/F-018-complete-asset-set/TASKS.md` → T-045, T-046
