---
name: byte-parity-checker
description: Prove the catalog regenerates the live runtime byte-for-byte; refuse export on any mismatch.
---

# byte-parity-checker

## Purpose
The catalog is the single source of truth (R-006) — the live runtime is a
generated artifact, not an editable surface. If rendering the catalog
produces bytes that differ from the live runtime, the system is in drift:
exporting would either overwrite intent or accept silent corruption. This
skill proves byte-for-byte that the catalog regenerates exactly what is
live, and refuses export when it cannot.

## When to use
- Immediately before every `aspis export`.
- During system-lead health checks (`aspis system-validate`).
- When a live runtime file is suspected stale, hand-edited, or written
  outside the export pipeline.
- As the gate that the protection engine (F-015) consults before writing.

## Procedure
1. **Catalog self-consistency** — invoke `aspis byte-parity --dry-run` to
   confirm the catalog is internally deterministic and renders without
   error. Stop on any rendering failure; export is impossible anyway.
2. **Hash-compare rendered output to live runtime** — for every agent the
   catalog renders, compute the byte hash of the live runtime file (in
   `.opencode/agents/` or `.claude/agents/`) and the hash of the
   adapter-translated expected output. Pair on translated output, not raw
   catalog.
3. **Classify each file:**
   - **CLEAN** — rendered hash equals live hash.
   - **DRIFT** — hashes differ; the live file is stale or hand-edited.
   - **MISSING** — no live file exists yet (first export of this agent).
4. **On any DRIFT** — refuse export. Emit a per-file report with `file:line`
   evidence and the hash delta for each drifted file. Require either an
   explicit `--force` acknowledgement or R-008 approval for protected
   assets before re-running.
5. **On all CLEAN (or only MISSING)** — parity passes; proceed with
   `aspis export`. MISSING is not drift; it is a first write.

## Outputs
- A per-file parity report classifying each runtime file as CLEAN / DRIFT /
  MISSING, with hash evidence and file paths.
- An overall verdict: **PASS** (safe to export) or **FAIL** (refuse export).
- Exit code 0 on PASS, 1 on FAIL — the gate that `aspis export` checks
  before any file is written.

## Anti-patterns
- Exporting despite DRIFT — silently corrupts the single source of truth
  and makes the next render diverge further.
- Hand-editing live runtime files instead of catalog source — bypasses
  R-006 and guarantees the next parity check fails with destructive
  overwrite risk.
- Skipping the check because "it's just a small change" — small changes
  cause the worst drift (a single permission field is enough).
- Treating MISSING as DRIFT — a first export of a new agent is not drift
  and must not block the pipeline.
