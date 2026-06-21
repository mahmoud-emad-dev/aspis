# Reference — Runtime model & provider detection (OpenCode, Claude Code)

**Topic:** How ASPIS can programmatically detect, per machine, which runtimes/providers/models
a user has — the foundation for F-010 (model selection system).
**Captured:** 2026-06-21. **Provenance:** OpenCode `sst/opencode` `dev` branch source + `opencode.ai/docs`;
Claude Code `code.claude.com/docs` + `platform.claude.com/docs`. Docs are live-updated with no version
pin — **re-confirm before relying on an exact string.** Each claim tagged VERIFIED / UNVERIFIED.

> This is a distilled reference, not a raw dump. It exists so F-010 (and future runtime adapters)
> never re-research detection mechanics. Update in place rather than duplicating.

---

## Part A — OpenCode

### A1 — `auth.json` (connected providers/credentials)

**Path** (VERIFIED, `packages/core/src/global.ts` + `xdg-basedir`):
`<XDG_DATA_HOME or ~/.local/share>/opencode/auth.json`

| OS | Path |
|---|---|
| Linux | `~/.local/share/opencode/auth.json` |
| macOS | `~/.local/share/opencode/auth.json` (NOT `~/Library/...`) |
| Windows (native) | `%USERPROFILE%\.local\share\opencode\auth.json` |
| Windows WSL | `~/.local/share/opencode/auth.json` (Linux path inside WSL) |

**Portability landmine (VERIFIED, issue #8235):** `xdg-basedir` is Linux-style — on Windows it uses
`%USERPROFILE%\.local\share`, **NOT `%APPDATA%`**. The config docs erroneously say `%APPDATA%` (that's a
third-party plugin). Resolve the real path on any machine with **`opencode debug paths`** — authoritative.

**Schema** (VERIFIED, `packages/opencode/src/auth/index.ts`): JSON object `Record<providerID, Info>`,
`Info` is a discriminated union on `type`:
```json
{
  "anthropic":  { "type": "api",   "key": "sk-ant-...", "metadata": {} },
  "openai":     { "type": "oauth", "refresh": "...", "access": "...", "expires": 1750000000000,
                  "accountId": "optional", "enterpriseUrl": "optional" },
  "opencode-go":{ "type": "api",   "key": "..." }
}
```
Keys = provider string IDs (`anthropic`, `openai`, `opencode`, `opencode-go`, ...). File mode `0o600`.
Env `OPENCODE_AUTH_CONTENT` injects the whole file's contents (bypasses disk).

### A2 — Listing available models (VERIFIED, `cli/cmd/models.ts`, `core/src/models-dev.ts`)

- Command: `opencode models [provider] [--verbose] [--refresh]`. **No `--json` flag.**
- Default output: one `providerID/modelID` per line, plain text. OpenCode providers first, then alpha.
- `--verbose`: after each line, emits `JSON.stringify(model, null, 2)` — full **models.dev** metadata
  (context window, pricing, capability flags `tool_call` / `reasoning` / `image_input`, ...).
  → **Objective model facts come from here; we don't hand-author context/pricing/caps.**
- `--refresh`: re-fetch `https://models.dev/api.json` (else 5-min cache; bg refresh 60 min).
- `opencode models anthropic` scopes to one provider (`"Provider not found"` if unknown).
- Catalog source: models.dev (override `OPENCODE_MODELS_URL`; skip with `OPENCODE_DISABLE_MODELS_FETCH`).
- UNVERIFIED whether listing is auth-gated; appears catalog-driven (lists known models regardless of auth).

### A3 — Config file (VERIFIED, `opencode.ai/docs/config`, `opencode.ai/config.json`)

- File: `opencode.json` / `opencode.jsonc`. Global: `~/.config/opencode/opencode.json`
  (Windows per source `%USERPROFILE%\.config\...`; docs claim `%APPDATA%` — CONFLICTED, use `opencode debug paths`).
- Project: `opencode.json` at the project/git root. Overrides: `OPENCODE_CONFIG_DIR`, `OPENCODE_CONFIG`.
- Key fields: `model`, `small_model`, `default_agent`, `provider.<id>` (custom providers via `npm` adapter +
  `options.apiKey`/`baseURL`, `whitelist`/`blacklist`), `agent.<name>.{model,temperature,prompt,mode,...}`.
- Precedence (low→high): remote `.well-known/opencode` → global → `OPENCODE_CONFIG` → project → `.opencode/`
  → `OPENCODE_CONFIG_CONTENT` → managed system → macOS MDM. Merged, not replaced.

### A4 — Validating a credential works (VERIFIED — no dedicated command)

- No `--check` / `auth status`. `opencode providers list` shows stored creds + type (`api`/`oauth`) but does
  **not** validate against the provider API. Only real validation = a live call:
  `opencode run -m <provider/model> "ping" --format json`.

### A5 — Plan / quota / rate-limit (VERIFIED — not natively exposed)

- No CLI exposes plan, quota, or rate limits. `opencode stats` = local token usage/cost only.
- OpenCode Zen (curated models) and OpenCode Go (low-cost subscription) are ordinary API-key providers in
  `auth.json` (IDs `opencode` / `opencode-go`); no quota surfaced.
- → **Scope detection to "which providers/credentials are connected," not plan limits.** Quota-aware
  routing would need third-party provider APIs → later feature, not core.

### A6 — Per-agent model assignment (VERIFIED, `opencode.ai/docs/agents`, `cli/cmd/run.ts`)

- Agent markdown frontmatter (`~/.config/opencode/agents/<name>.md` or `.opencode/agents/<name>.md`):
  `model: <provider/model>` (e.g. `anthropic/claude-sonnet-4-5`, `opencode-go/minimax-m3`).
- `opencode.json` `agent.<name>.model` — same format. Global default = top-level `model` (+ `small_model`).
- Per-run override: `opencode run -m <provider/model> "..."` (`--model`/`-m`, "format of provider/model").
  Agent select: `opencode run --agent <name>`.
- **Model string is always `provider_id/model_id`** (local providers' model_id may itself contain slashes).

### OpenCode env vars for detection
`XDG_DATA_HOME`, `XDG_CONFIG_HOME`, `OPENCODE_CONFIG_DIR`, `OPENCODE_CONFIG`, `OPENCODE_AUTH_CONTENT`,
`OPENCODE_MODELS_URL`, `OPENCODE_DISABLE_MODELS_FETCH`. **`opencode debug paths`** = per-machine path truth.

---

## Part B — Claude Code

### B1a — Model id strings accepted (VERIFIED, code.claude.com/docs/model-config)

Aliases (for `--model`, `ANTHROPIC_MODEL`, settings `model`, subagent frontmatter `model`):

| Alias | Resolves to (Anthropic API) |
|---|---|
| `opus` | `claude-opus-4-8` (AWS Claude Platform: `claude-opus-4-7`) |
| `sonnet` | `claude-sonnet-4-6` |
| `haiku` | `claude-haiku-4-5` (full `claude-haiku-4-5-20251001`) |
| `fable` / `best` | `claude-fable-5` (CC v2.1.170+; `best` may be org-gated) |
| `opusplan` | opus in plan mode, sonnet in execution |
| `inherit` | subagent frontmatter only — use parent's model |

`[1m]` suffix on any alias/id → 1M context (e.g. `claude-opus-4-8[1m]`; CC strips before sending).
→ **Prefer aliases (`opus`/`sonnet`/`haiku`) over dated ids for the Claude tier map — more durable.**

### B1b — Plan / available-model detection (VERIFIED + gaps)

- `claude auth status` (JSON; `--text` human). Exits 0 logged-in / 1 not. **UNVERIFIED** whether JSON carries
  a parseable `plan`/tier field. `/status` in-session shows account info (not scriptable).
- No `claude config`/`claude plan` command for plan. Loose inference from `default` alias resolution:
  Max/Team-Premium/API → `claude-opus-4-8`; Pro/Team-Standard → `claude-sonnet-4-6`.
- Config/credential paths:

| File | Linux/WSL | macOS | Windows |
|---|---|---|---|
| User settings | `~/.claude/settings.json` | same | `%USERPROFILE%\.claude\settings.json` |
| Project / local | `.claude/settings.json` / `.local.json` | same | `.claude\...` |
| Credentials | `~/.claude/.credentials.json` (0600) | macOS Keychain | `%USERPROFILE%\.claude\.credentials.json` |
| Session/MCP | `~/.claude.json` (tokens — do not expose) | same | `%USERPROFILE%\.claude.json` |
| Managed | `/etc/claude-code/` | `/Library/Application Support/ClaudeCode/` | `C:\Program Files\ClaudeCode\` |

`CLAUDE_CONFIG_DIR` relocates `.credentials.json`. **Readable without secrets:** `settings.json` (model
prefs/hooks/permissions). **Never expose:** `.credentials.json`, `~/.claude.json`.

### B1c — Model spec precedence (VERIFIED)

Main session (high→low): `--model` > `ANTHROPIC_MODEL` env > managed settings > `.local.json` >
project `settings.json` > user `~/.claude/settings.json`.
Subagent: `CLAUDE_CODE_SUBAGENT_MODEL` env > per-invocation param > frontmatter `model` (default `inherit`)
> inherited main model.
Alias overrides: `ANTHROPIC_DEFAULT_{FABLE,OPUS,SONNET,HAIKU}_MODEL`.
**Native fallback:** `--fallback-model a,b` (≤3) / `fallbackModel` setting — applies on overload, not
auth/billing errors. → later "fallback routing" can lean on this rather than rebuilding it.
Enterprise: `availableModels` + `enforceAvailableModels` restrict the selectable set.

---

## Design implications for F-010

1. **Detection is concrete & cheap:** OpenCode = read `auth.json` + `opencode models`; Claude = read
   `~/.claude/settings.json`. Resolve paths via `opencode debug paths` / `~/.claude` per OS.
2. **`opencode models --verbose` populates the catalog's objective facts** (context/pricing/caps from
   models.dev). Hand-authoring shrinks to subjective scores + tier classing.
3. **Plan/quota is not detectable** → detect provider *presence*, not limits; quota/cost-optimizer is later.
4. **Claude tier map uses aliases** (`deep: opus`), not pinned dated ids.
5. **Both runtimes have native fallback** (Claude `--fallback-model`) → a seam to lean on later.
6. **Per-agent model string differs per runtime** → canonical id + per-(runtime,provider) translation;
   detection enumerates the real available strings to match against (no fragile string-construction rule).
