---
name: security-review
description: Apply OWASP top 10 and core security checks (injection, authz, secrets, exposure) to a change before issuing a review verdict.
---

# security-review

## Purpose
Evaluate a code change for security vulnerabilities before the reviewer issues a
verdict. Covers the OWASP top 10 categories plus ASPIS-specific concerns (secret
leakage, permission escalation, protected-path access). Security findings are
always at least HIGH severity; a CRITICAL security finding is an automatic
REJECTED verdict.

## When to use
- During the reviewer's Evaluate step, under the Security dimension (dimension 6
  of 9).
- When a change touches authentication, authorization, input handling, data
  storage, or any protected path.
- On any V3 (cross-cutting) or V4 (critical) task packet.
- When the reviewer's mode is `production` — the Security dimension is Full.

## Procedure
1. **Classify the change's security surface:**
   - **Auth/Authz**: login, tokens, sessions, permission checks, role changes
   - **Input**: user input, file uploads, API parameters, command-line args
   - **Output**: rendered HTML, generated files, shell commands built from input
   - **Data**: secrets, PII, credentials, database queries, file paths
   - **Config**: permission blocks, allowlists, deny rules, mode settings
   - **None**: the change has no security surface — note this and skip deep checks
2. **Walk the OWASP top 10 relevant categories:**
   - **Injection** (SQL, OS command, path traversal): is user input concatenated
     into queries, commands, or paths?
   - **Broken Authentication**: are session tokens predictable? Is auth bypassed?
   - **Sensitive Data Exposure**: are secrets in logs, diffs, or plaintext files?
   - **XML External Entities (XXE)**: is XML parsed unsafely? (rare in Python)
   - **Broken Access Control**: does the change weaken or bypass a permission check?
   - **Security Misconfiguration**: are defaults insecure? Is debug mode on?
   - **Cross-Site Scripting (XSS)**: is output unsanitized? (web stacks)
   - **Insecure Deserialization**: is pickle/yaml.load used on untrusted data?
   - **Using Components with Known Vulnerabilities**: are pinned versions stale?
   - **Insufficient Logging & Monitoring**: are security events logged?
3. **Check ASPIS-specific concerns:**
   - **Secret leakage**: scan the diff for hardcoded keys, tokens, passwords.
     Use `git diff` + manual review (no secret-scanning tool assumed).
   - **Permission escalation**: does the change grant a new tool or widen a
     bash allowlist? Does it remove a deny rule?
   - **Protected-path access**: does the change touch `.opencode/`, `.claude/`,
     `rules/**`, `**/permissions*.yaml`, or `.aspis/current/active_feature.json`?
     If yes and no R-008 approval exists → CRITICAL finding.
   - **Model-tier bypass**: does the change let a cheap model handle security-
     sensitive work?
4. **Record findings** in the standard format: `file:line — what's wrong — why
   — severity — fix — evidence`.
5. **Fold into the verdict**: any CRITICAL security finding → REJECTED. Any HIGH
   security finding → CHANGES-REQUIRED.

## Outputs
- Security findings with file:line evidence, folded into the review report.
- A security-surface classification (even if "none") so the reviewer documents
  that security was considered.

## Anti-patterns
- Skipping security review because "this is just a small change" — small changes
  introduce big vulnerabilities (e.g. one line that opens a path traversal).
- Reviewing security on a change the reviewer doesn't understand — delegate to
  research-lead for current OWASP/stack-specific guidance if needed.
- Treating every input as a vulnerability — classify the surface first; a string
  constant is not an injection vector.
- Approving a change with a MEDIUM security finding without explicit deferral —
  security debt compounds.
