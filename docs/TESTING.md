# Manual test scenarios — install & usage

The automated suite (`uv run pytest`) covers the engine. This document is the
**human acceptance pass**: prove a real user can install ASPIS and run the loop on
**both Windows and Linux**. Run every scenario on each OS and compare.

Legend: ✅ pass · ⚠️ warn-but-ok · ❌ fix before publish.

---

## S1 — One-command install

**Linux / macOS**
```bash
git clone <repo> && cd aspis
./install.sh
```
**Windows (PowerShell)**
```powershell
git clone <repo>; cd aspis
.\install.ps1
```
Expect: prerequisite checks pass, `uv` installed if missing, `aspis --version` prints
`aspis 0.1.0b1`, `aspis doctor` runs. ✅ when `aspis` resolves from a new shell.

**Check:** `command -v aspis` (Linux) / `(Get-Command aspis).Source` (Windows) →
points at `~/.local/bin/aspis` (Linux) or `%USERPROFILE%\.local\bin\aspis.exe` (Windows).

---

## S2 — `aspis doctor` outside a project
```
aspis doctor
```
Expect: `[ok] python`, `[ok] aspis`, `[ok] git`, `[warn] project not an ASPIS project`,
and `All checks passed.` (exit 0). The project warning is expected (⚠️, not ❌).

**Edge cases:** run with an old Python (should refuse at install), with `git` absent
(doctor warns, still works).

---

## S3 — Initialize a fresh project
```
mkdir demo && cd demo
aspis init --write
```
Expect: `.aspis/` (brain: context, config, rules, templates), plus `.opencode/` and/or
`.claude/` (agents, skills, commands), `AGENTS.md`, and `CLAUDE.md` if Claude is a target.
Then:
```
aspis doctor          # now [ok] project
aspis status
```
✅ when the project is recognized and the runtime dirs contain agents + skills.

---

## S4 — Model detection & assignment
```
aspis models                 # per-runtime tiers, resolved to your connected models
aspis models --available     # the full menu from your connected plans only
aspis models --sync          # writes .aspis/config/agent-models.yaml
```
Open `.aspis/config/agent-models.yaml`: the menu (ranked per capability) is at the top,
every agent pre-assigned a best-fit available model, with a `by_capability` block.
- ✅ only models your plan provides appear.
- Edit a `by_capability` value, run `aspis models` → the change is reflected; a pin to a
  non-available model is flagged `[!] not available`.
- Connect a new provider, run `aspis doctor` → `[warn] connected plans changed — run
  aspis models --sync`.

---

## S5 — Commit flow (single writer + hooks)
```
# inside an initialized project that is a git repo
echo "test" > notes.md
aspis commit notes.md --type docs --title "add notes"
git log -1
```
Expect: the hooks run (pre-commit checks, commit-msg validates the convention,
post-commit refreshes context), the message follows the convention, and **no AI/tool
attribution** is present. ❌ if `-A` staging or attribution appears.

---

## S6 — Cross-platform parity
Run S3–S4 on Windows and on Linux/WSL against the **same** runtime/plan. The rendered
agent files and `aspis models` output should match (modulo line endings). ❌ on any
encoding, path, or line-ending divergence.

---

## S7 — Reinstall / uninstall
```
uv tool install --reinstall .     # after pulling changes
uv tool uninstall aspis           # clean removal
```
Expect: reinstall picks up the new version; uninstall removes the shim and leaves project
files untouched.

---

## Where things live (verify the layout)

| Item | Linux / macOS | Windows |
|---|---|---|
| `aspis` shim | `~/.local/bin/aspis` | `%USERPROFILE%\.local\bin\aspis.exe` |
| Tool environment | uv-managed (`uv tool dir`) | uv-managed (`uv tool dir`) |
| **Global** model config (optional) | `~/.aspis/config/project.yaml` | `%USERPROFILE%\.aspis\config\project.yaml` |
| **Per-project** brain (tracked) | `<project>/.aspis/` | `<project>\.aspis\` |
| Per-project generated state (gitignored) | `<project>/.aspis/state/` | `<project>\.aspis\state\` |
| Detected provider config (read, not written) | `~/.local/share/opencode/auth.json`, `~/.claude/settings.json` | `%USERPROFILE%\.local\share\opencode\auth.json`, `%USERPROFILE%\.claude\settings.json` |
