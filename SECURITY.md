# Security Policy

ASPIS is a **local, offline-first command-line tool**. It has no network service, sends no
telemetry, and stores no credentials. Its security surface is therefore local: the code it
runs on your machine, the git hooks and lifecycle scripts it installs, and the project files
it reads and writes.

## Supported versions

ASPIS is pre-1.0 (alpha). Security fixes are applied to the latest release only.

| Version | Supported |
|---------|-----------|
| latest  | ✅        |
| older   | ❌        |

## Reporting a vulnerability

**Please do not open a public issue for a security problem.**

Report privately through GitHub's **["Report a vulnerability"](https://github.com/mahmoud-emad-dev/aspis/security/advisories/new)**
button on the repository's *Security* tab (Private Vulnerability Reporting). If that is
unavailable, contact the maintainer privately via their GitHub profile
([@mahmoud-emad-dev](https://github.com/mahmoud-emad-dev)).

When reporting, please include:

- the ASPIS version (`aspis --version`) and your OS (Windows / Linux / WSL),
- a minimal reproduction,
- the impact you observed.

We aim to acknowledge a report within a few days and to coordinate a fix and disclosure
timeline with you.

## What is in scope

- Arbitrary code/command execution triggered by ASPIS beyond its documented behavior.
- A guard that fails to do its job — e.g. the secret-scan or scope/`R-009` protected-path
  hooks letting through what they are meant to block.
- Path traversal or unintended writes outside the project and its `.aspis/` brain.
- Injection via catalog assets, templates, or config that escalates to code execution.

## What is out of scope

- The behavior of the **AI models or runtimes** ASPIS drives (Claude Code, OpenCode, etc.) —
  report those to their respective vendors.
- Risks from **hooks, scripts, or catalog assets you author yourself** — ASPIS executes the
  project's own configured scripts by design; review what you add.
- Findings that require an already-compromised machine or account.

## Hardening notes for users

- ASPIS installs and runs git hooks and lifecycle scripts from `.aspis/scripts/`. Review them
  as you would any code you run.
- The secret-scan guard reduces, but does not guarantee, the absence of committed secrets.
  Keep real secrets out of the repository.
